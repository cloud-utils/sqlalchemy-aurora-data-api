import json, datetime

import aurora_data_api
from sqlalchemy import cast, util
from sqlalchemy.types import JSON as SA_JSON
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID, DATE, TIMESTAMP
from sqlalchemy.dialects.mysql.base import MySQLDialect


class AuroraMySQLDataAPIDialect(MySQLDialect):
    @classmethod
    def dbapi(cls):
        return aurora_data_api


class _ADA_SA_JSON(SA_JSON):
    def bind_expression(self, value):
        return cast(value, SA_JSON)


class _ADA_JSON(JSON):
    def bind_expression(self, value):
        return cast(value, JSON)


class _ADA_JSONB(JSONB):
    def bind_expression(self, value):
        return cast(value, JSONB)


class _ADA_UUID(UUID):
    def bind_expression(self, value):
        return cast(value, UUID)


# TODO: is TZ awareness needed here?
class _ADA_DATE(DATE):
    def bind_processor(self, dialect):
        def process(value):
            return value.isoformat()
        return process

    def bind_expression(self, value):
        return cast(value, DATE)

    def result_processor(self, dialect, coltype):
        def process(value):
            return datetime.date.fromisoformat(value)
        return process


class _ADA_TIMESTAMP(TIMESTAMP):
    def bind_processor(self, dialect):
        def process(value):
            return value.isoformat()
        return process

    def bind_expression(self, value):
        return cast(value, TIMESTAMP)

    def result_processor(self, dialect, coltype):
        def process(value):
            # FIXME: when the microsecond component ends in zero, it is omitted from the return value,
            # and datetime.datetime.fromisoformat can't parse it
            return datetime.datetime.fromisoformat(value)
        return process


class AuroraPostgresDataAPIDialect(PGDialect):
    colspecs = util.update_copy(PGDialect.colspecs, {
        SA_JSON: _ADA_SA_JSON,
        JSON: _ADA_JSON,
        JSONB: _ADA_JSONB,
        UUID: _ADA_UUID,
        DATE: _ADA_DATE,
        TIMESTAMP: _ADA_TIMESTAMP
    })
    @classmethod
    def dbapi(cls):
        return aurora_data_api


def register_dialects():
    from sqlalchemy.dialects import registry
    registry.register("mysql.auroradataapi", __name__, AuroraMySQLDataAPIDialect.__name__)
    registry.register("postgresql.auroradataapi", __name__, AuroraPostgresDataAPIDialect.__name__)
