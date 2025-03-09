
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
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"  # Driver SQL Server phù hợp với hệ điều hành của bạn
    "Server=47.130.30.15;"  # Địa chỉ IP của server
    "Database=VFundFuture;"  # Tên database bạn muốn kết nối
    "UID=sa;"  # Tên người dùng (user)
    "PWD=qjeF68CTt3UdVkxA;"  # Mật khẩu người dùng
    "Encrypt=yes;"  # Mã hóa kết nối
    "TrustServerCertificate=yes;"  # Tin tưởng chứng chỉ của server
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def get_transaction_by_user(cursor, user_id):
    cursor.execute('SELECT FundID, Donated FROM dbo.Transaction WHERE UserID = ?', user_id)
    funds = cursor.fetchall()
    return funds


def normalize_data(data):
    Max = max(data)
    Min = min(data)
    return [(x - Min) / (Max - Min)*5 for x in data]

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

def get_user_id_transform(user_id):
    return le_user.transform(user_id)

def get_fund_id_transform(fund_id):
    return le_fund.transform(fund_id)

def update_user_fund_id(user_id, fund_id):
    le_user.fit(user_id)
    le_fund.fit(fund_id)

def get_topic_related(cursor, user_id):
    cursor.execute('SELECT TopicID FROM dbo.UserTopic WHERE UserID = ?', user_id)
    topics = cursor.fetchall()
    return topics

def get_fund_followed_by_user(cursor, user_id):
    cursor.execute('SELECT FundID FROM dbo.UserFund WHERE UserID = ? AND isFollowed = 1', user_id)
    funds = cursor.fetchall()
    return funds

def get_fund_by_topic(cursor, topic_id):
    cursor.execute('SELECT FundID FROM dbo.FundTopic WHERE TopicID = ?', topic_id)
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

def intialize(cursor):

    cursor.execute('SELECT UserID FROM dbo.[User]')
    #cursor.execute('SELECT UserID FROM dbo.User') --> error: pyodbc.ProgrammingError: ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near the keyword 'User'. (156) (SQLExecDirectW)"
    users = cursor.fetchall()
    user_id = [user_id for user_id in users]


    cursor.execute('SELECT FundID FROM dbo.Fund')
    funds = cursor.fetchall()
    fund_id = [fund_id for fund_id in funds]
    
    update_user_fund_id(user_id, fund_id)

def get_score_collab(cursor, user_id):
    cursor.execute('SELECT UserID, FundID, Star FROM dbo.FundRate')
    stories = cursor.fetchall()
    df = pd.DataFrame([(user_id, fund_id, star) for user_id, fund_id, star in stories], 
				 columns=['UserID', 'FundID', 'Star'])
    df['UserID'] = get_user_id_transform(df['UserID'])
    df['FundID'] = get_fund_id_transform(df['FundID'])
    rs = MF(df.to_numpy(), K = 2, max_iter = 1000, print_every = 100)
    rs.fit()
    user_id = get_user_id_transform(user_id)
    score_collab = rs.pred_for_user(user_id)
    return score_collab

def get_lastest_fund_clicked(cursor, user_id):
    cursor.execute('SELECT FundID FROM dbo.UserFund where UserID = ?  ORDER BY JoinTime DESC', user_id)
    fund_id = cursor.fetchone()
    return fund_id

def get_funds_by_user(user_id):
    score_collab = get_score_collab(cursor, user_id)
    score = [0] * len(le_fund.classes_)
    score = np.array(score)
    for fund_id, sc in score_collab:
        score[le_fund.transform([fund_id])] = sc
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
        fund_related = get_funds_by_fund(cursor, last_fund)
        for fund_id in fund_related:
            score[le_fund.transform([fund_id])] += score_matching
    #sort score, keep id
    top = np.argsort(score)[::-1]
    top_three_fund_id = le_fund.inverse_transform(top)
    return top_three_fund_id
def get_funds_by_fund(fund_id, update = False):
    if update:
        all_stories = get_all_plain_text(cursor)
        similarity = update_similarity(all_stories)
        #save similarity to database
        np.save('similarity.npy', similarity)
    else:
        similarity = np.load('similarity.npy')
    print(similarity.shape)
    fund_id = le_fund.transform(fund_id)
    fund_index = np.where(fund_id == fund_id)
    print(fund_index)
    #find top three similar funds
    top_three = np.argsort(similarity[fund_index])[::-1]
    print(top_three)
    #flat
    top_three = top_three.flatten()
    top_three = top_three[:3]
    print(top_three)
    top_three_fund_id = le_fund.inverse_transform(top_three)

    return top_three_fund_id


if __name__ == "__main__":
    intialize(cursor)
    while True:
        choice = input('1. Recommend funds for user\n2. Recommend funds for fund\n3. Exit\n')
        if choice == '1':
            user_id = input('Enter user id: ')
            funds = get_funds_by_user(user_id)
            print(funds)
        elif choice == '2':
            fund_id = input('Enter fund id: ')
            fund_id = [fund_id]
            funds = get_funds_by_fund(fund_id)
            print(funds)
        elif choice == '3':
            break
        else:
            print('Invalid choice. Please try again.')
            continue