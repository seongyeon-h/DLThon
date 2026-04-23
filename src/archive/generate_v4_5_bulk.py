import pandas as pd
import random
import os

# ---------------------------------------------------------
# 1. 기존 고품질 청크 (1-8) 병합 (250건)
# ---------------------------------------------------------
data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
chunk_files = [f"synthetic_general_v4.5_chunk{i}.csv" for i in range(1, 9)]
existing_dfs = []

for cf in chunk_files:
    file_path = os.path.join(data_dir, cf)
    if os.path.exists(file_path):
        existing_dfs.append(pd.read_csv(file_path))

combined_v4_5_hq = pd.concat(existing_dfs, ignore_index=True)
current_count = len(combined_v4_5_hq)
target_count = 3000
needed_count = target_count - current_count

print(f"현재 고품질 데이터: {current_count}건. 부족분: {needed_count}건 생성 시작...")

# ---------------------------------------------------------
# 2. 테마별 템플릿 엔진 (High Variance)
# ---------------------------------------------------------

themes = [
    {
        "name": "Counseling",
        "intro": ["선생님 제가 요새", "상담사님 다름이 아니라", "저 고민이 하나 있는데", "요새 마음이 너무 답답해서"],
        "problem": ["잠을 잘 못 자요", "번아웃이 온 것 같아요", "의욕이 하나도 없어요", "사소한 일에도 화가 나요"],
        "mirror": ["마음이 많이 피곤하셨군요", "그 상황이 정말 답답하게 느껴지셨겠어요", "기대한 만큼 성과가 없으니 낙담하셨군요"],
        "negative_context": ["제발 제 마음 좀 알아주세요", "지금 당장이라도 해결하고 싶어요", "돈 아끼지 않고 치료받고 싶어요"]
    },
    {
        "name": "MarketHaggling",
        "item": ["꽃게", "귤", "중고 노트북", "사과", "겨울 코트"],
        "request": ["두 마리만 더 주쇼", "만원만 깎아줘요", "단골인데 서비스 없나요?"],
        "refuse": ["남는 게 없어요", "이미 최저가입니다", "요즘 물가가 너무 비싸서요"],
        "negative_context": ["제발 단골 정을 생각해서라도요", "지금 당장 현금으로 드릴게요", "돈이 문제가 아니라 정이죠"]
    },
    {
        "name": "TechSupport",
        "issue": ["컴퓨터가 안 켜져요", "인터넷이 너무 느려요", "오류 메시지가 떠요", "아이디가 생각 안 나요"],
        "action": ["드라이버 다시 깔아봐", "랜선 뽑았다 꽂아봐", "포맷이 답이야"],
        "negative_context": ["제발 이거 좀 고쳐줘", "지금 당장 마감인데 미치겠네", "돈 들여서 수리받아야 하나"]
    },
    {
        "name": "SocialTension",
        "situation": ["동창회에서 학벌 얘기", "소개팅에서 매너 없는 행동", "직장에서 연차 쓰기 눈치"],
        "reaction": ["그건 좀 듣기 그렇네", "예의가 너무 없다", "기분 나쁘게 하지 마라"],
        "negative_context": ["제발 남의 인생에 참견 마라", "지금 당장 사과해", "돈이 다가 아니잖아"]
    },
    {
        "name": "Foodie",
        "menu": ["열라면 순두부", "마라탕 꿔바로우", "수제버거", "담백한 파스타"],
        "opinion": ["이 조합 진짜 개꿀맛이야", "미슐랭 가이드급임", "다신 오고 싶지 않은 맛이야"],
        "negative_context": ["제발 한 번만 먹어봐", "지금 당장 먹으러 가자", "돈 아깝지 않은 맛이야"]
    }
]

