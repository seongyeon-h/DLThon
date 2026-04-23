import pandas as pd
import numpy as np

def finalize():
    print("=== Final Dataset Integration ===")
    
    # 1. Load Data
    train_threat = pd.read_csv('data/train_augmented_v1.csv')
    val_threat = pd.read_csv('data/val_holdout.csv')
    gen_synthetic = pd.read_csv('data/synthetic_general.csv')
    
    print(f"Loaded Threads: Train({len(train_threat)}), Val({len(val_threat)})")
    print(f"Loaded Synthetic General: {len(gen_synthetic)}")

    # 2. Split General into Train/Val (93% / 7% to match roughly 12000/800 ratio)
    # Target: 2800 for train, 200 for val
    val_gen = gen_synthetic.sample(n=200, random_state=42)
    train_gen = gen_synthetic.drop(val_gen.index)
    
    # 3. Combine
    train_final = pd.concat([train_threat, train_gen], ignore_index=True)
    val_final = pd.concat([val_threat, val_gen], ignore_index=True)
    
    # 4. Shuffle and Reset Index
    train_final = train_final.sample(frac=1, random_state=42).reset_index(drop=True)
    val_final = val_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Assign global idx
    train_final['idx'] = train_final.index
    val_final['idx'] = val_final.index
    
    # 5. Save
    train_final.to_csv('data/train_final.csv', index=False, encoding='utf-8-sig')
    val_final.to_csv('data/val_final.csv', index=False, encoding='utf-8-sig')
    
    print("\n--- Final Statistics ---")
    print("Train Dataset Distribution:")
    print(train_final['class'].value_counts())
    print("\nValidation Dataset Distribution:")
    print(val_final['class'].value_counts())
    
    print(f"\n✅ Total Train: {len(train_final)}")
    print(f"✅ Total Val: {len(val_final)}")
    print(f"Files saved: data/train_final.csv, data/val_final.csv")

if __name__ == "__main__":
    finalize()
