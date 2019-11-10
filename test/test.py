import os, sys, json, unittest, logging, datetime, getpass
from uuid import uuid4

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSONB, DATE, TIME, TIMESTAMP, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa

from sqlalchemy_aurora_data_api import register_dialects, _ADA_TIMESTAMP

logging.basicConfig(level=logging.INFO)
logging.getLogger("aurora_data_api").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

BasicBase = declarative_base()
Base = declarative_base()


class BasicUser(BasicBase):
    __tablename__ = "sqlalchemy_aurora_data_api_test"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


class User(Base):
    __tablename__ = "sqlalchemy_aurora_data_api_testI"

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


class TestAuroraDataAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_dialects()
        cls.db_name = os.environ.get("AURORA_DB_NAME", __name__)
        cls.engine = create_engine(cls.dialect + ':@/' + cls.db_name)

    @classmethod
    def tearDownClass(cls):
        pass


class TestAuroraDataAPIPostgresDialect(TestAuroraDataAPI):
    dialect = "postgresql+auroradataapi://"
    # dialect = "postgresql+psycopg2://" + getpass.getuser()

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
                       friends=friends)
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

    def test_timestamp_microsecond_padding(self):
        ts = '2019-10-31 09:37:17.3186'
        processor = _ADA_TIMESTAMP.result_processor(_ADA_TIMESTAMP, None, None)
        self.assertEqual(processor(ts), datetime.datetime.fromisoformat(ts.ljust(26, "0")))


class TestAuroraDataAPIMySQLDialect(TestAuroraDataAPI):
    dialect = "mysql+auroradataapi://"

    def test_execute(self):
        with self.engine.connect() as conn:
            for result in conn.execute("select * from information_schema.tables"):
                print(result)

    def test_orm(self):
        BasicBase.metadata.create_all(self.engine)
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.query(User).delete()
        session.commit()

        session.add(ed_user)
        self.assertEqual(session.query(User).filter_by(name='ed').first().name, "ed")
        session.commit()
        self.assertGreater(session.query(User).filter(User.name.like('%ed')).count(), 0)
        u = session.query(User).filter(User.name.like('%ed')).first()
        self.assertEqual(u.nickname, "edsnickname")


if __name__ == "__main__":
    unittest.main()
