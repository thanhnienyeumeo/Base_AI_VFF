from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from chatbot import *
from recommend import Recommend
from typing import List
app = FastAPI()

# Initialize the recommender system
recommender = Recommend()

class Item(BaseModel):
    text: str = None
    is_done: bool = False

class RecommendationRequest(BaseModel):
    update: bool = False

class RecommendationResponse(BaseModel):
    funds: List[str]

items = []

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[0:limit]

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
# @app.post("/ask")
# def ask_question(question: str):
#     return {"response": get_answer(question)}

# @app.post("/create_email")
# def create_email(email: str):
#     return {"response": create_email(email)}

@app.get("/main")
def main_page():
    return root()

# Recommendation endpoints
@app.get("/recommend/user/{user_id}", response_model=RecommendationResponse)
def recommend_for_user(user_id: str):
    try:
        funds = recommender.get_funds_by_user(user_id)
        return {"funds": [str(fund) for fund in funds]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/recommend/fund/{fund_id}", response_model=RecommendationResponse)
def recommend_for_fund(fund_id: str, request: RecommendationRequest = None):
    try:
        if request is None:
            request = RecommendationRequest()
        funds = recommender.get_funds_by_fund(fund_id, request.update)
        return {"funds": [str(fund) for fund in funds]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/fill_campaign")
def fill_campaign():
    return {}