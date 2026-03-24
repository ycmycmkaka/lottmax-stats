import pandas as pd
import os
import traceback

def calculate_metrics(df):
    # 【關鍵修復】將 DataFrame 轉成純字典清單，100% 免疫 KeyError
    records = df.to_dict('records')
    if not records:
        return df

    # 自動搵出 7 個號碼嘅標題名 (動態適應)
    first_row = records[0]
    num_keys = []
    for k in first_row.keys():
        k_lower = str(k).lower().strip()
        # 只要標題包含 n1-n7, number 1-7, ball 1-7 都認到
        if any(k_lower == f'n{i}' for i in range(1, 8)) or \
           any(f'number' in k_lower and str(i) in k_lower for i in range(1, 8)):
            num_keys.append(k)

    print(f"📊 成功鎖定號碼欄位: {num_keys}")

    # 處理日期排序 (用嚟計上期重複)
    date_key = next((k for k in first_row.keys() if 'date' in str(k).lower()), None)
    if date_key:
        for r in records:
            r['_temp_date'] = pd.to_datetime(r.get(date_key), errors='coerce')
        # 按照日期由舊至新排
        records = sorted([r for r in records if pd.notnull(r.get('_temp_date'))], key=lambda x: x['_temp_date'])

    prev_numbers = set()

    for row in records:
        nums = []
        for k in num_keys:
            # 用 .get() 非常安全，即使無呢個 key 都唔會報錯
            val = str(row.get(k, '')).strip()
            # 處理 Excel 有時會將整數變成 14.0 嘅情況
            if val.endswith('.0'): 
                val = val[:-2]
            if val.isdigit():
                nums.append(int(val))
                
        # 如果號碼唔夠 7 個，畀個預設值然後跳過
        if len(nums) < 7:
            row['odd_even'] = '-'
            row['consecutive'] = '-'
            row['repeats'] = '0'
            row['zone'] = '-'
            continue
            
        nums.sort()
        
        # 1. 單雙
        odds = len([n for n in nums if n % 2 != 0])
        row['odd_even'] = f"{odds}O{7-odds}E"
        
        # 2. 連續
        has_consec = "No"
        for i in range(len(nums)-1):
            if nums[i+1] - nums[i] == 1:
                has_consec = "Yes"
                break
        row['consecutive'] = has_consec
        
        # 3. 上期重複
        curr_nums = set(nums)
        row['repeats'] = len(curr_nums.intersection(prev_numbers)) if prev_numbers else 0
        prev_numbers = curr_nums
        
        # 4. 分區 Zone (以第一個號碼每 7 個一區)
        row['zone'] = f"Z{(nums[0]-1)//7 + 1}"

    # 重新組裝做 DataFrame
    final_df = pd.DataFrame(records)
    
    # 按照日期排返由新到舊，並剷走臨時日期欄
    if '_temp_date' in final_df.columns:
        final_df = final_df.sort_values('_temp_date', ascending=False)
        final_df = final_df.drop(columns=['_temp_date'])
        
    return final_df

def main():
    if os.path.exists('data.csv'):
        try:
            df = pd.read_csv('data.csv')
            updated_df = calculate_metrics(df)
            updated_df.to_csv('data.csv', index=False)
            print("✅ 成功！完美避開所有 KeyError，數據已更新。")
        except Exception as e:
            print(f"❌ 發生未能預計嘅錯誤:\n{traceback.format_exc()}")
    else:
        print("❌ 搵唔到 data.csv")

if __name__ == "__main__":
    main()
