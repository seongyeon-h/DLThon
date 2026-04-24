# 🚀 DLThon 실험 리포트 (Ablation Study)

## 1. 실험 배경
- **목표**: 합성 데이터(General)와 원본 데이터(Threat)의 순수 결합 상태에서 모델의 베이스라인 성능을 측정하고, 증강(Augmentation)의 필요성을 정량적으로 확인한다.
- **모델 아키텍처**: KLUE-RoBERTa (V2 Head: Weighted Layer Pooling + Residual Block)
- **데이터셋**: 
  - `final_train_no_aug.csv` (4,061건)
  - `final_val_no_aug.csv` (988건)

---

## 2. 실험 1: 노증강(No-Augmentation) 베이스라인
### 📈 학습 로그 (Epoch 1~10)

| Epoch | Train Loss | Train F1 | Val Loss | Val F1 | Time (s) | Best? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1.6003 | 0.2599 | 1.3444 | 0.4486 | 173.94 | ⭐ |
| 2 | 1.1809 | 0.5674 | 0.8890 | 0.7432 | 190.31 | ⭐ |
| 3 | 0.8349 | 0.7887 | 0.6289 | 0.8812 | 194.78 | ⭐ |
| 4 | 0.6968 | 0.8531 | 0.6164 | 0.8917 | 195.24 | ⭐ |
| 5 | 0.6325 | 0.8901 | 0.6158 | 0.8943 | 194.65 | ⭐ |
| 6 | 0.5950 | 0.9072 | 0.5817 | 0.9178 | 195.72 | ⭐ |
| 7 | 0.5638 | 0.9248 | 0.6177 | 0.9049 | 196.31 | - |
| 8 | 0.5481 | 0.9281 | 0.5589 | 0.9177 | 227.21 | - |
| **9** | **0.5278** | **0.9403** | **0.5582** | **0.9260** | **328.05** | ⭐ |
| 10 | 0.5124 | 0.9463 | 0.5838 | 0.9177 | 281.93 | - |

---

### 🔍 성능 분석 (Epoch 9 기준)

#### 1) 클래스별 예측 분포 (Test Set 500건)
| 클래스 | 예측 수 | 실제 수(목표) | 비고 |
| :--- | :---: | :---: | :--- |
| **협박 대화** | 100 | 100 | 목표 수량과 일치 (실제 정답 여부는 미상) |
| **갈취 대화** | 113 | 100 | 예측 과다 (FP 발생 의심) |
| **기타 괴롭힘 대화** | 110 | 100 | 예측 과다 (FP 발생 의심) |
| **직장 내 괴롭힘 대화** | 108 | 100 | 예측 과다 (FP 발생 의심) |
| **일반 대화** | **69** | 100 | **예측 과소 (FN 발생 의심)** |

#### 2) 종합 스코어
- **Validation Best F1**: **0.9260**
- **Public Test Score**: **0.8500**

---

### 💡 통합 심층 분석: 오분류(FP/FN) 원인 및 모델의 "꼼수(Lazy Learning)" 파악

EDA 리포트(`eda_report.md` 및 `eda_general.md`)를 종합 분석한 결과, 모델이 문맥을 온전히 이해하지 않고 4가지 표면적 특징(꼼수)에 의존하여 0.85 스코어에 정체되어 있음이 확인됨.

1.  **꼼수 1: 특정 부사/조사 카운팅 (Hard Negative 취약)**
    *   위협 대화는 `진짜`, `지금 당장` 등 긴박한 부사와 `잖아`의 빈도가 높음. 모델은 이 단어들의 개수만으로 위협을 판별하려 함.
    *   반면, 합성 일반 대화에는 치명적 함정 단어인 **`죄송합니다`(0.05회), `당장`(0.04회), `제발`(0.03회)**이 거의 등장하지 않아, 실전에서 이 단어가 포함된 무해한 일상 대화를 모두 위협(FP)으로 오분류함.
2.  **꼼수 2: '예의 바름(Politeness)'의 함정**
    *   직장 내 괴롭힘의 존댓말 비율이 3.22로 압도적으로 높음.
    *   모델은 "존댓말을 쓰며 갈등이 있으면 직장 내 괴롭힘"이라는 공식을 세워, '고객센터 클레임' 같은 일반 대화도 괴롭힘으로 몽땅 오분류함.
