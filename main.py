from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_session, init_db
from schemas import CheckRequest, CheckResponse
from services import run_full_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создаёт таблицы при старте, закрывает движок при остановке."""
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="Anti-Fraud API",
    description="Скоринг и проверка пользователей по email и IP",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/v1/health")
async def health() -> dict:
    """Простой healthcheck."""
    return {"status": "ok"}


@app.post("/api/v1/check", response_model=CheckResponse)
async def check(
    payload: CheckRequest,
    session: AsyncSession = Depends(get_session),
) -> CheckResponse:
    """Проверяет email + IP, возвращает фрод-скор и вердикт."""
    result = await run_full_check(
        email=payload.email,
        ip_address=str(payload.ip_address),
        session=session,
    )
    return result