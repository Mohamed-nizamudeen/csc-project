from sqlalchemy import Column, Integer, String
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    product = Column(String)
    user_type = Column(String)
    query_type = Column(String)
    message = Column(String)
    response = Column(String)
    status = Column(String, default="Pending")