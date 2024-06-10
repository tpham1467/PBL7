import sys
sys.path.insert(1, '/content/sentence-transformers')
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

data_path = '/content/data.csv'
df = pd.read_csv(data_path, encoding='utf-8')

bert = SentenceTransformer('/content/vn_sbert_deploy/phobert_base_mean_tokens_NLI_STS')

corpus_embeddings = bert.encode(df['keyword'], show_progress_bar=True)

def cal_cosine_similarity(inputembedding, corpus_embeddings):
  j = 0
  scoredict = {}
  countdict = {}
  meanScore = {}

  for i in corpus_embeddings:
      phoneName = df.loc[j]['name']
      cosine = cosine_similarity(
          i.reshape(1, -1),
          inputembedding[0].reshape(1, -1))
      if phoneName in scoredict:
        scoredict[phoneName] = scoredict[phoneName] + cosine
        countdict[phoneName] = countdict[phoneName] + 1
      else:
        scoredict[phoneName] = cosine
        countdict[phoneName] = 1
      j = j + 1

  for x in scoredict:
    meanScore[x] = scoredict[x]/countdict[x]
    # print(x, ' :',scoredict[x]/countdict[x])

  top_3_phones = dict(sorted(meanScore.items(), key=lambda item: item[1], reverse=True)[:3])

  for phone, score in top_3_phones.items():
    print(f"{phone}: {score}")
  return top_3_phones

def predict(text):
  inputembedding = bert.encode(text, show_progress_bar=False)
  return cal_cosine_similarity(inputembedding, corpus_embeddings)

# corpus = ['có khả năng quay phim 4k','điện thoại cho người già', 'Điện thoại chơi game tốt chip snapdragon', 'Chụp ảnh đẹp sang chảnh', 'điện thoại có màn hình gập', 'Tôi muốn điện thoại iphone Công nghệ màn hình OLED tân số quét 60 HZ', 'Thương hiệu oppo', 'Thương hiệu realme']

# for i in corpus:
#   print(i)
#   predict([i])
#   print()