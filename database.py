from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db" # when switching to PostgresSQL only the connection string needs to be changed, no more than this is required

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # the dict key-value here are SQLite specific not required for SQL or PostgresSQL, required here because SQLite is single threaded and fastapi allows for multiple threads in SQLite, so need to disable this by the given key-value, not required for PostgresSQL or SQL
)
# SessionLocal is a factory that creates DB sessions
# Session: Is a transaction between DB's, each request gets its own separate sessions
# autocommit=False & autoflush=False, to manually make the changes for commits; These are std fastapi pattern
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# get_db() is a dependency function; It provides session routes; Its a generator using yield; with statement here works as a context manager(kind of like a window), it gives cleanup if an error occurs
def get_db():
    with SessionLocal() as db:
        yield db