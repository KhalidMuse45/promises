from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from .db import Base


class Promise(Base):
    __tablename__ = "promises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    promise_type = Column(String)
    content = Column(String)
    created_at = Column(Integer)
    deadline_at = Column(Integer)
    status = Column(String)
    hash_value = Column(String)
