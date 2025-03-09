from sentence_transformers import SentenceTransformer
import time
# import sqlite3
import os
import numpy as np
import pyodbc
import json
#embedding part
model = SentenceTransformer("BAAI/bge-m3", device='cpu')

def get_all_plain_text(cursor):
    cursor.execute('SELECT Story FROM dbo.Fund')
    stories = cursor.fetchall()
    all_stories = []
    for story in stories:
        print(story.Story)
        raw_data = json.loads(story.Story)
        print(raw_data)
        all_stories.append(raw_data[0]['PlainText'])
    return all_stories

def update_similarity(all_stories):
    t1 = time.time()
    # all_stories = get_all_stories()
    embeddings = model.encode(all_stories)
    similarities = model.similarity(embeddings, embeddings)
    
    print('time needed: ', time.time() - t1)
    return similarities