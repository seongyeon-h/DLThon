"""
correct.md에서 일반 대화로 선정된 ID를 추출하여 test.csv에서 해당 대화를 correct.csv로 복사
"""
import pandas as pd
import re

# correct.md에서 ID 추출 (일반 대화 목록 테이블)
with open(r"c:\Users\Hwang\Desktop\황성연\DLThon\correct.md", "r", encoding="utf-8") as f:
    content = f.read()

# 테이블에서 t_XXX 패턴 추출
all_ids = re.findall(r'\|\s*\d+\s*\|\s*(t_\d+)\s*\|', content)
print(f"전체 추출된 ID: {len(all_ids)}개")

# 제외 대상: ❌ 표시 또는 재분류된 것들
exclude_ids = {
    't_005',  # ❌ 삭제 — 손톱 뽑는 고문/협박
    't_125',  # 갈취 대화로 재분류
    't_315',  # 기타 괴롭힘으로 재분류
    't_411',  # 기타 괴롭힘으로 재분류
}

general_ids = [tid for tid in all_ids if tid not in exclude_ids]
print(f"제외 후 일반 대화 ID: {len(general_ids)}개")
print(f"제외된 ID: {exclude_ids}")

# test.csv 로드
test_df = pd.read_csv(r"c:\Users\Hwang\Desktop\황성연\DLThon\data\test.csv")
print(f"\ntest.csv 전체: {len(test_df)}행")
print(f"컬럼: {list(test_df.columns)}")

# ID 컬럼 확인 (첫 번째 컬럼이 ID)
id_col = test_df.columns[0]
text_col = test_df.columns[1]

# 필터링
correct_df = test_df[test_df[id_col].isin(general_ids)]
print(f"매칭된 행: {len(correct_df)}개")

# 누락 ID 체크
found_ids = set(correct_df[id_col].tolist())
missing = set(general_ids) - found_ids
if missing:
    print(f"[경고] 매칭 안 된 ID: {missing}")

# conversation 컬럼만 추출하여 저장
output_df = correct_df[[text_col]].copy()
output_df.columns = ['conversation']
output_df.to_csv(
    r"c:\Users\Hwang\Desktop\황성연\DLThon\data\correct.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"\n[완료] data/correct.csv 저장: {len(output_df)}건")
