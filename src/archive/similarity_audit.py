import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def audit_similarity(file_path):
    df = pd.read_csv(file_path)
    texts = df['conversation'].tolist()
    
    # Use TF-IDF to find near-duplicates
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))
    tfidf = vectorizer.fit_transform(texts)
    
    sim_matrix = cosine_similarity(tfidf)
    
    # Mask mirror and diagonal
    sim_matrix = np.triu(sim_matrix, k=1)
    
    high_sim_indices = np.where(sim_matrix > 0.8)
    pairs = list(zip(high_sim_indices[0], high_sim_indices[1]))
    
    print(f"Total samples: {len(texts)}")
    print(f"Pairs with >0.8 similarity: {len(pairs)}")
    
    if len(pairs) > 0:
        print("\nExample of high similarity pair:")
        i, j = pairs[0]
        print(f"Index {i}: {texts[i][:150]}...")
        print(f"Index {j}: {texts[j][:150]}...")
        print(f"Similarity Score: {sim_matrix[i][j]:.4f}")

if __name__ == "__main__":
    audit_similarity('data/synthetic_general_v4.csv')
