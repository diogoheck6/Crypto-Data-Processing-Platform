from fastapi import FastAPI

from src.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Crypto Data Processing Platform",
        description="Financial transaction processing engine for cryptocurrency data.",
        version="0.1.0",
        debug=settings.debug,
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
