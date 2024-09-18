import re
from typing import Optional

from fastapi import Request, Query

from core.schemas.base import FilterSchema, SearchSchema


class FilterParameter:

    @classmethod
    async def parse_params(cls, request: Request) -> FilterSchema:
        query_params = dict(request.query_params)
        filter_result = {}
        for parameter in FilterSchema.model_fields.keys():
            filters = [
                {'name': re.search(r"\[(.*?)\]", k).group(1), 'value': v}  # type: ignore
                for k, v in query_params.items() if f'{parameter}[' in k
            ]
            filter_result[parameter] = filters
        return FilterSchema(**filter_result)


async def search_params(search_fields: Optional[list[str]] = Query(None, alias='search_fields[]'), query: Optional[str] = Query(None),) -> SearchSchema:
    return SearchSchema(
        fields=search_fields,
        query=query,
    )
