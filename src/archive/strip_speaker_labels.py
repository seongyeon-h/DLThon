import pandas as pd
import re

def strip_labels(file_path):
    print(f"Processing: {file_path}")
    df = pd.read_csv(file_path)
    
    # Regex pattern: 
    # ^([A-Z]):\s* -> Start of line, One uppercase letter, Colon, Optional spaces
    # We use re.MULTILINE to catch prefixes in the middle of the 'conversation' string (\n based)
    pattern = re.compile(r'^([A-Z]):\s*', re.MULTILINE)
    
    def cleaner(text):
        if not isinstance(text, str):
            return text
        return pattern.sub('', text)
    
    df['conversation'] = df['conversation'].apply(cleaner)
    
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Success: Stripped speaker labels from {file_path}")

if __name__ == "__main__":
    strip_labels('data/train_final.csv')
    strip_labels('data/val_final.csv')
