import pandas as pd
import re

def check_datasets():
    print("=== DLThon Dataset Quality Verification ===")
    
    # Load datasets
    train = pd.read_csv('data/train_augmented_v1.csv')
    val = pd.read_csv('data/val_holdout.csv')
    
    # 1. Leakage Check
    overlap = set(train['conversation']) & set(val['conversation'])
    leakage_ok = len(overlap) == 0
    print(f"[1] Data Leakage Check: {'PASS' if leakage_ok else 'FAIL'}")
    if not leakage_ok:
        print(f"    - Found {len(overlap)} overlapping conversations.")

    # 2. Class Balance Check
    print("\n[2] Class Balance (Train):")
    print(train['class'].value_counts())
    print("\n[2] Class Balance (Val):")
    print(val['class'].value_counts())

    # 3. Keyword Preservation Check (Step 4 & 6)
    CORE_KEYWORDS = ["제발", "죽어", "죽여", "당장", "돈", "안돼", "부장님", "죄송"]
    print("\n[3] Keyword Preservation (Sample Check):")
    # Check if augmented samples still contain core keywords compared to original intents
    # This is qualitative, but we can check if keywords exist in augmented data
    threat_classes = ['협박 대화', '갈취 대화', '직장 내 괴롭힘 대화', '기타 괴롭힘 대화']
    for cls in threat_classes:
        subset = train[train['class'] == cls]
        keyword_hits = subset['conversation'].str.contains('|'.join(CORE_KEYWORDS)).sum()
        hit_rate = (keyword_hits / len(subset)) * 100
        print(f"    - {cls}: Keyword Hit Rate {hit_rate:.1f}%")

    # 4. Special Character Check (Step 6)
    print("\n[4] Special Character Pattern (!, ?):")
    for df_name, df_obj in [("Train", train), ("Val", val)]:
        exclaim_rate = df_obj['conversation'].str.count('!').mean()
        question_rate = df_obj['conversation'].str.count(r'\?').mean()
        print(f"    - {df_name} Avg (!): {exclaim_rate:.2f}, Avg (?): {question_rate:.2f}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    check_datasets()
