import pandas as pd
import random
import os
import re

# ==============================================================================
# 1. 고도화된 시나리오 시드 (Entity & Paraphrasing Pools)
# ==============================================================================

ENTITIES = {
    "COMPANIES": ["삼성", "카카오", "네이버", "쿠팡", "배민", "현대차", "LG", "SK", "당근마켓", "토스"],
    "CELEBS": ["아이유", "방탄", "창모", "뉴진스", "송중기", "송혜교", "유재석", "임영웅", "지드래곤"],
    "LOCATIONS": ["강남역", "홍대", "에버랜드", "제주도", "부산", "편의점", "카페", "교보문고", "한강공원"],
    "REASONS": ["코로나", "경기 불황", "갑작스러운 사고", "개인 사정", "그냥 심심해서", "학업 때문에"]
}

POOLS = {
    "CAREER_START": ["이번에 {company} 지원했어?", "{company} 공고 떴던데 봤어?", "너 저번에 {company} 면접 본다며?", "요즘 {company} 분위기 어때?"],
    "CAREER_HARD": ["자소서 문항이 너무 함정이야.", "경쟁률이 진짜 말도 안 돼.", "코딩 테스트가 너무 어렵더라.", "면접 질문이 날카로워서 당황했어."],
    "SYMPATHY": ["와 진짜 공감돼요.", "응응 내 말이 그 말이야.", "아 진짜? 몰랐네.", "헐 대박이다.", "나도 그렇게 생각해."],
    "REACTION_SOFT": ["그럴 수도 있겠다", "근데 좀 아쉽긴 하더라", "솔직히 나도 그래", "마음이 좀 그러네", "그래도 다행이다"],
    "HOBBY_START": ["혹시 {celeb} 신곡 들어봤어?", "{celeb} 나오는 드라마 봤어?", "너 {celeb} 팬이라며?", "어제 {celeb} 영상 올라온 거 봤어?"],
    "SOCIAL_START": ["요즘 {topic} 뉴스 봤어?", "{topic} 문제가 진짜 심각한 거 같아.", "날씨 보니까 {topic} 실감 나더라."]
}

# ==============================================================================
# 2. 고난도 고유성 보장 엔진 (Turn-level Randomness)
# ==============================================================================

def gen_career_flow_v2():
    company = random.choice(ENTITIES['COMPANIES'])
    s = []
    s.append(f"A: {random.choice(POOLS['CAREER_START']).format(company=company)}")
    s.append(f"B: 아니 나 서류 쓰다가 {random.choice(['포기했어', '중단했어', '꼬였어'])}. 너무 힘들더라.")
    s.append(f"A: 왜? 너 {random.choice(['스펙', '학점', '준비한 거'])} 좋잖아. {random.choice(['자신감 가져', '괜찮아'])}.")
    s.append(f"B: 아 그게 문제가 아니라 {random.choice(POOLS['CAREER_HARD'])} 무슨 철학 문제인 줄.")
    s.append(f"A: 하긴 요새 대기업들이 좀 {random.choice(['별나긴', '까다롭긴'])} 하지. 제발 이번에는 붙자.")
    s.append(f"B: 나도 그래. 진짜 {random.choice(['취업', '합격'])} 안 되면 어쩌나 걱정이야. 부모님께도 죄송하고.")
    s.append(f"A: {random.choice(POOLS['SYMPATHY'])} 원래 다 그런 거야. 지금 당장 결과 안 나온다고 {random.choice(['낙담마', '슬퍼마'])}.")
    s.append(f"B: 고맙다. 너는 어떻게 돼가? {random.choice(['준비 잘해?', '상황 어때?'])}")
    s.append(f"A: 나도 뭐 비슷하지. 근데 나는 이번에 {random.choice(['영어 성적', '자격증', '코테'])}가 좀 낮게 나와서.")
    s.append(f"B: 에이 {random.choice(['다시 보면 되지', '괜찮아'])}. 우리 이따가 {random.choice(['스터디', '맥주', '밥'])}나 같이 할까?")
    s.append(f"A: {random.choice(['그래 좋아', '오 좋지'])}. 이따 {random.choice(ENTITIES['LOCATIONS'])}에서 보자.")
    s.append(f"B: 오키. {random.choice(['조심히 와', '나중에 봐', '확인'])}.")
    return " ".join(s)

