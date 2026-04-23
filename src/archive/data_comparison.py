import pandas as pd

df_train = pd.read_csv("data/train_final_v5.csv")
df_test = pd.read_csv("data/test.csv")

# 훈련셋 '일반 대화' vs 테스트셋 스타일 비교
general = df_train[df_train['class'] == '일반 대화']

print("=== 훈련셋 일반 대화 샘플 5건 ===")
for i in [0, 300, 700, 1500, 2500]:
    if i < len(general):
        txt = general.iloc[i]['conversation'][:150]
        print(f"[Train #{i}] {txt}")
        print()

print("=== 테스트셋 샘플 5건 ===")
for i in [3, 50, 100, 200, 400]:
    if i < len(df_test):
        txt = df_test.iloc[i]['conversation'][:150]
        print(f"[Test #{i}] {txt}")
        print()

# 위협 클래스 원본 vs 증강 비교
threat = df_train[df_train['class'] != '일반 대화']
print("=== 위협 클래스 샘플 ===")
for cls in threat['class'].unique():
    subset = threat[threat['class'] == cls]
    txt = subset.iloc[0]['conversation'][:150]
    print(f"[{cls}] {txt}")
    print()

# 핵심 통계
print("=== 핵심 통계 ===")
print(f"Train 평균 길이: {df_train['conversation'].str.len().mean():.0f}자")
print(f"Test  평균 길이: {df_test['conversation'].str.len().mean():.0f}자")
print(f"Train 일반대화 평균 길이: {general['conversation'].str.len().mean():.0f}자")
