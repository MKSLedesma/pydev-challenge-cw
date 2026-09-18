from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PharmaMetricSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company: str = Field(..., description="Nombre del laboratorio")
    ticker: str = Field(..., description="Ticker")
    main_share_price: Optional[float] = None
    currency: Optional[str] = "USD"
    market_cap: Optional[float] = None
    week_52_price_change: Optional[float] = None
    extracted_at_utc: datetime