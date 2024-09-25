from sqladmin import Admin, ModelView
from models.model import Admin,Student,Book,Rating,BannerModel

class AdminView(ModelView, model=Admin):
    #name = "Teacher"
    column_list = [Admin.id, Admin.username, Admin.birthday,Admin.position,Admin.active,Admin.createdate]
    icon = "fa-solid fa-user-circle"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class StudentView(ModelView, model=Student):
    name = "Teacher/Student"
    name_plural = "Teachers/Students"
    column_list = [Student.id, Student.username, Student.phoneno,Student.rfid, Student.role, Student.rollno, Student.description, Student.createdate, Student.active]
    icon = "fa-solid fa-user"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class BookView(ModelView, model=Book):
    column_list = [Book.id, Book.title, Book.author,Book.barcode, Book.rollno, Book.edition,Book.publishdate,Book.postImage,Book.ebook,Book.remark,Book.location]
    icon = "fa-solid fa-book"
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    #can_edit = False


class RatingView(ModelView, model=Rating):
    column_list = [Rating.id,Rating.userId, Rating.bookId,Rating.rate,Rating.borrowdate,Rating.returndate]
    name = "Virtual"
    icon = "fa-solid fa-thumbs-up"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class BannerView(ModelView, model=BannerModel):
    name = "Banner"
    name_plural = "Banners"
    column_list = [BannerModel.id,BannerModel.title, BannerModel.description,BannerModel.postImage]
    icon = "fa-solid fa-television"
    page_size = 50
    page_size_options = [25, 50, 100, 200]
