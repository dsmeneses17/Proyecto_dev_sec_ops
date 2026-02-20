from app.db import Base, engine
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish


Base.metadata.create_all(bind=engine)