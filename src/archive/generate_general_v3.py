import pandas as pd
import random
import os
import re

# ==============================================================================
# 1. Configuration per Strategy.md
# ==============================================================================
TARGET_COUNT = 3000
TURN_RANGE = (8, 12)
CHAR_RANGE = (180, 250)
DOMAINS = {
    "WORK": 0.30,
    "SCHOOL": 0.20,
    "CAFE": 0.20,
    "FREE": 0.30
}

# Hard Negative Keywords to Inject naturally
HARD_NEGATIVES = ["돈이", "제발", "지금 당장", "죄송합니다", "무슨", "진짜"]

# ==============================================================================
# 2. Situational building blocks (High Variety)
# ==============================================================================

VOCAB = {
    "names": ["민지", "철수", "현우", "지수", "혜진", "성민", "유리", "준호"],
    "roles": ["부장님", "대리님", "팀장님", "과장님", "선생님", "조교님"],
    "verbs": ["준비했어요", "확인해볼게요", "말씀드려야겠네요", "봤어요?", "다녀왔나요?", "생각중이에요"],
    "fillers": ["어어", "음", "글쎄요", "글쎄", "아무튼", "사실", "솔직히", "그니깐"],
    "polite_closings": ["네 알겠습니다.", "들어가보겠습니다.", "수고하세요.", "감사합니다."],
    "casual_closings": ["응 이따 봐.", "잘 자~", "오키 확인.", "다음에 또 얘기하자."]
}

# ==============================================================================
# 3. Scenario Engines (Multi-turn Flow)
# ==============================================================================

