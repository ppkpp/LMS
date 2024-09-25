from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Float,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
    ARRAY,
    Boolean,
    BigInteger
)
from handlers.database import Base
import datetime
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType

from fastapi_storages import FileSystemStorage 
storage = FileSystemStorage(path="uploads/")



class Admin(Base):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    birthday = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(FileType(storage=storage))
    active = Column(Boolean, unique=False, default=True)
    position = Column(String, unique=False, nullable=False)
    role = Column(String, unique=False, nullable=False)
class UserInDB(Admin):
    password: Column(String, nullable=False)


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phoneno = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(FileType(storage=storage))
    active = Column(Boolean, unique=False, default=False)
    description = Column(String, nullable=False)
    rollno =  Column(Integer,nullable=True,index=True)
    role = Column(String)
    rfid = Column(String, nullable=True)
    
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    author = Column(String, nullable=False)
    rollno =  Column(Integer,nullable=True,index=True)
    edition =  Column(String,nullable=True,index=True)
    createdate = Column(DateTime, default=datetime.datetime.now)
    publishdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(FileType(storage=storage))
    ebook = Column(FileType(storage=storage))
    remark = Column(String, nullable=False)
    barcode = Column(String, nullable=True)
    location = Column(String,nullable=True)

class Rating(Base):
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True, index=True)
    userId =  Column(Integer,nullable=False,index=True)
    bookId =  Column(Integer,nullable=False,index=True)
    rate = Column(Integer,nullable=False,index=True)
    borrowdate = Column(DateTime,default=datetime.datetime.now)
    returndate = Column(DateTime,default=datetime.datetime.now)
class BannerModel(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String,nullable=False)
    description = Column(String, nullable=False)
    postImage = Column(FileType(storage=storage))
    createdate = Column(DateTime, default=datetime.datetime.now)

