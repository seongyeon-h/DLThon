import pandas as pd
import os
import io

def repair_chunks():
    data_dir = "c:/Users/Hwang/Desktop/황성연/DLThon/data"
    chunks = [f"synthetic_general_v4.5_chunk{i}.csv" for i in range(1, 21)]
    
    for chunk_file in chunks:
        path = os.path.join(data_dir, chunk_file)
        if not os.path.exists(path):
            continue
        
        print(f"Repairing {chunk_file}...")
        
        # 1. 원본 파일을 텍스트로 읽음
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 2. 첫 줄(헤더) 제외하고 '일반 대화,'로 시작하는 행을 기준으로 대화 뭉치기
        repaired_rows = []
        current_conversation = []
        
        for line in lines[1:]: # 헤더 스킵
            if line.startswith("일반 대화,"):
                if current_conversation:
                    repaired_rows.append({
                        'class': '일반 대화',
                        'conversation': "".join(current_conversation).strip()
                    })
                current_conversation = [line[len("일반 대화,"):]]
            else:
                current_conversation.append(line)
        
        # 마지막 남은 대화 추가
        if current_conversation:
            repaired_rows.append({
                'class': '일반 대화',
                'conversation': "".join(current_conversation).strip()
            })
            
        # 3. Pandas를 이용해 '안전하게(Quoted)' 다시 저장
        df_repaired = pd.DataFrame(repaired_rows)
        df_repaired.to_csv(path, index=False, encoding='utf-8-sig', quoting=1) # 1 = csv.QUOTE_ALL

    print("All chunks repaired successfully.")

if __name__ == "__main__":
    repair_chunks()
