import datetime

from sqlalchemy import func, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class IntIdPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class CreateUpdateDateMixin:
    created_date: Mapped[datetime.date] = mapped_column(
        DateTime, server_default=func.now()
    )
    event_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
