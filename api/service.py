"""
service.py

This module provides API routes for service-related endpoints in the Education-app API.
"""
from fastapi import APIRouter

service_router = APIRouter()


@service_router.get("/ping")
async def ping():
    """
    Endpoint to check if the service is running.

    Returns:
        dict: A dictionary indicating success.
    """
    return {"Success": True}
