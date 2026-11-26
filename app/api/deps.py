from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated, TypeVar

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.base import Base
from app.gen.engine import Engine
from app.gen.jobs import JobManager


def get_db(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_engine(request: Request) -> Engine:
    engine: Engine = request.app.state.engine
    return engine


def get_jobs(request: Request) -> JobManager:
    jobs: JobManager = request.app.state.jobs
    return jobs


DbSession = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
EngineDep = Annotated[Engine, Depends(get_engine)]
JobsDep = Annotated[JobManager, Depends(get_jobs)]


T = TypeVar("T", bound=Base)


def get_or_404(db: Session, model: type[T], obj_id: int) -> T:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {obj_id} not found")
    return obj
