import datetime
from typing import Optional

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base
from core.models.mixins.base import IntIdPkMixin, CreateUpdateDateMixin


class User(Base, IntIdPkMixin, CreateUpdateDateMixin):
    __tablename__ = 'user'

    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    avatar: Mapped[str | None]

    soc_type: Mapped[str]
    soc_token: Mapped[str]
    firebase_token: Mapped[str]
    timezone: Mapped[str] = mapped_column(String(length=128), default='UTC')
    is_deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

    def __str__(self):
        return f'#{self.id} {self.email}'

    def __repr__(self):
        return f'User <#{self.id} {self.email}>'
