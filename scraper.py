import pandas as pd
import os

def calculate_metrics(df):
    # 1. 搵日期欄位 (唔理大細寫)
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col]).sort_values(date_col)

    # 2. 定義號碼欄位 (鎖定 n1, n2... n7)
    # 呢度我哋將標題全部轉細寫嚟搵，確保 100% 搵到
    cols_map = {c.lower().strip(): c for c in df.columns}
    target_cols = [cols_map[f'n{i}'] for i in range(1, 8) if f'n{i}' in cols_map]

    if len(target_cols) < 7:
        print(f"❌ 錯誤：喺 CSV 搵唔到 n1-n7 欄位！現有欄位：{list(df.columns)}")
        return df

    prev_numbers = set()
    results = []

    for _, row in df.iterrows():
        try:
            # 攞出 7 個號碼，並確保係整數
            nums = []
            for col in target_cols:
                val = str(row[col]).strip()
                if val and val.isdigit():
                    nums.append(int(val))
            
            if len(nums) < 7: continue # 數據唔夠就跳過
            nums.sort()
            
            # 單雙 (Odd/Even)
            odds = len([n for n in nums if n % 2 != 0])
            row['odd_even'] = f"{odds}O{7-odds}E"
            
            # 連續 (Consecutive)
            has_consec = "No"
            for i in range(len(nums)-1):
                if nums[i+1] - nums[i] == 1:
                    has_consec = "Yes"
                    break
            row['consecutive'] = has_consec
            
            # 上期重複 (Repeats)
            current_numbers = set(nums)
            row['repeats'] = len(current_numbers.intersection(prev_numbers)) if prev_numbers else 0
            prev_numbers = current_numbers
            
            # 自動分區 (Zone) - 每 7 個號碼一區
            row['zone'] = f"Z{(nums[0]-1)//7 + 1}"
            
            results.append(row)
        except Exception as e:
            print(f"跳過一行數據，原因: {e}")
            continue

    final_df = pd.DataFrame(results)
    if date_col:
        final_df = final_df.sort_values(date_col, ascending=False)
    return final_df

def main():
    if os.path.exists('data.csv'):
        try:
            df = pd.read_csv('data.csv')
            # 移除所有重複嘅 Row 費事撞
            df = df.drop_duplicates()
            updated_df = calculate_metrics(df)
            updated_df.to_csv('data.csv', index=False)
            print("✅ 成功！數據已完美更新。")
        except Exception as e:
            print(f"❌ 讀取 CSV 失敗: {e}")
    else:
        print("❌ 搵唔到 data.csv，請確認檔案名係咪正確。")

if __name__ == "__main__":
    main()
