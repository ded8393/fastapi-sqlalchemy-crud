from typing import Any

import rich.traceback
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_sess, init_db
from .models import Base

rich.traceback.install()

app = FastAPI()

cors = Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.user_middleware.insert(0, cors)


@app.get("/")
async def root():
    return {"message": "Hello World"}


def update_model(model: Base, item: Base, data: dict[str, Any], session: Session):
    # marshmallow loads nested items as model objects, which can be set on model
    serializer = model.__marshmallow__(session=session)
    m_item: Base = serializer.load(data)
    for field in data:
        setattr(item, field, getattr(m_item, field))
    return item


def register_model(table_name: str, model: type[Base]):
    @app.get(
        f"/{table_name}",
        response_model=list[model.__pydantic__],
        summary=f"Get all {table_name}s",
    )
    def _get_all(session: Session = Depends(get_sess)):
        with session.begin():
            data = session.query(model).all()
            return [model.__pydantic__.model_validate(d) for d in data]

    @app.get(
        f"/{table_name}/{{id}}",
        response_model=model.__pydantic__,
        summary=f"Get a {table_name} by ID",
    )
    def _get_by_id(id: str | int, session: Session = Depends(get_sess)):
        with session.begin():
            item = session.get(model, id)
            if item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {table_name} with ID {id}")
            return model.__pydantic__.model_validate(item)

    # TODO: allow many?
    @app.post(
        f"/{table_name}",
        response_model=model.__pydantic__,
        summary=f"Create a {table_name}",
        status_code=status.HTTP_201_CREATED,
    )
    def _create(
        data: model.__pydantic_put__,
        session: Session = Depends(get_sess),
    ):
        with session.begin():
            serializer = model.__marshmallow__(session=session)
            item: Base = serializer.load(data.model_dump())
            session.add(item)
            session.flush()
            resp = model.__pydantic__.model_validate(item)
            session.commit()
        return resp

    @app.put(
        f"/{table_name}/{{id}}",
        response_model=model.__pydantic__,
        summary=f"Add or Update a {table_name}",
        status_code=status.HTTP_200_OK,
    )
    def _put(
        id: str | int,
        data: model.__pydantic_put__,  # NB: cannot use PUT for `IdMixin`-derived models
        response: Response,
        session: Session = Depends(get_sess),
    ):
        with session.begin():
            if id != data.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"routing ID {id} does not match ID in data {data.id}")
            # https://docs.sqlalchemy.org/en/20/orm/contextual.html#sqlalchemy.orm.scoped_session.get
            if item := session.get(model, id):
                update_model(model, item, data.model_dump(), session)
            else:
                item = model(**data.model_dump())
                response.status_code = status.HTTP_201_CREATED
            session.add(item)
            session.flush()
            resp = model.__pydantic__.model_validate(item)
            session.commit()
        return resp

    @app.patch(
        f"/{table_name}/{{id}}",
        response_model=model.__pydantic__,
        status_code=status.HTTP_200_OK,
        summary=f"Update a {table_name}",
    )
    def _patch(
        id: str | int,
        data: dict[str, Any],
        session: Session = Depends(get_sess),
    ):
        with session.begin():
            if not (item := session.get(model, id)):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {table_name} with ID {id}")

            update_model(model, item, {**data, "id": id}, session)
            session.add(item)
            session.flush()
            resp = model.__pydantic__.model_validate(item)
            session.commit()
        return resp


table_name2model = init_db()
for table_name, model in table_name2model.items():
    register_model(table_name, model)
