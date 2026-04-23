import pandas as pd

def forensic_check(file_path, name):
    df = pd.read_csv(file_path)
    print(f"\n--- {name} ({file_path}) ---")
    
    if 'class' in df.columns:
        for cls in df['class'].unique():
            sample = str(df[df['class'] == cls].iloc[0]['conversation'])
            print(f"Class: [{cls}]")
            print(f"  - Length: {len(sample)}")
            print(f"  - Newline count: {sample.count('\n')}")
            print(f"  - Repr (first 100): {repr(sample)[:100]}...")
    else:
        sample = str(df.iloc[0]['conversation'])
        print(f"Test Data")
        print(f"  - Length: {len(sample)}")
        print(f"  - Newline count: {sample.count('\n')}")
        print(f"  - Repr (first 100): {repr(sample)[:100]}...")

if __name__ == "__main__":
    forensic_check('data/train_final.csv', "Train Final")
    forensic_check('data/test.csv', "Test Data")
