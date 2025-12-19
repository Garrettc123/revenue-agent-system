from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Revenue Agent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "operational",
        "service": "Revenue Agent System",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