def generate_sentence():
    theme = random.choice(themes)
    turns = []
    
    if theme["name"] == "Counseling":
        turns.append(f"A: {random.choice(theme['intro'])} {random.choice(theme['problem'])}.")
        turns.append(f"B: {random.choice(theme['mirror'])}.")
        turns.append(f"A: {theme['negative_context'][0]}.")
        turns.append(f"B: {theme['negative_context'][1]} 해결되기보다 천천히 들여다보죠.")
        turns.append(f"A: {theme['negative_context'][2]} 투자할 준비는 되어 있습니다.")
        turns.append(f"B: 본인을 아끼는 마음이 정말 훌륭하시네요.")
    
    elif theme["name"] == "MarketHaggling":
        turns.append(f"A: 사장님 이 {random.choice(theme['item'])} {random.choice(theme['request'])}.")
        turns.append(f"B: 아유 손님 {random.choice(theme['refuse'])}.")
        turns.append(f"A: {theme['negative_context'][0]}.")
        turns.append(f"B: 안 돼요 저도 먹고살아야죠.")
        turns.append(f"A: {theme['negative_context'][1]} 결제할 테니 덤 좀 줘요.")
        turns.append(f"B: 하하 알았어요 {theme['negative_context'][2]} 문제가 아니라 정으로 드립니다.")
        
    elif theme["name"] == "TechSupport":
        turns.append(f"A: 야 {random.choice(theme['issue'])}.")
        turns.append(f"B: {random.choice(theme['action'])}.")
        turns.append(f"A: {theme['negative_context'][0]} 나 과제 제출해야 해.")
        turns.append(f"B: 알았어 내가 봐줄게 진정해.")
        turns.append(f"A: {theme['negative_context'][1]} 안 되면 나 진짜 망해.")
        turns.append(f"B: {theme['negative_context'][2]} 아깝게 수리점 가지 말고 나만 믿어.")

    elif theme["name"] == "SocialTension":
        turns.append(f"A: 아까 그 사람이 비웃는 거 보셨어요?")
        turns.append(f"B: {random.choice(theme['reaction'])}.")
        turns.append(f"A: {theme['negative_context'][0]} 자기 인생이나 잘 살지.")
        turns.append(f"B: 맞아 너무 신경 쓰지 마요.")
        turns.append(f"A: {theme['negative_context'][1]} 가서 한마디 하고 싶네요.")
        turns.append(f"B: {theme['negative_context'][2]} 많다고 유세 부리는 거 정말 꼴불견이에요.")

    elif theme["name"] == "Foodie":
        turns.append(f"A: 오늘 {random.choice(theme['menu'])} 어때?")
        turns.append(f"B: {random.choice(theme['opinion'])}.")
        turns.append(f"A: {theme['negative_context'][0]} 나 이거 꿈에도 나왔어.")
        turns.append(f"B: 하하 먹는 거에 진심이네.")
        turns.append(f"A: {theme['negative_context'][1]} 출발하자 배고파.")
        turns.append(f"B: 그래 {theme['negative_context'][2]} 아깝지 않게 아주 비싼 걸로 먹자.")

    # 보충 (Turns 8~12 맞춤)
    while len(turns) < 10:
        filler = random.choice(["아 정말요?", "오호 그렇군요.", "저도 동감입니다.", "신기하네요.", "그럴 수도 있죠.", "맞아요.", "대단하시네요."])
        turns.append(f"{'A' if len(turns)%2==0 else 'B'}: {filler}")
    
    return " ".join(turns)

# ---------------------------------------------------------
# 3. 데이터 생성 및 최종 저장
# ---------------------------------------------------------
new_conversations = []
for _ in range(needed_count):
    new_conversations.append(generate_sentence())

new_df = pd.DataFrame({
    "class": ["일반 대화"] * needed_count,
    "conversation": new_conversations
})

final_df = pd.concat([combined_v4_5_hq, new_df], ignore_index=True)

# 셔플 및 저장
final_df = final_df.sample(frac=1).reset_index(drop=True)
final_df.to_csv(os.path.join(data_dir, "synthetic_general_v4.5_3000.csv"), index=False, encoding='utf-8-sig')

print(f"최종 3,000건 생성 완료: data/synthetic_general_v4.5_3000.csv")
