
from fastapi import Query

from core.schemas.base import SortSchema


class SortParameter:

    @classmethod
    async def parse_params(
        cls,
        sort_field: str = Query(default='id'),
        desc: bool = Query(default=True),
        sort_case_ids: str | None = Query(default=None),
    ) -> SortSchema:
        return SortSchema(
            sort_field=sort_field,
            desc=desc,
            sort_case_ids=sort_case_ids,
        )
