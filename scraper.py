import pandas as pd
import os

def calculate_metrics(df):
    # 確保按日期排序（由舊到新），方便計「上期重複」
    df['Draw Date'] = pd.to_datetime(df['Draw Date'])
    df = df.sort_values('Draw Date')
    
    prev_numbers = set()
    
    # 呢度定義 Zone 邏輯（例如 1-7 號係 Zone 1，8-14 號係 Zone 2...）
    # 你可以之後按你 Excel 嘅規則修改呢度
    def get_zone(nums):
        # 簡單範例：攞第一個號碼嚟分區
        first_num = nums[0]
        return f"Zone {(first_num-1)//7 + 1}"

    results = []
    for _, row in df.iterrows():
        # 攞出 7 個號碼
        nums = sorted([int(row[f'n{i}']) for i in range(1, 8)])
        
        # 1. 單雙 (Odd/Even)
        odds = len([n for n in nums if n % 2 != 0])
        row['odd_even'] = f"{odds}O{7-odds}E"
        
        # 2. 連續 (Consecutive)
        has_consec = "No"
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                has_consec = "Yes"
                break
        row['consecutive'] = has_consec
        
        # 3. 上期重複 (Repeats)
        current_numbers = set(nums)
        row['repeats'] = len(current_numbers.intersection(prev_numbers)) if prev_numbers else 0
        prev_numbers = current_numbers
        
        # 4. Zone (自動計 Zone)
        row['Zone'] = get_zone(nums)
        
        results.append(row)

    # 計完之後排返轉頭，最新嘅擺最頂
    return pd.DataFrame(results).sort_values('Draw Date', ascending=False)

def main():
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
        # 執行計算
        updated_df = calculate_metrics(df)
        # 儲存覆蓋原本個 CSV
        updated_df.to_csv('data.csv', index=False)
        print("✅ 數據統計計算完成！")
    else:
        print("❌ 搵唔到 data.csv")

if __name__ == "__main__":
    main()
