from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


# Создаем базовый класс для моделей
Base = declarative_base()

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
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)


class Welders(Base):
    __tablename__ = 'welders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
