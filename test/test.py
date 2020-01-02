import os, sys, json, unittest, logging, datetime, getpass, enum
from uuid import uuid4

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, LargeBinary, Numeric, Date, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, DATE, TIME, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa

from sqlalchemy_aurora_data_api import register_dialects, _ADA_TIMESTAMP

logging.basicConfig(level=logging.INFO)
logging.getLogger("aurora_data_api").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

dialect_interface_attributes = {
    "name",
    "driver",
    "positional",
    "paramstyle",
    "convert_unicode",
    "encoding",
    "statement_compiler",
    "ddl_compiler",
    "server_version_info",
    "default_schema_name",
    "execution_ctx_cls",
    "execute_sequence_format",
    "preparer",
    "supports_alter",
    "max_identifier_length",
    "supports_unicode_statements",
    "supports_unicode_binds",
    "supports_sane_rowcount",
    "supports_sane_multi_rowcount",
    "preexecute_autoincrement_sequences",
    "implicit_returning",
    "colspecs",
    "supports_default_values",
    "supports_sequences",
    "sequences_optional",
    "supports_native_enum",
    "supports_native_boolean",
    "dbapi_exception_translation_map"
}

dialect_interface_methods = {
    "connect",
    "create_connect_args",
    "create_xid",
    "denormalize_name",
    "do_begin",
    "do_begin_twophase",
    "do_close",
    "do_commit",
    "do_commit_twophase",
    "do_execute",
    "do_execute_no_params",
    "do_executemany",
    "do_prepare_twophase",
    "do_recover_twophase",
    "do_release_savepoint",
    "do_rollback",
    "do_rollback_to_savepoint",
    "do_rollback_twophase",
    "do_savepoint",
    "engine_created",
    "get_check_constraints",
    "get_columns",
    "get_dialect_cls",
    "get_foreign_keys",
    "get_indexes",
    "get_isolation_level",
    "get_pk_constraint",
    "get_table_comment",
    "get_table_names",
    "get_temp_table_names",
    "get_temp_view_names",
    "get_unique_constraints",
    "get_view_definition",
    "get_view_names",
    "has_sequence",
    "has_table",
    "initialize",
    "is_disconnect",
    "normalize_name",
    "reflecttable",
    "reset_isolation_level",
    "set_isolation_level",
    "type_descriptor"
}

BasicBase = declarative_base()
Base = declarative_base()


class Socks(enum.Enum):
    red = 1
    green = 2
    black = 3


class BasicUser(BasicBase):
    __tablename__ = "sqlalchemy_aurora_data_api_test"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    fullname = Column(String(64))
    nickname = Column(String(64))


class User(Base):
    __tablename__ = "sqlalchemy_aurora_data_api_testL"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    doc = Column(JSONB)
    uuid = Column(UUID)
    woke = Column(Boolean, nullable=True)
    nonesuch = Column(Boolean, nullable=True)
    birthday = Column(DATE)
    wakes_up_at = Column(TIME)
    added = Column(TIMESTAMP)
    floated = Column(Float)
    nybbled = Column(LargeBinary)
    friends = Column(ARRAY(String))
    num_friends = Numeric(asdecimal=True)
    num_laptops = Numeric(asdecimal=False)
    first_date = Column(Date)
    note = Column(Text)
    socks = Column(Enum(Socks))


class TestAuroraDataAPI(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        pass

    def test_interface_conformance(self):
        for attr in dialect_interface_attributes:
            self.assertIn(attr, dir(self.engine.dialect))

        for attr in dialect_interface_methods:
            self.assertIn(attr, dir(self.engine.dialect))
            assert callable(getattr(self.engine.dialect, attr))


class TestAuroraDataAPIPostgresDialect(TestAuroraDataAPI):
    dialect = "postgresql+auroradataapi://"
    # dialect = "postgresql+psycopg2://" + getpass.getuser()

    @classmethod
    def setUpClass(cls):
        register_dialects()
        cls.db_name = os.environ.get("AURORA_DB_NAME", __name__)
        cls.engine = create_engine(cls.dialect + ':@/' + cls.db_name)

    def test_execute(self):
        with self.engine.connect() as conn:
            for result in conn.execute("select * from pg_catalog.pg_tables"):
                print(result)

    def test_orm(self):
        uuid = uuid4()
        doc = {'foo': [1, 2, 3]}
        blob = b"0123456789ABCDEF" * 1024
        friends = ["Scarlett O'Hara", 'Ada "Hacker" Lovelace']
        Base.metadata.create_all(self.engine)
        added = datetime.datetime.now()
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname', doc=doc, uuid=str(uuid), woke=True,
                       birthday=datetime.datetime.fromtimestamp(0), added=added, floated=1.2, nybbled=blob,
                       friends=friends, num_friends=500, num_laptops=9000, first_date=added, note='note',
                       socks=Socks.red)
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.query(User).delete()
        session.commit()

        session.add(ed_user)
        self.assertEqual(session.query(User).filter_by(name='ed').first().name, "ed")
        session.commit()
        self.assertGreater(session.query(User).filter(User.name.like('%ed')).count(), 0)
        u = session.query(User).filter(User.name.like('%ed')).first()
        self.assertEqual(u.doc, doc)
        self.assertEqual(u.woke, True)
        self.assertEqual(u.nonesuch, None)
        self.assertEqual(u.birthday, datetime.date.fromtimestamp(0))
        self.assertEqual(u.added, added)
        self.assertEqual(u.floated, 1.2)
        self.assertEqual(u.nybbled, blob)
        self.assertEqual(u.friends, friends)
        self.assertEqual(u.num_friends, 500)
        self.assertEqual(u.num_laptops, 9000)
        self.assertEqual(u.first_date, added.date())
        self.assertEqual(u.note, 'note')
        self.assertEqual(u.socks, Socks.red)

        u.socks = Socks.green
        session.commit()

        session2 = Session()
        u2 = session2.query(User).filter(User.name.like('%ed')).first()
        self.assertEqual(u2.socks, Socks.green)

    def test_timestamp_microsecond_padding(self):
        ts = '2019-10-31 09:37:17.3186'
        processor = _ADA_TIMESTAMP.result_processor(_ADA_TIMESTAMP, None, None)
        self.assertEqual(processor(ts), datetime.datetime.fromisoformat(ts.ljust(26, "0")))


class TestAuroraDataAPIMySQLDialect(TestAuroraDataAPI):
    dialect = "mysql+auroradataapi://"

    @classmethod
    def setUpClass(cls):
        register_dialects()
        cls.db_name = os.environ.get("AURORA_DB_NAME", __name__)
        cls.engine = create_engine(cls.dialect + ':@/' + cls.db_name + "?charset=utf8mb4")

    def test_execute(self):
        with self.engine.connect() as conn:
            for result in conn.execute("select * from information_schema.tables"):
                print(result)

    def test_orm(self):
        BasicBase.metadata.create_all(self.engine)
        ed_user = BasicUser(name='ed', fullname='Ed Jones', nickname='edsnickname')
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.query(BasicUser).delete()
        session.commit()

        session.add(ed_user)
        self.assertEqual(session.query(BasicUser).filter_by(name='ed').first().name, "ed")
        session.commit()
        self.assertGreater(session.query(BasicUser).filter(BasicUser.name.like('%ed')).count(), 0)
        u = session.query(BasicUser).filter(BasicUser.name.like('%ed')).first()
        self.assertEqual(u.nickname, "edsnickname")


if __name__ == "__main__":
    unittest.main()
