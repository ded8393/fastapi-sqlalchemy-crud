from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, configure_mappers, sessionmaker

from .base import configure_base, get_tablename_model_mapping
from .serializers import setup_schema
from .settings import CACHE_DIR, DEBUG

DB_PATH = CACHE_DIR / "db.sqlite"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine_url = f"sqlite+pysqlite:///{DB_PATH}"
engine = create_engine(engine_url, echo=DEBUG)


def get_sessionmaker(engine: Engine = engine, *, autocommit: bool = False, autoflush: bool = False) -> sessionmaker[Session]:
    SessionLocal: sessionmaker[Session] = sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=engine)
    return SessionLocal


def init_db(
    base: type[DeclarativeBase], engine: Engine = engine, mk_session: sessionmaker[Session] | None = None
) -> dict[str, type[DeclarativeBase]]:
    configure_base(base)
    if mk_session is None:
        mk_session = get_sessionmaker(engine)
    base.metadata.create_all(bind=engine, checkfirst=True)
    configure_mappers()

    session = mk_session()
    setup_schema(base, session=session)  # depends on mappers being configured
    session.close()

    return get_tablename_model_mapping(base)


def get_sess():
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
