import asyncio
import aiohttp

class AsyncSessionManager:
    _session = None
    _semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent requests
    
    @classmethod
    async def get_session(cls):
        if cls._session is None or cls._session.closed:
            print("Starting async session...\n")
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session:
            print("\nClosing async session...")
            await cls._session.close()
            cls._session = None
    
    @classmethod
    async def request_with_limit(cls, url, retries=0):
        async with cls._semaphore:
            session = await cls.get_session()
            if session:
                async with session.get(url) as response:
                    if response.status == 200:                             
                        session.cookie_jar.clear()
                        
                        # Return JSON response if successful
                        return await response.json()
                    
                    # Check for rate limiting (HTTP 429)
                    if response.status == 429 and retries < 1:
                        retries = retries + 1
                        retry_after = int(response.headers.get("Retry-After", 5))
                        print(f"Rate limited. Retries left: {retries}. Retrying after {retry_after} seconds...")
                        
                        # Close and recycle the session if rate limited
                        session.cookie_jar.clear()
                        await cls.close_session()
                        
                        # Wait before retrying
                        await asyncio.sleep(retry_after)
                        
                        # Retry the request with a new session
                        return await cls.request_with_limit(url, retries)
                    else:
                        raise BaseException({'message': 'Request error.', 'status': response.status, 'reason': response.reason})
           
