"""
main.py

This script serves as the entry point for the Education-app FastAPI application.

It initializes the FastAPI instance, sets up the main API router, includes various
sub-routers for handling different endpoints, and runs the FastAPI application using
the Uvicorn server.

Usage:
    Run this script to start the FastAPI application.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handlers import user_router
from api.login_handler import login_router
from api.service import service_router

# create instance of the app
app = FastAPI(title="User Power")

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
main_api_router.include_router(service_router, tags=["service"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run("main:app", port=8000, reload=True)