def gen_hobby_flow_v2():
    celeb = random.choice(ENTITIES['CELEBS'])
    s = []
    s.append(f"A: {random.choice(POOLS['HOBBY_START']).format(celeb=celeb)}")
    s.append(f"B: 아 당연히 봤지. 나 그거 나오자마자 {random.choice(['열 번 넘게', '무한 반복', '계속'])}했잖아.")
    s.append(f"A: 그니깐! 특히 {random.choice(['후반부', '초반부', '하이라이트'])} 연출이 진짜 소름 돋았어.")
    s.append(f"B: 나는 중간에 {random.choice(['노래', '대사', '표정'])}가 참 좋더라. 사실 좀 울컥했어.")
    s.append(f"A: {random.choice(POOLS['SYMPATHY'])} 솔직히 이번 작업물은 {random.choice(['역대급', '최고', '대박'])}인 거 같아.")
    s.append(f"B: 근데 댓글 보니까 {random.choice(['실망했다는', '별로라는', '이상하다는'])} 사람들도 있더라고.")
    s.append(f"A: 뭐 모든 사람을 만족시키는 건 불가능하니까. 근데 {random.choice(['나쁘지 않은 듯', '난 좋았어'])}.")
    s.append(f"B: 맞아. 나도 그렇게 생각해. {celeb} 싫어하는 사람도 있듯이 다 다른 거지.")
    s.append(f"A: 그치. 내 주변에는 다 좋다고 난리인데 말이야. 나중에 {random.choice(['콘서트', '팬미팅'])} 꼭 가자.")
    s.append(f"B: 와 진짜 꼭 가고 싶다. 제발 {random.choice(['티켓팅', '표'])} 성공했으면 좋겠다.")
    s.append(f"A: 내가 {random.choice(['광클해서', '도와줘서'])} 꼭 잡아줄게. 우리 같이 가야지.")
    s.append(f"B: 역시 너뿐이다. {random.choice(['나중에 연락해', '이따 봐'])}.")
    return " ".join(s)

def gen_deep_talk_v2():
    s = []
    s.append(f"A: 요즘 마음이 좀 {random.choice(['그래', '복잡해', '허해'])}. 내가 잘 살고 있나 싶고.")
    s.append(f"B: 왜? 무슨 일 있었어? 너 요새 좀 {random.choice(['힘들어', '피곤해', '조용해'])} 보이긴 하더라.")
    s.append(f"A: 아니 그냥 특별한 일은 없는데 문득 그런 생각이 드네. 내가 {random.choice(['바보', '부족한 사람'])} 같아서.")
    s.append(f"B: 그런 말 하지 마. 누구나 그럴 때가 있어. 나도 사실 {random.choice(['요즘 그래', '항상 고민해'])}.")
    s.append(f"A: 진짜? 너는 되게 {random.choice(['씩씩해', '밝아', '평온해'])} 보여서 몰랐어.")
    s.append(f"B: 그럼. 속마음 털어놓는 게 쉬운 건 아니니까. {random.choice(['기도', '명상', '독서'])}도 해보고 해.")
    s.append(f"A: 오 몰랐네. 그래도 믿는 구석이 있으면 {random.choice(['든든', '차분'])}해지긴 하겠다.")
    s.append(f"B: 응 마음이 훨씬 좋아지더라. 너도 이따 시간 되면 같이 {random.choice(['이야기', '커피'])} 좀 할래?")
    s.append(f"A: 고마워. 이렇게 말해주는 것만으로도 {random.choice(['실망감', '우울함'])}이 좀 사라지는 느낌이야.")
    s.append(f"B: 너는 더 좋아질 거야. 진짜 장담해. 충분히 {random.choice(['잘하고', '멋지게 살고'])} 있으니까.")
    s.append(f"A: 위로해줘서 정말 고마워. 마음이 한결 가벼워졌어. 나중에 {random.choice(['선물', '밥'])} 사줄게.")
    s.append(f"B: 아니야 당연히 할 일을 한 건데. 우리 {random.choice(['조만간 봐', '내일 봐'])}.")
    return " ".join(s)

# ==============================================================================
# 3. Main Generation (Ensure Uniqueness)
# ==============================================================================

def main():
    print("V4.3 'Deep-Context' Generation starting (Fixing Uniqueness)...")
    all_conversations = set()
    target = 3000
    engines = [gen_career_flow_v2, gen_hobby_flow_v2, gen_deep_talk_v2]
    
    while len(all_conversations) < target:
        engine = random.choice(engines)
        conv = engine()
        if len(conv) >= 150:
             all_conversations.add(conv)
             if len(all_conversations) % 500 == 0:
                  print(f"Generated {len(all_conversations)} unique high-quality samples...")

    df = pd.DataFrame({'class': '일반 대화', 'conversation': list(all_conversations)})
    
    # Forensic Clean
    df['conversation'] = df['conversation'].str.replace(r'^[A-Z]:\s*', '', regex=True)
    df['conversation'] = df['conversation'].str.replace(r'\s+[A-Z]:\s*', ' ', regex=True)
    df['conversation'] = df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_general_v4_3.csv', index=False, encoding='utf-8-sig')
    print(f"Dataset created: data/synthetic_general_v4_3.csv ({len(df)} samples)")

if __name__ == "__main__":
    main()
