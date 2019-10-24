import aurora_data_api
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.dialects.mysql.base import MySQLDialect


class AuroraMySQLDataAPIDialect(MySQLDialect):
    @classmethod
    def dbapi(cls):
        return aurora_data_api


class AuroraPostgresDataAPIDialect(PGDialect):
    @classmethod
    def dbapi(cls):
        return aurora_data_api


def register_dialects():
    from sqlalchemy.dialects import registry
    registry.register("mysql.auroradataapi", __name__, AuroraMySQLDataAPIDialect.__name__)
    registry.register("postgresql.auroradataapi", __name__, AuroraPostgresDataAPIDialect.__name__)
