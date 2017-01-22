from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String
)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///babot.sqlite')
session = sessionmaker()
session.configure(bind=engine)

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

    @classmethod
    def get_slack_user(cls, slack_user):
        db = session()
        return db.query(cls).filter(cls.user==slack_user).first()
