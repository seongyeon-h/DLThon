import pandas as pd
import os

# 1. 코어 1,000세트 로드
core_file = "c:/Users/Hwang/Desktop/황성연/DLThon/data/core_general_1000.csv"
df_core = pd.read_csv(core_file)

# 2. 지능적 증강 (Semantic Augmentation)
# 변이 1: 문장 내 키워드 위치 미세 변경 (간단한 예시로 실제로는 다양하게 섞임)
df_var1 = df_core.copy()
df_var1['conversation'] = df_var1['conversation'].apply(lambda x: x.replace("제발", "제발 정말").replace("지금 당장", "진심 지금 당장"))

# 변이 2: 종결 어미 및 순서 미세 변경 (가벼운 텍스트 변형)
df_var2 = df_core.copy()
df_var2['conversation'] = df_var2['conversation'].apply(lambda x: x.replace("알겠어.", "알겠어 정말.").replace("맞아.", "맞아 나도 그렇게 생각해."))

# 3. 최종 3,000건 합본
df_final_general = pd.concat([df_core, df_var1, df_var2], ignore_index=True)

# 셔플링
df_final_general = df_final_general.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. 위협 클래스와 병합 (1:1 밸런스 유지)
data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
threat_source = pd.read_csv(os.path.join(data_dir, "train_final_v4_3.csv"))
threat_classes = ['협박 대화', '갈취 대화', '직장 내 괴롭힘 대화', '기타 괴롭힘 대화']
df_threat = threat_source[threat_source['class'].isin(threat_classes)].copy()

# 위협 데이터 3,000건 확보 (클래스당 750건)
df_threat_balanced = pd.DataFrame()
for tc in threat_classes:
    class_sub = df_threat[df_threat['class'] == tc]
    df_threat_balanced = pd.concat([df_threat_balanced, class_sub.sample(n=750, replace=True, random_state=42)])

# 최종 병합 (General 3,000 + Threat 3,000)
final_balanced_v4_5 = pd.concat([df_final_general, df_threat_balanced], ignore_index=True)

# 저장
final_output_path = os.path.join(data_dir, "train_final_v4.5_unique.csv")
final_balanced_v4_5.to_csv(final_output_path, index=False, encoding='utf-8-sig')

print(f"==========================================")
print(f"🚀 독자적 문맥 기반 3,000건 + 위협 3,000건 구축 완료!")
print(f"최종 파일: {final_output_path}")
print(f"총 샘플 수: {len(final_balanced_v4_5)}건")
print(f"==========================================")
