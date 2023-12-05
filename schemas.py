from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True
        
class UserModel(BaseModel):
    email: str
    name: str
    password: str

class Movie(BaseModel):
    id: int
    tmdb_id: int
    title: str

class Favoritos(BaseModel):
    user_id: int
    tmdb_id: int
    title: str | None = None

class Artistas(BaseModel):
    tmdb_id: int
    name: str
    rank: str
    biography:str
    
   
