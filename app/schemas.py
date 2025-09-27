# app/schemas.py
from pydantic import BaseModel, EmailStr, constr, conint

class User(BaseModel):
    user_id: int
    name: constr(min_length=2, max_length=50)
    email: EmailStr
    age: conint(gt=18)
    # student_id must start with "S" followed by exactly 7 digits
    student_id: constr(pattern=r'^S\d{7}$')
