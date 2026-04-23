"""
합성 일반대화(synthesis.csv) 증강 스크립트
- 기존 RS/RD/RI를 synthesis 구조에 맞게 수정
- 목표: 990건 → 3,000건 (클래스당 밸런스)
"""

import pandas as pd
import numpy as np
import random
import os
from tqdm import tqdm

# ============================================================
# 0. 설정
# ============================================================
random.seed(42)
np.random.seed(42)

TARGET_COUNT = 3000
INPUT_PATH = 'data/synthesis.csv'
OUTPUT_PATH = 'data/synthesis_augmented.csv'

# 일반대화용 추임새 (절대 "ㅋㅋ" 포함 금지!)
FILLERS_GENERAL = [
    "진짜", "아", "그니까", "좀", "막", "근데", "뭐", "걍",
    "아니", "어", "야", "그래", "음", "대박", "아 진짜",
    "와", "헐", "오", "에이", "아이고"
]

# ============================================================
# 1. 증강 함수 정의
# ============================================================

def word_level_shuffle(text, chunk_size=4):
    """
    [WS] Word-level Shuffle: 공백 기반 단어 묶음(chunk) 교체
    기존 RS(줄바꿈 기반)를 대체 — synthesis에는 줄바꿈이 없으므로
    """
    words = text.split()
    if len(words) < chunk_size * 2 + 2:
        return text
    
    max_start = len(words) - chunk_size * 2
    start = random.randint(0, max_start)
    
    chunk1 = words[start:start+chunk_size]
    chunk2 = words[start+chunk_size:start+chunk_size*2]
    
    words[start:start+chunk_size] = chunk2
    words[start+chunk_size:start+chunk_size*2] = chunk1
    
    return ' '.join(words)


def multi_insertion(text, target_len=175, max_inserts=6):
    """
    [Multi-RI] 목표 길이에 접근할 때까지 추임새 반복 삽입
    기존 RI(p=0.1 단일)를 강화 — 길이를 correct 평균(172자)에 접근시키기 위함
    """
    words = text.split()
    if len(words) < 3:
        return text
    
    inserts = 0
    current_len = len(text)
    
    while current_len < target_len and inserts < max_inserts:
        idx = random.randint(1, len(words) - 1)
        filler = random.choice(FILLERS_GENERAL)
        words.insert(idx, filler)
        current_len = len(' '.join(words))
        inserts += 1
    
    return ' '.join(words)


def span_repetition(text):
    """
    [SR] Span Repetition: 2~3단어 구간을 중복 삽입 (구어체 반복 효과)
    새로 추가된 기법 — 대화체에서 흔한 반복 강조 패턴 모방
    """
    words = text.split()
    if len(words) < 10:
        return text
    
    span_len = random.randint(2, 3)
    start = random.randint(0, len(words) - span_len - 1)
    span = words[start:start+span_len]
    
    # 원본 위치 뒤쪽 어딘가에 삽입
    insert_pos = random.randint(start + span_len + 1, min(start + span_len + 6, len(words)))
    for i, w in enumerate(span):
        words.insert(insert_pos + i, w)
    
    return ' '.join(words)


def conditional_deletion(text, p=0.08):
    """
    [Conditional RD] 200자 이상 장문에서만 단어 삭제
    기존 RD를 조건부로 변경 — 이미 짧은 synthesis에서 삭제하면 격차 확대
    """
    if len(text) < 200:
        return text  # 짧은 건 건드리지 않음
    
    words = text.split()
    new_words = [w for w in words if random.random() > p]
    result = ' '.join(new_words)
    return result if result.strip() else text


def augment_text_v2(text):
    """
    통합 증강 파이프라인 v2
    
    적용 우선순위:
    1. Multi-point RI (60%) — 길이 보충 핵심
    2. Word-level Shuffle (40%) — 어순 다양성
    3. Span Repetition (20%) — 구어체 반복
    4. Conditional RD (10%, 200자↑만) — 장문 변이
    """
    result = text
    
    # 1차: Multi-RI (75% 확률)
    if random.random() < 0.75:
        result = multi_insertion(result)
    
    # 2차: Word-level Shuffle (40% 확률)
    if random.random() < 0.40:
        result = word_level_shuffle(result)
    
    # 3차: Span Repetition (20% 확률)
    if random.random() < 0.20:
        result = span_repetition(result)
    
    # 4차: Conditional RD (10% 확률, 200자↑만)
    if random.random() < 0.10:
        result = conditional_deletion(result)
    
    return result


