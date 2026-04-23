import pandas as pd
import os

def get_dataset_profile(file_path, label):
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    # Extract sample from General class if it exists (for Train/Val) or first row for Test
    if 'class' in df.columns:
        gen_sample = str(df[df['class'] == '일반 대화'].iloc[0]['conversation']) if '일반 대화' in df['class'].unique() else str(df.iloc[0]['conversation'])
    else:
        gen_sample = str(df.iloc[0]['conversation'])
        
    return {
        "Dataset": label,
        "Columns": ", ".join(df.columns),
        "Newline Count": gen_sample.count('\n'),
        "Speaker Labels (A:, B:)": ("A:" in gen_sample or "B:" in gen_sample),
        "Avg Length": int(df['conversation'].apply(lambda x: len(str(x))).mean()),
        "Sample Preview": repr(gen_sample)[:80] + "..."
    }

if __name__ == "__main__":
    profiles = []
    profiles.append(get_dataset_profile('data/train_final.csv', "Train (Final)"))
    profiles.append(get_dataset_profile('data/val_final.csv', "Val (Final)"))
    profiles.append(get_dataset_profile('data/test.csv', "Test (Real)"))
    
    report = pd.DataFrame([p for p in profiles if p is not None])
    print("\n" + "="*80)
    print("FINAL DATASET ALIGNMENT REPORT")
    print("="*80)
    print(report.to_string(index=False))
    print("="*80)
