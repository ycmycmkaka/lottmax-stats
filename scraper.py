import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_web_data():
    all_draws = []
    current_year = datetime.now().year
    
    # 全自動去網上爬過去 4 年嘅數據
    for year in range(current_year, current_year - 4, -1):
        url = f"https://www.lottomaxnumbers.com/numbers/{year}"
        print(f"📡 自動獲取緊 {year} 年嘅數據...")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # 【核心過濾】用 Regex 自動清走日期旁邊嘅 "Latest" 或 "*" 等干擾字眼
                    raw_date = cols[0].get_text(" ", strip=True)
                    clean_date = re.sub(r'(?i)latest|\*', '', raw_date).strip()
                    
                    balls = []
                    for element in cols[1].find_all(['li', 'div', 'span']):
                        txt = element.get_text(strip=True)
                        if txt.isdigit():
                            balls.append(int(txt))
                    
                    if len(balls) >= 7:
                        nums = sorted(balls[:7])
                        all_draws.append({
                            'date': clean_date,
                            'n1': nums[0], 'n2': nums[1], 'n3': nums[2],
                            'n4': nums[3], 'n5': nums[4], 'n6': nums[5], 'n7': nums[6]
                        })
        except Exception as e:
            print(f"⚠️ 讀取 {year} 年網頁時發生錯誤: {e}")
            
    return pd.DataFrame(all_draws)

def calculate_metrics(df):
    # 處理日期，排好次序
    df['date_obj'] = pd.to_datetime(df['date'], errors='coerce')
    # 剷走無效日期，然後剷走重複
    df = df.dropna(subset=['date_obj']).sort_values('date_obj', ascending=True)
    df = df.drop_duplicates(subset=['date_obj'], keep='first')
    
    prev_numbers = set()
    results = []
    
    for _, row in df.iterrows():
        nums = [int(row[f'n{i}']) for i in range(1, 8)]
        
        # 1. 單雙
        odds = sum(1 for n in nums if n % 2 != 0)
        row['odd_even'] = f"{odds}單 {7-odds}雙"
        
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
        
        # 4. 精準分區 Zone
        zones_hit = set([(n - 1) // 10 + 1 for n in nums])
        zones_list = sorted(list(zones_hit))
        row['zone'] = f"{len(zones_list)}個區 ({','.join(map(str, zones_list))})"
        
        results.append(row)
        
    # 排返由新到舊
    final_df = pd.DataFrame(results).sort_values('date_obj', ascending=False)
    final_df['date'] = final_df['date_obj'].dt.strftime('%Y-%m-%d')
    
    # 淨係保留要用嘅欄位
    cols_to_keep = ['date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'odd_even', 'consecutive', 'repeats', 'zone']
    return final_df[cols_to_keep]

def main():
    print("🚀 啟動 100% 全自動網頁爬蟲...")
    df = get_web_data()
    
    if len(df) > 0:
        final_df = calculate_metrics(df)
        final_df.to_csv('data.csv', index=False)
        print(f"✅ 大功告成！全自動抓取並分析咗 {len(final_df)} 期數據！")
    else:
        print("❌ 錯誤：爬唔到任何數據。")

if __name__ == "__main__":
    main()
