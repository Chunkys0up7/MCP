from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from ..config.settings import settings

def init_db():
    """Initialize the database with all tables."""
    # Create database URL
    DATABASE_URL = f"postgresql://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.database}"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 