3.  **꼼수 3: 대화 후반부 감정 폭발 (기승전결 템포 의존)**
    *   위협 대화는 후반부(7~10턴)로 갈수록 어조가 0.6~0.7대로 폭발함. 모델은 문장 내용보다 이 후반부 템포에 크게 의존함.
4.  **꼼수 4: 길이와 호흡의 언밸런스 (Length Bias)**
    *   위협은 평균 210자/10턴이나, 합성 일반 대화는 130자/6턴으로 지나치게 짧음.
    *   모델은 문맥을 무시하고 "짧으면 일반 대화, 길면 위협"으로 찍어버릴 빌미를 제공받음.

---

### 🚀 최종 증강 전략 (Augmentation 2.0 Master Plan)

모델의 4대 꼼수를 원천 차단하고 편향을 파훼하기 위해, 위협 대화와 일반 대화에 **정반대의 맞춤형 증강 기법**을 적용함.

**🟢 1. 일반 대화: 안티-꼼수 증강 (편향 파괴 및 스펙 보강)**
*   **[길이 강제 연장 (Padding/Merge)]**: 짧은 일반 대화 2개를 이어 붙이거나 의미 없는 턴을 추가해 길이를 200자/10턴 수준으로 늘림 (꼼수 4 파훼).
*   **[Hard Negative 수동 주입]**: 대화 빈 공간에 "아 제발~", "아니 죄송합니다만", "당장"을 무작위로 꽂아 넣어 모델의 특정 단어 카운팅 의존도 파괴 (꼼수 1 파훼).
*   **['예의 바른 갈등' 주입]**: 직장 도메인이 아닌 상황(중고거래, 고객센터)에서 극도로 깍듯한 존댓말로 싸우는 데이터를 증강 (꼼수 2 파훼).
*   **[Sentence Shuffle (문장 순서 섞기)]**: 발화 순서를 마구 섞어 '후반부 감정 폭발'이라는 기승전결 템포에 대한 기대를 박살 냄 (꼼수 3 파훼).

**🔴 2. 위협 대화: 본질 유지 및 어휘 확장**
*   **[Synonym Replacement (동의어 교체) 및 역번역]**: 기승전결의 흐름(시간적 패턴)은 위협 대화의 핵심 Feature이므로 철저히 유지. 대신 위협 어휘 자체를 다양하게 변형하여 모델의 범용성을 높임. (※ 위협 대화에 Shuffle 적용은 엄격히 금지).
*   **[Random Deletion (무작위 단어 삭제 노이즈)]**: 대화 내 단어를 무작위로 소량 삭제하여, 모델이 특정 조사(예: '~잖아', '의', '과') 빈도에만 과도하게 의존하는 편향을 방지함.       



---

# 실제 구현 코드

### 📝 Augmentation 2.0: 안티-꼼수 및 어휘 확장 로직 명세

이 시스템은 모델이 문맥을 무시하고 표면적 특징에 의존하는 **'Lazy Learning'**을 파괴하기 위해 설계되었습니다.

#### 1️⃣ 공통 유틸리티 (1개)
*   **split_utterances**: 단일 문자열로 된 대화 데이터를 종결어미(요, 다, 까, 어, 지, 네) 기준으로 분리하여 리스트로 만듭니다. 이를 통해 문장 단위의 조작(셔플, 주입 등)이 가능해집니다.

#### 🟢 2️⃣ 일반 대화 증강 (4개 기법 - "안티-꼼수 백신")
일반 대화는 모델의 편향을 깨기 위해 모든 기법을 강력하게(100% 혹은 고정 확률) 적용합니다.

