import os, sys, json, unittest, logging, uuid

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa

import sqlalchemy_aurora_data_api

logging.basicConfig(level=logging.INFO)
logging.getLogger("aurora_data_api").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

Base = declarative_base()


class User(Base):
    __tablename__ = "sqlalchemy_aurora_data_api_test"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


class TestAuroraDataAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sqlalchemy_aurora_data_api.register_dialects()
        cls.db_name = os.environ.get("AURORA_DB_NAME", __name__)
        cls.engine = create_engine('postgresql+auroradataapi://:@/' + cls.db_name)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_execute(self):
        with self.engine.connect() as conn:
            for result in conn.execute("select * from pg_catalog.pg_tables"):
                print(result)

    def test_orm(self):
        Base.metadata.create_all(self.engine)
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add(ed_user)
        self.assertEqual(session.query(User).filter_by(name='ed').first().name, "ed")
        session.commit()
        self.assertGreater(session.query(User).filter(User.name.like('%ed')).count(), 0)


if __name__ == "__main__":
    unittest.main()
