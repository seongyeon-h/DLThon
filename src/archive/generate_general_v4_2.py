import pandas as pd
import random
import os
import re

# ==============================================================================
# Utils: Korean Particle Handler & Noise Engine
# ==============================================================================

def get_josa(word, josa_type):
    if not word: return ""
    try:
        char_code = ord(word[-1]) - 0xAC00
        if char_code < 0 or char_code > 11171: return josa_type.split('/')[1]
        has_jong = char_code % 28 != 0
        pairs = {'은/는': ('은', '는'), '이/가': ('이', '가'), '을/를': ('을', '를'), '와/과': ('과', '와')}
        if josa_type in pairs:
            return pairs[josa_type][0] if has_jong else pairs[josa_type][1]
    except:
        pass
    return ""

def attach_josa(word, josa_type):
    return f"{word}{get_josa(word, josa_type)}"

def inject_noise(text, noise_level=0.2):
    """Randomly removes spaces and adds chat noise."""
    if random.random() > 0.7: # Only noise 30% of global samples
        return text
    
    # Remove spaces randomly
    words = text.split()
    new_words = []
    for i, w in enumerate(words):
        if i > 0 and random.random() < noise_level:
            new_words[-1] = new_words[-1] + w
        else:
            new_words.append(w)
    text = " ".join(new_words)
    
    # Add trailing slang/punctuation
    if random.random() < 0.3:
        slang = random.choice([" ㅋㅋ", " ㄹㅇ", " ㅎ", " ㅎㅇ", " !!", " ...", " ㅜㅜ", " ?"])
        text += slang
        
    return text

# ==============================================================================
# 1. 'Street' Vocabulary & Slang Pools
# ==============================================================================

POOLS = {
    "SLANG": ["ㅋㅋ", "ㅎㅎ", "ㄹㅇ", "인정", "개꿀", "개졸령", "옹개꿀띠", "레알", "커엽", "뭥미", "킹받네", "와웅", "어떢함", "대박"],
    "GREETING_CASUAL": ["야", "머해", "안녕", "하이", "ㅎㅇ", "자냐?", "심심함"],
    "RESPONSE_CASUAL": ["웅웅", "몰라", "어어 왜", "먼데", "말해바", "ㄱㄱ", "ㅇㅇ", "ㄴㄴ"],
    "TOPICS": ["게임", "유튜브", "넷플릭스", "치킨", "편의점", "알바", "학교", "과제", "소개팅", "주식", "코인", "운동"],
    "REACTIONS": ["와 실화냐", "에바임", "개웃겨", "미쳤다", "대박이네", "슬프노", "개졸려", "졸귀"],
    "FAREWELL": ["ㅂㅇ", "ㅂㅂ", "잘자", "낼바", "오키", "ㅃㅃ"]
}

# ==============================================================================
# 2. 'Street' Scenario Engines
# ==============================================================================

def gen_street_chat_flow():
    topic = random.choice(POOLS['TOPICS'])
    s = []
    # Turn 1
    s.append(f"A: {random.choice(POOLS['GREETING_CASUAL'])} {topic} {random.choice(['봤냐', '했음?', '어떰?'])}?")
    # Turn 2
    s.append(f"B: {random.choice(POOLS['RESPONSE_CASUAL'])} {random.choice(POOLS['SLANG'])} {topic} {random.choice(['완전', '진짜', '너무'])} {random.choice(['재밌음', '노잼', '에바임'])}")
    # Turn 3
    s.append(f"A: {random.choice(POOLS['REACTIONS'])} {random.choice(['나도', '난 별로'])} {random.choice(['하고싶다', '보고싶다', '안함'])}")
    # Turn 4
    s.append(f"B: {random.choice(POOLS['AGREEMENT'] if 'A' in POOLS else ['인정', 'ㄹㅇ'])} {random.choice(POOLS['SLANG'])} {random.choice(['언제', '지금 당장'])} {random.choice(['할까', '보자', 'ㄱㄱ'])}")
    # Turn 5
    s.append(f"A: {random.choice(['오키', '그래', '좋아'])} {random.choice(POOLS['SLANG'])} 근데 나 {random.choice(['돈', '포인트', '시간'])} 없음")
    # Turn 6
    s.append(f"B: {random.choice(['에바야', '괜춘', '내가 냄'])} {random.choice(POOLS['SLANG'])} 나중에 {random.choice(['갚으셈', 'ㄱㄱ'])}")
    # Turn 7
    s.append(f"A: {random.choice(POOLS['REACTIONS'])} 역시 {random.choice(['너뿐임', '대박임'])} {random.choice(POOLS['FAREWELL'])}")
    
    return " ".join([inject_noise(line) for line in s])

