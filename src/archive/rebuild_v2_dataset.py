import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split

def forensic_clean(txt):
    if not isinstance(txt, str):
        return ""
    # 1. Flatten newlines
    txt = txt.replace('\n', ' ')
    # 2. Strip speaker labels (A:, B:, :)
    txt = re.sub(r'^[A-Z]:\s*', '', txt, flags=re.MULTILINE)
    txt = re.sub(r'\s[A-Z]:\s*', ' ', txt) # Labels in the middle
    # 3. Normalize whitespace
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt

def main():
    print("Starting Dataset Reconstruction v2...")
    
    # 1. Load Data
    df_org = pd.read_csv('data/train.csv')
    df_aug_threat = pd.read_csv('data/train_augmented_v1.csv')
    df_new_gen = pd.read_csv('data/synthetic_general_v2.csv')
    
    print(f"Loaded Original: {len(df_org)} rows")
    print(f"Loaded Augmented Threat: {len(df_aug_threat)} rows")
    print(f"Loaded New General: {len(df_new_gen)} rows")
    
    # 2. Filter original segments (Keep original threats as base)
    # The original train.csv has 4 classes (Threats). 
    # We will keep them all.
    df_org = df_org[['class', 'conversation']]
    df_aug_threat = df_aug_threat[['class', 'conversation']]
    df_new_gen = df_new_gen[['class', 'conversation']]
    
    # 3. Combine
    df_total = pd.concat([df_org, df_aug_threat, df_new_gen], ignore_index=True)
    
    # 4. Global Forensic Cleaning
    print("Applying global forensic cleaning (Flattening & Stripping)...")
    df_total['conversation'] = df_total['conversation'].apply(forensic_clean)
    
    # 5. Label Standardization
    df_total['class'] = df_total['class'].astype(str).str.strip()
    
    # 6. Quality Check: Remove duplicates
    before_dup = len(df_total)
    df_total = df_total.drop_duplicates(subset=['conversation'])
    print(f"Removed {before_dup - len(df_total)} duplicates.")
    
    # 7. Final Split (95% Train, 5% Val)
    train_df, val_df = train_test_split(
        df_total, 
        test_size=0.05, 
        random_state=42, 
        stratify=df_total['class']
    )
    
    print(f"\nFinal Distribution:")
    print(train_df['class'].value_counts())
    
    # 8. Save
    train_df.to_csv('data/train_final_v2.csv', index=False, encoding='utf-8-sig')
    val_df.to_csv('data/val_final_v2.csv', index=False, encoding='utf-8-sig')
    
    print("\n✅ Dataset Reconstruction Complete!")
    print(f"Train: data/train_final_v2.csv ({len(train_df)} rows)")
    print(f"Val: data/val_final_v2.csv ({len(val_df)} rows)")

if __name__ == "__main__":
    main()
