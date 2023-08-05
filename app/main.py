from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from . import crud, models, schemas
from .database import SessionLocal, engine

from typing import Annotated
from .jwt_handler import signJWT, decodeJWT

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/users/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fake_hashed_password(password: str):
    return password + "notreallyhashed"

@app.post("/auth/users/", tags=["signup"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.phone)
    print(user)
    if db_user:
        raise HTTPException(status_code=403, detail="Username already exists")
    new_user = crud.create_user(db=db, user=user)
    return Response(status_code=200)
    
@app.post("/auth/users/login", tags=["login"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password.")
    hashed_password = fake_hashed_password(form_data.password)
    if not hashed_password == db_user.hashed_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password.")
    token = signJWT(db_user.id)
    print(token)
    return {"access_token": token, "token_type": "bearer"}

@app.patch("/auth/users/me", tags=["update"])
def update_user(user: schemas.UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decodeJWT(token=token)["user_id"]
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    return Response(status_code=200)

@app.get("/auth/users/me", response_model=schemas.User, tags=["profile"])
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decodeJWT(token=token)["user_id"]
    db_user = crud.get_user_by_id(db=db, user_id=user_id)
    return db_user

@app.post("/shanyraks", tags=["create advert"])
def create_advert(advert: schemas.CreateAdvert, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decodeJWT(token=token)["user_id"]
    db_advert = crud.create_advert(db=db, advert=advert, user_id=user_id)
    return {"id": db_advert.id}

@app.get("/shanyraks/{id}", tags=["get advert"], response_model=schemas.Advert)
def get_advert(id: int, db: Session = Depends(get_db)):
    db_advert = crud.get_advert_by_id(db=db, advert_id=id)
    db_advert.total_comments = len(db_advert.comments)
    return db_advert

@app.patch("/shanyraks/{id}", tags=["update advert"])
def update_advert(id: int, advert: schemas.AdvertUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decodeJWT(token=token)["user_id"]
    db_advert = crud.update_advert(db=db, user_id=user_id, advert_id=id, advert=advert)
    if not db_advert:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return Response(status_code=200)

@app.delete("/shanyraks/{id}", tags=["delete advert"])
def delete_advert(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decodeJWT(token=token)["user_id"]
    deleted = crud.delete_advert(db=db, advert_id=id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return Response(status_code=200)

@app.post("/shanyraks/{id}/comments", tags=["create comment"])
def create_comment(
    id: int,
    comment: schemas.CreateComment,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = decodeJWT(token=token)["user_id"]
    db_advert = crud.get_advert_by_id(db=db, advert_id=id)
    if not db_advert:
        return HTTPException(status_code=404, detail="Advert does not exist.")
    db_comment = crud.create_comment(db=db, comment=comment, advert_id=id, user_id=user_id)
    return Response(status_code=200)

@app.get("/shanyraks/{id}/comments", response_model= schemas.Comments,tags=["get comments"])
def get_comments(id: int, db: Session = Depends(get_db)):
    db_advert = crud.get_advert_by_id(db=db, advert_id=id)
    if not db_advert:
        return HTTPException(status_code=404, detail="Advert does not exist.")
    return schemas.Comments(comments=db_advert.comments)

@app.patch("/shanyraks/{id}/comments/{comment_id}", tags=["update comment"])
def update_comment(
    id: int,
    comment_id: int,
    comment: schemas.CreateComment,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_id = decodeJWT(token=token)["user_id"]
    db_comment = crud.get_comment_by_advert_id_comment_id(db=db, advert_id=id, comment_id=comment_id)
    if not db_comment or db_comment.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db_comment = crud.update_comment_by_id(db=db, comment_id=comment_id, comment=comment)
    return Response(status_code=200)

@app.delete("/shanyraks/{id}/comments/{comment_id}", tags=["delete comment"])
def delete_comment(
    id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_id = decodeJWT(token=token)["user_id"]
    db_comment = crud.get_comment_by_advert_id_comment_id(db=db, advert_id=id, comment_id=comment_id)
    if not db_comment or (db_comment.author_id != user_id and db_comment.advert.user_id != user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    crud.delete_comment(db=db, comment_id=comment_id)
    return Response(status_code=200)

@app.post("/auth/users/favorites/shanyraks/{id}", tags=["add favorite advert"])
def add_favorite(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = decodeJWT(token=token)["user_id"]
    db_fadvert = crud.add_fadvert(db=db, advert_id=id, user_id=user_id)
    return Response(status_code=200)

@app.get("/auth/users/favorites/shanyraks", tags=["get favorite adverts"])
def get_favorties(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = decodeJWT(token=token)["user_id"]
    db_fadverts = crud.get_fadverts(db=db, user_id=user_id)
    fadverts = [schemas.Fadvert(_id=fadvert._id, address=fadvert.advert.address) for fadvert in db_fadverts]
    return schemas.Fadverts(shanyraks=fadverts)

@app.delete("/auth/users/favorites/shanyraks/{id}", tags=["delete favorite advert"])
def delete_favorite(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = decodeJWT(token=token)["user_id"]
    db_fadvert = crud.delete_fadvert(db=db, advert_id=id, user_id=user_id)
    return Response(status_code=200)

def rename_id_to__id(item):
    item._id = item.id
    return item

@app.get("/shanyraks/", tags=["get shanyraks"])
def get_shanyraks(
    params: schemas.Shanyrak = Depends(),
    db: Session = Depends(get_db)
):
    filter_conditions = []
    if params.type is not None:
        filter_conditions.append(models.Advert.type == params.type)
    if params.rooms_count is not None:
        filter_conditions.append(models.Advert.rooms_count == params.rooms_count)
    if params.price_from is not None:
        filter_conditions.append(models.Advert.price >= params.price_from)
    if params.price_until is not None:
        filter_conditions.append(models.Advert.price <= params.price_until)

    query_filter = and_(*filter_conditions)
    total_rows = db.query(models.Advert).filter(and_(*filter_conditions)).count()

    # Query the database with pagination and filtering
    results = db.query(models.Advert).filter(query_filter).order_by(desc(models.Advert.created_at)).offset(params.offset).limit(params.limit).all()
    results = [schemas.ShanyrakAdvert(_id = orm_object.id, type=orm_object.type, price=orm_object.price, address=orm_object.address, area=orm_object.area, rooms_count=orm_object.rooms_count) for orm_object in results]

    return schemas.ResponseShanyrak(total=total_rows, objects=results) 
