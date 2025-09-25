# 비즈니스 로직

from db import SessionLocal
from crud import get_object_by_name
from models import Object

db = SessionLocal()
object = get_object_by_name(db, "fox")
print("name =", object.name)

