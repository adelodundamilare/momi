
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.endpoints import auth, account, utility, ingredient, formula, trend, chat, commercial_workflow, news_feed, insight_portal, supplier, marketing
from fastapi.exceptions import RequestValidationError
from app.middleware.exceptions import global_exception_handler
import logging

logging.basicConfig(level=logging.INFO)

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
app.include_router(trend.router, prefix="/trends", tags=["trends"])
app.include_router(news_feed.router, prefix="/news-feed", tags=["news_feed"])
app.include_router(ingredient.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(formula.router, prefix="/formulas", tags=["formulas"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(commercial_workflow.router, prefix="/commercial-workflow", tags=["commercial_workflow"])
app.include_router(insight_portal.router, prefix="/insight-portal", tags=["insight_portal"])
app.include_router(supplier.router, prefix="/suppliers", tags=["suppliers"])
app.include_router(marketing.router, tags=["marketing"])
app.include_router(utility.router, prefix="/utility", tags=["utility"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)