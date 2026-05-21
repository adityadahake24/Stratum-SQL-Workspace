from fastapi import APIRouter
from app.api.v1 import auth, connections, queries, schema, history, undo, support

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(schema.router, prefix="/schema", tags=["schema"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(undo.router, prefix="/undo", tags=["undo"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