def gen_noisy_fragment_flow():
    # To mimic t_102 and t_016 (Raw fragments)
    topic = random.choice(POOLS['TOPICS'])
    lines = []
    lines.append(f"{random.choice(POOLS['SLANG'])} {topic} {random.choice(['개꿀', '개졸령', '옹개꿀띠'])}")
    lines.append(f"{random.choice(POOLS['RESPONSE_CASUAL'])} {random.choice(['진짜루', 'ㄹㅇ루'])}")
    lines.append(f"근데 이거 {random.choice(['어떢함', '어케함'])}")
    lines.append(f"몰라 {random.choice(POOLS['SLANG'])}")
    lines.append(f"{random.choice(POOLS['REACTIONS'])}")
    
    # Randomly shuffle or repeat
    if random.random() > 0.5:
        lines = lines[::-1]
    
    return " ".join(lines)

def gen_obsessive_consumer_flow():
    # Mix of polite and rude (customer harassment)
    item = random.choice(['커피', '편의점 도시락', '택배', '배달'])
    s = []
    s.append(f"A: 저기 {item} {random.choice(['언제와요', '왜 안와요', '바꿔줘요'])}")
    s.append(f"B: 네 손님 잠시만요 확인해드릴게요")
    s.append(f"A: 아까부터 계속 기다렸는데 {random.choice(['에바잖아요', '빡치네요'])}")
    s.append(f"B: 죄송합니다 지금 주문이 밀려서요")
    s.append(f"A: {random.choice(POOLS['SLANG'])} 진짜 짜증나네요 빨리 해주세요")
    s.append(f"B: 최대한 빨리 해드리겠습니다")
    
    return " ".join([inject_noise(line) for line in s])

# ==============================================================================
# 3. Main Generation
# ==============================================================================

def main():
    print("V4.2 'Street-Style' Noise-Injected Generation starting...")
    all_conversations = set()
    target = 4000
    engines = [gen_street_chat_flow, gen_noisy_fragment_flow, gen_obsessive_consumer_flow]
    
    while len(all_conversations) < target:
        engine = random.choice(engines)
        conv = engine()
        if len(conv) >= 80:
             all_conversations.add(conv)
             if len(all_conversations) % 1000 == 0:
                  print(f"Generated {len(all_conversations)} street samples...")

    df = pd.DataFrame({'class': '일반 대화', 'conversation': list(all_conversations)})
    
    # Forensic Clean (Removing Role Prefixes)
    df['conversation'] = df['conversation'].str.replace(r'^[A-Z]:\s*', '', regex=True)
    df['conversation'] = df['conversation'].str.replace(r'\s+[A-Z]:\s*', ' ', regex=True)
    df['conversation'] = df['conversation'].str.replace('\n', ' ')
    df['conversation'] = df['conversation'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_general_v4_2.csv', index=False, encoding='utf-8-sig')
    print(f"Dataset created: data/synthetic_general_v4_2.csv ({len(df)} samples)")
    print("Sample Output:")
    print(df['conversation'].head(3).tolist())

if __name__ == "__main__":
    main()
