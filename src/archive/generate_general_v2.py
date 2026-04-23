import pandas as pd
import random
import os
import re

# ==============================================================================
# Expanded Lexicon for High Variance
# ==============================================================================

ADVERBS = ["진짜", "완전", "되게", "엄청", "너무", "정말", "막", "졸라", "개", "겁나", "무지"]
FILLERS = ["어어", "응응", "그니까", "음", "뭐랄까", "아무튼", "글쎄", "사실", "솔직히"]
ENDINGS = ["그치?", "그럴걸?", "맞지?", "아닌가?", "인정?", "말도 안 돼", "대박", "헐", "ㅋㅋㅋ"]

CASUAL_SLANG = {
    "openings": ["야", "헐", "대박", "미친", "근데 있잖아", "진짜 어이없어", "요즘 왜 이래", "내 말 좀 들어봐", "근데 너 그거 알아?", "생각해보면"],
    "topics": ["어제 본 드라마", "오늘 먹은 마라탕", "주말에 간 카페", "편의점 신상", "유튜브 쇼츠", "넷플릭스 영화", "인물 사진", "코인 떡상"],
    "resolutions": ["배고프다 밥먹자", "나중에 또 얘기해", "인생 시트콤이네", "오케이 확인", "ㅋㅋㅋ 담에 봐", "좀이따 톡해", "나 씻으러 감"]
}

WORKPLACE_NEUTRAL = {
    "roles": ["과장님", "대리님", "팀장님", "부장님", "사원님", "매니저님", "파트장님", "실장님"],
    "tasks": ["보고서", "회의록", "마감 일정", "메일 발송", "파일 공유", "주간 회의", "점심 메뉴", "기획안", "데이터 분석"],
    "gossip": ["어우 피곤해", "퇴사 마렵다", "연봉 협상", "주말 출근 안하겠지", "커피 한잔 하실래요?", "이번 달 보너스", "점심 뭐 먹죠?"],
    "closing": ["네 알겠습니다", "수고하셨습니다", "이따 뵙겠습니다", "잘 부탁드려요", "먼저 퇴근합니다"]
}

FINANCIAL_NEUTRAL = {
    "topics": ["중고거래", "번개장터", "계좌이체", "택배 송장", "할인 쿠폰", "주식 폭락", "물가 장난 아님", "코인 투자", "가계부 정리"],
    "phrases": ["이거 네고 되나요?", "송금 완료했습니다", "직거래 선호해요", "입금 확인 부탁드려요", "적금 만기", "수수료 비싸네", "돈 모으기 힘들다"]
}

FAMILY_NAGGING = {
    "moods": ["공부 좀 해라", "방 청소 언제 하니", "학원 늦겠다", "밥 차려놨다", "일찍 좀 다녀라", "동생 좀 챙겨", "이거 좀 먹어봐"],
    "replies": ["알았어 한다고", "배고파", "나 피곤해", "내일 할게요", "미안해 엄마", "잉", "지금 가요", "좀이따 할게"]
}

VENTING_EMOTIONAL = {
    "topics": ["취업 준비", "면접 광탈", "코로나 짜증", "인생 권태기", "헤어진 연인", "학점 망함", "인간 관계", "공부하기 싫음"],
    "phrases": ["나 진짜 열심히 살았는데", "왜 나만 안 되지?", "세상은 넓고 갈 곳은 없다", "부모님께 죄송해", "술 마시고 싶다", "다 때려치우고 싶다"]
}

# ==============================================================================
# Diversified Generation Engine
# ==============================================================================

def get_sentence(pool_type):
    adv = random.choice(ADVERBS)
    fil = random.choice(FILLERS)
    end = random.choice(ENDINGS)
    
    if pool_type == "casual":
        o = random.choice(CASUAL_SLANG["openings"])
        t = random.choice(CASUAL_SLANG["topics"])
        r = random.choice(CASUAL_SLANG["resolutions"])
        return f"{o} {adv} {t} 봤어? {fil} {end} {r}. 나도 {adv} {t} 생각 중이었는데 {fil} {end}."
    
    elif pool_type == "work":
        ro = random.choice(WORKPLACE_NEUTRAL["roles"])
        ta = random.choice(WORKPLACE_NEUTRAL["tasks"])
        go = random.choice(WORKPLACE_NEUTRAL["gossip"])
        cl = random.choice(WORKPLACE_NEUTRAL["closing"])
        return f"{ro} {adv} {ta} 확인 부탁드려요. {fil} {go}. {cl}."
    
    elif pool_type == "financial":
        t = random.choice(FINANCIAL_NEUTRAL["topics"])
        p = random.choice(FINANCIAL_NEUTRAL["phrases"])
        return f"저기 {t} 때문에 연락했는데 {adv} {p}. {fil} {t} 가능한가요? {p}."
    
    elif pool_type == "nagging":
        m = random.choice(FAMILY_NAGGING["moods"])
        re = random.choice(FAMILY_NAGGING["replies"])
        return f"야 {adv} {m}. {re}. {fil} 너 진짜 {adv} {m}. {re}."
    
    elif pool_type == "venting":
        t = random.choice(VENTING_EMOTIONAL["topics"])
        p = random.choice(VENTING_EMOTIONAL["phrases"])
        return f"아 {adv} {t} 때문에 힘들다. {fil} {p}. {t} 잘 될까? {p}."
    
    return "이건 그냥 지나가는 말이야."

def main():
    all_conversations = []
    
    # Increase n to 10,000 to ensure uniqueness after deduplication
    for _ in range(2000): all_conversations.append(get_sentence("casual"))
    for _ in range(1500): all_conversations.append(get_sentence("work"))
    for _ in range(1500): all_conversations.append(get_sentence("financial"))
    for _ in range(1500): all_conversations.append(get_sentence("nagging"))
    for _ in range(1500): all_conversations.append(get_sentence("venting"))
    
    # Static Description & Jokes with variety
    for _ in range(1000):
        gender = random.choice(["남자", "여자", "분", "사람", "친구"])
        look = random.choice(["안경 쓰고", "키 크고", "단발인", "파란 옷 입은", "웃는"])
        item = random.choice(["청바지", "치마", "반팔", "가방", "모자"])
        all_conversations.append(f"그 때 {gender} 한 명 있었는데 {look} 것 같았어. {random.choice(FILLERS)} {item} 입고 있었는데 기억나? {random.choice(ENDINGS)}")

    for _ in range(1000):
        quote = random.choice(['나 다시 돌아갈래', '인생은 초콜릿 상자 같아', '넌 나에게 모욕감을 줬어', '미안하다 사랑한다'])
        type_ = random.choice(['노래 가사', '영화 대사', '드라마 명대사', '상황극'])
        all_conversations.append(f"너 {quote} 이거 알아? 무슨 {type_}인가? 응 {type_} {random.choice(ADVERBS)} 해본 거야. {random.choice(ENDINGS)}.")

    random.shuffle(all_conversations)
    
    df = pd.DataFrame({
        'class': '일반 대화',
        'conversation': all_conversations
    })
    
    # DEDUPLICATION HERE
    before = len(df)
    df = df.drop_duplicates(subset=['conversation'])
    print(f"Removed {before - len(df)} duplicates during generation.")
    
    # Take top 4,000 unique ones
    df = df.head(4000)
    
    df['conversation'] = df['conversation'].str.replace('\n', ' ')
    df['conversation'] = df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_general_v2.csv', index=False, encoding='utf-8-sig')
    print(f"Successfully created data/synthetic_general_v2.csv with {len(df)} unique samples.")

if __name__ == "__main__":
    main()
