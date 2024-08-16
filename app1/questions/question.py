from fastapi import APIRouter, status, Depends, HTTPException
from app1 import model
from ..database import engine, SessionLocal
from sqlalchemy.orm import session
from pydantic import BaseModel
from typing import Annotated
from ..options.option import CreateOption
from ..auth.auth import user_dependency

model.Base.metadata.create_all(bind=engine)

class CreateQuestion(BaseModel):
    title:str

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[session, Depends(get_db)]

question_router = APIRouter(prefix='/api/question')

@question_router.get('/{id}')
def get_question(user:user_dependency,id:int,db: db_dependency):                                       # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    db_ques = db.query(model.Question).filter(model.Question.id == id).first()    # type: ignore
    if db_ques is None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, 
                            detail= "Question Not Found")
    
    db_options = db.query(model.Option).filter(model.Option.q_id == id).all()     # type: ignore

    return {"question":db_ques,"options":db_options}


@question_router.post('/create')
def create_question(ques:CreateQuestion, user: user_dependency, db: db_dependency):                       # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if user.get('role') == "user":
        raise HTTPException(status_code=401, detail='Access Denied')
    
    db_ques = model.Question(**ques.dict())
    db.add(db_ques)                                                                # type: ignore
    db.commit()                                                                    # type: ignore
    db.refresh(db_ques)                                                            # type: ignore
    return db_ques

@question_router.post('/{id}/option/create')
def create_option(id:int,option:CreateOption, user: user_dependency, db: db_dependency):                   # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if user.get('role') == "user":
        raise HTTPException(status_code=401, detail='Access Denied')
    
    db_ques = db.query(model.Question).filter(model.Question.id == id).first()     # type: ignore

    if db_ques is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Question Not Found")

    option.q_id = id
    db_option = model.Option(**option.dict())
    db.add(db_option)         # type: ignore
    db.commit()               # type: ignore
    db.refresh(db_option)     # type: ignore
 
    db_option.links = f"http://127.0.0.1:8001/api/option/{db_option.id}/add_vote" # type: ignore
    db.commit()            # type: ignore
    db.refresh(db_option)  # type: ignore
    return db_option


@question_router.delete('/{id}/delete')
def delete_question(id:int,user: user_dependency, db: db_dependency): # type: ignore
    try:
        if user is None:
            raise HTTPException(status_code=401, detail='Authentication Failed')
        if user.get('role') == "user":
            raise HTTPException(status_code=401, detail='Access Denied')
        
        db_ques = db.query(model.Question).filter(model.Question.id == id).first() # type: ignore

        if db_ques is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail= "Question Not Found")

        
        db_options = db.query(model.Option).filter(model.Option.q_id == id).all() # type: ignore
        
        for option in db_options:
            if option.votes != 0:
                return {"msg":"Cannot delete Question"}
                    
        db.delete(db_ques) # type: ignore
        db.commit() # type: ignore

        return {"msg":"question deleted successfully"}
    
    except Exception as e:
        return str(e)
    
