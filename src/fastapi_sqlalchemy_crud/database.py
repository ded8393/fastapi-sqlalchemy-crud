from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, configure_mappers, sessionmaker

from .models import Base, get_tablename_model_mapping
from .serializers import setup_schema
from .settings import CACHE_DIR, DEBUG

DB_PATH = CACHE_DIR / "db.sqlite"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite+pysqlite:///{DB_PATH}", echo=DEBUG)

SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(engine: Engine = engine, mk_session: sessionmaker[Session] = SessionLocal) -> dict[str, type[Base]]:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    configure_mappers()

    session = mk_session()
    setup_schema(Base, session=session)  # depends on mappers being configured
    session.close()

    return get_tablename_model_mapping()


def get_sess():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
