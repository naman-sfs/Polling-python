from fastapi import APIRouter, status, Depends, HTTPException
from app1 import model
from ..database import engine, SessionLocal
from sqlalchemy.orm import session
from pydantic import BaseModel
from typing import Annotated,Optional
from ..auth.auth import user_dependency

model.Base.metadata.create_all(bind=engine)

class CreateOption(BaseModel):
    title:str
    q_id:Optional[int] = None
    votes:Optional[int] = 0
    links:Optional[str] = ""

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[session, Depends(get_db)]

option_router = APIRouter(prefix='/api/option')

@option_router.get('/{id}')
def get_option(id:str,user: user_dependency, db: db_dependency):   # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    db_option = db.query(model.Option).filter(model.Option.id == id).first() # type: ignore
    if db_option is None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, 
                            detail= "Option Not Found")
    return db_option

@option_router.delete('/{id}/delete')
def delete_option(id:int,user : user_dependency, db: db_dependency):     # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if user.get('role') == "user":
        raise HTTPException(status_code=401, detail='Access Denied')
    
    db_option = db.query(model.Option).filter(model.Option.id == id).first()    # type: ignore
    if db_option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Option Not Found")
    if db_option.votes != 0:
        return {"msg":"Cannot delete option"}
    
    db.delete(db_option)    # type: ignore
    db.commit()             # type: ignore
    return db_option

@option_router.get('/{id}/add_vote')
def add_vote(id:int, user: user_dependency, db: db_dependency):         # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if user.get('role') == "admin":
        raise HTTPException(status_code=401, detail='Access Denied')
    
    user_id = user.get('id')
    votes_by_user = db.query(model.Vote).filter(model.Vote.user_id == user_id).first()    # type: ignore
    if votes_by_user:
        print(votes_by_user.question_voted)
    else:
        vote = AddVote(user_id)                                                        # type: ignore
        
        db_vote = model.Vote(**vote.dict())
        db.add(db_ques)                                                                # type: ignore
        db.commit()                                                                    # type: ignore
        db.refresh(db_vote)                                                            # type: ignore

    db_option = db.query(model.Option).filter(model.Option.id == id).first()    # type: ignore
    if db_option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Option Not Found")
    
    db_option.votes = db_option.votes + 1
    db.commit()      # type: ignore
    return {"msg":"Voted Successfully","total votes":db_option.votes}

