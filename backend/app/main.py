from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import AnalysisRequest, AnalysisResponse
from .services import build_placeholder_analysis

app = FastAPI(
    title="KPAstroGem API",
    version="0.1.0",
    description="FastAPI backend for the KPAstroGem MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "kp-astro-backend"}


@app.post("/api/kp/analyze", response_model=AnalysisResponse)
async def analyze_kp(payload: AnalysisRequest) -> AnalysisResponse:
    try:
        return build_placeholder_analysis(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

