"""Lightweight stand-in for the aiosqlite package used in tests.

This implementation provides the minimal async API surface that SQLAlchemy's
aiosqlite dialect relies on. It wraps the standard sqlite3 module and executes
blocking operations in a thread so that it behaves like the real aiosqlite
library for basic usage.
"""

from __future__ import annotations

import asyncio
import contextlib
import sqlite3
from typing import Any, Callable, Iterable

Error = sqlite3.Error
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError

PARSE_COLNAMES = sqlite3.PARSE_COLNAMES
PARSE_DECLTYPES = sqlite3.PARSE_DECLTYPES
Binary = sqlite3.Binary
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info
Row = sqlite3.Row


class Cursor:
    def __init__(self, connection: "Connection", cursor: sqlite3.Cursor):
        self._connection = connection
        self._cursor = cursor

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
        params = parameters or []
        await asyncio.to_thread(self._cursor.execute, sql, params)
        return self

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]):
        await asyncio.to_thread(self._cursor.executemany, sql, seq_of_parameters)
        return self

    async def executescript(self, sql_script: str):
        await asyncio.to_thread(self._cursor.executescript, sql_script)
        return self

    async def fetchall(self):
        return await asyncio.to_thread(self._cursor.fetchall)

    async def fetchone(self):
        return await asyncio.to_thread(self._cursor.fetchone)

    async def fetchmany(self, size: int | None = None):
        if size is None:
            return await asyncio.to_thread(self._cursor.fetchmany)
        return await asyncio.to_thread(self._cursor.fetchmany, size)

    @property
    def description(self):
        return self._cursor.description

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    async def close(self):
        await asyncio.to_thread(self._cursor.close)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        return False


class Connection:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.row_factory = getattr(conn, "row_factory", None)
        self.isolation_level = conn.isolation_level
        self._tx: asyncio.Queue[tuple[asyncio.Future, Callable[[], Any]]] = asyncio.Queue()
        self._tx_worker = asyncio.create_task(self._process_tx_queue())

    @classmethod
    async def _connect(cls, database: str, **kwargs: Any) -> "Connection":
        kwargs["check_same_thread"] = False
        conn = await asyncio.to_thread(sqlite3.connect, database, isolation_level=None, **kwargs)
        return cls(conn)

    async def _process_tx_queue(self):
        try:
            while True:
                future, func = await self._tx.get()
                if future.cancelled():
                    continue
                try:
                    result = await asyncio.to_thread(func)
                except Exception as exc:  # noqa: BLE001
                    if not future.done():
                        future.set_exception(exc)
                else:
                    if not future.done():
                        future.set_result(result)
        except asyncio.CancelledError:
            return

    def __getattr__(self, item: str) -> Any:
        return getattr(self._conn, item)

    async def cursor(self) -> Cursor:
        cur = await asyncio.to_thread(self._conn.cursor)
        return Cursor(self, cur)

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
        cursor = await self.cursor()
        await cursor.execute(sql, parameters)
        return cursor

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]):
        cursor = await self.cursor()
        await cursor.executemany(sql, seq_of_parameters)
        return cursor

    async def executescript(self, sql_script: str):
        cursor = await self.cursor()
        await cursor.executescript(sql_script)
        return cursor

    async def commit(self):
        await asyncio.to_thread(self._conn.commit)

    async def rollback(self):
        await asyncio.to_thread(self._conn.rollback)

    async def close(self):
        await asyncio.to_thread(self._conn.close)
        if self._tx_worker:
            self._tx_worker.cancel()
            with contextlib.suppress(Exception):
                await self._tx_worker

    def _queue_work(self, func: Callable[[], Any]):
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._tx.put_nowait((future, func))
        return future

    def create_function(self, *args: Any, **kwargs: Any):
        def run():
            self._conn.create_function(*args, **kwargs)

        return asyncio.create_task(asyncio.to_thread(run))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        return False


class ConnectionMaker:
    def __init__(self, database: str, **kwargs: Any):
        self.database = database
        self.kwargs = kwargs
        self.daemon = False

    def __await__(self):
        return Connection._connect(self.database, **self.kwargs).__await__()


def connect(database: str, **kwargs: Any) -> ConnectionMaker:
    return ConnectionMaker(database, **kwargs)
