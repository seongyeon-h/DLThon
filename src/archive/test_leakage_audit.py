import pandas as pd
import os
import re

def normalize_text(text):
    """공백 및 특수문자 제거하여 비교 강도 높임"""
    text = re.sub(r'[^가-힣A-Za-z0-9]', '', str(text))
    return text

def get_jaccard_sim(str1, str2):
    """단어 집합 기준 자카드 유사도 계산"""
    a = set(str1.split())
    b = set(str2.split())
    if not a or not b: return 0
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def audit_leakage():
    data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
    chunks = [f"synthetic_general_v4.5_chunk{i}.csv" for i in range(1, 21)]
    test_path = os.path.join(data_dir, "test.csv")
    
    if not os.path.exists(test_path):
        print("Error: test.csv not found.")
        return

    # 1. 테스트셋 로드 & 정규화
    df_test = pd.read_csv(test_path)
    test_texts = df_test['conversation'].tolist()
    test_normalized = [normalize_text(t) for t in test_texts]
    
    # 2. 모든 합성 데이터 로드
    all_synthetic = []
    for chunk_file in chunks:
        path = os.path.join(data_dir, chunk_file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            all_synthetic.extend(df['conversation'].tolist())
    
    print(f"Auditing {len(all_synthetic)} synthetic samples against {len(test_texts)} test samples...")
    
    exact_matches = 0
    high_similarity = []
    
    for i, syn_text in enumerate(all_synthetic):
        syn_norm = normalize_text(syn_text)
        
        for j, test_text in enumerate(test_texts):
            # (1) 완전 일치 확인
            if syn_norm == test_normalized[j]:
                exact_matches += 1
                print(f"[ALERT] Exact Match found between SynIdx {i} and TestID t_{j:03d}")
                continue
                
            # (2) 유사도 확인 (단어 기준 60% 이상이면 위험)
            sim = get_jaccard_sim(syn_text, test_text)
            if sim > 0.6:
                high_similarity.append({
                    'syn_idx': i,
                    'test_id': f"t_{j:03d}",
                    'sim': sim,
                    'syn_content': syn_text[:50],
                    'test_content': test_text[:50]
                })

    print("\n[Audit Results]")
    print(f"- Exact Matches: {exact_matches}")
    print(f"- High Similarity (>60%): {len(high_similarity)}")
    
    if high_similarity:
        print("\n[Sample High Similarity Pairs]")
        for pair in high_similarity[:5]:
            print(f"- Test {pair['test_id']} vs Syn {pair['syn_idx']} (Sim: {pair['sim']:.2f})")
            print(f"  Test: {pair['test_content']}...")
            print(f"  Syn:  {pair['syn_content']}...")

if __name__ == "__main__":
    audit_leakage()
