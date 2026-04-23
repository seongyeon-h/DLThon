import pandas as pd
import numpy as np
import random
import os
from tqdm import tqdm
import sys

# src.augment_synthesis 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from augment_synthesis import augment_text_v2

random.seed(42)
np.random.seed(42)

def main():
    print("🚀 [Step 1] synthesis.csv 로드 및 분할 (Train/Val)")
    synthesis_df = pd.read_csv('data/synthesis.csv')
    # synthesis.csv는 conversation 컬럼만 존재
    
    val_records = []
    train_records = []
    
    # 33개 프롬프트 x 30개 문장 = 990개 가정
    for i in range(0, len(synthesis_df), 30):
        chunk = synthesis_df.iloc[i:i+30]
        # 무작위로 6개 샘플링 (Val 용)
        val_chunk = chunk.sample(n=6, random_state=42)
        train_chunk = chunk.drop(val_chunk.index)
        
        for _, row in val_chunk.iterrows():
            val_records.append({'class': '일반 대화', 'conversation': row['conversation']})
        for _, row in train_chunk.iterrows():
            train_records.append({'class': '일반 대화', 'conversation': row['conversation'], 'is_augmented': False})
            
    val_synth_df = pd.DataFrame(val_records)
    train_synth_df = pd.DataFrame(train_records)
    
    print(f"  - 검증용 일반대화 (Val): {len(val_synth_df)}건")
    print(f"  - 훈련용 일반대화 (Train 원본): {len(train_synth_df)}건")
    
    val_synth_df.to_csv('data/val_holdout_synthesis.csv', index=False, encoding='utf-8-sig')
    print("  ✔️ data/val_holdout_synthesis.csv 저장 완료\n")
    
    print("🚀 [Step 2] 훈련용 일반대화 증강 (792건 -> 3000건)")
    TARGET_COUNT = 3000
    augment_needed = TARGET_COUNT - len(train_synth_df)
    
    augmented_records = train_synth_df.to_dict('records')
    generated = set()
    retries = 0
    max_retries = augment_needed * 3
    
    with tqdm(total=augment_needed, desc="🔄 Augmenting '일반 대화'") as pbar:
        while augment_needed > 0 and retries < max_retries:
            sample = train_synth_df.sample(n=1).iloc[0]
            new_text = augment_text_v2(sample['conversation'])
            
            if new_text == sample['conversation'] or new_text in generated:
                retries += 1
                continue
                
            generated.add(new_text)
            augmented_records.append({
                'class': '일반 대화',
                'conversation': new_text,
                'is_augmented': True
            })
            augment_needed -= 1
            retries = 0
            pbar.update(1)
            
    train_synth_aug_df = pd.DataFrame(augmented_records).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"  - 증강 후 일반대화 총 길이: {len(train_synth_aug_df)}건")
    train_synth_aug_df[['class', 'conversation']].to_csv('data/train_augmented_synthesis.csv', index=False, encoding='utf-8-sig')
    print("  ✔️ data/train_augmented_synthesis.csv 저장 완료\n")
    
    print("🚀 [Step 3] 최종 Val 및 Train 데이터셋 병합")
    # 기존 데이터 로드
    val_holdout = pd.read_csv('data/val_holdout.csv')
    train_aug_v1 = pd.read_csv('data/train_augmented_v1.csv')
    
    # idx 컬럼이 있다면 제거하고 병합 후 다시 붙이거나, 그냥 제거 (모델은 class와 conversation만 주로 사용)
    # 다만 기존 형태를 유지하기 위해, idx를 다시 생성.
    for col in ['idx', 'is_augmented']:
        if col in val_holdout.columns: val_holdout = val_holdout.drop(columns=[col])
        if col in train_aug_v1.columns: train_aug_v1 = train_aug_v1.drop(columns=[col])
        if col in val_synth_df.columns: val_synth_df = val_synth_df.drop(columns=[col])
        
    val_final = pd.concat([val_holdout, val_synth_df], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    val_final.insert(0, 'idx', range(len(val_final)))
    
    train_final = pd.concat([train_aug_v1, train_synth_aug_df[['class', 'conversation']]], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    train_final.insert(0, 'idx', range(len(train_final)))
    
    val_final.to_csv('data/val_final.csv', index=False, encoding='utf-8-sig')
    train_final.to_csv('data/train_final.csv', index=False, encoding='utf-8-sig')
    
    print(f"  ✔️ data/val_final.csv 저장 완료 (총 {len(val_final)}건)")
    print(val_final['class'].value_counts())
    print()
    print(f"  ✔️ data/train_final.csv 저장 완료 (총 {len(train_final)}건)")
    print(train_final['class'].value_counts())
    
if __name__ == "__main__":
    main()
