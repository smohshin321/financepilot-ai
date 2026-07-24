import asyncio
import sys

from app.core.database import database_is_ready, get_engine


async def main() -> int:
    for attempt in range(1, 31):
        if await database_is_ready(get_engine()):
            print("PostgreSQL is ready.")
            await get_engine().dispose()
            return 0
        print(f"Waiting for PostgreSQL ({attempt}/30)...")
        await asyncio.sleep(1)
    await get_engine().dispose()
    print("PostgreSQL did not become ready in time.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
