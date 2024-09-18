from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db"

database = Database(DATABASE_URL)
metadata = MetaData()
