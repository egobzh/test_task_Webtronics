from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, Boolean,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///db.sqlite3")

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    userfrom = Column(Integer, nullable=False)
    text = Column(String(150), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32),unique=True,nullable=False)
    email = Column(String(100),unique=True,nullable=False)
    hashed_password = Column(String(32),nullable=False)
    is_active = Column(Boolean,default=True,nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

class like(Base):
    __tablename__ = 'like'
    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey("post.id"))
    user = Column(Integer, ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"post:{self.user}, user:{self.user}"

class dislike(Base):
    __tablename__ = 'dislike'
    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey("post.id"))
    user = Column(Integer, ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"post:{self.user}, user:{self.user}"

#User.__table__.create(engine)
#like.__table__.create(engine)
#Post.__table__.create(engine)
#dislike.__table__.create(engine)