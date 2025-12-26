"""
API Package
"""
from . import models_router
from . import platforms_router
from . import workers_router
from . import capture_router
from . import auth_router
from . import kpi_router

__all__ = [
    "models_router",
    "platforms_router",
    "workers_router",
    "capture_router",
    "auth_router",
    "kpi_router"
]
