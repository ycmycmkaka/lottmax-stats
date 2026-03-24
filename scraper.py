import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def scrape_url(url, all_draws):
    print(f"📡 嘗試獲取數據: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 搵網頁入面所有嘅表格行
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                # 【清洗日期】用正則表達式強制鏟走 "Latest" 或 "*" 等字眼
                raw_date = cols[0].get_text(" ", strip=True)
                clean_date = re.sub(r'(?i)latest|\*', '', raw_date).strip()
                
                # 攞號碼
                balls = []
                for element in cols[1].find_all(['li', 'div', 'span']):
                    txt = element.get_text(strip=True)
                    if txt.isdigit():
                        balls.append(int(txt))
                
                # 確保有 7 個波先至記錄低
                if len(balls) >= 7:
                    nums = sorted(balls[:7])
                    all_draws.append({
                        'date': clean_date,
                        'n1': nums[0], 'n2': nums[1], 'n3': nums[2],
                        'n4': nums[3], 'n5': nums[4], 'n6': nums[5], 'n7': nums[6]
                    })
    except Exception as e:
        print(f"⚠️ 讀取 {url} 時發生錯誤: {e}")

def get_web_data():
    all_draws = []
    
    # 🌟 第一步：必定先去 past-numbers 攞最新鮮嘅數據 (解決 20 號失蹤問題)
    scrape_url("https://www.lottomaxnumbers.com/past-numbers", all_draws)
    
    # 🌟 第二步：去歷史年份表攞返過去 4 年嘅舊數據
    current_year = datetime.now().year
    for year in range(current_year, current_year - 4, -1):
        scrape_url(f"https://www.lottomaxnumbers.com/numbers/{year}", all_draws)
            
    return pd.DataFrame(all_draws)

def calculate_metrics(df):
    # 將日期轉做標準格式，如果出錯就變 NaN
    df['date_obj'] = pd.to_datetime(df['date'], errors='coerce')
    
    # 鏟走日期無效嘅行，然後排好時間
    df = df.dropna(subset=['date_obj']).sort_values('date_obj', ascending=True)
    
    # 🌟 關鍵：因為我哋爬咗兩個網頁，實有重複，呢句會自動幫你鏟走相同日期嘅多餘數據
    df = df.drop_duplicates(subset=['date_obj'], keep='first')
    
    prev_numbers = set()
    results = []
    
    for _, row in df.iterrows():
        nums = [int(row[f'n{i}']) for i in range(1, 8)]
        
        # 單雙
        odds = sum(1 for n in nums if n % 2 != 0)
        row['odd_even'] = f"{odds}單 {7-odds}雙"
        
        # 連續
        has_consec = "No"
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                has_consec = "Yes"
                break
        row['consecutive'] = has_consec
        
        # 上期重複
        curr_set = set(nums)
        row['repeats'] = len(curr_set.intersection(prev_numbers)) if prev_numbers else 0
        prev_numbers = curr_set
        
        # 精準分區 Zone
        zones_hit = set([(n - 1) // 10 + 1 for n in nums])
        zones_list = sorted(list(zones_hit))
        row['zone'] = f"{len(zones_list)}個區 ({','.join(map(str, zones_list))})"
        
        results.append(row)
        
    # 排返由最新一期開始顯示
    final_df = pd.DataFrame(results).sort_values('date_obj', ascending=False)
    final_df['date'] = final_df['date_obj'].dt.strftime('%Y-%m-%d')
    
    # 淨低你要用嘅欄位
    cols_to_keep = ['date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'odd_even', 'consecutive', 'repeats', 'zone']
    return final_df[cols_to_keep]

def main():
    print("🚀 啟動「雙管齊下」全自動網頁爬蟲...")
    df = get_web_data()
    
    if len(df) > 0:
        final_df = calculate_metrics(df)
        final_df.to_csv('data.csv', index=False)
        print(f"✅ 大功告成！全自動抓取並分析咗 {len(final_df)} 期數據！")
    else:
        print("❌ 錯誤：爬唔到任何數據。")

if __name__ == "__main__":
    main()
