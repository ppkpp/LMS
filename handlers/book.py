import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,BookReviewSchema,BorrowSchema
)
from typing import List, Dict
from .database import get_db

from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc
from scipy.spatial.distance import cosine
from models.model import  Student as User
from models.model import Book,Rating,BannerModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from modules.utils import pagination
import sys
import datetime
from fastapi.responses import HTMLResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

np.set_printoptions(threshold=sys.maxsize)
router = APIRouter()
auth_handler = AuthToken()
templates = Jinja2Templates(directory="templates")

@router.get("/download/apk")
def download_apk():
    file_path = "downloads/app.apk"
    return FileResponse(path=file_path, filename="yourapp.apk", media_type='application/vnd.android.package-archive')
    
###Barcode
@router.get("/create_barcode", response_class=HTMLResponse)
def create_barcode(request:Request):
    return templates.TemplateResponse(request=request, name="barcode.html", context={"books":[]})
    
@router.get("/app_download", response_class=HTMLResponse)
def create_barcode(request:Request):
    return templates.TemplateResponse(request=request, name="download.html", context={"books":[]})

###Barcode


@router.get("/students/{rfid}", tags=["student"])
def get_student_byrfid(rfid: str, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.rfid==rfid).first()
    if not student:
        raise HTTPException(status_code=404, detail="RFID not found.")
    return {"students":student}


@router.get("/profiles/{id}", tags=["library"])
def get_profile(id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    profile_data = db.get(User, current_user["id"])
    if not profile_data:
        raise HTTPException(status_code=404, detail="User ID not found.")
    return {"profile":profile_data}



@router.get("/banners", tags=["banner"])
async def get_app_banners(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db)#, current_user: CurrentUser = Depends(get_current_user)
):
    banners = db.query(BannerModel).order_by(desc(BannerModel.createdate)).all()
    return {"banner":banners}

