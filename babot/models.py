from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String
)

Base = declarative_base()

class BairesUser(Base):

    __tablename__ = 'baires_user'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    email = Column(String)
    password = Column(String)

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
        self.password = password

    def __repr__(self):
        return '<BairesUser ({}) {}>'.format(email)
