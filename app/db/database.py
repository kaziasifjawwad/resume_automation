from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

username = "sa"
password = quote_plus("BS@Dhaka")  # encodes @ -> %40
host = "localhost"
port = "5432"
database = "resumeautomation"

DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