def build_dialogue(domain):
    turns = []
    num_turns = random.randint(TURN_RANGE[0], TURN_RANGE[1])
    
    # Context specific components
    if domain == "WORK":
        r = random.choice(VOCAB["roles"][:4]) # Office roles
        turns.append(f"A: {r}, 오늘 오전에 {random.choice(['회의', '보고', '일정'])} 어떻게 되나요?")
        turns.append(f"B: 아, {random.choice(VOCAB['names'])}씨. {random.choice(['죄송합니다', '진짜'])}만 제가 지금 {random.choice(['통화', '업무'])} 중이라서요.")
        turns.append(f"A: 아 네, 그럼 나중에 {random.choice(['부장님', '대리님'])} 시간 되실 때 다시 여쭤볼까요?")
        turns.append(f"B: {random.choice(['음', '글쎄요'])}, {random.choice(['지금 당장', '이따가'])}는 좀 그렇고 점심쯤이 좋겠네요.")
        turns.append(f"A: 알겠습니다. 그럼 오후 1시쯤에 {random.choice(['회의실', '사무실'])}로 찾아뵐게요.")
        turns.append(f"B: 네, {random.choice(['부장님', '과장님'])}께도 제가 미리 말씀드려 놓겠습니다.")
        turns.append(f"A: 네 감사합니다. {random.choice(['준비', '정리'])} 잘 해놓겠습니다.")
        turns.append(f"B: 그래요. 수고하세요.")
        if num_turns > 8:
            turns.append(f"A: 감사합니다. {random.choice(VOCAB['polite_closings'])}")
            turns.append(f"B: 네 들어가세요.")
            
    elif domain == "SCHOOL":
        r = "선생님"
        turns.append(f"A: {r}, {random.choice(['제발', '진짜'])} 이번 한 번만 {random.choice(['과제', '청소', '시험'])} 미뤄주시면 안 될까요?")
        turns.append(f"B: 아휴, {random.choice(VOCAB['names'])}야. {random.choice(['무슨', '진짜'])} 소리를 하는 거니.")
        turns.append(f"A: 제가 어제 갑자기 {random.choice(['감기', '정전', '사고'])} 때문에 정신이 없었거든요.")
        turns.append(f"B: 다른 친구들은 다 해왔는데 너만 특혜를 줄 수는 없단다.")
        turns.append(f"A: {random.choice(['선생님', '제발'])}요. {random.choice(['지금 당장', '오늘 내로'])} 꼭 해서 제출하겠습니다.")
        turns.append(f"B: 그럼 오늘 방과 후까지 교무실로 꼭 가져오렴.")
        turns.append(f"A: 네 정말 감사합니다! 꼭 가져갈게요.")
        turns.append(f"B: 그래. 약속 어기면 안 된다.")
        if num_turns > 8:
            turns.append(f"A: 네! 안녕히 계세요.")
            turns.append(f"B: 그래 공부 열심히 하렴.")

    elif domain == "CAFE":
        turns.append(f"A: 어서오세요. 주문 도와드릴까요?")
        turns.append(f"B: 저기 {random.choice(['아메리카노', '라떼'])} 한 잔이랑 조각 케이크 하나 주세요.")
        turns.append(f"A: 네. {random.choice(['돈이', '결제'])}는 카드로 하시나요?")
        turns.append(f"B: 네 여기요. 혹시 {random.choice(['포인트', '적립'])} 가능한가요?")
        turns.append(f"A: {random.choice(['죄송합니다', '아쉽게도'])} 저희 매장은 적립 서비스가 종료되었습니다.")
        turns.append(f"B: 아 {random.choice(['무슨', '진짜'])}요? 아쉽네요. 그럼 그냥 주세요.")
        turns.append(f"A: 네 {random.choice(['지금 당장', '잠시만'])} 기다려주시면 벨로 알려드릴게요.")
        turns.append(f"B: 네 감사합니다. 영수증은 버려주세요.")
        if num_turns > 8:
            turns.append(f"A: 네 주문하신 메뉴 곧 나갑니다.")
            turns.append(f"B: 알겠습니다.")

    else: # FREE
        turns.append(f"A: 야 너 지난 주말에 {random.choice(['영화', '여행', '카페'])} {random.choice(['진짜', '무슨'])} 거 본 거야?")
        turns.append(f"B: 아 그거? {random.choice(['무슨', '진짜'])} 슬픈 {random.choice(['영화', '다큐'])}였는데 이름이 기억 안 나네.")
        turns.append(f"A: 에이 {random.choice(['제발', '말도 안돼'])}. {random.choice(['지금 당장', '얼른'])} 검색해봐.")
        turns.append(f"B: {random.choice(['음', '글쎄'])}... 내 핸드폰에 아까 찍은 사진 있을 수도 있어.")
        turns.append(f"A: {random.choice(['무슨', '진짜'])} 사진? 너 영화 보면서 사진 찍었어?")
        turns.append(f"B: 아니 영화 포스터 찍었지 인마. {random.choice(['돈이', '포인트'])} 아깝게 영화를 왜 찍니.")
        turns.append(f"A: 아하 {random.choice(['진짜', '대박'])}. 그럼 나중에 제목 알아내면 알려줘.")
        turns.append(f"B: 그래. 생각나면 바로 카톡할게.")
        if num_turns > 8:
            turns.append(f"A: 오케이 {random.choice(VOCAB['casual_closings'])}")
            turns.append(f"B: 어 잘 자.")

    # Flatten and validate length
    full_text = " ".join(turns)
    
    # Adjust length if too short (Add fillers)
    while len(full_text) < CHAR_RANGE[0]:
        full_text += f" {random.choice(VOCAB['fillers'])} 그건 그렇고 다음엔 뭐할까? {random.choice(VOCAB['verbs'])}."
    
    # Truncate if too long
    if len(full_text) > CHAR_RANGE[1]:
        full_text = full_text[:CHAR_RANGE[1]-3] + "..."
        
    return full_text

# ==============================================================================
# 4. Global Generation Logic
# ==============================================================================

def main():
    print("Principle-Driven Dataset Generation (v3) starting...")
    records = []
    
    for domain, ratio in DOMAINS.items():
        count = int(TARGET_COUNT * ratio)
        print(f"Generating {count} samples for {domain}...")
        for _ in range(count):
            txt = build_dialogue(domain)
            records.append({
                'class': '일반 대화',
                'conversation': txt
            })
            
    random.shuffle(records)
    df = pd.DataFrame(records)
    
    # Force physical Spec Clean
    df['conversation'] = df['conversation'].str.replace(r'^[A-Z]:\s*', '', regex=True) # First line strip
    df['conversation'] = df['conversation'].str.replace(r'\s[A-Z]:\s*', ' ', regex=True) # Middle strip
    df['conversation'] = df['conversation'].str.replace('\n', ' ')
    df['conversation'] = df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_general_v3.csv', index=False, encoding='utf-8-sig')
    print(f"✅ V3 Dataset created: data/synthetic_general_v3.csv ({len(df)} samples)")

if __name__ == "__main__":
    main()
