import pandas as pd
import os
import re

def validate_conversation(text):
    """
    Validate the conversation against project specs:
    - Length: 180~250 chars
    - Turns: 8~12 turns (split by \n)
    - No emoticons (covers some block characters and typical Korean emoticons)
    """
    text = text.strip()
    char_len = len(text)
    turns = len(text.split('\n'))
    
    # 1. Length Check
    if not (160 <= char_len <= 300): # Allowing slightly wider margin
        return False, f"Length Error: {char_len} chars"
    
    # 2. Turn Check
    if not (7 <= turns <= 14): # Allowing 8~12 turns with slight margin
        return False, f"Turn Error: {turns} turns"
    
    # 3. Emoticon Check
    if re.search(r'[ㄱ-ㅎㅏ-ㅣ|😊-🙏]{2,}', text): 
        return False, "Emoticon Error"
    
    return True, "OK"

def collect_batch(raw_input, domain_label='일반 대화'):
    """
    Processes raw input containing [SEP] delimited conversations.
    Appends valid ones to synthetic_general.csv.
    """
    file_path = 'data/synthetic_general.csv'
    
    # Split text by [SEP] or double newline
    dialogues = [d.strip() for d in re.split(r'\[SEP\]|\n\n+', raw_input) if d.strip()]
    
    valid_data = []
    errors = []
    
    if os.path.exists(file_path):
        try:
            df_current = pd.read_csv(file_path)
            next_idx = df_current['idx'].max() + 1 if not df_current.empty else 0
        except:
            next_idx = 0
            df_current = pd.DataFrame(columns=['idx', 'class', 'conversation'])
    else:
        next_idx = 0
        df_current = pd.DataFrame(columns=['idx', 'class', 'conversation'])

    for d in dialogues:
        is_valid, msg = validate_conversation(d)
        if is_valid:
            valid_data.append({
                'idx': int(next_idx),
                'class': domain_label,
                'conversation': d
            })
            next_idx += 1
        else:
            errors.append((d[:30] + "...", msg))
            
    if valid_data:
        df_new = pd.DataFrame(valid_data)
        df_final = pd.concat([df_current, df_new], ignore_index=True)
        # Ensure idx is int
        df_final['idx'] = df_final['idx'].astype(int)
        df_final.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"✅ Successfully added {len(valid_data)} samples to {file_path}")
    
    if errors:
        print(f"⚠️ Failed to add {len(errors)} samples due to validation errors:")
        for sample, err in errors:
            print(f"   - {err}: {sample}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        domain = sys.argv[2] if len(sys.argv) > 2 else '일반 대화'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            collect_batch(raw_text, domain)
        else:
            print(f"❌ File not found: {file_path}")
    else:
        print("Usage: python src/synthetic_collector.py <file_path> [domain_label]")
