import pandas as pd
import random
import os
import re

# ==============================================================================
# Utils: Korean Particle Handler
# ==============================================================================

def get_josa(word, josa_type):
    """
    josa_type: '은/는', '이/가', '을/를', '와/과'
    """
    if not word: return ""
    char_code = ord(word[-1]) - 0xAC00
    if char_code < 0 or char_code > 11171: # Not Hangul
        return josa_type.split('/')[1] # Default to '는', '가', etc.
    
    has_jong = char_code % 28 != 0
    
    pairs = {
        '은/는': ('은', '는'),
        '이/가': ('이', '가'),
        '을/를': ('을', '를'),
        '와/과': ('과', '와')
    }
    
    if josa_type in pairs:
        return pairs[josa_type][0] if has_jong else pairs[josa_type][1]
    return ""

def attach_josa(word, josa_type):
    return f"{word}{get_josa(word, josa_type)}"

# ==============================================================================
# 1. Diversity Engine: Step-wise Paraphrasing Pools
# ==============================================================================

POOLS = {
    "GREETING_CASUAL": ["야", "안녕", "좋은 아침", "하이하이", "오랜만이다", "뭐해?", "심심해"],
    "GREETING_POLITE": ["안녕하세요", "과장님 안녕하세요", "대리님 좋은 아침입니다", "선생님 계신가요?", "팀장님 바쁘세요?"],
    
    "RESPONSE_CASUAL": ["응응", "나야 뭐 맨날 똑같지", "어어 왜?", "말해봐", "듣고 있어", "무슨 일이야?"],
    "RESPONSE_POLITE": ["네 사원님", "아 지수씨", "네 무슨 일이신가요?", "아 들리시나요?", "네 듣고 있습니다"],
    
    "AGREEMENT": ["맞아", "인정", "내 말이", "나도 그렇게 생각해", "당연하지", "그럼 그렇고말고", "옳소"],
    "DISAGREEMENT": ["에이 설마", "에바야", "그건 좀 아닌듯", "말도 안 돼", "글쎄 나는 반댄데", "다시 생각해봐"],
    
    "FILLER": ["진짜", "대박", "엄청", "되게", "막", "완전", "뭐랄까", "사실", "솔직히", "아무래도"],
    "POLITE_SOFTENER": ["죄송합니다만", "실례지만", "바쁘시겠지만", "혹시"],
    
    "FAREWELL_CASUAL": ["이따 봐", "담에 봐", "잘 자", "톡해", "바이바이", "바이", "오키 확인"],
    "FAREWELL_POLITE": ["수고하세요", "들어가보겠습니다", "내일 뵙겠습니다", "감사합니다", "안녕히 계세요"]
}

# ==============================================================================
# 2. Scenario Engines (Polished Logic)
# ==============================================================================

def gen_workplace_flow():
    manager = random.choice(["부장님", "과장님", "대리님", "팀장님"])
    s = []
    s.append(f"A: {manager} 안녕하세요. {random.choice(['일정', '회의', '보고'])} 건으로 여쭐 게 있어요.")
    s.append(f"B: {random.choice(POOLS['RESPONSE_POLITE'])}. {random.choice(POOLS['POLITE_SOFTENER'])} 제가 지금 바쁘긴 한데 짧게 말해봐요.")
    s.append(f"A: 아, {manager}께 제출할 서류 작업이 좀 {random.choice(['늦어져서', '꼬여서'])} {random.choice(['죄송합니다', '걱정되네요'])}.")
    s.append(f"B: {random.choice(POOLS['DISAGREEMENT'])}! {attach_josa(random.choice(['지금 당장', '이따가']), '은/는')} 끝낼 수 있는 거죠?")
    s.append(f"A: 네, {attach_josa(random.choice(['지금 당장', '오늘 내로']), '은/는')} 꼭 마무리해서 {random.choice(['전달', '공유'])} 드릴게요.")
    s.append(f"B: 알겠어요. {manager} 기분이 좀 예민하시니까 {random.choice(POOLS['FILLER'])} 조심하시고요.")
    s.append(f"A: 네 {random.choice(POOLS['AGREEMENT'])}. 정보 공유 감사합니다.")
    s.append(f"B: 네 {random.choice(POOLS['FAREWELL_POLITE'])}.")
    return " ".join(s)

