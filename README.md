# 🛡️ DLthon: 대화형 위협 탐지 및 분류 프로젝트

본 프로젝트는 대화 데이터를 분석하여 **협박, 갈취, 직장 내 괴롭힘, 기타 괴롭힘** 및 **일반 대화**의 5개 클래스를 정밀 분류하는 자연어 처리(NLP) 모델을 개발하는 것을 목표로 합니다. 특히 데이터 누수를 철저히 차단하고, 모델의 가중치를 보호하는 보수적 파인튜닝 전략을 사용하여 최적의 일반화(Generalization) 성능을 확보했습니다.

---

### 📂 Repository Structure

```text
DLthon/
├── data/               # 데이터셋 (Raw, Processed, Synthetic)
│   ├── past/           # 이전 버전의 구형 데이터 및 실험용 임시 파일 백업 폴더
│   ├── train.csv       # 원본 학습 데이터 (불균형 데이터)
│   ├── test.csv        # 대회 평가용 추론 데이터
│   ├── correct.csv     # 추출된 실제 일반 대화 정답셋 (분석용)
│   ├── synthesis.csv   # 생성된 일반 대화 합성 원본 (1,000건)
│   ├── train_final.csv # 위협 증강 + 합성 데이터 증강 완료된 최종 학습셋 (완벽 밸런스 15,000건)
│   ├── val_final.csv   # Leakage 방지가 적용된 최종 검증셋
│   └── submission.csv  # 최종 변환이 완료된 대회 제출용 파일
├── docs/               # 가이드라인 및 전략 문서
│   ├── DLThon.md       # 대회 규칙 및 평가 지표 정의
│   ├── eda_list.md     # EDA 설계안 모음
│   ├── strategy.md     # 데이터/모델 전체 핵심 전략 보고서
│   ├── plan_model.md   # 모델 아키텍처 및 Ablation Study 계획서
│   ├── plan_train_augmentation.md # 학습 데이터 증강 세부 파이프라인 설계
│   ├── correct.md      # 실제 일반 대화 정답셋 교차검증 리포트
│   └── gem_prompt.md   # 합성 데이터 생성을 위한 프롬프트 가이드라인
├── models/             # 모델 가중치 및 체크포인트
│   └── model_test.ipynb # 모델 전용 테스트 및 분석 노트북
├── notebooks/          # Interactive Notebook
│   ├── train_eda.ipynb # EDA 시각화 및 주요 특징 도출 노트북
│   ├── baseline_dataset.ipynb # 초기 베이스라인 증강 탐색 노트북
│   ├── model.ipynb     # 차등 학습률 적용 최종 모델 학습 및 추론 파이프라인
│   └── submission.csv  # 추론 직후 원본 레이블로 추출된 임시 결과물
├── reports/            # 분석 결과물 및 검증 리포트
│   ├── eda_results.txt # EDA 상세 수치 결과
│   └── eda_code_check.md # 정합성 검증 보고서
├── src/                # 모듈화된 핵심 소스 코드
│   ├── archive/        # 일회성 분석 스크립트 및 구버전 생성/재빌드 코드 백업 폴더
│   ├── augment_synthesis.py # 합성 데이터(일반 대화)의 비정형성을 위한 전용 증강 모듈 (Multi-RI 구현)
│   ├── build_final_dataset.py # Train/Val 셋 병합 및 Hold-out 밸런싱 스크립트
│   └── extract_correct.py # 테스트 데이터에서 정답 셋을 별도로 추출하는 포렌식 로직
└── README.md           # 프로젝트 전체 개요
```


### 🚀 Current Progress (Project Status)

1. **데이터 분석 (EDA) 완료 ✅**
   - 6대 범주 13개 지표 정밀 분석 완수 (`train_eda.ipynb`).
   - 일반 대화와 위협 대화 간의 길이 불균형 구체화 (합성=110자, 위협=200자 이상).

2. **무결점 Data-Centric 파이프라인 구축 ✅**
   - **누수 완전 차단 (No Leakage):** 일반 대화 합성에 사용된 33개 도메인 프롬프트 중 무작위 6개씩을 완전히 격리하여 순수한 `val_holdout_synthesis.csv` 구축.
   - **Perfect Balancing:** 최종 `train_final.csv`를 각 클래스별 3,000건, 총 15,000건으로 완벽하게 균형 맞춤.
   - **약점 극복 (비정형성 부여):** 합성 데이터가 '너무 깨끗해서 생기는 꼼수 학습(Shortcut)'을 방지하기 위해 추임새를 무작위로 투입하는 Multi-RI, 말을 꼬는 SR(Span Repetition) 등의 커스텀 Augmentation을 `augment_synthesis.py`에 구현.

3. **모델 구조 및 차등 파인튜닝 (Discriminative Learning) 학습 완료 ✅**
   - **선정 모델**: `klue/roberta-base` + **Enhanced Head**(FC 256-dim -> GELU -> Dropout 0.3) 결합.
   - **차등 학습률 전략 (Conservative Strategy):** 이미 완성된 한국어 지식을 가진 Backbone은 아주 보수적으로 업데이트(`4e-6`)하고, 신규 분류 Head는 기본 속도로 강하게(`2e-5`) 훈련하여 Catastrophic Forgetting 원천 차단.
   - **조기 종료 (Early Stopping):** 훈련 Loss의 급락과 Validation Loss의 반등 시작 지점(Epoch 2)에서 선제적으로 훈련을 중단하여 과적합 통제 대성공 (Val F1 0.923).

4. **추론 및 성능 검증(Validation) 완료 ✅**
   - 테스트셋 기반 추론 결과, 실제 일반 대화(수작업 레이블 `correct.md` 104건)에 비추어 보았을 때 모델의 일반 대화 식별 **정밀도(Precision) 96.4%** 수준 달성 증명.
   - 기존 모델이 범했던 치명적 오분류(ex. 온라인 아이템 갈취를 일반 게임 대화로 오판)를 완벽하게 잡아내는 견고성 확보.

---

### 🛠️ Data-Centric Strategy (Key Highlights)

- **Leak-proof Architecture**: 훈련에 쓰인 프롬프트가 생성한 문장이 검증셋에 침범하지 못하도록 물리적 데이터 격리(Isolation) 시행.
- **Hard Negative Synthesis**: 위협 빈출 단어('돈', '죽어', '당장')를 포함하되 문맥은 완벽히 무해한 일반 대화(세이프-컨텍스트) 생성으로 모델의 변별력 한계 돌파.
- **Shortcut 방지 설계**: "ㅋㅋ" 등 특정 텍스트 사용을 원천 차단하고, 맞춤법이 지나치게 완벽한 합성 일반 대화를 다양한 노이즈(Multi-RI)로 오염시켜, 모델이 '단어나 띄어쓰기'가 아닌 **'문맥 유무'**로만 판별하도록 유도.

---

### 📊 Evaluation & Metrics

- **Primary Metric**: Macro F1 Score
- **Validation**:
  - `Epoch 1`: Train Loss 0.565 / Val F1 0.918
  - `Epoch 2 (Selected)`: Train Loss 0.123 / **Val F1 0.923** (조기 종료 포인트)
  - 일반 대화 검출 테스트 검증 Precision: **96.4%**

---

### 🔗 Getting Started

- **Prerequisites**: Python 3.8+, PyTorch, Transformers, Pandas
- **Run Pipeline**:
  ```bash
  # 1. 최종 데이터 병합 및 세팅 
  python src/build_final_dataset.py

  # 2. 모델 학습 (Interactive Notebook)
  jupyter notebook notebooks/model.ipynb


