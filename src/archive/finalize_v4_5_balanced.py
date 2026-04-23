import pandas as pd
import random
import os
from tqdm import tqdm

# [1] 증강 로직 및 옵션 설정 (baseline_dataset.ipynb 계승)
CORE_KEYWORDS = [
    "제발", "죽어", "죽여", "당장", "돈", "안돼", "부장님", "죄송", 
    "나오면", "다", "해", "맞을래", "조용히", "기다려", "진짜", "가지고"
]
FILLERS = ["진짜", "아니", "그러니까", "좀", "막", "근데"]

def sentence_shuffle(text):
    """[RS] 대화 내 인접 문장 순서 교체"""
    sentences = text.split('\n')
    if len(sentences) < 3:
        return text
    idx = random.randint(0, len(sentences) - 2)
    sentences[idx], sentences[idx+1] = sentences[idx+1], sentences[idx]
    return '\n'.join(sentences)

def random_deletion_safe(text, p=0.1):
    """[RD] 핵심 키워드 보호하며 무작위 단어 삭제"""
    words = text.split()
    if len(words) < 10:
        return text
    new_words = []
    for word in words:
        is_core = any(core in word for core in CORE_KEYWORDS)
        if not is_core and random.random() < p:
            continue
        new_words.append(word)
    return ' '.join(new_words)

def random_insertion(text, p=0.1):
    """[RI] 일상 어구 삽입"""
    words = text.split()
    if random.random() < p:
        insert_idx = random.randint(0, len(words))
        words.insert(insert_idx, random.choice(FILLERS))
    return ' '.join(words)

def augment_text(text):
    """통합 증강 디스패처 (RS, RD, RI 중 1~2개 적용)"""
    methods = [sentence_shuffle, random_deletion_safe, random_insertion]
    selected_methods = random.sample(methods, random.randint(1, 2))
    for method in selected_methods:
        text = method(text)
    return text

# [2] 데이터 로드 및 분리 로직
def finalize_dataset():
    data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
    chunks = [f"synthetic_general_v4.5_chunk{i}.csv" for i in range(1, 21)]
    
    val_list = []
    train_core_list = []
    
    print("Step 1: Collecting and Splitting Chunks...")
    for chunk_file in chunks:
        path = os.path.join(data_dir, chunk_file)
        if not os.path.exists(path):
            continue
        
        df = pd.read_csv(path)
        # 셔플 후 각 청크당 정확히 10개를 val로 격리
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        val_samples = df.head(10)
        train_samples = df.tail(len(df) - 10)
        
        val_list.append(val_samples)
        train_core_list.append(train_samples)
    
    df_val = pd.concat(val_list, ignore_index=True)
    df_train_core = pd.concat(train_core_list, ignore_index=True)
    
    print(f"- Validation Samples (Isolated): {len(df_val)}")
    print(f"- Training Core Samples (Unique): {len(df_train_core)}")

    # [3] 3,000개까지 증강 실행
    print("Step 2: Augmenting Training Core to 3,000 samples...")
    current_count = len(df_train_core)
    target_count = 3000
    needed = target_count - current_count
    
    augmented_list = [df_train_core]
    
    for _ in tqdm(range(needed)):
        # 기존 코어에서 하나 선택 후 증강
        source_row = df_train_core.sample(n=1).iloc[0]
        aug_text = augment_text(source_row['conversation'])
        augmented_list.append(pd.DataFrame([{
            'class': '일반 대화',
            'conversation': aug_text
        }]))
        
    df_train_final_general = pd.concat(augmented_list, ignore_index=True)
    print(f"- Final General Training Set: {len(df_train_final_general)}")

    # [4] 기존 원본 위협 데이터와 통합 (train.csv 기준)
    print("Step 3: Integrating with Threat Data from original train.csv...")
    train_path = os.path.join(data_dir, "train.csv")
    if os.path.exists(train_path):
        df_orig = pd.read_csv(train_path)
        # 위협 데이터만 필터링 (원본에 '일반 대화'가 있을 수 있으나 우리는 우리 것만 쓰기로 함)
        df_threat = df_orig[df_orig['class'] != '일반 대화']
        
        # 위협 클래스도 각각 약 700~800개 수준인데, 밸런스를 맞추기 위해 증강이 필요할 수 있음
        # 하지만 일단 여기서는 합치는 것에 집중하고, 밸런스는 전체 훈련셋 구성을 따름
        # 최종 병합
        df_final_train = pd.concat([df_threat, df_train_final_general], ignore_index=True)
        
        # 저장
        final_train_path = os.path.join(data_dir, "train_final_v4_5.csv")
        val_holdout_path = os.path.join(data_dir, "val_holdout_v4_5.csv")
        
        df_final_train.to_csv(final_train_path, index=False, encoding='utf-8-sig')
        df_val.to_csv(val_holdout_path, index=False, encoding='utf-8-sig')
        
        print(f"\nFinal training data saved to: {final_train_path}")
        print(f"Validation hold-out saved to: {val_holdout_path}")
        print(f"Total Final Training Size: {len(df_final_train)}")
    else:
        print("Error: original train.csv not found for core threat data.")

if __name__ == "__main__":
    finalize_dataset()
