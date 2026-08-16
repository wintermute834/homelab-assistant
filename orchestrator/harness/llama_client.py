"""
An client that connects to a llama.cpp server and sends/recieves queries.
"""

from typing import Optional

import httpx

from .types.messages import UserMessage
from .types.query import Query
from .types.response import ServerResponse



class ClientError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)



class LlamaClient:
    __slots__ = "url"

    def __init__(self, url: Optional[str] = None) -> None:
        """
        Creates a client to the llama server at the given url.

        If `url` is not specified, it defaults to http://localhost:8080
        """

        self.url = "http://localhost:8080" if url is None else url

    def health(self) -> bool:
        """
        Returns the health of the llama.cpp server, `True` when the server is running `False` otherwise.
        """

        try:
            response = httpx.get(f"{self.url}/health")
            response.raise_for_status()

            return response.text == "{\"status\":\"ok\"}"
        
        except httpx.HTTPError:
            return False


    def query(self, query: Query) -> ServerResponse:
        """
        Sends a `Query` to the given model on the server and returns the response.

        Can throw an `httpx.HTTPError` or `ClientError`.
        """

        response = httpx.post(
            f"{self.url}/v1/chat/completions",
            headers = {"Content-Type": "application/json"},
            json = query.model_dump(exclude_none=True),
            timeout = httpx.Timeout(10, read=None) # unlimited read time because model can take long times
        )
        response.raise_for_status()

        server_response = ServerResponse(**response.json())

        if len(server_response.choices) == 0:
            raise ClientError("Error: Server response didn't include any completion options.")

        else:
            return server_response


    def get_response(self, model: str, message: str) -> str:
        """
        Sends a single message to a model and returns the response in plain text.

        Output doesn't include the reasoning and the model doesn't have access to any tools.

        Can throw an `httpx.HTTPError` or `ClientError`.
        """

        response = self.query(Query(
            model = model,
            messages = [
                UserMessage(
                    content = message
                )
            ]
        ))
        
        return response.choices[0].message.content

