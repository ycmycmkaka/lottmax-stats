import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_web_data():
    all_draws = []
    current_year = datetime.now().year
    
    for year in range(current_year, current_year - 4, -1):
        url = f"https://www.lottomaxnumbers.com/numbers/{year}"
        print(f"📡 自動獲取緊 {year} 年嘅數據...")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                date_str = cols[0].get_text(strip=True)
                balls = []
                for element in cols[1].find_all(['li', 'div', 'span']):
                    txt = element.get_text(strip=True)
                    if txt.isdigit():
                        balls.append(int(txt))
                
                if len(balls) >= 7:
                    nums = sorted(balls[:7])
                    all_draws.append({
                        'date': date_str,
                        'n1': nums[0], 'n2': nums[1], 'n3': nums[2],
                        'n4': nums[3], 'n5': nums[4], 'n6': nums[5], 'n7': nums[6]
                    })
                    
    return pd.DataFrame(all_draws)

def calculate_metrics(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).drop_duplicates(subset=['date']).sort_values('date', ascending=True)
    
    prev_numbers = set()
    results = []
    
    for _, row in df.iterrows():
        nums = [int(row[f'n{i}']) for i in range(1, 8)]
        
        # 1. 單雙 (轉做直觀廣東話)
        odds = sum(1 for n in nums if n % 2 != 0)
        evens = 7 - odds
        row['odd_even'] = f"{odds}單 {evens}雙"
        
        # 2. 連續
        has_consec = "No"
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                has_consec = "Yes"
                break
        row['consecutive'] = has_consec
        
        # 3. 上期重複
        curr_set = set(nums)
        row['repeats'] = len(curr_set.intersection(prev_numbers)) if prev_numbers else 0
        prev_numbers = curr_set
        
        # 4. 精準分區 Zone (1-10為1區, 11-20為2區... 41-50為5區)
        zones_hit = set()
        for n in nums:
            zone_num = (n - 1) // 10 + 1
            zones_hit.add(zone_num)
        
        zones_list = sorted(list(zones_hit))
        # 顯示格式例如: "4個區 (1,3,4,5)"
        row['zone'] = f"{len(zones_list)}個區 ({','.join(map(str, zones_list))})"
        
        results.append(row)
        
    final_df = pd.DataFrame(results).sort_values('date', ascending=False)
    final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')
    return final_df

def main():
    print("🚀 啟動全自動網頁爬蟲...")
    df = get_web_data()
    
    if len(df) > 0:
        final_df = calculate_metrics(df)
        final_df.to_csv('data.csv', index=False)
        print(f"✅ 大功告成！成功分析 {len(final_df)} 期數據！")
    else:
        print("❌ 錯誤：爬唔到任何數據。")

if __name__ == "__main__":
    main()
