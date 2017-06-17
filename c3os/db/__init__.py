from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from c3os.objects import region, instance
from c3os.db.pool import DBPool
from c3os import conf

engine = create_engine('sqlite:///c3os.db', echo=False,
                       connect_args={'check_same_thread': False})

conf.Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine, ))
session = Session()

pool = DBPool(session, [instance.Instance, region.Region])


def generate_pool():
    """ Generating a new DBPool class instance """
    engine = create_engine('sqlite:///c3os.db', echo=False,
                           connect_args={'check_same_thread': False})
    conf.Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine, ))
    session = Session()

    return DBPool(session, [instance.Instance, region.Region])
