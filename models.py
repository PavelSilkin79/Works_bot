from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


# Создаем базовый класс для моделей
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    tg_id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Boolean, default=False)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)

    def __repr__(self):
        return f"<Admin user_id={self.user_id}>"

class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)


class Installers(Base):
    __tablename__ = 'installers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    photo_id = Column(String, nullable=True)  # <- храним file_id
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)



class Welders(Base):
    __tablename__ = 'welders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    photo_id = Column(String, nullable=True)  # <- храним file_id
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
