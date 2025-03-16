from sentence_transformers import SentenceTransformer
import time
# import sqlite3
import os
import numpy as np
import pyodbc
import json
#embedding part
# path = 'jinaai/jina-embeddings-v3'
path = "BAAI/bge-m3"
model = SentenceTransformer(path, device='cpu', trust_remote_code=True)

def get_all_plain_text(cursor):
    cursor.execute('SELECT FundName, Story FROM dbo.Fund')
    stories = cursor.fetchall()
    all_stories = [[], []]
    for story in stories:
        # print(story.Story)
        raw_data = json.loads(story.Story)
        # print(raw_data)
        text = raw_data[0]['PlainText']
        if '(Ảnh' in text:
            text = text[:text.index('(Ảnh')]
        fund_name = story.FundName
        all_stories[0].append(fund_name)
        all_stories[1].append(text)
        
    return all_stories

def update_similarity(all_stories):
    t1 = time.time()
    # all_stories = get_all_stories()
    embeddings = model.encode(all_stories[0])
    similarities = model.similarity(embeddings, embeddings)
    
    
    np.save('similarity.npy', similarities)

    embeddings = model.encode(all_stories[1])
    similarities = model.similarity(embeddings, embeddings)
    
    print('time needed: ', time.time() - t1)
    np.save('similarity2.npy', similarities)