@router.get("/books", tags=["books"])
async def get_book_categories(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(Book).count()
    meta_data =  pagination(page,per_page,count)
    book = db.query(Book).order_by(desc(Book.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"book":book}

@router.get("/books/{id}", tags=["books"])
def get_book_byid(id: int, db: Session = Depends(get_db)):
    book_data = db.get(Book, id)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book ID not found.")
    return {"book":book_data}

@router.post("/add_review", tags=["books"])
async def add_review(
    request: Request, data: BookReviewSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(data.dict())
    req = data.dict()
    book_rate  = int(req["rating"] * 2)
    book_id = req["book_id"]
    user_id = current_user["id"]
    print(book_rate)
    is_rating = db.query(Rating).filter(Rating.userId==user_id,Rating.bookId==book_id).first()
    if is_rating:
        is_rating.rate = book_rate
        db.commit()
        db.refresh(is_rating)
        return {"status":"update","rating":req["rating"]}
    else:
        rating_db = Rating(userId=current_user["id"],bookId=book_id,rate=book_rate)
        db.add(rating_db)
        db.commit()
        db.refresh(rating_db)
        return {"status":"create","rating":req["rating"]}


@router.get("/get_review/{book_id}", tags=["books"])
def get_review(book_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    is_rating = db.query(Rating).filter(Rating.userId==current_user["id"],Rating.bookId==book_id).first()
    if not is_rating:
        return {"rating":0}
    print(is_rating.rate)
    return {"rating":is_rating.rate/2}

from pydantic import BaseModel
class BookRecommendation(BaseModel):
    id: int
    book_id: int
    title: str
    author: str
    remark: str
    location: str
    publishdate: datetime.datetime
    similarity_score: float

@router.get("/gui_predict/{userId}", response_class=HTMLResponse)
def calculate_book_recommendations( request: Request,userId: int, db: Session = Depends(get_db)):
    # Fetch all ratings
    ratings = db.query(Rating).all()
    books = db.query(Book).all()

    # Create a dictionary of user ratings
    user_ratings = {}
    for rating in ratings:
        if rating.userId not in user_ratings:
            user_ratings[rating.userId] = {}
        user_ratings[rating.userId][rating.bookId] = rating.rate
    
    # Get the target user ratings
    target_user_ratings = user_ratings.get(userId, {})
    
    # Calculate similarities
    similarities = []
    for other_user_id, other_user_ratings in user_ratings.items():
        if other_user_id == userId:
            continue
        common_books = set(target_user_ratings.keys()).intersection(set(other_user_ratings.keys()))
        if not common_books:
            continue
        target_ratings_vector = [target_user_ratings[book_id] for book_id in common_books]
        other_ratings_vector = [other_user_ratings[book_id] for book_id in common_books]
        similarity = 1 - cosine(target_ratings_vector, other_ratings_vector)
        similarities.append((other_user_id, similarity))

    # Aggregate book recommendations
    book_scores = {}
    for other_user_id, similarity in similarities:
        for book_id, rating in user_ratings[other_user_id].items():
            if book_id not in target_user_ratings:
                if book_id not in book_scores:
                    book_scores[book_id] = 0
                book_scores[book_id] += rating * similarity
    
    # Create a list of recommended books
    recommended_books = []
    for book_id, score in book_scores.items():
        book = next(book for book in books if book.id == book_id)
        recommended_books.append(BookRecommendation(
	   id=book.id,
            book_id=book.id,
            title=book.title,
            author=book.author,
            remark=book.remark,
            publishdate=book.publishdate,
            location = book.location,
            similarity_score=score
        ))
    
    recommended_books.sort(key=lambda x: x.similarity_score, reverse=True)
    #return recommended_books
    return templates.TemplateResponse(
        request=request, name="book.html", context={"books":recommended_books[:10],"userId":userId}
    )




@router.get("/recommendations", tags=["predict"])
async def get_predict1(
   db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
	# Fetch all ratings
    ratings = db.query(Rating).all()
    print("*********")
    books = db.query(Book).all()
    userId = current_user["id"]
    # Create a dictionary of user ratings
    print(userId)
    user_ratings = {}
    for rating in ratings:
        if rating.userId not in user_ratings:
            user_ratings[rating.userId] = {}
        user_ratings[rating.userId][rating.bookId] = rating.rate
    
    # Get the target user ratings
    target_user_ratings = user_ratings.get(userId, {})
    
    # Calculate similarities
    similarities = []
    for other_user_id, other_user_ratings in user_ratings.items():
        if other_user_id == userId:
            continue
        common_books = set(target_user_ratings.keys()).intersection(set(other_user_ratings.keys()))
        if not common_books:
            continue
        target_ratings_vector = [target_user_ratings[book_id] for book_id in common_books]
        other_ratings_vector = [other_user_ratings[book_id] for book_id in common_books]
        similarity = 1 - cosine(target_ratings_vector, other_ratings_vector)
        similarities.append((other_user_id, similarity))

    # Aggregate book recommendations
    book_scores = {}
    for other_user_id, similarity in similarities:
        for book_id, rating in user_ratings[other_user_id].items():
            if book_id not in target_user_ratings:
                if book_id not in book_scores:
                    book_scores[book_id] = 0
                book_scores[book_id] += rating * similarity
    
    # Create a list of recommended books
    recommended_books = []
    for book_id, score in book_scores.items():
        book = next(book for book in books if book.id == book_id)
        recommended_books.append(BookRecommendation(
            id=book.id,
	    book_id=book.id,
            title=book.title,
            author=book.author,
            remark=book.remark,
            publishdate=book.publishdate,
		location=book.location,
            similarity_score=score
        ))
    #print(recommended_books)
    recommended_books.sort(key=lambda x: x.similarity_score, reverse=True)
    return {"recommendation":recommended_books[:10]}
    #return recommended_books
    #return templates.TemplateResponse(
    #    request=request, name="book.html", context={"books":recommended_books[:10],"userId":userId}
    #)


@router.get("/get_user_by_barcode/{barcode}", tags=["student"])
def get_user_by_barcode(barcode: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.barcode==barcode).first()
    if not book:
        raise HTTPException(status_code=404, detail="barcode not found.")
    return {"book":book}



@router.post("/borrow", tags=["books"])
async def add_borrow(
    request: Request, data: BorrowSchema, db: Session = Depends(get_db)
):
    print("********************")
    logger.info(data.dict())
    req = data.dict()
    print(req)
    book_rate  = int(req["rating"] * 1)
    book_id = req["book_id"]
    user_id = req["user_id"]
    borrowdate = req["borrowdate"]
    returndate =req["returndate"]
    print(book_rate)
    is_rating = db.query(Rating).filter(Rating.userId==user_id,Rating.bookId==book_id).first()
    if is_rating:
        is_rating.rate = book_rate
        db.commit()
        db.refresh(is_rating)
        return {"status":"update","rating":req["rating"]}
    else:
        rating_db = Rating(userId=user_id,bookId=book_id,rate=book_rate,borrowdate=borrowdate,returndate=returndate)
        db.add(rating_db)
        db.commit()
        db.refresh(rating_db)
        return {"status":"create","rating":req["rating"]}
