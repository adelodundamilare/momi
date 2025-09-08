
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.endpoints import auth, account, utility, ingredient, formula, trend, chat, ai_insight
from fastapi.exceptions import RequestValidationError
from app.middleware.exceptions import global_exception_handler


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(account.router, prefix="/account", tags=["account"])
app.include_router(utility.router, prefix="/utility", tags=["utility"])
app.include_router(ingredient.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(formula.router, prefix="/formulas", tags=["formulas"])
app.include_router(trend.router, prefix="/trends", tags=["trends"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(ai_insight.router, prefix="/insights", tags=["insights"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)