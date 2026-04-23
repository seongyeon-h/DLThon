import pandas as pd

def flatten_conversation(file_path):
    print(f"Flattening: {file_path}")
    df = pd.read_csv(file_path)
    
    def strip_newlines(text):
        if not isinstance(text, str):
            return text
        # Replace newlines with a single space and collapse multiple spaces
        text = text.replace('\n', ' ')
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    df['conversation'] = df['conversation'].apply(strip_newlines)
    
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Success: Flattened {file_path}")

if __name__ == "__main__":
    flatten_conversation('data/train_final.csv')
    flatten_conversation('data/val_final.csv')
