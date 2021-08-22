# --------------------------------------------------------------------------
#                                    Imports
# --------------------------------------------------------------------------
import asyncpg
import json
import traceback


# --------------------------------------------------------------------------
#                                    Run Bot
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#                                    Run Bot
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#                                    Run Bot
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#                                    Run Bot
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#                                  Maybe Aquire 
# --------------------------------------------------------------------------
class MaybeAcquire:
    def __init__(self, connection, *, pool):
        self.connection = connection
        self.pool = pool
        self._cleanup = False

    async def __aenter__(self):
        if self.connection is None:
            self._cleanup = True
            self._connection = c = await self.pool.acquire()
            return c
        return self.connection

    async def __aexit__(self, *args):
        if self._cleanup:
            await self.pool.release(self._connection)


# --------------------------------------------------------------------------
#                                    DB Class
# --------------------------------------------------------------------------
class DB:
    @classmethod
    async def create_pool(cls, uri: str, **kwargs):
        
        def _encode_jsonb(value):
            return json.dumps(value)

        def _decode_jsonb(value):
            return json.loads(value)

        old_init = kwargs.pop('init', None)

        async def init(con):
            await con.set_type_codec('jsonb', schema='pg_catalog', encoder=_encode_jsonb, decoder=_decode_jsonb, format='text')
            if old_init is not None:
                await old_init(con)
        
        cls._pool = pool = await asyncpg.create_pool(uri, **kwargs)

        return pool


    @classmethod
    def aquire_connection(cls, conn):
        return MaybeAcquire(conn, pool=cls._pool)