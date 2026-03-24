import pandas as pd
import os

def calculate_metrics(df):
    # 1. 智能搵「日期」欄位
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
    else:
        print("警告：搵唔到日期欄位，將跳過排序。")

    # 2. 智能搵「號碼」欄位 (n1-n7 或 Number 1-7)
    num_cols = [c for c in df.columns if any(x in c.lower() for x in ['n', 'ball', 'number']) and any(str(i) in c for i in range(1, 8))]
    if len(num_cols) < 7:
        # 如果搵唔到 n1-n7，試下直接攞前 7 個數值欄位
        num_cols = df.select_dtypes(include=['number']).columns[:7].tolist()

    print(f"分析中：日期欄位=[{date_col}], 號碼欄位={num_cols}")

    prev_numbers = set()
    results = []

    for _, row in df.iterrows():
        try:
            # 攞出 7 個號碼
            nums = sorted([int(row[c]) for c in num_cols])
            
            # 單雙
            odds = len([n for n in nums if n % 2 != 0])
            row['odd_even'] = f"{odds}O{7-odds}E"
            
            # 連續
            has_consec = "No"
            for i in range(len(nums)-1):
                if nums[i+1] - nums[i] == 1:
                    has_consec = "Yes"
                    break
            row['consecutive'] = has_consec
            
            # 重複
            current_numbers = set(nums)
            row['repeats'] = len(current_numbers.intersection(prev_numbers)) if prev_numbers else 0
            prev_numbers = current_numbers
            
            results.append(row)
        except:
            # 跳過格式唔啱嘅 Row
            continue

    final_df = pd.DataFrame(results)
    if date_col:
        final_df = final_df.sort_values(date_col, ascending=False)
    return final_df

def main():
    if os.path.exists('data.csv'):
        try:
            df = pd.read_csv('data.csv')
            updated_df = calculate_metrics(df)
            updated_df.to_csv('data.csv', index=False)
            print("✅ 成功！數據已更新。")
        except Exception as e:
            print(f"❌ 錯誤：{e}")
    else:
        print("❌ 搵唔到 data.csv")

if __name__ == "__main__":
    main()
