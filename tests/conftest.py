from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from fastapi_sqlalchemy_crud.database import init_db
from fastapi_sqlalchemy_crud.server import get_sess

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@pytest.fixture
def configured_base():
    class Base(DeclarativeBase):
        pass

    class Author(Base):
        __tablename__ = "author"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column()
        books: Mapped[list[Book]] = relationship(back_populates="author")

    class Book(Base):
        __tablename__ = "book"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column()
        author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
        author: Mapped[Author] = relationship(back_populates="books")

    return Base, Author, Book


@pytest.fixture
def db_session(tmp_path: Path, configured_base) -> Generator[Session, None, None]:
    Base, Author, Book = configured_base
    test_engine = create_engine(f"sqlite+pysqlite:///{tmp_path}/db.sqlite")
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    init_db(Base, engine=test_engine, mk_session=SessionTest)

    db_session = SessionTest()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture
def client(db_session, configured_base) -> Generator[TestClient, None, None]:
    from fastapi_sqlalchemy_crud.server import init_server

    Base, Author, Book = configured_base
    app = init_server(Base)
    client = TestClient(app)

    def get_test_sess():
        yield db_session

    app.dependency_overrides[get_sess] = get_test_sess
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
