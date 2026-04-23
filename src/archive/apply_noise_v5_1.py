import pandas as pd
import random
import re
import os
from tqdm import tqdm

# [1] 한국어 구어체 노이즈 사전 (Style Transfer용)
CASUAL_MAP = {
    "봐요": "바", "봐": "바", "예요": "야", "이에요": "이야",
    "해요": "해", "가요": "가", "하나요": "해", "있나요": "있어",
    "맞나요": "맞아", "드립니다": "드림", "합니다": "함",
    "거예요": "거야", "건가요": "거냐", "네요": "네",
    "주세요": "줘", "거지": "거쥐", "진짜": "진짜루",
    "맞아요": "맞아", "아니요": "아니", "모르겠어요": "몰라"
}

def apply_street_noise(text):
    """표준어/정중체 문장을 구어체/노이즈 문장으로 변조"""
    # 1. 종결 어미 변환 (정중 -> 구어)
    for k, v in CASUAL_MAP.items():
        text = text.replace(k, v)
    
    # 2. 맞춤법 노이즈 (일부 단어 변형)
    text = text.replace("어떻게", "어케")
    text = text.replace("지금 당장", "지금당장")
    text = text.replace("제발", "젭알")
    text = text.replace("진짜", "찐자")
    
    # 3. 무작위 공백 제거 (30% 확률)
    if random.random() < 0.3:
        words = text.split()
        if len(words) > 5:
            idx = random.randint(0, len(words)-2)
            words[idx] = words[idx] + words[idx+1]
            del words[idx+1]
            text = " ".join(words)
            
    # 4. 추임새(Filler) 강화
    fillers = ["어...", "아니 ", "음.. ", "근데 ", "암튼 ", "그니깐 "]
    if random.random() < 0.2:
        text = random.choice(fillers) + text
        
    return text

def create_v5_1_noisy_dataset():
    data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
    train_v5_path = os.path.join(data_dir, "train_final_v5.csv")
    val_v5_path = os.path.join(data_dir, "val_final_v5.csv")
    
    if not os.path.exists(train_v5_path):
        print("Error: train_final_v5.csv not found.")
        return

    # 로드
    df_train = pd.read_csv(train_v5_path)
    df_val = pd.read_csv(val_v5_path)
    
    print("Applying 'Street-Style' Noise to General Conversations...")
    
    # 일반 대화에만 특히 강하게 노이즈 주입 (테스트셋의 일반 대화 스타일과 맞추기 위함)
    # 훈련셋의 일반 대화 중 70% 정도를 '지저분하게' 변조
    def noise_heavy(row):
        if row['class'] == '일반 대화' and random.random() < 0.7:
            return apply_street_noise(row['conversation'])
        return row['conversation']

    tqdm.pandas()
    df_train['conversation'] = df_train.progress_apply(noise_heavy, axis=1)
    df_val['conversation'] = df_val.progress_apply(noise_heavy, axis=1)
    
    # 저장
    save_train_path = os.path.join(data_dir, "train_final_v5_1.csv")
    save_val_path = os.path.join(data_dir, "val_final_v5_1.csv")
    
    df_train.to_csv(save_train_path, index=False, encoding='utf-8-sig')
    df_val.to_csv(save_val_path, index=False, encoding='utf-8-sig')
    
    print(f"\n[V5.1 Success] Noisy dataset saved to {save_train_path}")

if __name__ == "__main__":
    create_v5_1_noisy_dataset()
