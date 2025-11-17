from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.sessions import router as sessions_router
from app.api.roles import router as roles_router


from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title='Authentication as a Service'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
app.include_router(roles_router, prefix="/roles")
app.include_router(sessions_router, prefix="/sessions")