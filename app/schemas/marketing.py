from pydantic import BaseModel, Field
from typing import List, Optional


class MarketingCopyBase(BaseModel):
    product_name: str
    tagline: str
    key_features: List[str]
    marketing_copy: str
    product_mockup_url: Optional[str] = None


class AIMarketingCopy(BaseModel):
    product_name: str = Field(..., description="A catchy and market-friendly name for the product.")
    tagline: str = Field(..., description="A short, memorable slogan for the product.")
    key_features: List[str] = Field(..., description="A list of 3-5 key selling points or features.", min_items=3, max_items=5)
    marketing_copy: str = Field(..., description="A compelling paragraph of marketing text for the product.")


class MarketingCopyCreate(MarketingCopyBase):
    formula_id: int


class MarketingCopy(MarketingCopyBase):
    id: int
    formula_id: int

    class Config:
        from_attributes = True
