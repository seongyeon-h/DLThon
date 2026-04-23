import pandas as pd
import os

# 설정
data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
general_file = os.path.join(data_dir, "synthetic_general_v4.5_3000.csv")
# 이전 버전에서 가장 우수했던 위협 데이터를 가져오기 위해 v4.2 또는 원본 보존 파일을 참조합니다.
# 여기서는 최신 증강 로직이 반영된 v4.3 합본을 소스로 활용합니다.
threat_source_file = os.path.join(data_dir, "train_final_v4_3.csv") 

# 1. 파일 로드
df_general = pd.read_csv(general_file)
df_threat_source = pd.read_csv(threat_source_file)

# 2. 위협 데이터만 추출 (4개 클래스)
threat_classes = ['협박 대화', '갈취 대화', '직장 내 괴롭힘 대화', '기타 괴롭힘 대화']
df_threat = df_threat_source[df_threat_source['class'].isin(threat_classes)].copy()

# 3. 데이터 밸런싱 (위협 3000건 확보)
# 각 클래스별로 균등하게 750건씩 샘플링 (부족할 경우 복원 추출)
df_threat_balanced = pd.DataFrame()
target_per_class = 750

for tc in threat_classes:
    class_sub = df_threat[df_threat['class'] == tc]
    if len(class_sub) >= target_per_class:
        df_threat_balanced = pd.concat([df_threat_balanced, class_sub.sample(n=target_per_class, random_state=42)])
    else:
        # 부족한 경우 오버샘플링
        df_threat_balanced = pd.concat([df_threat_balanced, class_sub.sample(n=target_per_class, replace=True, random_state=42)])

# 4. 일반 대화와 병합 (3000 + 3000 = 6000)
final_df = pd.concat([df_general, df_threat_balanced], ignore_index=True)

# 5. 최종 데이터 정제 (공백 제거, 셔플)
final_df['conversation'] = final_df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

# 6. 저장
final_path = os.path.join(data_dir, "train_final_v4.5.csv")
final_df.to_csv(final_path, index=False, encoding='utf-8-sig')

print(f"==========================================")
print(f"✅ 최종 데이터셋 구축 완료!")
print(f"파일 경로: {final_path}")
print(f"총 샘플 수: {len(final_df)}건")
print(f"--- 클래스별 분포 ---")
print(final_df['class'].value_counts())
print(f"==========================================")
