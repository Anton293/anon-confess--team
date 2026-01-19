# PostgreSQL async driver
#apt install libpq-dev
#pip install psycopg[binary]
import psycopg
from psycopg import sql
from psycopg import AsyncConnection


import json
from types import SimpleNamespace
from datetime import datetime, timedelta
from functools import lru_cache


from sqlalchemy import func, distinct
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Date, Time, DateTime, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import text, BigInteger, UniqueConstraint, Index
from src.core.config import settings

# DSN for connection to PostgreSQL
#DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}{'' if not POSTGRES_USE_SSL else '?sslmode=require'}"
DSN = settings.database_url

# Ініціалізація бази даних (ORM)
Base = declarative_base()


class User(Base):
    """Клас для таблиці користувачів."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    token = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    fingerprint = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_token', 'token'),
    )


class BannedIp(Base):
    """Клас для таблиці забанених IP-адрес."""
    __tablename__ = 'banned_ips'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, unique=True, nullable=False)
    reason = Column(Text, nullable=True)
    banned_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_ip_address', 'ip_address'),
        UniqueConstraint('ip_address', name='unique_ip_address'),
    )


class BannedFingerprint(Base):
    """Клас для таблиці забанених відбитків пристроїв."""
    __tablename__ = 'banned_fingerprints'

    id = Column(Integer, primary_key=True)
    fingerprint = Column(String, unique=True, nullable=False)
    reason = Column(Text, nullable=True)
    banned_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_fingerprint', 'fingerprint'),
        UniqueConstraint('fingerprint', name='unique_fingerprint'),
    )

class Room(Base):
    """Клас для таблиці кімнат."""
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    own_token_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Створення таблиць
# Base.metadata.create_all(engine) # WARNING: Use alembic migrations instead! `alembic revision --autogenerate -m "Initial structure"`


########################################################################################################################
# Додавання даних в базу даних                                                                                         #
########################################################################################################################


async def add_user(name: str, email: str | None = None, ip_address: str | None = None, fingerprint: str | None = None) -> User:
    """Add new user to the database and return the User object"""
    async with await AsyncConnection.connect(DSN) as conn:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (name, email, ip_address, fingerprint)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, email, ip_address, fingerprint, created_at, is_active
                    """,
                    (name, email, ip_address, fingerprint)
                )
                row = await cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                user_data = dict(zip(columns, row))
                return User(**user_data)


async def register_banned_ip(ip_address: str, reason: str | None = None) -> BannedIp:
    """Register a banned IP address in the database"""
    async with await AsyncConnection.connect(DSN) as conn:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO banned_ips (ip_address, reason)
                    VALUES (%s, %s)
                    RETURNING id, ip_address, reason, banned_at
                    """,
                    (ip_address, reason)
                )
                row = await cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                banned_ip_data = dict(zip(columns, row))
                return BannedIp(**banned_ip_data)
            

async def register_banned_fingerprint(fingerprint: str, reason: str | None = None) -> BannedFingerprint:
    """Register a banned fingerprint in the database"""
    async with await AsyncConnection.connect(DSN) as conn:
        async with conn.transaction():
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO banned_fingerprints (fingerprint, reason)
                    VALUES (%s, %s)
                    RETURNING id, fingerprint, reason, banned_at
                    """,
                    (fingerprint, reason)
                )
                row = await cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                banned_fingerprint_data = dict(zip(columns, row))
                return BannedFingerprint(**banned_fingerprint_data)



# async def get_users_with_notifications():
#     """Хочаб один з параметрів повинен бути True"""
#     async with await AsyncConnection.connect(DSN) as conn:
#         async with conn.transaction():
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     SELECT id, telegram_id, settings
#                     FROM users
#                     WHERE settings->'notifications'->>'first_available' = 'true'
#                        OR settings->'notifications'->>'first' = 'true'
#                        OR settings->'notifications'->>'last' = 'true'
#                        OR settings->'notifications'->>'custom' = 'true'
#                        OR settings->'notifications'->>'all' = 'true'
#                        OR settings->'notifications'->>'notify_after_missed' = 'true'
#                     """
#                 )
#                 return await cur.fetchall()


# async def update_user_settings(user_id, settings_space, settings_name, new_value):
#     # Формуємо шлях як масив ключів, наприклад: '{notifications,all}'
#     path = f'{{{settings_space},{settings_name}}}'
#     async with await AsyncConnection.connect(DSN) as conn:
#         async with conn.transaction():
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     UPDATE users
#                     SET settings = jsonb_set(settings, %s, %s::jsonb)
#                     WHERE id = %s
#                     """,
#                     (path, json.dumps(new_value), user_id)
#                 )


# async def get_user_settings(user_id, settings_space):
#     async with await AsyncConnection.connect(DSN) as conn:
#         async with conn.transaction():
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     SELECT settings->%s
#                     FROM users
#                     WHERE id = %s
#                     """,
#                     (settings_space, user_id)
#                 )
#                 return await cur.fetchone()


# async def get_user_object(user_id: int) -> dict:
#     """Отримуємо користувача з бази даних"""
#     async with await AsyncConnection.connect(DSN) as conn:
#         async with conn.transaction():
#             async with conn.cursor() as cur:
#                 await cur.execute(
#                     """
#                     SELECT *
#                     FROM users
#                     WHERE id = %s
#                     """,
#                     (user_id,)
#                 )

#                 if result := await cur.fetchone():
#                     columns = [desc[0] for desc in cur.description]
#                     return dict(zip(columns, result))

