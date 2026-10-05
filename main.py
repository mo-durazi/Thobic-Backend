import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Controllers
from controllers.users import router as UsersRouter
from controllers.profiles import router as ProfilesRouter
from controllers.client_measurements import router as ClientMeasurementsRouter
from controllers.materials import router as MaterialsRouter
from controllers.admin import router as AdminRouter
from controllers.material_order import router as MaterialOrderRouter

tags_metadata = [
    {"name": "Auth", "description": "Register, login, current user"},
    {"name": "Admin", "description": "Admin creates tailor and provider accounts"},
    {"name": "Profiles", "description": "User and shop profiles"},
    {"name": "Client Measurements", "description": "Client's single measurement set"},
    {"name": "Materials", "description": "Shop and provider materials"},
    {"name": "Material Orders", "description": "Provider accepts/rejects/ships, tailor marks delivered"},
]

app = FastAPI(
    title="Thobic API",
    description="API for Thobic, a platform for managing orders and materials.",
    version="1.0.0",
    openapi_tags= tags_metadata,
)


# Allow your React dev server(s) to call the API
origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes
app.include_router(UsersRouter, prefix="/api", tags = ["Auth"])
app.include_router(AdminRouter, prefix="/api", tags = ["Admin"])
app.include_router(ProfilesRouter, prefix="/api", tags = ["Profiles"])
app.include_router(ClientMeasurementsRouter, prefix="/api", tags = ["Client Measurements"])
app.include_router(MaterialsRouter, prefix="/api", tags = ["Materials"])
app.include_router(MaterialOrderRouter, prefix="/api", tags = ["Material Orders"])

@app.get("/health")
def health_check():
    return {"message": "Api is running"}