*   **augment_general_merge (길이 연장)**: 짧은 대화 2개를 무작위로 합칩니다. "짧으면 일반 대화"라는 모델의 길이 편향을 파괴합니다.
*   **augment_general_inject_hard_negative (함정 주입)**: 위협 대화의 전유물이었던 "당장", "제발", "진짜" 등의 단어를 무조건 주입합니다. 단어 카운팅 꼼수를 파훼합니다.
*   **augment_general_inject_polite_conflict (예의 바른 갈등)**: 극도로 존댓말을 쓰며 싸우는 문장을 30% 확률로 주입합니다. **"존댓말 갈등 = 직장 괴롭힘"**이라는 공식을 박살냅니다.
*   **augment_general_shuffle (문장 순서 섞기)**: 발화 순서를 마구 뒤섞습니다. **"후반부에 감정이 폭발하면 위협"**이라는 템포 의존성을 제거합니다.

#### 🔴 3️⃣ 위협 대화 증강 (3개 기법 - "어휘 및 표현 확장")
위협 대화는 범죄의 본질(기승전결 템포)을 해치지 않기 위해 확률(p)에 기반하여 세밀하게 변형합니다.

*   **augment_threat_synonym_replacement (동의어 교체)**: 위협 키워드를 발견하면 30% 확률로 비슷한 단어로 바꿉니다. 모델의 어휘 대응력을 높입니다.
*   **augment_threat_back_translation (역번역)**: 10% 확률로 한-영-한 번역을 거칩니다. 문장 구조와 어투를 자연스럽게 변형하여 범용성을 확보합니다.
*   **augment_threat_random_deletion (무작위 삭제)**: 5% 확률로 단어를 지웁니다. 특정 조사(~잖아, 의)에 과하게 의존하는 **과적합(Overfitting)**을 방지합니다.

#### 🚀 데이터 생성 프로세스 요약
1.  **바구니 분류 (Grouping)**: 원본 데이터를 5개 클래스 바구니로 나눕니다.
2.  **부족분 계산 (Sampling)**: 각 클래스가 정확히 2,000건이 되도록 모자란 만큼 원본에서 무작위로 다시 뽑습니다.
3.  **맞춤 요리 (Augmenting)**:
    *   **일반 바구니**: 4개 백신 로직을 풀가동하여 '독한' 데이터를 생성합니다.
    *   **위협 바구니**: 확률에 따라 원본의 느낌을 살린 '다양한' 변종을 생성합니다.
4.  **최종 결합 (Merging)**: 생성된 10,000건을 다시 하나로 합치고 순서를 완전히 섞어 final_train_aug.csv로 저장합니다.

