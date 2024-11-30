import re
from typing import Any

from fastapi import Request

from app.core.schemas.base import FilterSchema, SearchSchema


class FilterParameter:
    @classmethod
    async def parse_params(cls, request: Request) -> FilterSchema:
        # Initialize the result with keys from FilterSchema
        filter_result: dict[str, Any] = {key: [] for key in FilterSchema.model_fields}

        # Function to parse the key
        def parse_key(key: str) -> tuple[str, list[str]]:
            pattern = r"^([^\[]+)((?:\[[^\]]+\])*)$"
            m = re.match(pattern, key)
            if m:
                base_key = m.group(1)
                subkeys_str = m.group(2)
                subkeys = re.findall(r"\[([^\]]+)\]", subkeys_str)

                if len(subkeys) == 2 and subkeys[1].isdigit():
                    del subkeys[1]

                if len(subkeys) > 2:
                    subkeys = subkeys[:2]

                return base_key, subkeys
            return key, []

        # Recursive function to build nested structure
        def build_nested(
            subkeys: list[str],
            value: str,
        ) -> str | dict[str, str | dict[str, str]]:
            if not subkeys:
                return value
            return {"name": subkeys[0], "value": build_nested(subkeys[1:], value)}  # type: ignore

        # Get all key-value pairs, including duplicate keys
        items = request.query_params.multi_items()
        for key, value in items:
            base_key, subkeys = parse_key(key)
            if base_key in filter_result:
                nested_dict = build_nested(subkeys, value)
                filter_result[base_key].append(nested_dict)
        return FilterSchema(**filter_result)


async def search_params(request: Request) -> SearchSchema:
    return await SearchParameter.parse_params(request)


class SearchParameter:
    @classmethod
    async def parse_params(cls, request: Request) -> SearchSchema:
        # Initialize the result with keys from FilterSchema
        search_result: dict[str, Any] = {key: [] for key in SearchSchema.model_fields}

        # Function to parse the key
        def parse_key(key: str) -> tuple[str, list[str]]:
            pattern = r"^([^\[]+)((?:\[[^\]]+\])*)$"
            m = re.match(pattern, key)
            if m:
                base_key = m.group(1)
                subkeys_str = m.group(2)
                subkeys = re.findall(r"\[([^\]]+)\]", subkeys_str)
                if len(subkeys) > 2:
                    subkeys = subkeys[:2]
                return base_key, subkeys
            return key, []

        # Recursive function to build nested structure
        def build_nested(
            subkeys: list[str],
            value: str,
        ) -> str | dict[str, str | dict[str, str]]:
            if not subkeys:
                return value
            return {"name": subkeys[0], "value": build_nested(subkeys[1:], value)}  # type: ignore

        # Get all key-value pairs, including duplicate keys
        items = request.query_params.multi_items()
        for key, value in items:
            base_key, subkeys = parse_key(key)
            if base_key in search_result:
                nested_dict = build_nested(subkeys, value)
                search_result[base_key].append(nested_dict)

        return SearchSchema(**search_result)
