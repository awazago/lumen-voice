from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String) # NUNCA guarde a senha em texto!
    credits = Column(Integer, default=10)

    stripe_customer_id = Column(String, unique=True, index=True, nullable=True)
    plan = Column(String, nullable=True, default="free") # ex: free, hobby, pro