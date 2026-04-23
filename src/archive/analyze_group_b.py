import pandas as pd
import re
from collections import Counter

df = pd.read_csv('data/synthesis.csv')
group_b = df.iloc[390:]

texts = group_b['conversation'].tolist()
all_text = ' '.join(texts)

# 반복 패턴/표현 빈도 분석
patterns = {
    '사랑해': len(re.findall(r'사랑해', all_text)),
    '미안해/미안': len(re.findall(r'미안해|미안', all_text)),
    '고마워/고맙': len(re.findall(r'고마워|고맙', all_text)),
    '알았어': len(re.findall(r'알았어', all_text)),
    '자기야': len(re.findall(r'자기야', all_text)),
    '오빠': len(re.findall(r'오빠', all_text)),
    '여보': len(re.findall(r'여보', all_text)),
    '엄마': len(re.findall(r'엄마', all_text)),
    '아빠': len(re.findall(r'아빠', all_text)),
    '형': len(re.findall(r'형 |형이|형한테', all_text)),
    '언니': len(re.findall(r'언니', all_text)),
    '화 풀어': len(re.findall(r'화 풀어|화풀어', all_text)),
    '이번만/한 번만': len(re.findall(r'이번만|한 번만|이번 한 번', all_text)),
    '앞으론/다음부터': len(re.findall(r'앞으론|앞으로는|다음부터|다음엔', all_text)),
    '진짜': len(re.findall(r'진짜', all_text)),
}

print('=== 핵심 표현 빈도 ===')
for k, v in sorted(patterns.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}회')

# 문장 시작 패턴 분석
starts = []
for t in texts:
    first_word = t.split()[0] if t.split() else ''
    starts.append(first_word)
print(f'\n=== 대화 시작 단어 TOP 15 ===')
for word, cnt in Counter(starts).most_common(15):
    print(f'  "{word}": {cnt}회')

# 마무리 패턴 분석
endings = []
for t in texts:
    words = t.split()
    if len(words) >= 2:
        last = ' '.join(words[-2:])
        endings.append(last)
print(f'\n=== 대화 끝 패턴 TOP 15 ===')
for word, cnt in Counter(endings).most_common(15):
    print(f'  "{word}": {cnt}회')

# 대화 구조 분석 (마무리가 화해/양보인지)
resolve_keywords = ['미안', '알았', '화 풀', '사랑해', '고마워', '응', '그래', '이따', '사줄', '봐준']
resolved = sum(1 for t in texts if any(k in t[-30:] for k in resolve_keywords))
print(f'\n=== 마무리 톤 ===')
print(f'화해/양보/긍정으로 끝남: {resolved}개 ({resolved/len(texts)*100:.1f}%)')
print(f'기타: {len(texts)-resolved}개 ({(len(texts)-resolved)/len(texts)*100:.1f}%)')

# 대화 전개 패턴 분류
print(f'\n=== 서브그룹별 뉘앙스 샘플 ===')

# P14 커플 달달 샘플
print('\n--- P14 커플 달달 (처음 3개) ---')
sweet_count = 0
for t in texts:
    if any(w in t for w in ['사랑해', '보고싶', '예뻐', '공주님', '설렌다']) and '서운' not in t and '화났' not in t:
        if sweet_count < 3:
            print(f'  [{len(t)}자] {t[:80]}...')
            sweet_count += 1

# P15 커플 다툼 샘플
print('\n--- P15 커플 다툼 (처음 3개) ---')
fight_count = 0
for t in texts:
    if any(w in t for w in ['서운', '기분 나빠', '실망', '화났', '짜증', '왜 그렇게']):
        if fight_count < 3:
            print(f'  [{len(t)}자] {t[:80]}...')
            fight_count += 1

# P16 부모자녀 샘플
print('\n--- P16 부모-자녀 (처음 3개) ---')
pc_count = 0
for t in texts:
    if any(w in t for w in ['엄마', '아빠']) and '오빠' not in t:
        if pc_count < 3:
            print(f'  [{len(t)}자] {t[:80]}...')
            pc_count += 1

# P17 형제 샘플
print('\n--- P17 형제자매 (처음 3개) ---')
sib_count = 0
for t in texts:
    if any(w in t for w in ['언니 ', '형 나', '동생']) and '엄마' not in t and '자기' not in t:
        if sib_count < 3:
            print(f'  [{len(t)}자] {t[:80]}...')
            sib_count += 1

# P18 부부 샘플
print('\n--- P18 부부 일상 (처음 3개) ---')
married_count = 0
for t in texts:
    if any(w in t for w in ['여보', '퇴근', '장보', '에어컨', '보일러', '카드값', '침대 시트']):
        if married_count < 3:
            print(f'  [{len(t)}자] {t[:80]}...')
            married_count += 1

# 반복 구조 체크 (동일 시작 패턴)
print(f'\n=== 반복 구조 위험 체크 ===')
# "자기야"로 시작하는 비율
jagi_start = sum(1 for t in texts if t.startswith('자기야'))
obba_start = sum(1 for t in texts if t.startswith('오빠'))
yeobo_start = sum(1 for t in texts if t.startswith('여보'))
print(f'"자기야"로 시작: {jagi_start}개')
print(f'"오빠"로 시작: {obba_start}개')
print(f'"여보"로 시작: {yeobo_start}개')

# "사랑해"로 끝나는 비율
love_end = sum(1 for t in texts if t.rstrip().endswith('사랑해'))
print(f'"사랑해"로 끝남: {love_end}개')

# 테스트셋 correct.csv와 결 비교
correct = pd.read_csv('data/correct.csv')
correct_text = ' '.join(correct['conversation'].tolist())

# correct에 커플/가족 관련 키워드가 얼마나 있는지
print(f'\n=== 테스트셋(correct.csv)의 커플/가족 관련 키워드 ===')
for kw in ['사랑', '자기', '오빠', '여보', '엄마', '아빠', '형', '언니', '동생']:
    cnt = len(re.findall(kw, correct_text))
    print(f'  "{kw}": {cnt}회')
