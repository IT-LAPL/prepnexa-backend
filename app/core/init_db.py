import asyncio

from app.core.database import engine, Base
from app.models import (
    exam,
    file,
    predicted_paper,
    processed_text,
    question_topic,
    question,
    upload,
    user,
)  # noqa: F401 (important)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
