import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import pandas as pd
import re
import os

# 1. 모델 아키텍처 정의 (v5 저장 당시 구조)
class ConversationClassifier(nn.Module):
    def __init__(self, model_name='klue/roberta-base', num_classes=5, dropout_rate=0.3):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        hidden_size = self.backbone.config.hidden_size
        
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.fc1 = nn.Linear(hidden_size, 256)
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(256, num_classes)
    
    def mean_pooling(self, last_hidden_state, attention_mask):
        mask_expanded = attention_mask.unsqueeze(-1).float()
        sum_embeddings = torch.sum(last_hidden_state * mask_expanded, dim=1)
        sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
        return sum_embeddings / sum_mask
    
    def forward(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = self.mean_pooling(outputs.last_hidden_state, attention_mask)
        pooled_output = self.layer_norm(pooled_output)
        hidden = self.fc1(pooled_output)
        hidden = self.activation(hidden)
        hidden = self.dropout(hidden)
        logits = self.fc2(hidden)
        return logits

# 2. 전처리 함수
def clean_text(text):
    # 사용자 요청: 큰따옴표 제거 (+ 줄바꿈 공백 처리)
    text = str(text).replace('"', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    tokenizer = AutoTokenizer.from_pretrained('klue/roberta-base')

    model = ConversationClassifier().to(device)
    model_path = 'models/best_model_v5.pt'
    
    if not os.path.exists(model_path):
        print(f'❌ 모델 파일을 찾을 수 없습니다: {model_path}')
        return
        
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print('✅ 모델 가중치 로드 성공!')
    except Exception as e:
        print(f'❌ 가중치 로드 실패: {e}')
        return
        
    model.eval()

    # 라벨 매핑 
    # train.csv 등에서 쓰던 통상적인 label encodings
    # 0:'갈취 대화', 1:'기타 괴롭힘 대화', 2:'일반 대화', 3:'직장 내 괴롭힘 대화', 4:'협박 대화'
    # (알파벳 정렬 기준. 만약 다르면 결과에서 클래스 번호 확인)
    id2label = {0: '갈취 대화', 1: '기타 괴롭힘 대화', 2: '일반 대화', 3: '직장 내 괴롭힘 대화', 4: '협박 대화'}

    # 4. 데이터 로드 및 추론
    test_df = pd.read_csv('data/test.csv')
    predicted_general = []

    print('🚀 추론 시작...')
    import warnings
    warnings.filterwarnings("ignore")
    
    with torch.no_grad():
        for idx, row in test_df.iterrows():
            text = clean_text(row['conversation'])
            inputs = tokenizer(
                text, 
                return_tensors='pt', 
                truncation=True, 
                max_length=256, 
                padding='max_length'
            ).to(device)
            
            logits = model(inputs['input_ids'], inputs['attention_mask'])
            pred_id = torch.argmax(logits, dim=1).item()
            pred_label = id2label.get(pred_id, f'Unknown({pred_id})')
            
            # 클래스 인덱스가 다를 수도 있으니 확률이 튀는 것을 전부 '일반대화'로 볼 건지 결정
            # 일단 알파벳 정렬 기준 id2label[2] 가 일반대화인지 확인
            predicted_general.append((row['idx'], pred_label, text))

    print('\n' + '='*60)
    
    # 일반 대화로 예측된 것만 필터
    gen_convos = [item for item in predicted_general if item[1] == '일반 대화']
    
    if len(gen_convos) == 0:
        print('라벨 매핑이 달랐을 수 있습니다. 예측된 라벨 분포:')
        from collections import Counter
        print(Counter([x[1] for x in predicted_general]))
    else:
        print(f'🎯 [일반 대화]로 예측된 샘플 갯수: {len(gen_convos)}개 (Test 전체 500개 중)')
        print('='*60 + '\n')
        
        for i, (orig_id, pred_label, text) in enumerate(gen_convos):
            print(f'[{i+1}] (원본 ID: {orig_id})')
            print(f'{text[:150]}...' if len(text) > 150 else text)
            print('-'*50)

if __name__ == '__main__':
    main()
