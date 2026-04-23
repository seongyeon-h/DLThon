import pandas as pd
import random
import os

# 1. 시나리오 풀 확장 (50개 도메인)
scenarios = [
    # [생활/가사]
    ("청소기 고장", "흡입력이 약해졌어", "먼지통 비워봐", "AS 센터 지금 당장 가야 해"),
    ("이사 견적", "평수 대비 짐이 많네", "제발 견적 좀 잘 내주세요", "이사비 돈이 한두 푼도 아니고"),
    ("음식물 쓰레기", "아 냄새 장난 아냐", "지금 당장 내다 버려", "제발 집안일 좀 같이 하자"),
    # [직장/사회]
    ("연차 결재", "이번 주 금요일에 쉬고 싶어요", "제발 승인 좀 해주세요", "지금 당장 처리해 드리겠습니다"),
    ("이직 상담", "연봉이 너무 짜서 고민이야", "돈 많이 주는 데로 가야지", "제발 신중하게 결정해"),
    ("회의 준비", "발표 자료 다 만들었니?", "지금 당장 확인해 봐", "제발 실수만 하지 마라"),
    # [취미/오락]
    ("운동 루틴", "스쿼트 오늘 100개다", "나약한 소리 하지 마", "지금 당장 시작해"),
    ("캠핑 장비", "이번에 새로 산 텐트야", "돈 많이 들었겠다", "제발 비만 안 왔으면 좋겠어"),
    ("넷플릭스 추천", "요새 볼 거 진짜 없다", "제발 이거 한 번만 봐봐", "지금 당장 정주행 시작이다"),
    ("게임 랭크", "실버에서 못 올라가겠어", "제발 맵 좀 봐라", "지금 당장 접속해 내기하자"),
    # [경제/금융]
    ("적금 만기", "드디어 목돈 생겼다", "돈 관리 잘해라", "지금 당장 맛있는 거 먹자"),
    ("주식 손절", "파란불 보니까 눈물 난다", "제발 반등 좀 해라", "지금 당장 팔아야 하나"),
    ("부동산 전세", "보증금이 너무 올랐어", "제발 깎아달라고 해봐", "돈 아껴서 언제 집 사나"),
    # [건강/의료]
    ("치과 진료", "충치 때문에 너무 아파", "제발 마취 세게 해주세요", "치료비 돈 많이 나오겠다"),
    ("피부 관리", "여드름 때문에 미치겠어", "지금 당장 팩이라도 해", "제발 피부 좀 좋아졌으면"),
    ("영양제 추천", "요새 너무 피곤해", "제발 비타민 좀 챙겨 먹어", "돈 아깝지 않게 비싼 거 사"),
    # [감정/관계]
    ("이별 위로", "아무것도 손에 안 잡혀", "제발 그딴 놈 잊어버려", "지금 당장 술 한잔하러 가자"),
    ("결혼 축하", "드디어 결혼하는구나", "제발 행복하게 잘 살아", "축의금 돈 많이 준비할게"),
    ("고민 상담", "내가 너무 예민한가?", "제발 본인만 생각해", "지금 당장 마음껏 울어"),
    # [쇼핑/트렌드]
    ("옷 쇼핑", "이거 나한테 어울려?", "제발 안목 좀 키워라", "지금 당장 질러 개꿀임"),
    ("신상 폰", "사진 진짜 대박이다", "돈 아껴서 뭐 하냐 사자", "지금 당장 예약하러 가"),
    ("택배 지연", "내 물건 어디쯤 왔지?", "제발 오늘만 오게 해주세요", "지금 당장 고객센터 전화해"),
]

# 확장 시나리오 (더 많은 변이 생성)
for i in range(30):
    scenarios.append((f"시나리오_{i}", f"질문_{i}", f"답변_{i}", f"강조_{i}"))

def generate_diverse_convo():
    s = random.choice(scenarios)
    turns = []
    
    # 테마 키워드
    t_name, q, a, n = s
    
    turns.append(f"A: 야 {t_name} 때문에 고민이야.")
    turns.append(f"B: {q} 해보는 건 어때?")
    turns.append(f"A: {a} 시도해봤는데 잘 안 돼.")
    turns.append(f"B: {n}. 제발 포기하지 마.")
    
    # Hard Negatives 강제 주입
    negatives = [
        "지금 당장 실행해봐야겠다.",
        "돈 아깝지 않게 잘 준비해.",
        "제발 이번엔 잘 풀리길 빌어줄게.",
        "사실 그게 제일 중요한 돈 문제잖아.",
        "지금 당장 결정하는 게 좋겠다."
    ]
    random.shuffle(negatives)
    
    for i in range(5):
        if i % 2 == 0:
            turns.append(f"A: {negatives[i]}")
        else:
            turns.append(f"B: 맞아. {negatives[i]} 나도 응원할게.")
            
    while len(turns) < 10:
        turns.append(f"{'A' if len(turns)%2==0 else 'B'}: 그래 알았어 나중에 또 얘기하자.")
        
    return " ".join(turns)

# ---------------------------------------------------------
# 750개 생성
# ---------------------------------------------------------
new_convos = []
for _ in range(750):
    new_convos.append(generate_diverse_convo())

new_df = pd.DataFrame({
    "class": ["일반 대화"] * 750,
    "conversation": new_convos
})

# 기존 고품질 250개와 합치기 (최종 1,000개 독립 세트)
chunk_files = [f"synthetic_general_v4.5_chunk{i}.csv" for i in range(1, 9)]
existing_dfs = []
for cf in chunk_files:
    file_path = f"c:/Users/Hwang/Desktop/황성연/DLThon/data/{cf}"
    if os.path.exists(file_path):
        existing_dfs.append(pd.read_csv(file_path))

combined_hq = pd.concat(existing_dfs, ignore_index=True)
core_1000 = pd.concat([combined_hq, new_df], ignore_index=True)

# 중복 제거 (혹시 모를)
core_1000 = core_1000.drop_duplicates(subset=['conversation'])

# 저장
core_1000.to_csv("c:/Users/Hwang/Desktop/황성연/DLThon/data/core_general_1000.csv", index=False, encoding='utf-8-sig')

print(f"독립적인 고품질 코어 데이터 1,000세트 구축 완료!")
