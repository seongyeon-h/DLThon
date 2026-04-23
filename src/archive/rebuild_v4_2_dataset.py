import pandas as pd
import os
import re
import random
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

def inject_global_noise(txt, space_strip_prob=0.15):
    """Randomly removes spaces to mimic 'No Space' raw chat style."""
    if random.random() > 0.4: # Only apply noise to 40% of the total dataset
        return txt
    
    words = txt.split()
    new_words = []
    for i, w in enumerate(words):
        if i > 0 and random.random() < space_strip_prob:
            new_words[-1] = new_words[-1] + w
        else:
            new_words.append(w)
    return "".join(new_words) if random.random() < 0.05 else " ".join(new_words) # 5% extreme no-space

def main():
    print("Starting Dataset Reconstruction v4.2 (Street-Style Alignment)...")
    
    # 1. Load Data
    df_org = pd.read_csv('data/train.csv')
    df_aug_threat = pd.read_csv('data/train_augmented_v1.csv')
    df_new_gen = pd.read_csv('data/synthetic_general_v4_2.csv')
    
    print(f"Loaded Original: {len(df_org)} rows")
    print(f"Loaded Augmented Threat: {len(df_aug_threat)} rows")
    print(f"Loaded New General Street-Style: {len(df_new_gen)} rows")
    
    # 2. Extract relative columns
    df_org = df_org[['class', 'conversation']]
    df_aug_threat = df_aug_threat[['class', 'conversation']]
    df_new_gen = df_new_gen[['class', 'conversation']]
    
    # 3. Combine
    df_total = pd.concat([df_org, df_aug_threat, df_new_gen], ignore_index=True)
    
    # 4. Global Forensic Cleaning
    print("Applying global forensic cleaning...")
    df_total['conversation'] = df_total['conversation'].apply(forensic_clean)
    
    # 5. NOISE INJECTION (CRITICAL FOR TEST SET ROBUSTNESS)
    print("Injecting 'Street-Style' Noise (Space stripping)...")
    df_total['conversation'] = df_total['conversation'].apply(inject_global_noise)
    
    # 6. Label Standardization
    df_total['class'] = df_total['class'].astype(str).str.strip()
    
    # 7. Quality Check: Remove duplicates
    before_dup = len(df_total)
    df_total = df_total.drop_duplicates(subset=['conversation'])
    print(f"Removed {before_dup - len(df_total)} exact duplicates.")
    
    # 8. Final Split (95% Train, 5% Val)
    train_df, val_df = train_test_split(
        df_total, 
        test_size=0.05, 
        random_state=42, 
        stratify=df_total['class']
    )
    
    print("\nFinal Distribution (v4.2):")
    print(train_df['class'].value_counts())
    
    # 9. Save
    train_df.to_csv('data/train_final_v4_2.csv', index=False, encoding='utf-8-sig')
    val_df.to_csv('data/val_final_v4_2.csv', index=False, encoding='utf-8-sig')
    
    print("\nDataset Reconstruction Complete (v4.2)!")
    print(f"Train: data/train_final_v4_2.csv ({len(train_df)} rows)")
    print(f"Val: data/val_final_v4_2.csv ({len(val_df)} rows)")

if __name__ == "__main__":
    main()