```
import random
import re
import pandas as pd

# =====================================================================
# 🛠️ 공통 유틸리티
# =====================================================================
def split_utterances(text):
    """띄어쓰기로 연결된 대화를 종결어미 기준으로 분리"""
    sentences = re.split(r'(?<=[요다까어해지네냐])\s+', text.strip())
    return [s for s in sentences if s.strip()]

# =====================================================================
# 🟢 1. 일반 대화 전용: 안티-꼼수 증강 함수 (편향 파괴)
# =====================================================================

def augment_general_merge(conv1, conv2):
    """
    [꼼수 4 파훼: 길이 강제 연장]
    짧은 대화 2개를 무작위로 이어 붙여 위협 대화 수준(200자 이상)으로 길이를 맞춥니다.
    ※ 이 함수는 DataFrame 전체를 다룰 때 개별적으로 적용해야 합니다.
    """
    return str(conv1).strip() + " " + str(conv2).strip()

def augment_general_inject_hard_negative(conversation):
    """
    [꼼수 1 파훼: Hard Negative 수동 주입]
    위협 클래스의 단골 단어를 무작위 문장 맨 앞에 꽂아넣어 카운팅 의존도를 부수기 위함입니다.
    """
    # 마스터 플랜에 명시된 독한 함정 단어들
    hard_negatives = [
        "아 제발", "아니 죄송합니다만", "당장", "진짜", 
        "아니 그게 아니라", "근데 생각해보면 맞잖아"
    ]
    sentences = split_utterances(conversation)
    if not sentences: return conversation
    
    num_injects = random.randint(1, 2)
    target_indices = random.sample(range(len(sentences)), min(num_injects, len(sentences)))
    
    for idx in target_indices:
        hn = random.choice(hard_negatives)
        if not sentences[idx].startswith(hn):
            sentences[idx] = hn + " " + sentences[idx]
            
    return ' '.join(sentences)

def augment_general_inject_polite_conflict(conversation):
    """
    [꼼수 2 파훼: 예의 바른 갈등 주입]
    존댓말=직장괴롭힘 이라는 편견을 깨기 위해, 극도로 깍듯한 고객센터/중고거래 갈등 문장을 삽입합니다.
    """
    polite_conflicts = [
        "고객님 정말 죄송하지만 규정상 환불은 어렵습니다",
        "아무리 그래도 이건 너무하신 것 같습니다",
        "제가 분명히 말씀드렸는데 착오가 있으셨나 보네요",
        "선생님 기분 상하셨다면 사과드립니다만 원칙대로 처리하겠습니다",
        "정말 죄송하지만 약속 시간을 자꾸 어기시면 곤란합니다"
    ]
    sentences = split_utterances(conversation)
    if not sentences: return conversation
    
    # 30% 확률로 예의 바른 갈등 문장 하나를 대화 중간에 억지로 쑤셔 넣음
    if random.random() < 0.3:
        insert_idx = random.randint(0, len(sentences))
        sentences.insert(insert_idx, random.choice(polite_conflicts))
        
    return ' '.join(sentences)

def augment_general_shuffle(conversation):
    """
    [꼼수 3 파훼: Sentence Shuffle (문장 순서 섞기)]
    발화 순서를 마구 섞어 후반부에 감정이 폭발한다는 기승전결 템포 규칙을 파괴합니다.
    """
    sentences = split_utterances(conversation)
    if len(sentences) > 3:
        random.shuffle(sentences)
    return ' '.join(sentences)

# =====================================================================
# 🔴 2. 위협 대화 전용: 본질 유지 및 어휘 확장 함수
# =====================================================================

def augment_threat_synonym_replacement(conversation, p=0.2):
    """
    [본질 유지 및 어휘 확장]
    기승전결 흐름은 유지하고(Shuffle 금지) 핵심 위협 단어만 동의어로 교체합니다.
    """
    synonym_dict = {
        "죽여버린다": ["가만 안 둔다", "끝장낸다", "박살낸다"],
        "돈 내놔": ["현금 가져와", "돈 줘", "입금해라"],
        "뒤져서 나오면": ["털어서 나오면", "몸 뒤져서 나오면"],
        "맞을래": ["맞고 싶냐", "혼날래"],
        "부장님": ["팀장님", "과장님", "이사님"],
        "죄송합니다": ["잘못했습니다", "면목없습니다"],
        "시키는 대로": ["하라는 대로", "말하는 대로"]
    }
    
    augmented_conv = conversation
    for target, synonyms in synonym_dict.items():
        if target in augmented_conv and random.random() < p:
            augmented_conv = augmented_conv.replace(target, random.choice(synonyms), 1)
            
    return augmented_conv

# 먼저 라이브러리 설치가 필요합니다: pip install googletrans==4.0.0-rc1
from googletrans import Translator
import random
import time

translator = Translator()

def augment_threat_back_translation(conversation, p=0.1):
    """
    [어휘 확장: 역번역]
    확률 p에 따라 한국어 -> 영어 -> 한국어로 번역하여 문장의 구조와 어휘를 자연스럽게 변형합니다.
    """
    if random.random() > p:
        return conversation
    
    try:
        # 1. 한국어 -> 영어 번역
        en_translation = translator.translate(conversation, src='ko', dest='en').text
        time.sleep(0.5) # API 차단 방지용 딜레이
        
        # 2. 영어 -> 한국어 역번역
        ko_back_translation = translator.translate(en_translation, src='en', dest='ko').text
        time.sleep(0.5)
        
        # 번역 결과가 너무 짧아지거나 깨진 경우 원본 유지
        if len(ko_back_translation) < len(conversation) // 2:
            return conversation
            
        return ko_back_translation
        
    except Exception as e:
        # API 오류 시 원본 반환
        print(f"Translation Error: {e}")
        return conversation

import random

def augment_threat_random_deletion(conversation, p=0.05):
    """
    [본질 유지 및 어휘 확장: 무작위 단어 삭제]
    단어를 무작위로 살짝 삭제하여 특정 조사(의, 과, 잖아 등)에 의존하는 것을 방지합니다.
    """
    words = conversation.split()
    
    # 너무 짧은 문장은 삭제를 건너뜀
    if len(words) < 5:
        return conversation
        
    # 절반 이상은 지워지지 않도록 방어 (핵심 의미 보존)
    retained_words = [word for word in words if random.random() > p]
    if len(retained_words) < len(words) // 2:
        retained_words = words
        
    return ' '.join(retained_words)




# =====================================================================
# 🚀 1. 통합 증강 파이프라인 함수 (모든 기법 적용)
# =====================================================================
def apply_augmentation(row):
    text = str(row['conversation'])
    label = row['class']
    
    if label == "일반 대화":
        # 일반 대화: 안티-꼼수 증강 (편향 파괴)
        text = augment_general_inject_hard_negative(text)     # [꼼수 1 파훼] 센 단어 주입
        text = augment_general_inject_polite_conflict(text)   # [꼼수 2 파훼] 예의 바른 갈등 주입
        text = augment_general_shuffle(text)                  # [꼼수 3 파훼] 순서 마구 섞기
    
    else:
        # 위협 대화: 기승전결 유지 및 어휘 확장
        text = augment_threat_synonym_replacement(text, p=0.3) # [어휘 확장 1] 위협 단어 동의어 교체
        text = augment_threat_back_translation(text, p=0.1)    # [어휘 확장 2] 10% 확률로 역번역 수행
        text = augment_threat_random_deletion(text, p=0.05)    # [어휘 확장 3] 무작위 단어 삭제 노이즈
        
    return text

# =====================================================================
# 🚀 2. 데이터 로드 및 증강 실행 (클래스당 2,000건 맞추기)
# =====================================================================
input_path = '../data/final_train_no_aug.csv'
df_origin = pd.read_csv(input_path)

counts = df_origin['class'].value_counts()
TARGET_COUNT = 2000 # 각 클래스별 목표 수량 (총 10,000건)
augmented_rows = []

# tqdm으로 클래스별 증강 진행률 표시
for cls in counts.index:
    current_count = counts[cls]
    needed = TARGET_COUNT - current_count
    
    if needed <= 0: 
        continue # 이미 2,000건 이상이면 패스
        
    print(f"⏳ [{cls}] 증강 중... (목표: {needed}건 추가)")
    cls_df = df_origin[df_origin['class'] == cls].copy()
    
    for _ in tqdm(range(needed), desc=cls, leave=False):
        # 1. 무작위 원본 샘플 1개 추출
        sample = cls_df.sample(1).iloc[0]
        text = str(sample['conversation'])
        
        # 2. 일반 대화 전용 길이 연장 (꼼수 4 파훼)
        # 30% 확률로 다른 짧은 일반 대화와 병합하여 길이를 위협 대화급으로 늘림
        if cls == "일반 대화" and random.random() < 0.3:
            extra_sample = cls_df.sample(1).iloc[0]
            text = augment_general_merge(text, str(extra_sample['conversation']))
            
        # 3. 위에서 정의한 모든 기법이 들어간 통합 파이프라인 통과
        augmented_text = apply_augmentation({'conversation': text, 'class': cls})
        
        # 4. 결과 리스트에 추가
        augmented_rows.append({
            'class': cls,
            'conversation': augmented_text
        })

# =====================================================================
# 🚀 3. 원본 + 증강본 결합 및 최종 저장
# =====================================================================
df_augmented = pd.DataFrame(augmented_rows)

# 원본 4,000건과 증강본 6,000건을 병합
final_df = pd.concat([df_origin, df_augmented], ignore_index=True)

# 모델이 패턴을 외우지 못하도록 전체 데이터를 무작위로 섞음 (Shuffle)
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

# 새로운 인덱스 부여 및 컬럼 정리
final_df['idx'] = range(len(final_df))
final_df = final_df[['idx', 'class', 'conversation']]

# 최종 파일 저장
# 최종 파일 저장
output_path = '../data/final_train_aug.csv'
final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

print("\n🎉 최종 데이터셋 생성 완료!")
print(f"💾 저장 경로: {output_path}")
print("📊 [최종 데이터 클래스 분포]")
print(final_df['class'].value_counts())

```