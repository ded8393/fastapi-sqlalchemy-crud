from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from sqlalchemy.orm import DeclarativeBase, registry

if TYPE_CHECKING:
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
    from pydantic import BaseModel

reg = registry()


class Base(DeclarativeBase):
    registry = reg
    # added in serializers.py
    __marshmallow__: ClassVar[type[SQLAlchemyAutoSchema]]
    __pydantic__: ClassVar[type[BaseModel]]
    __pydantic_put__: ClassVar[type[BaseModel]]


def get_tablename_model_mapping() -> dict[str, type[Base]]:
    registry = Base.registry._class_registry
    models = [cast(type[Base], m) for k, m in registry.items() if not k.startswith("_")]
    tablename_model_mapping = {m.__tablename__: m for m in models}
    return tablename_model_mapping
