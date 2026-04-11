from .commands import router as commands_router
from .alarms import router as alarms_router
from .admin import router as admin_router
from .callbacks import router as callbacks_router

__all__ = ["commands_router", "alarms_router", "admin_router", "callbacks_router"]