# ============================================================
# 2. 증강 실행
# ============================================================
def main():
    # 데이터 로드
    df = pd.read_csv(INPUT_PATH)
    # synthesis.csv는 'conversation' 컬럼만 존재 → 클래스는 '일반 대화'로 고정
    CLASS_LABEL = '일반 대화'
    current_count = len(df)
    augment_needed = TARGET_COUNT - current_count

    print(f"📦 원본 데이터: {current_count}건")
    print(f"🎯 목표: {TARGET_COUNT}건 (증강 필요: {augment_needed}건)")
    print(f"📊 증강 배율: {TARGET_COUNT / current_count:.2f}x")
    print()

    # 원본 통계
    orig_lens = [len(t) for t in df['conversation']]
    print(f"📏 원본 길이 통계: mean={np.mean(orig_lens):.0f}, std={np.std(orig_lens):.0f}, "
          f"min={min(orig_lens)}, max={max(orig_lens)}")

    # 증강 데이터 생성
    augmented_records = []

    # 원본 데이터 유지
    for _, row in df.iterrows():
        augmented_records.append({
            'class': CLASS_LABEL,
            'conversation': row['conversation'],
            'is_augmented': False
        })

    # 증강 루프
    max_retries = augment_needed * 3  # 무한루프 방지
    retries = 0
    generated = set()  # 중복 방지

    with tqdm(total=augment_needed, desc="🔄 Augmenting") as pbar:
        while augment_needed > 0 and retries < max_retries:
            sample = df.sample(n=1).iloc[0]
            new_text = augment_text_v2(sample['conversation'])

            # 원본과 동일하면 재시도
            if new_text == sample['conversation']:
                retries += 1
                continue

            # 이미 생성된 것과 동일하면 재시도
            if new_text in generated:
                retries += 1
                continue

            generated.add(new_text)
            augmented_records.append({
                'class': CLASS_LABEL,
                'conversation': new_text,
                'is_augmented': True
            })
            augment_needed -= 1
            retries = 0
            pbar.update(1)

    # DataFrame 생성 및 셔플
    result_df = pd.DataFrame(augmented_records)
    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 증강 후 통계
    aug_lens = [len(t) for t in result_df['conversation']]
    aug_only = result_df[result_df['is_augmented'] == True]
    aug_only_lens = [len(t) for t in aug_only['conversation']]
    
    print()
    print(f"✅ 최종 데이터: {len(result_df)}건")
    print(f"  - 원본: {len(result_df[result_df['is_augmented']==False])}건")
    print(f"  - 증강: {len(aug_only)}건")
    print()
    print(f"📏 전체 길이 통계: mean={np.mean(aug_lens):.0f}, std={np.std(aug_lens):.0f}, "
          f"min={min(aug_lens)}, max={max(aug_lens)}")
    print(f"📏 증강분 길이 통계: mean={np.mean(aug_only_lens):.0f}, std={np.std(aug_only_lens):.0f}, "
          f"min={min(aug_only_lens)}, max={max(aug_only_lens)}")

    # 길이 분포
    print()
    print("📊 길이 분포 비교:")
    bins = [(0,80), (80,130), (130,200), (200,300), (300,500)]
    for label, lens_list in [('원본', orig_lens), ('전체(증강후)', aug_lens)]:
        print(f"  {label}:")
        for lo, hi in bins:
            cnt = sum(1 for l in lens_list if lo <= l < hi)
            pct = cnt / len(lens_list) * 100
            print(f"    {lo}-{hi}자: {cnt}건 ({pct:.1f}%)")

    # "ㅋㅋ" 체크
    kk_count = sum(1 for t in result_df['conversation'] if 'ㅋㅋ' in t)
    print(f"\n🚫 'ㅋㅋ' 포함 건수: {kk_count}건 (0이어야 함)")

    # 저장 (is_augmented 제외)
    final = result_df[['class', 'conversation']].copy()
    final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n💾 저장 완료: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
