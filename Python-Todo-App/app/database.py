from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# connect_args={"check_same_thread": False} is required only for SQLite.
# It allows multiple threads to access the same database session.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for retrieving database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
