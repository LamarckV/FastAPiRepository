import psycopg2

from app.config import DATABASE_URL

def get_conn():
    """opens and returns the conexion on postgres"""
    return psycopg2.connect(DATABASE_URL)