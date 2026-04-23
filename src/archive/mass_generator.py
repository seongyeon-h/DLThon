import pandas as pd
import random
import os

# --- 1. 변중 리스트 (Variants for Combinatorial Generation) ---
NAMES = ["부장님", "대리님", "팀장님", "과장님", "차장님", "사원님", "민수", "영미", "현우", "지수", "지혜", "철수"]
PLACES = ["회의실", "탕비실", "카페", "편의점", "식당", "매점", "공연장", "공원", "지하철역", "도서관", "운동장"]
MENUS = ["아메리카노", "라떼", "샌드위치", "김밥", "제육덮밥", "김치찜", "파스타", "피자", "삼겹살", "떡볶이"]
TIMES = ["지금 당장", "이따가 오후에", "내일 아침에", "조금 뒤에", "퇴근하기 전에", "수업 끝나고"]
FEELINGS = ["기대되네요", "다행이에요", "조금 걱정되지만 괜찮아요", "즐거울 것 같아요", "맛있겠네요"]

# --- 2. 도메인별 템플릿 구조 (Templates) ---
# 각 템플릿은 변수를 채울 수 있는 f-string 구조를 가집니다.
# 실전 데이터셋(test.csv)과 형식을 통일하기 위해 모든 개행(\n)을 공백으로 평탄화합니다.
TEMPLATES = {
    "WORKPLACE": [
        "{name} {time} {place}에서 회의 가능한가요? 네 {name} 지금 바로 준비해서 이동할게요. 준비물은 제가 미리 챙겨두었으니 몸만 오셔요. 알겠습니다 {feeling} 얼른 가서 뵙겠습니다. 네 {place} 앞에서 기다리고 있을게요. 서둘러서 가겠습니다 조금만 기다려 주세요. 죄송합니다 바쁘신데 갑자기 연락드려서. 아니에요 제 업무인걸요 {time} 뵙죠.",
        "{name} 오늘 점심 메뉴 {menu} 어떠신가요? 오 {feeling} 저도 그거 먹고 싶었어요. 그럼 {time} {place} 앞에서 뵙는 거로 할까요? 좋지요 제가 {place} 미리 예약 가능한지 알아볼게요. 네 {name} 예약되면 바로 연락 부탁드립니다. 네 알겠습니다 {name}도 이따 뵙겠습니다. 제발 예약이 꽉 차지 않았으면 좋겠네요. 제가 {time} 확인해보고 바로 말씀드릴게요.",
    ],
    "SCHOOL": [
        "{name} 오늘 점심 메뉴 {menu} 나온다는데 봤어? 와 진짜? 대박이다 나 {menu} 진짜 좋아하거든. 그러니까 우리 {time} 수업 끝나자마자 {place}으로 튀어가자. 좋아 제발 줄이 안 길었으면 좋겠네. 그러게 요즘 애들 손이 너무 빨라서 걱정이야. 우리가 더 빨리 가면 되지 걱정 마 {feeling}. 그럼 4교시 끝나자마자 정문 앞에서 봐. 응 이따가 {time} 정문 앞에서 만나!",
    ],
    "CAFE": [
        "어서 오세요 {place}입니다 주문 도와드릴까요? {menu} 두 잔이랑 조각 케이크 하나 주세요. 네 알겠습니다 {menu}은 {feeling} 따뜻한 거로 드릴까요? 아뇨 시원한 아이스로 한 잔 해주시고 하나는 따뜻하게요. 네 총 얼마입니다 결제는 카드로 하시나요? 네 여기요 {menu} 나오는데 오래 걸리나요? 아뇨 {time} 준비해 드릴게요 잠시만 기다려 주세요. 네 영수증은 버려주시고 벨 울리면 가지러 올게요.",
    ],
    "FREE": [
        "오늘 날씨 {feeling} 그치? 산책하기 딱 좋아. 응 미세먼지도 없고 {place} 가기에 완벽한 날씨네. 우리 {time} 근처 {place}이라도 잠시 다녀올까? 좋아 돗자리랑 간단한 간식 {menu} 같은 거 챙겨가자. 제발 주말 내내 날씨가 이랬으면 좋겠다 그치? 그러게 일기예보 보니까 당분간 계속 맑다고 하더라고. 오 {feeling} 그럼 내일 {time} 준비해서 가자. 응 내가 {menu} 미리 주문해 놓을게.",
    ]
}

def generate_3000(target_total=3000):
    import re
    records = []
    print(f"Generating {target_total} synthetic samples using combinatorial templates...")
    
    # 도메인 비율 설정 (strategy.md 준수)
    domains = ["WORKPLACE", "SCHOOL", "CAFE", "FREE"]
    
    for i in range(target_total):
        domain = random.choice(domains)
        template = random.choice(TEMPLATES[domain])
        
        # 무작위 변수 조합
        content = template.format(
            name=random.choice(NAMES),
            place=random.choice(PLACES),
            menu=random.choice(MENUS),
            time=random.choice(TIMES),
            feeling=random.choice(FEELINGS)
        )
        
        # 물리적 스펙 보정 (글자 수가 너무 짧으면 문구 추가)
        if len(content) < 180:
            content += " 아 그리고 혹시 모르니까 연락처 하나만 남겨주세요. 네 제 번호는 아까 명함에 적어드린 대로입니다."
        
        # 최종 정제: 개행 제거 및 화자 표식 방어
        content = content.replace('\n', ' ')
        content = re.sub(r'^([A-Z]):\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s+', ' ', content).strip()
        
        records.append({
            'idx': i,
            'class': '일반 대화',
            'conversation': content
        })
        
    df = pd.DataFrame(records)
    df.to_csv('data/synthetic_general.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Successfully generated {len(df)} samples in data/synthetic_general.csv")

if __name__ == "__main__":
    generate_3000()
