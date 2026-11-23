import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_DATABASE = os.getenv("DB_DATABASE")
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8mb4"
)
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "")
PROVEEDORES_URL = os.getenv("PROVEEDORES_URL", "")
SERVICE_TIMEOUT = 2
