import json, datetime, re

from sqlalchemy import cast, func, util
from sqlalchemy.types import JSON as SA_JSON
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID, DATE, TIME, TIMESTAMP, ARRAY
from sqlalchemy.dialects.mysql.base import MySQLDialect

import aurora_data_api


class AuroraMySQLDataAPIDialect(MySQLDialect):
    # See https://docs.sqlalchemy.org/en/13/core/internals.html#sqlalchemy.engine.interfaces.Dialect
    driver = "aurora_data_api"
    default_schema_name = None

    @classmethod
    def dbapi(cls):
        return aurora_data_api

    def _detect_charset(self, connection):
        return connection.execute("SHOW VARIABLES LIKE 'character_set_client'").fetchone()[1]

    def _extract_error_code(self, exception):
        return exception.args[0]


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
class _ADA_DATETIME_MIXIN:
    iso_ts_re = re.compile(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+")

    def bind_processor(self, dialect):
        def process(value):
            return value.isoformat() if isinstance(value, self.py_type) else value
        return process

    def bind_expression(self, value):
        return cast(value, self.sa_type)

    def result_processor(self, dialect, coltype):
        def process(value):
            # When the microsecond component ends in zeros, they are omitted from the return value,
            # and datetime.datetime.fromisoformat can't parse the result (example: '2019-10-31 09:37:17.31869'). Pad it.
            if isinstance(value, str) and self.iso_ts_re.match(value):
                value = self.iso_ts_re.sub(lambda match: match.group(0).ljust(26, "0"), value)
            return self.py_type.fromisoformat(value) if isinstance(value, str) else value
        return process


class _ADA_DATE(_ADA_DATETIME_MIXIN, DATE):
    py_type = datetime.date
    sa_type = DATE


class _ADA_TIME(_ADA_DATETIME_MIXIN, TIME):
    py_type = datetime.time
    sa_type = TIME


class _ADA_TIMESTAMP(_ADA_DATETIME_MIXIN, TIMESTAMP):
    py_type = datetime.datetime
    sa_type = TIMESTAMP


class _ADA_ARRAY(ARRAY):
    def bind_processor(self, dialect):
        def process(value):
            # FIXME: escape strings properly here
            return "\v".join(value) if isinstance(value, list) else value
        return process

    def bind_expression(self, value):
        return func.string_to_array(value, "\v")


class AuroraPostgresDataAPIDialect(PGDialect):
    # See https://docs.sqlalchemy.org/en/13/core/internals.html#sqlalchemy.engine.interfaces.Dialect
    driver = "aurora_data_api"
    default_schema_name = None
    colspecs = util.update_copy(PGDialect.colspecs, {
        SA_JSON: _ADA_SA_JSON,
        JSON: _ADA_JSON,
        JSONB: _ADA_JSONB,
        UUID: _ADA_UUID,
        DATE: _ADA_DATE,
        TIME: _ADA_TIME,
        TIMESTAMP: _ADA_TIMESTAMP,
        ARRAY: _ADA_ARRAY
    })
    @classmethod
    def dbapi(cls):
        return aurora_data_api


def register_dialects():
    from sqlalchemy.dialects import registry
    registry.register("mysql.auroradataapi", __name__, AuroraMySQLDataAPIDialect.__name__)
    registry.register("postgresql.auroradataapi", __name__, AuroraPostgresDataAPIDialect.__name__)
