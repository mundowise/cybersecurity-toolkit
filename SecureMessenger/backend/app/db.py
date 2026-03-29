# app/db.py
from __future__ import annotations
import aiosqlite
from contextlib import asynccontextmanager

DB_PATH = "securemessenger.db"

PRAGMAS = [
    "PRAGMA foreign_keys = ON;",
    "PRAGMA journal_mode = WAL;",
    "PRAGMA synchronous = NORMAL;",
    "PRAGMA busy_timeout = 5000;",
]

# v6: tabla chat_keys para ECDH pubkeys por chat/usuario
SCHEMA_VERSION = 6

SCHEMA_SQL = [
    # Usuarios
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
    # Chats
    """
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        is_group INTEGER NOT NULL DEFAULT 0,
        name TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """,
    # Miembros
    """
    CREATE TABLE IF NOT EXISTS chat_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role TEXT DEFAULT 'member',
        display_name TEXT,
        joined_at TEXT DEFAULT (datetime('now')),
        UNIQUE(chat_id, user_id)
    );
    """,
    # Mensajes
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        content TEXT,
        sent_at TEXT DEFAULT (datetime('now')),
        expires_at TEXT,
        type TEXT DEFAULT 'text',
        filename TEXT,
        mimetype TEXT
    );
    """,
    # Invitaciones
    """
    CREATE TABLE IF NOT EXISTS invites (
        code TEXT PRIMARY KEY,
        creator_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        is_group INTEGER NOT NULL DEFAULT 0,
        max_uses INTEGER NOT NULL DEFAULT 1,
        uses INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        expires_at TEXT NOT NULL
    );
    """,
    # Claves públicas por chat (ECDH X25519)
    """
    CREATE TABLE IF NOT EXISTS chat_keys (
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        pubkey TEXT NOT NULL, -- base64
        PRIMARY KEY (chat_id, user_id)
    );
    """,
    # Índices
    "CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_messages_expires ON messages(expires_at);",
    "CREATE INDEX IF NOT EXISTS idx_members_user ON chat_members(user_id);",
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_chat_members_chat_user ON chat_members(chat_id, user_id);",
    "CREATE INDEX IF NOT EXISTS idx_invites_expires ON invites(expires_at);",
]

async def _apply_pragmas(conn: aiosqlite.Connection):
    for p in PRAGMAS:
        await conn.execute(p)

async def _get_user_version(conn: aiosqlite.Connection) -> int:
    async with conn.execute("PRAGMA user_version;") as cur:
        row = await cur.fetchone()
        return 0 if row is None else int(row[0])

async def _set_user_version(conn: aiosqlite.Connection, v: int) -> None:
    await conn.execute(f"PRAGMA user_version = {v};")

async def _table_exists(conn: aiosqlite.Connection, table: str) -> bool:
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,)
    ) as cur:
        return (await cur.fetchone()) is not None

async def _col_exists(conn: aiosqlite.Connection, table: str, col: str) -> bool:
    async with conn.execute(f"PRAGMA table_info({table});") as cur:
        cols = [r[1] async for r in cur]
        return col in cols

async def _migrate(conn: aiosqlite.Connection, current: int):
    # Asegura tablas base
    for sql in SCHEMA_SQL:
        await conn.execute(sql)

    # messages columnas
    if not await _col_exists(conn, "messages", "type"):
        await conn.execute("ALTER TABLE messages ADD COLUMN type TEXT DEFAULT 'text';")
    if not await _col_exists(conn, "messages", "filename"):
        await conn.execute("ALTER TABLE messages ADD COLUMN filename TEXT;")
    if not await _col_exists(conn, "messages", "mimetype"):
        await conn.execute("ALTER TABLE messages ADD COLUMN mimetype TEXT;")
    if not await _col_exists(conn, "messages", "expires_at"):
        await conn.execute("ALTER TABLE messages ADD COLUMN expires_at TEXT;")

    # chat_members.role/display_name
    if await _table_exists(conn, "chat_members") and not await _col_exists(conn, "chat_members", "role"):
        await conn.execute("ALTER TABLE chat_members ADD COLUMN role TEXT DEFAULT 'member';")
        await conn.execute("UPDATE chat_members SET role='member' WHERE role IS NULL;")
    if await _table_exists(conn, "chat_members") and not await _col_exists(conn, "chat_members", "display_name"):
        await conn.execute("ALTER TABLE chat_members ADD COLUMN display_name TEXT;")

    # invites ya existe en v5; asegura columnas mínimas
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_invites_expires ON invites(expires_at);")

    # chat_keys
    if not await _table_exists(conn, "chat_keys"):
        await conn.execute("""
            CREATE TABLE chat_keys (
                chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                pubkey TEXT NOT NULL,
                PRIMARY KEY (chat_id, user_id)
            );
        """)

    # Índices
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, sent_at);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_expires ON messages(expires_at);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_members_user ON chat_members(user_id);")
    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_chat_members_chat_user ON chat_members(chat_id, user_id);")

    await conn.commit()

@asynccontextmanager
async def get_db():
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        await _apply_pragmas(conn)
        for sql in SCHEMA_SQL:
            await conn.execute(sql)
        current = await _get_user_version(conn)
        if current < SCHEMA_VERSION:
            await _migrate(conn, current)
            await _set_user_version(conn, SCHEMA_VERSION)
        await conn.commit()
        yield conn
    finally:
        await conn.close()

async def init_db():
    async with get_db() as _:
        return
