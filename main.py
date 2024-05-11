import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handlers import user_router

# create instance of the app
app = FastAPI(title="Education-app")


#########################
# BLOCK WITH API ROUTES #
#########################
# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run("main:app", port=8000, reload=True)
