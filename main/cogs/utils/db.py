# TODO REDO THIS 

from typing import ClassVar
import asyncpg
import json



class Table:
    @classmethod
    async def create_pool(cls, uri, **kwargs):
        def _encode_jsonb(value):
            return json.dumps(value)

        def _decode_jsonb(value):
            return json.loads(value)

        old_init = kwargs.pop('init', None)

        async def init(con):
            await con.set_type_codec('jsonb', schema='pg_catalog', encoder=_encode_jsonb, decoder=_decode_jsonb, format='text')
            if old_init is not None:
                await old_init(con)

        try:
            cls._pool = pool = await asyncpg.create_pool(uri, **kwargs)
        except Exception as e:
            print(e)
        return pool