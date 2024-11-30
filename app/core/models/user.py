from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base
from app.core.models.mixins.base import CreateUpdateDateMixin, IntIdPkMixin


class User(Base, IntIdPkMixin, CreateUpdateDateMixin):
    __tablename__ = "user"

    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    avatar: Mapped[str | None]

    soc_type: Mapped[str]
    soc_token: Mapped[str]
    firebase_token: Mapped[str]
    timezone: Mapped[str] = mapped_column(String(length=128), default="UTC")
    is_deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

    def __str__(self) -> str:  # type: ignore[no-untyped-def]
        return f"#{self.id} {self.email}"

    def __repr__(self) -> str:  # type: ignore[no-untyped-def]
        return f"User <#{self.id} {self.email}>"
