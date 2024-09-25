
from sklearn.metrics import confusion_matrix

def evaluate_recommendations(recommended_books, user_ratings, threshold=4):
    actual = [rating.bookId for rating in user_ratings if rating.rate >= threshold]
    predicted = [book.id for book in recommended_books]
    
    # Create binary vectors for confusion matrix
    all_books_ids = list(set([rating.bookId for rating in user_ratings] + [book.id for book in recommended_books]))
    actual_vector = [1 if book_id in actual else 0 for book_id in all_books_ids]
    predicted_vector = [1 if book_id in predicted else 0 for book_id in all_books_ids]
    
    cm = confusion_matrix(actual_vector, predicted_vector)
    print("Confusion Matrix:\n", cm)
    return cm

def get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix, num_recommendations=10):
    """
    Get top recommendations for a given user.
    """
    user_ratings = session.query(Rating).filter_by(userId=user_id).all()
    rated_books = [rating.bookId for rating in user_ratings]
    unrated_books_indices = [i for i, book in enumerate(all_books) if book.id not in rated_books]
    user_ratings_vector = ratings_matrix[user_id-1, :]  # Get the user's ratings vector
    print("***")
    #print(user_ratings_vector)
    #print(ratings_matrix[0])
    user_similarity_scores = cosine_similarity([user_ratings_vector], ratings_matrix)[0]  # Compute similarity scores
    user_sim_scores_sum = np.sum(user_similarity_scores)  # Sum of similarity scores
    print("Similarity Score")
    print(user_similarity_scores)
    sorted_indices = np.argsort(user_similarity_scores)[::-1]  # Sort indices in descending order
    #print(sorted_indices)
    recommended_books_indices = [index for index in sorted_indices if index in unrated_books_indices][:num_recommendations]
    recommendations = [all_books[index] for index in recommended_books_indices]
    return recommendations


@router.get("/recommendations2", tags=["predict"])
async def get_recom(
   session: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    user_id = current_user["id"]
    print(user_id)
    all_books = session.query(Book).all()
    num_books = len(all_books)
    num_users = session.query(User).count()
    ratings_matrix = np.zeros((num_users+1, num_books+1))
    print(ratings_matrix)
    print(num_users)
    print(num_books)
    print(session.query(Rating).count())
    for rating in session.query(Rating).all():
        try:
            print(ratings_matrix[rating.bookId , rating.userId ])
            ratings_matrix[rating.bookId , rating.userId ] = rating.rate
        except:
            pass
        print(ratings_matrix)
    cosine_similarity_matrix = cosine_similarity(ratings_matrix.T, ratings_matrix.T)
    recommendations = get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix)
    return {"recommendations":recommendations}


@router.get("/predict/{id}", tags=["predict"])
async def get_predict(
   id:int, session: Session = Depends(get_db)
):
    user_id = id
    all_books = session.query(Book).all()
    num_books = len(all_books)
    num_users = session.query(User).count()
    ratings_matrix = np.zeros((num_users, num_books))
    for rating in session.query(Rating).all():
        try:
            print(ratings_matrix[rating.bookId , rating.userId ])
            ratings_matrix[rating.bookId , rating.userId ] = rating.rate
        except:
            pass
        print(ratings_matrix)
    cosine_similarity_matrix = cosine_similarity(ratings_matrix.T, ratings_matrix.T)
    print(ratings_matrix)
    recommendations = get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix)
    print("Recommendations for user with ID", user_id)
    for book in recommendations:
        print(book.title)
    # Evaluate recommendations
    user_ratings = session.query(Rating).filter_by(userId=user_id).all()
    cm = evaluate_recommendations(recommendations, user_ratings)
    #print()
    return {"books":recommendations,"confusion_matrix": cm.tolist(),}

"""
@router.get("/gui_predict/{id}", tags=["predict"])
async def get_predict(
   request: Request,id:int, session: Session = Depends(get_db), response_class=HTMLResponse
):
    user_id = id
    all_books = session.query(Book).all()
    num_books = len(all_books)
    num_users = session.query(User).count()
    ratings_matrix = np.zeros((num_users, num_books))
    for rating in session.query(Rating).all():
        ratings_matrix[rating.bookId , rating.userId ] = rating.rate
        #except:
        #    pass
        print(ratings_matrix)
    cosine_similarity_matrix = cosine_similarity(ratings_matrix.T, ratings_matrix.T)
    print(ratings_matrix)
    recommendations = get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix)
    print("Recommendations for user with ID", user_id)
    for book in recommendations:
        print(book.title)
    # Evaluate recommendations
    user_ratings = session.query(Rating).filter_by(userId=user_id).all()
    cm = evaluate_recommendations(recommendations, user_ratings)
    #print()
    #return {"books":recommendations,"confusion_matrix": cm.tolist(),}
    return templates.TemplateResponse(
        request=request, name="book.html", context={"books":recommendations}
    )"""
