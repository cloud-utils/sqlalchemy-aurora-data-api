import aurora_data_api
from sqlalchemy.dialects.postgresql.base import PGDialect


class AuroraPostgresDataAPIDialect(PGDialect):
    @classmethod
    def dbapi(cls):
        return aurora_data_api
