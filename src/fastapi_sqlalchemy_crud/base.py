from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from sqlalchemy.orm import DeclarativeBase, registry

if TYPE_CHECKING:
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
    from pydantic import BaseModel


def configure_base(base: type[DeclarativeBase]) -> type[DeclarativeBase]:
    """Configure base model with registry and serializer properties."""
    base.registry = registry()
    base.__marshmallow__: type[SQLAlchemyAutoSchema] = None
    base.__pydantic__: ClassVar[type[BaseModel]] = None
    base.__pydantic_put__: ClassVar[type[BaseModel]] = None

    return base


def get_tablename_model_mapping(base: type[DeclarativeBase]) -> dict[str, type[DeclarativeBase]]:
    registry = base.registry._class_registry
    models = [cast(type[base], m) for k, m in registry.items() if not k.startswith("_")]
    tablename_model_mapping = {m.__tablename__: m for m in models}
    return tablename_model_mapping
