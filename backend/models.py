from pydantic import BaseModel, Field
from typing import Optional, List

class CampaignGoal(BaseModel):
    objective: str = Field(description="The primary objective of the digital marketing campaign")
    budget: float = Field(description="Total budget available for the campaign in USD")
    industry: str = Field(description="The client's industry")
    target_audience: str = Field(description="Primary target demographic")
    website_url: Optional[str] = Field(default="", description="Target website to generate/analyze")
    brand_context: Optional[str] = Field(default="", description="Visual brand aesthetics and tone")
    brand_color: Optional[str] = Field(default="#6C63FF", description="Primary brand HEX color")
    secondary_color: Optional[str] = Field(default="#FF6584", description="Secondary brand HEX color")
    logo_data: Optional[str] = Field(default="", description="Base64 encoded logo image data")
    target_pages: Optional[List[str]] = Field(default=[], description="Specific pages to generate")
