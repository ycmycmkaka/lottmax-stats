import pandas as pd
import os

def calculate_metrics(df):
    # 智能搵日期
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)

    # 搵號碼欄位 (n1-n7)
    num_cols = [c for c in df.columns if any(x in c.lower() for x in ['n', 'ball', 'number']) and any(str(i) in c for i in range(1, 8))]
    
    prev_numbers = set()
    results = []

    for _, row in df.iterrows():
        try:
            nums = sorted([int(row[c]) for c in num_cols])
            
            # 1. 強制標題名：odd_even
            odds = len([n for n in nums if n % 2 != 0])
            row['odd_even'] = f"{odds}O{7-odds}E"
            
            # 2. 強制標題名：consecutive
            has_consec = "No"
            for i in range(len(nums)-1):
                if nums[i+1] - nums[i] == 1:
                    has_consec = "Yes"
                    break
            row['consecutive'] = has_consec
            
            # 3. 強制標題名：repeats
            current_numbers = set(nums)
            row['repeats'] = len(current_numbers.intersection(prev_numbers)) if prev_numbers else 0
            prev_numbers = current_numbers
            
            # 4. 強制標題名：zone
            row['zone'] = f"Z{(nums[0]-1)//7 + 1}"
            
            results.append(row)
        except:
            continue

    final_df = pd.DataFrame(results)
    if date_col:
        final_df = final_df.sort_values(date_col, ascending=False)
    return final_df

def main():
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
        updated_df = calculate_metrics(df)
        updated_df.to_csv('data.csv', index=False)
        print("✅ 標題已統一並完成計算！")

if __name__ == "__main__":
    main()