def gen_school_flow():
    teacher = random.choice(["선생님", "조교님", "교수님"])
    s = []
    s.append(f"A: {teacher}, {random.choice(['제발', '진짜'])} 이번 한 번만 {random.choice(['과제', '수행', '시험'])} 미뤄주시면 안 될까요?")
    s.append(f"B: 아휴, {random.choice(['철수', '영희', '지수'])}야. {random.choice(['무슨', '말도 안 되는'])} 소리를 하는 거니.")
    s.append(f"A: 제가 어제 갑자기 {random.choice(['감기', '가정사', '사고'])} 때문에 정신이 없었거든요.")
    s.append(f"B: 다른 친구들은 다 해왔는데 너만 특혜를 줄 수는 없단다.")
    s.append(f"A: {attach_josa(teacher, '이/가')} {random.choice(['제발', '이번만'])} 도와주세요. {attach_josa(random.choice(['지금 당장', '내일']), '은/는')} 꼭 해서 제출하겠습니다.")
    s.append(f"B: 그럼 오늘 방과 후까지 교무실로 꼭 가져오렴.")
    s.append(f"A: 네 정말 감사합니다! 꼭 {random.choice(['제출', '완성'])}하겠습니다.")
    s.append(f"B: 그래. 약속 어기면 안 된다.")
    return " ".join(s)

def gen_cafe_flow():
    item = random.choice(['아메리카노', '라떼', '조각 케이크', '샌드위치'])
    s = []
    s.append(f"A: 어서오세요. 주문 도와드릴까요?")
    s.append(f"B: 저기 {item} {random.choice(['하나', '두 잔', '지금 당장'])} 주문 가능한가요?")
    s.append(f"A: 네 가능합니다. {attach_josa(random.choice(['결제', '돈']), '은/는')} 카드로 하시겠어요?")
    s.append(f"B: 네 여기요. 혹시 {random.choice(['포인트', '적립', '할인'])} {random.choice(['무슨', '어떤'])} 방법 없나요?")
    s.append(f"A: {random.choice(POOLS['POLITE_SOFTENER'])} 저희 매장은 {attach_josa(random.choice(['적립', '할인']), '이/가')} 마감되었습니다.")
    s.append(f"B: 아 {random.choice(POOLS['FILLER'])} 아쉽네요. 그럼 그냥 주세요.")
    s.append(f"A: 네 {random.choice(['지금 당장', '잠시만'])} 기다려주시면 벨로 알려드릴게요.")
    s.append(f"B: 네 {random.choice(POOLS['FAREWELL_POLITE'])}.")
    return " ".join(s)

def gen_free_flow():
    topic = random.choice(['영화', '여행', '게임', '쇼핑'])
    s = []
    s.append(f"A: {random.choice(POOLS['GREETING_CASUAL'])}. 너 지난 주말에 {topic} {random.choice(['진짜', '무슨'])} 거 본 거야?")
    s.append(f"B: 아 그거? {random.choice(['진짜', '무슨'])} {random.choice(['슬픈', '무서운', '웃긴'])} {random.choice(['내용', '스토리', '영상'])}이었는데 이름이 안 나네.")
    s.append(f"A: 에이 {random.choice(POOLS['DISAGREEMENT'])}. {random.choice(['지금 당장', '얼른'])} 검색해봐.")
    s.append(f"B: {random.choice(POOLS['FILLER'])}... 내 핸드폰에 아까 찍은 사진 있을 수도 있어.")
    s.append(f"A: {random.choice(['무슨', '진짜'])} 사진? 너 사진 찍었어?")
    s.append(f"B: 아니 그냥 포스터 찍었지 인마. {attach_josa(random.choice(['돈', '포인트', '시간']), '이/가')} 아깝게 그걸 왜 찍니.")
    s.append(f"A: 아하 {random.choice(POOLS['FILLER'])}. 그럼 나중에 제목 알아내면 알려줘.")
    s.append(f"B: 그래. 생각나면 바로 카톡할게. {random.choice(POOLS['FAREWELL_CASUAL'])}")
    return " ".join(s)

# ==============================================================================
# 3. Main Generation
# ==============================================================================

def main():
    print("Principle-Driven Polished Generation (v4.1) starting...")
    all_conversations = set()
    target = 3000
    engines = [gen_workplace_flow, gen_school_flow, gen_cafe_flow, gen_free_flow]
    
    while len(all_conversations) < target:
        engine = random.choice(engines)
        conv = engine()
        if len(conv) >= 150:
             all_conversations.add(conv)
             if len(all_conversations) % 500 == 0:
                 print(f"Generated {len(all_conversations)} refined samples...")

    df = pd.DataFrame({'class': '일반 대화', 'conversation': list(all_conversations)})
    
    # Forensic Clean
    df['conversation'] = df['conversation'].str.replace(r'^[A-Z]:\s*', '', regex=True)
    df['conversation'] = df['conversation'].str.replace('\n', ' ')
    df['conversation'] = df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_general_v4.1.csv', index=False, encoding='utf-8-sig')
    print(f"Dataset created: data/synthetic_general_v4.1.csv ({len(df)} samples)")

if __name__ == "__main__":
    main()
