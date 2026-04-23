import pandas as pd

def fix_leakage():
    print("=== Fixing Data Leakage (Leakage Recovery) ===")
    
    # 1. Load data
    train = pd.read_csv('data/train_final.csv')
    val = pd.read_csv('data/val_final.csv')
    
    print(f"Original Train: {len(train)}")
    print(f"Original Val: {len(val)}")
    
    # 2. Identify and Remove Duplicates from Train (Keep Val pure)
    val_conversations = set(val['conversation'])
    train_cleaned = train[~train['conversation'].isin(val_conversations)].copy()
    
    # Also check for internal duplicates in train/val just in case
    train_cleaned = train_cleaned.drop_duplicates(subset=['conversation'])
    val_cleaned = val.drop_duplicates(subset=['conversation'])
    
    print(f"\nCleaned Train: {len(train_cleaned)} (Removed {len(train) - len(train_cleaned)} rows)")
    print(f"Cleaned Val: {len(val_cleaned)} (Removed {len(val) - len(val_cleaned)} rows)")
    
    # 3. Final Check
    new_overlap = set(train_cleaned['conversation']) & set(val_cleaned['conversation'])
    print(f"New Overlap size: {len(new_overlap)}")
    
    # 4. Save
    train_cleaned['idx'] = range(len(train_cleaned))
    val_cleaned['idx'] = range(len(val_cleaned))
    
    train_cleaned.to_csv('data/train_final.csv', index=False, encoding='utf-8-sig')
    val_cleaned.to_csv('data/val_final.csv', index=False, encoding='utf-8-sig')
    
    print("\n✅ Leakage fixed. Files updated.")

if __name__ == "__main__":
    fix_leakage()
