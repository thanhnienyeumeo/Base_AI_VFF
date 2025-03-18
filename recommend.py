from config import DRIVER, SERVER, DATABASE, UID, PWD, ENCRYPT, TRUSTSERVERCERTIFICATE
from similarity import *
import numpy as np
#ánh xạ user_id và movie_id sang index
from sklearn import preprocessing
from Matrix_Factor import MF
import pandas as pd
le_user = preprocessing.LabelEncoder()
le_fund = preprocessing.LabelEncoder()

score_topic = 0.3
score_colab = 0.4
score_matching = 0.15
score_donate = 0.15
score_outstanding = 0.2
conn_str = f"""
    Driver={DRIVER};
    Server={SERVER};
    Database={DATABASE};
    UID={UID};
    PWD={PWD};
    Encrypt={ENCRYPT};
    TrustServerCertificate={TRUSTSERVERCERTIFICATE};
"""

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

#now i have a stored procedure to get all outstanding fund name dbo.SelectOutstandingFunds
#function to execute the stored procedure 
def get_all_outstanding_fund(cursor):
    cursor.execute("EXEC dbo.SelectOutstandingFunds")
    funds = cursor.fetchall()
    return funds

def get_user_id_transform(user_id):
    return le_user.transform(user_id)
def get_fund_id_transform(fund_id):
    return le_fund.transform(fund_id)
def normalize_data(data):
    Max = max(data)
    Min = min(data)
    return [(x - Min) / (Max - Min)*5 for x in data]
def get_fund_by_topic(cursor, topic_id):
    cursor.execute('SELECT FundID FROM dbo.FundTopic WHERE TopicID = ?', topic_id)
    funds = cursor.fetchall()
    return funds
def get_transaction_by_user(cursor, user_id):
    cursor.execute('SELECT FundID, Donated FROM dbo.Transaction WHERE UserID = ?', user_id)
    funds = cursor.fetchall()
    return funds

def get_topic_related(cursor, user_id):
        cursor.execute('SELECT TopicID FROM dbo.UserTopic WHERE UserID = ?', user_id)
        topics = cursor.fetchall()
        return topics
def get_fund_followed_by_user(cursor, user_id):
        cursor.execute('SELECT FundID FROM dbo.UserFund WHERE UserID = ? AND isFollowed = 1', user_id)
        funds = cursor.fetchall()
        return funds
def get_fund_by_topics(cursor, topic_ids):
        funds = []
        for topic_id in topic_ids:
            funds.extend(get_fund_by_topic(cursor, topic_id))
        return funds

def is_user_follow_fund(cursor, user_id, fund_id):
        cursor.execute('SELECT * FROM dbo.UserFund WHERE UserID = ? AND FundID = ? AND isFollowed = 1', user_id, fund_id) #need to adapt: if user unfollow fund
        return cursor.fetchall() != []

def get_all_fund_activity(cursor, user_id):
        cursor.execute('SELECT FundActivityID FROM dbo.UserFundActivityEmotion WHERE UserID = ?', user_id)
        fund_activity = cursor.fetchall()
        fund_activity_ids = []
        for story in fund_activity:   
            cursor.execute('SELECT FundID FROM dbo.FundActivity WHERE FundActivityID = ?', story)
            funds = cursor.fetchall()
            fund_activity_ids.extend(funds.FundID)
        return fund_activity_ids
def get_lastest_fund_clicked(cursor, user_id):
        cursor.execute('SELECT FundID FROM dbo.UserFund where UserID = ?  ORDER BY JoinTime DESC', user_id)
        fund_id = cursor.fetchone()
        return fund_id
