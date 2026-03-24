import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_web_data():
    all_draws = []
    current_year = datetime.now().year
    
    # 自動爬取過去 4 年嘅開彩數據
    for year in range(current_year, current_year - 4, -1):
        url = f"https://www.lottomaxnumbers.com/numbers/{year}"
        print(f"📡 自動獲取緊 {year} 年嘅數據...")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 喺網頁 HTML 入面搵開彩表格
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                # 1. 攞日期
                date_str = cols[0].get_text(strip=True)
                
                # 2. 攞號碼波波
                balls = []
                for element in cols[1].find_all(['li', 'div', 'span']):
                    txt = element.get_text(strip=True)
                    if txt.isdigit():
                        balls.append(int(txt))
                
                # 3. 確保抽齊 7 個號碼
                if len(balls) >= 7:
                    nums = sorted(balls[:7])
                    all_draws.append({
                        'date': date_str,
                        'n1': nums[0], 'n2': nums[1], 'n3': nums[2],
                        'n4': nums[3], 'n5': nums[4], 'n6': nums[5], 'n7': nums[6]
                    })
                    
    return pd.DataFrame(all_draws)

def calculate_metrics(df):
    # 排好日期，由舊到新
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).drop_duplicates(subset=['date']).sort_values('date', ascending=True)
    
    prev_numbers = set()
    results = []
    
    for _, row in df.iterrows():
        nums = [int(row[f'n{i}']) for i in range(1, 8)]
        
        # 統計 1: 單雙
        odds = sum(1 for n in nums if n % 2 != 0)
        row['odd_even'] = f"{odds}O{7-odds}E"
        
        # 統計 2: 連續
        has_consec = "No"
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                has_consec = "Yes"
                break
        row['consecutive'] = has_consec
        
        # 統計 3: 上期重複
        curr_set = set(nums)
        row['repeats'] = len(curr_set.intersection(prev_numbers)) if prev_numbers else 0
        prev_numbers = curr_set
        
        # 統計 4: 分區 Zone
        row['zone'] = f"Z{(nums[0]-1)//7 + 1}"
        
        results.append(row)
        
    # 最後排返由新到舊
    final_df = pd.DataFrame(results).sort_values('date', ascending=False)
    final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')
    return final_df

def main():
    print("🚀 啟動全自動網頁爬蟲...")
    df = get_web_data()
    
    if len(df) > 0:
        final_df = calculate_metrics(df)
        final_df.to_csv('data.csv', index=False)
        print(f"✅ 大功告成！成功上網獲取並分析咗 {len(final_df)} 期 Lotto Max 數據！")
    else:
        print("❌ 錯誤：爬唔到任何數據。")

if __name__ == "__main__":
    main()
