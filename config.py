import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Путь к БД в корне проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "service.db")

# Создаем engine (SQLite)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Создаем sessionmaker (не сессию!)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def db_session():
    """
    Контекстный менеджер дя безопасной работы с сессией
    :return:
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
