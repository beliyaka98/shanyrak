import datetime

from sqlalchemy.orm import Session

from . import models, schemas


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        username=user.username,
        phone=user.phone,
        hashed_password=fake_hashed_password,
        name=user.name, city=user.city
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def update_user(db: Session, user_id, user: schemas.UserUpdate):
    db_user = get_user_by_id(db=db, user_id=user_id)
    for key, value in user.dict().items():
        if value:
            setattr(db_user, key, value)
    db.commit()
    return db_user            

def create_advert(db: Session, advert: schemas.CreateAdvert, user_id: int):
    db_advert = models.Advert(**advert.dict(), user_id=user_id, created_at=datetime.datetime.now())
    db.add(db_advert)
    db.commit()
    db.refresh(db_advert)
    return db_advert

def get_advert_by_id(db: Session, advert_id: int):
    db_advert = db.query(models.Advert).filter(models.Advert.id == advert_id).first()
    return db_advert

def update_advert(db: Session, user_id: int, advert_id: int, advert: schemas.AdvertUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for db_advert in db_user.adverts:
        if db_advert.id == advert_id:
            for key, value in advert.dict().items():
                if value is not None:
                    setattr(db_advert, key, value)
            db.commit()
            return db_advert
    return False

def delete_advert(db: Session, advert_id: int, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if any(db_advert.id == advert_id for db_advert in db_user.adverts):
        db_advert = db.query(models.Advert).filter(models.Advert.id == advert_id).first()
        db.delete(db_advert)
        db.commit()
        return True
    return False

def create_comment(db: Session, comment: schemas.CreateComment, advert_id: int, user_id: int):
    db_comment = models.Comment(**comment.dict(), author_id=user_id, advert_id=advert_id, created_at=datetime.datetime.now())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comment_by_advert_id_comment_id(db: Session, advert_id: int, comment_id:int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.advert_id == advert_id).first()
    return db_comment

def update_comment_by_id(db: Session, comment_id: int, comment: schemas.CreateComment):
    db_comment = db_user = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    db_comment.content = comment.content
    db.commit()
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    db.delete(db_comment)
    db.commit()
    return True

def add_fadvert(db: Session, advert_id: int, user_id: int):
    db_fadvert = db.query(models.Fadvert).filter(models.Fadvert._id == advert_id, models.Fadvert.owner_id == user_id).first()
    if db_fadvert:
        return db_fadvert
    else:
        db_fadvert = models.Fadvert(owner_id = user_id, _id = advert_id)
        db.add(db_fadvert)
        db.commit()
        db.refresh(db_fadvert)
        return db_fadvert

def get_fadverts(db: Session, user_id: int):
    db_fadverts = db.query(models.Fadvert).filter(models.Fadvert.owner_id == user_id).all()
    return db_fadverts

def delete_fadvert(db: Session, user_id: int, advert_id: int):
    db_fadvert = db.query(models.Fadvert).filter(models.Fadvert.owner_id == user_id, models.Fadvert._id == advert_id).first()
    if db_fadvert:
        db.delete(db_fadvert)
        db.commit()
        return True
    return False
