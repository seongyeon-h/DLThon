import pandas as pd
import numpy as np
import re

def analyze_dataset(file_path, label_name):
    df = pd.read_csv(file_path)
    print(f"--- {label_name} Analysis ---")
    
    # 1. Basic Stats
    print(f"Total Rows: {len(df)}")
    print("Class Distribution:")
    print(df['class'].value_counts())
    
    # 2. Length Stats
    df['char_len'] = df['conversation'].str.len()
    df['turn_count'] = df['conversation'].str.count('\n') + 1
    
    stats = df.groupby('class')[['char_len', 'turn_count']].agg(['mean', 'std'])
    print("\nLength Stats by Class:")
    print(stats)
    
    # 3. Keyword Check (Hard Negatives)
    CORE_KEYWORDS = ["제발", "죽어", "죽여", "당장", "돈", "안돼", "부장님", "죄송"]
    print("\nKeyword Frequency by Class (Percentage found):")
    for kw in CORE_KEYWORDS:
        df[kw] = df['conversation'].str.contains(kw)
        
    keyword_summary = df.groupby('class')[CORE_KEYWORDS].mean() * 100
    print(keyword_summary)
    
    return df

def check_leakage(train, val):
    print("\n--- Leakage & Integrity Check ---")
    overlap = set(train['conversation']) & set(val['conversation'])
    print(f"Overlapping conversations (Exact): {len(overlap)}")
    
    # Check for empty or too short strings
    empty_train = train[train['conversation'].str.len() < 10]
    empty_val = val[val['conversation'].str.len() < 10]
    print(f"Suspiciously short conversations: Train({len(empty_train)}), Val({len(empty_val)})")

if __name__ == "__main__":
    train_df = analyze_dataset('data/train_final_v3.csv', 'Final Training Set V3')
    print("\n" + "="*50 + "\n")
    val_df = analyze_dataset('data/val_final_v3.csv', 'Final Validation Set V3')
    check_leakage(train_df, val_df)
