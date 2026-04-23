import pandas as pd
import os

def merge_v5_final():
    data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
    
    # [1] 훈련셋 병합 (15,000건 목표)
    print("Step 1: Merging Training Data...")
    train_aug_v1_path = os.path.join(data_dir, "train_augmented_v1.csv")
    general_aug_v4_5_path = os.path.join(data_dir, "train_final_v4_5.csv") 
    
    # 원본 위협 데이터 로드
    df_aug_v1 = pd.read_csv(train_aug_v1_path)
    # 위협 클래스만 필터링 (협박, 갈취, 직장 내 괴롭힘, 기타 괴롭힘)
    df_threats = df_aug_v1[df_aug_v1['class'] != '일반 대화']
    print(f"- Loaded Threat Classes from v1: {len(df_threats)} samples")
    
    # 우리가 만든 고품질 일반 대화 로드 (3,000건)
    df_v4_5_all = pd.read_csv(general_aug_v4_5_path)
    df_general_v4_5 = df_v4_5_all[df_v4_5_all['class'] == '일반 대화']
    print(f"- Loaded High-Quality General Class: {len(df_general_v4_5)} samples")
    
    # 병합 및 셔플
    df_train_v5 = pd.concat([df_threats, df_general_v4_5], ignore_index=True)
    df_train_v5 = df_train_v5.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # [2] 검증셋 병합
    print("\nStep 2: Merging Validation Data...")
    val_orig_path = os.path.join(data_dir, "val_holdout.csv")
    val_v4_5_path = os.path.join(data_dir, "val_holdout_v4_5.csv")
    
    df_val_orig = pd.read_csv(val_orig_path)
    df_val_v4_5 = pd.read_csv(val_v4_5_path)
    
    df_val_final = pd.concat([df_val_orig, df_val_v4_5], ignore_index=True)
    df_val_final = df_val_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # [3] 저장
    train_v5_save_path = os.path.join(data_dir, "train_final_v5.csv")
    val_v5_save_path = os.path.join(data_dir, "val_final_v5.csv")
    
    df_train_v5.to_csv(train_v5_save_path, index=False, encoding='utf-8-sig')
    df_val_final.to_csv(val_v5_save_path, index=False, encoding='utf-8-sig')
    
    print(f"\n- [SUCCESS] Final Training Set (V5): {len(df_train_v5)} samples saved to {train_v5_save_path}")
    print(f"- [SUCCESS] Final Validation Set (V5): {len(df_val_final)} samples saved to {val_v5_save_path}")
    
    # 클래스별 분포 확인
    print("\n[V5 Class Distribution]")
    print(df_train_v5['class'].value_counts())

if __name__ == "__main__":
    merge_v5_final()