class Recommend:
    def __init__(self, cursor = cursor):
        self.update = 1
        self.intialize(cursor)
        self.update = 0

        


    

    def get_score_donate(cursor, user_id):
        cursor.execute('SELECT UserID, FundID, Donated FROM dbo.Transaction')
        stories = cursor.fetchall()
        df = pd.DataFrame([(user_id, fund_id, star) for user_id, fund_id, star in stories], 
                    columns=['UserID', 'FundID', 'Star'])
        df['UserID'] = get_user_id_transform(df['UserID'])
        df['FundID'] = get_fund_id_transform(df['FundID'])
        df['Star'] = normalize_data(df['Star'])
        rs = MF(df.to_numpy(), K = 2, max_iter = 1000, print_every = 100)
        rs.fit()
        user_id = get_user_id_transform(user_id)
        score_collab = rs.pred_for_user(user_id)
        return score_collab

    

    

    def update_user_fund_id(self, user_id, fund_id):
        le_user.fit(user_id)
        le_fund.fit(fund_id)

    

    

    

    

    def intialize(self, cursor):

        cursor.execute('SELECT UserID FROM dbo.[User]')
        #cursor.execute('SELECT UserID FROM dbo.User') --> error: pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near the keyword 'User'. (156) (SQLExecDirectW)"
        users = cursor.fetchall()
        user_id = [user_id for user_id in users]


        cursor.execute('SELECT FundID FROM dbo.Fund')
        funds = cursor.fetchall()
        fund_id = [fund_id for fund_id in funds]
        
        self.update_user_fund_id(user_id, fund_id)

    def get_score_collab(self, cursor, user_id):
        cursor.execute('SELECT UserID, FundID, Star FROM dbo.FundRate')
        stories = cursor.fetchall()
        df = pd.DataFrame([(user_id, fund_id, star) for user_id, fund_id, star in stories], 
                    columns=['UserID', 'FundID', 'Star'])
        df['UserID'] = get_user_id_transform(df['UserID'])
        df['FundID'] = get_fund_id_transform(df['FundID'])
        rs = MF(df.to_numpy(), K = 2, max_iter = 1000, print_every = 100)
        rs.fit()
        user_id = get_user_id_transform([user_id])
        score_collab = rs.pred_for_user(user_id)
        return score_collab

    

    def get_funds_by_user(self, user_id):
        score_collab = self.get_score_collab(cursor, user_id)
        score = np.zeros(len(le_fund.classes_))
        for id, sc in score_collab:
            score[id] = sc
        #get topic related to user
        topics = get_topic_related(cursor, user_id)
        fund_topic = get_fund_by_topics(cursor, topics)
        for fund_id in fund_topic:
            score[le_fund.transform([fund_id])] += score_topic
        #get fund followed by user
        fund_followed = get_fund_followed_by_user(cursor, user_id)
        for fund_id in fund_followed:
            #set all to 0 --> don't recommend fund followed by user
            score[le_fund.transform([fund_id])] = 0
        #get last fund clicked by user
        last_fund = get_lastest_fund_clicked(cursor, user_id)
        #get fund by this fund
        if last_fund:
            fund_related = self.get_funds_by_fund(last_fund.FundID, False)
            for fund_id in fund_related:
                score[le_fund.transform([fund_id])] += score_matching
        #sort score, keep id

        #get outstanding fund
        outstanding_funds = get_all_outstanding_fund(cursor)
        for fund in outstanding_funds:
            score[le_fund.transform([fund.FundID])] += score_outstanding
        top = np.argsort(score)[::-1]
        top_three_fund_id = le_fund.inverse_transform(top)
        return top_three_fund_id
    def get_funds_by_fund(self, fund_id, update = False):
        if update:
            all_stories = get_all_plain_text(cursor)
            update_similarity(all_stories)
            #save similarity to database
            
       
        similarity = np.load('similarity.npy')
        similarity2 = np.load('similarity2.npy')
        similarity = 0.75 * similarity + 0.25 * similarity2
        print(similarity.shape)
        fund_id = le_fund.transform([fund_id])
        fund_index = np.where(fund_id == fund_id)
        print(fund_index)
        #find top three similar funds
        top_three = np.argsort(similarity[fund_index])

        print(top_three)
        top_three = top_three[::-1]
        #flat
        top_three = top_three.flatten()
        top_three = top_three[:3]
        print(top_three)
        top_three_fund_id = le_fund.inverse_transform(top_three)

        return top_three_fund_id

import sys
if __name__ == "__main__":
    recommend = Recommend()
    update = sys.argv[1]
    if update.lower() == 'true':
        update = True
    else:
        update = False
    while True:
        choice = input('1. Recommend funds for user\n2. Recommend funds for fund\n3. Exit\n')
        if choice == '1':
            user_id = input('Enter user id: ')
            funds = recommend.get_funds_by_user(user_id)
            print(funds)
        elif choice == '2':
            fund_id = input('Enter fund id: ')
            fund_id = [fund_id]
            funds = recommend.get_funds_by_fund(fund_id, update)
            update = False
            print(funds)
        elif choice == '3':
            break
        else:
            print('Invalid choice. Please try again.')
            continue