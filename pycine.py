from site import USER_BASE
from fastapi import FastAPI
from tmdb import get_json
from schemas import UserModel
app = FastAPI()

from fastapi.middleware.cors import (
     CORSMiddleware
)
# habilita CORS (permite que o Svelte acesse o fastapi)
# por padrao o svelte roda na porta 5173
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

# =====================================================
# USERS
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3 ENDPOINTS
# =============================
# Criar novo usuario
# =============================
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# =============================
# Retorna todos os usuarios (Read) - findAll
# =============================
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# =============================
# Retorna o Usuario do ID informado
# =============================
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
# =============================
# Deletar Usuario
# =============================
@app.delete("/user/delete/{id}")
def delete_user(id: int,db: Session = Depends(get_db)):
    if not crud.get_user(db,id):
        raise HTTPException(status_code=404,
            detail=f'No user with this id: {id}found')
    db_user = crud.delete_user(db, id)
    return db_user


# =============================
# Atualiar usuario
# =============================
@app.put("/user/update/{user_id}")
def update_user(user_id: int, user, db: Session = Depends(get_db)):

    db_user = crud.update_user(user_id=user_id, db=db, user=user)
    return db_user

# =============================
# Favoritar filme
# =============================

@app.post("/favoritos/", response_model=schemas.Favoritos)
async def favoritar_filme(favorito: schemas.Favoritos, db: Session = Depends(get_db)):
    return crud.favoritar(db=db, favorito=favorito)
# =============================
# Listar filmes favoritos
# =============================

@app.get("/favoritos/", response_model=list[schemas.Favoritos])
async def favoritar_filme(user_id: str, db: Session = Depends(get_db)):
    return crud.get_favorito_by_tmdb_id(db, user_id)
# =============================
# Excluir filme favorito
# =============================
@app.delete("/favoritos/{tmdb_id}", response_model=schemas.Favoritos)
async def delete_favorito(tmdb_id: str, db: Session = Depends(get_db)):
    db_favoritos = crud.get_favorito_by_tmdb_id (db, tmdb_id)
    if db_favoritos is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_favorito=crud.delete_favorito(db, tmdb_id)
    return deleted_favorito



# =============================
# ATIVIDADE 1
# =============================
@app.get("/filme/{title}")
async def find_movie(title: str):
    """ 
    procura filmes pelo titulo e ordena pelos mais populares 
    Exemplo: /filme/avatar
    """
    data = get_json("/search/movie", f"?query={title}&language=en-US")

    filtro=[]
    results = data['results']
    

    for title in results:
        filtro.append({
            'title': title['title'],
            'rank':title['popularity']
            }
        )

    filtro.sort(reverse = True, key=lambda title:title['rank'])

    return filtro

# ========================================================
# =============================
# ATIVIDADE 2
# =============================
@app.get("/artista/filmes")
async def find_filmes_artista(personId: int):
    """ 
    busca os filmes mais populares de um artista 
    Exemplo: /artista/filmes?personId=1100
    """
    person_data = get_json(f"/person/{personId}", "?language=en-US")
    
    person_name = person_data.get("name", "Artista Desconhecido")
    
    movie_data = get_json("/search/movie", f"?query={person_name}&language=en-US")

    results = movie_data.get("results", [])

    filmes = []

    for movie in results:
        filmes.append({
            "title": movie.get("title", "Título Desconhecido"),
            "rank": movie.get("popularity", 0)
        })

    filmes.sort(reverse=True, key=lambda movie: movie["rank"])

    return {
        "person_id": personId,
        "person_name": person_name,
        "filmes": filmes
    }
    

# ========================================================

@app.get("/filmes")
async def filmes_populares(limit=3):
    """ Obtem os filmes mais populares usando endpoint discover """
    data = get_json(
        "/discover/movie", "?sort_by=vote_count.desc"
    )
    results = data['results']
    filtro = []
    for movie in results:
        filtro.append({
            "ID": movie['id'], 
            "title": movie['original_title'], 
            "image": 
               f"https://image.tmdb.org/t/p/w185{movie['poster_path']}"
        })
    return filtro

# Precisa implementar o endpoint artista/1100
# app.get("")
# https://api.themoviedb.org/3/person/1100/


@app.get("/artista/{name}")
async def get_artista(name: str):
    """ 
    obtem lista de artista pelo nome e popularidade 
    """
    data = get_json(
        "/search/person", f"?query={name}&language=en-US"
    )
    results = data['results']
    filtro = []
    for artist in results:
        filtro.append({
            'id': artist['id'],
            'name': artist['name'],
            'rank': artist['popularity']
        })
    # ordenar lista de artistas (filtro) pelo atributo rank
    filtro.sort(reverse=True, key=lambda artist:artist['rank'])
    # return data
    return filtro

@app.get("/artista/id/{id}")
async def get_artista_id(id: int):
   
    data = get_json(
        "/search/person", f"?query={id}&language=en-US"
    )
    results = data['results']
    filtro = []
    for artist in results:
        filtro.append({
            'id': artist['id'],
            'name': artist['name'],
            'rank': artist['popularity']
        })
    # ordenar lista de artistas (filtro) pelo atributo rank
    filtro.sort(reverse=True, key=lambda artist:artist['rank'])
    # return data
    return filtro

# 1. ativar o env
# source env/bin/activate

# 2. iniciar o uvicorn
# uvicorn pycine:app --reload

# 3. abre no navegador
# localhost:8000/filmes