from http.client import HTTPException
from sqlalchemy.orm import Session
import models, schemas


def get_user(db: Session, user_id: int):
    # SELECT * from users id = user_id
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(name=user.name,email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, id: int):
    db_user = db.query(models.User).filter(models.User.id ==id).first()
    db.delete(db_user)
    db.commit()
    return db_user



def update_user(db: Session, user_id: int, user):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    db_user = db_query.first()
    # if not db_user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f'No user with this id: {user_id} found')
    update_data = user.dict(exclude_unset=True)
    print(f'Received data:', update_data)
    print(f'User data:', db_user)
    db_query.filter(models.User.id == user_id).update(update_data, 
                                                        synchronize_session=False)

    db.commit()
    db.refresh(db_user)
    return {"status": "success", "user": db_user}

# 
def get_tmdb_id(db: Session, user_id: int, tmdb_id: int):
    return db.query(models.Favorito_movie).filter_by(user_id=user_id, tmdb_id=tmdb_id).all()


def favoritar(db:Session, favorito: schemas.Favoritos):
    existing_favorito = get_tmdb_id(db, favorito.user_id, favorito.tmdb_id)
    if existing_favorito:
        raise HTTPException(status_code=400, detail="Movie already favorited by this user")
    db_favorito= models.Favorito_movie(tmdb_id=favorito.tmdb_id, user_id=favorito.user_id )
    db.add(db_favorito)
    db.commit()
    db.refresh(db_favorito)
    return db_favorito

def get_favorito_by_tmdb_id(db: Session, user_id: int):
    return db.query(models.Favorito_movie).filter_by(user_id=user_id).all()

def get_tmdb_id(db: Session, user_id: int, tmdb_id: int):
    return db.query(models.Favorito_movie).filter_by(user_id=user_id, tmdb_id=tmdb_id).all()

def delete_favorito(db: Session, tmdb_id: int):
    favorito = db.query(models.Favorito_movie).filter(models.Favorito_movie.tmdb_id == tmdb_id).first()
    db.delete(favorito)
    db.commit()
    return favorito

def artistas(db:Session, artistas: schemas.Artistas):
 
    db_artistas= models.Artistas(tmdb_id=artistas.tmdb_id, name=artistas.name, rank = artistas.rank)
    db.add(db_artistas)
    db.commit()
    db.refresh(db_artistas)
    return db_artistas