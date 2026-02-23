from asyncio import sleep
from typing import Optional

from aiohttp import ClientError, ClientSession


class HttpRequestClient:
    """HTTP client with exponential backoff retry logic"""

    def __init__(self):
        self.session: Optional[ClientSession] = None

    async def initialize(self):
        """Initialize the HTTP session"""
        if not self.session or self.session.closed:
            self.session = ClientSession()

    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def send_with_backoff(
        self,
        url: str,
        data: dict,
        retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> int:
        """Send POST request with exponential backoff retry"""
        if not self.session or self.session.closed:
            raise RuntimeError("Session not initialized. Call initialize() first.")

        last_exception: Optional[Exception] = None

        for attempt in range(retries):
            try:
                status = await self._post(url, data)

                if 200 <= status < 300:
                    return status

                if status >= 500:
                    wait_time = backoff_factor**attempt
                    print(
                        f"Server error {status}. Retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{retries})"
                    )
                    await sleep(wait_time)
                    continue

                if 400 <= status < 500:
                    raise ValueError(f"Client error: {status}")

            except ClientError as e:
                last_exception = e
                wait_time = backoff_factor**attempt
                print(
                    f"Network error: {e}. Retrying in {wait_time}s... "
                    f"(attempt {attempt + 1}/{retries})"
                )
                await sleep(wait_time)

        error_msg = f"Failed after {retries} attempts"
        if last_exception:
            raise ConnectionError(f"{error_msg}: {last_exception}") from last_exception

        raise ConnectionError(error_msg)

    async def _post(self, url: str, data: dict) -> int:
        """Execute POST request and return status code"""
        async with self.session.post(url, json=data) as response:
            return response.status
