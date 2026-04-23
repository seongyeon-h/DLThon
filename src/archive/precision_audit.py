import pandas as pd
import re
from collections import Counter

def get_stats(df, label):
    conversations = df['conversation'].astype(str)
    char_lens = conversations.apply(len)
    word_counts = conversations.apply(lambda x: len(x.split()))
    # Check for punctuation patterns common in bullying (e.g. repeated !, ?)
    excl_counts = conversations.apply(lambda x: x.count('!'))
    ques_counts = conversations.apply(lambda x: x.count('?'))
    
    return {
        "Dataset": label,
        "Samples": len(df),
        "Avg Chars": int(char_lens.mean()),
        "Avg Words": int(word_counts.mean()),
        "Avg ! count": round(excl_counts.mean(), 2),
        "Avg ? count": round(ques_counts.mean(), 2),
        "Max Length": char_lens.max()
    }

def precision_audit():
    train_df = pd.read_csv('data/train_final.csv')
    val_df = pd.read_csv('data/val_final.csv')
    test_df = pd.read_csv('data/test.csv')
    
    stats = []
    stats.append(get_stats(train_df, "Train (Final)"))
    stats.append(get_stats(val_df, "Val (Final)"))
    stats.append(get_stats(test_df, "Test (Real)"))
    
    report_df = pd.DataFrame(stats)
    
    print("\n" + "="*85)
    print("FINAL PRECISION AUDIT REPORT: TRAIN vs VAL vs TEST")
    print("="*85)
    print(report_df.to_string(index=False))
    print("-" * 85)
    
    # Check for lexical overlap/consistency (Top 20 non-stopwords)
    def get_top_tokens(df, top_n=50):
        all_text = " ".join(df['conversation'].astype(str))
        tokens = [t for t in re.findall(r'[가-힣]+', all_text) if len(t) > 1]
        return set([t for t, c in Counter(tokens).most_common(top_n)])

    train_top = get_top_tokens(train_df)
    test_top = get_top_tokens(test_df)
    overlap = train_top.intersection(test_top)
    
    print(f"Lexical Overlap Score: {len(overlap)} / {len(test_top)} (Top 50 keywords)")
    print(f"Overlap Examples: {list(overlap)[:10]}")
    print("="*85)
    
    # Final Sanity Check for hidden markers in test
    print("\n[Test Data Hidden Marker Check (Repr)]")
    samples = test_df['conversation'].iloc[:3].apply(repr).tolist()
    for i, s in enumerate(samples):
        print(f"Sample {i}: {s[:150]}...")

if __name__ == "__main__":
    precision_audit()
