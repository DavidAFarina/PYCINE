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

class FavModel(BaseModel):
    idmovie: int
    userid: int


class Fav(FavModel):
    id: int
    class Config:
        orm_mode = True