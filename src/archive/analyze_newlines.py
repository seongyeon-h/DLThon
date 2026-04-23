import pandas as pd
import os

def analyze_newlines(file_path, label=""):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    print(f"\n=== Analyzing {label} ({file_path}) ===")
    
    if 'class' in df.columns:
        for cls in df['class'].unique():
            samples = df[df['class'] == cls]['conversation']
            avg_newlines = samples.apply(lambda x: str(x).count('\n')).mean()
            print(f"Class: {cls:20} | Avg Newlines: {avg_newlines:.2f}")
            print(f"Sample (repr): {repr(samples.iloc[0])[:150]}...")
    else:
        # Assuming it's test data
        samples = df['conversation']
        avg_newlines = samples.apply(lambda x: str(x).count('\n')).mean()
        print(f"Test Data            | Avg Newlines: {avg_newlines:.2f}")
        print(f"Sample (repr): {repr(samples.iloc[0])[:150]}...")

if __name__ == "__main__":
    analyze_newlines('data/train_final.csv', "Final Train")
    analyze_newlines('data/test.csv', "Test Data")
    analyze_newlines('data/train.csv', "Original Train")
