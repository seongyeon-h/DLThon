import pandas as pd
import re

def identify_prefixes(file_path):
    df = pd.read_csv(file_path)
    # Only check classes that were synthesized or augmented
    gen_df = df[df['class'] == '일반 대화']
    
    # Regex to find anything at the start of a line ending with a colon
    prefix_pattern = re.compile(r'^([^:\n]+):', re.MULTILINE)
    
    all_prefixes = []
    for text in gen_df['conversation']:
        all_prefixes.extend(prefix_pattern.findall(text))
        
    unique_prefixes = set(all_prefixes)
    print(f"File: {file_path}")
    print(f"Unique Prefixes Found: {unique_prefixes}")
    return unique_prefixes

if __name__ == "__main__":
    identify_prefixes('data/train_final.csv')
