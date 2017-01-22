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
    slack_user = Column(String)
    user = Column(String)
    password = Column(String)

    def __init__(self, slack_user, user, password):
        self.slack_user = slack_user
        self.user = user
        self.password = password

    def __repr__(self):
        return '<BairesUser ({}) {}>'.format(self.id, self.user)

    @classmethod
    def get_slack_user(cls, slack_user):
        db = session()
        return db.query(cls).filter(cls.slack_user==slack_user).first()
