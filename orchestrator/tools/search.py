
from typing import Iterable, Optional, cast

import googlesearch
from pydantic import BaseModel

from llama_client import Tool




class SearchResult(BaseModel):
    url: str
    title: str
    description: Optional[str] = None




def _search(*, query: str, num_results: int = 10, description: bool = False) -> list[SearchResult]:
    return [] if num_results <= 0 else [
        SearchResult(
            url=url.url,
            title=url.title,
            description=url.description if description else None
        )
        for url in cast(Iterable[SearchResult], googlesearch.search(query, min(25, num_results), advanced=True, unique=True))
    ]


def _get_url(*, url: str) -> str:
    # TODO: implement the fetching of data from a url and possible parsing using beautiful soup
    return ""



search = Tool(**{
    "definition": {
        "function": {
            "name": "search",
            "description": "Searches the internet for the given query, returning the titles, urls, and optional descriptions.",
            "parameters": {
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query that will be searched."
                    },
                    "num_results": {
                        "type": "number",
                        "description": "The number of results to be returned. Clamped to a maximum of 25."
                    },
                    "description": {
                        "type": "boolean",
                        "description": "Whether or not to include the description of each web page."
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },
    "function": _search
})

