import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Plants(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    plant = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    message = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    sender = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.TEXT,
                                     default=datetime.datetime.now().strftime("%d.%m.%Y"))
