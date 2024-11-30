import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class IntIdPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class CreateUpdateDateMixin:
    created_date: Mapped[datetime.date] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    event_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
