from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    f_name = Column(String(20))
    l_name = Column(String(20))
    role = Column(String(10),default="user")
    email = Column(String(30))
    password = Column(LONGTEXT)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    
    options = relationship("Option", backref="question", cascade="all, delete-orphan")

class Option(Base):
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    q_id = Column(Integer, ForeignKey('questions.id'))
    votes = Column(Integer,default=0)
    links = Column(String(200))
    #questions = relationship("Question", back_populates="options")

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer,primary_key=True)
    question_voted = Column(JSON)


