from fastapi import APIRouter, status, Depends, HTTPException, Cookie
from app1 import model
from ..database import engine, SessionLocal
from sqlalchemy.orm import session
from pydantic import BaseModel
from typing import Annotated
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from .email import send_login_email

SECRET_KEY = "fjklgfklgfjdslgjflg;jsd5654654"  # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

model.Base.metadata.create_all(bind=engine)

class CreateUser(BaseModel):
    f_name:str
    l_name:str
    email:str
    password:str

class UserLogin(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[session, Depends(get_db)]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter(prefix='/api/auth')

@auth_router.get('/')
def auth():
    return "auth router"

@auth_router.post('/user/create')
def create_user(user:CreateUser, db: db_dependency):                       # type: ignore
    user.password = pwd_context.hash(user.password)
    db_item=model.User(**user.model_dump())
    db.add(db_item)  # type: ignore
    db.commit()      # type: ignore
    db.refresh(db_item)  # type: ignore
    return db_item

@auth_router.post("/login")
def login(form_data:UserLogin,db: db_dependency):     # type: ignore
    
    user = authenticate_user(form_data.email, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user.')
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))
    
    response = JSONResponse({"access_token": token, "token_type": "bearer"})
    response.set_cookie(key="token", value=token,httponly=False,path='/')
    send_login_email()
    return response


def authenticate_user(email: str, password: str, db):
    user = db.query(model.User).filter(model.User.email == email).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str, user_id: int,role:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, "role": role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

#token: Annotated[str, Depends(oauth2_bearer)]
def get_current_user(token: str = Cookie(None)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')    # type: ignore
        user_id: int = payload.get('id')      # type: ignore
        role: str = payload.get('role')       # type: ignore
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, "role":role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


# @auth_router.post("/token", response_model=Token)
# def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
#     user = authenticate_user(form_data.username, form_data.password, db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail='Could not validate user.')
#     token = create_access_token(user.email, user.id, timedelta(minutes=20))

#     return {'access_token': token, 'token_type': 'bearer'}

user_dependency = Annotated[dict, Depends(get_current_user)]

@auth_router.get('/user', status_code=status.HTTP_200_OK)
def get_user(user: user_dependency, db: db_dependency):    # type: ignore
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(model.User).filter(model.User.id == user.get('id')).first()     # type: ignore


