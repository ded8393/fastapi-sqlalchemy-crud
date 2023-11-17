from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fastapi_sqlalchemy_crud.database import init_db
from fastapi_sqlalchemy_crud.server import get_sess


@pytest.fixture
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    test_engine = create_engine(f"sqlite+pysqlite:///{tmp_path}/db.sqlite")
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    init_db(engine=test_engine, mk_session=SessionTest)

    db_session = SessionTest()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    from fastapi_sqlalchemy_crud.server import app

    client = TestClient(app)

    def get_test_sess():
        yield db_session

    app.dependency_overrides[get_sess] = get_test_sess
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
