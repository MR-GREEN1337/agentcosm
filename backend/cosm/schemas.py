"""
Pydantic schemas for structured outputs
"""

from pydantic import BaseModel, Field
from typing import List


class MarketSignal(BaseModel):
    signal_type: str = Field(description="Type of market signal")
    content: str = Field(description="Signal content")
    source: str = Field(description="Source platform")
    sentiment: str = Field(description="Signal sentiment")
    urgency: str = Field(description="Urgency level")


class CompetitionAnalysis(BaseModel):
    competition_level: str = Field(description="Overall competition level")
    direct_competitors: List[str] = Field(description="List of direct competitors")
    market_gaps: List[str] = Field(description="Identified market gaps")
    competitive_advantages: List[str] = Field(
        description="Potential competitive advantages"
    )


class MarketValidation(BaseModel):
    opportunity_name: str = Field(description="Market opportunity name")
    market_size_estimate: int = Field(description="TAM estimate in USD")
    competition_analysis: CompetitionAnalysis
    demand_strength: float = Field(description="Demand strength score 0-1")
    opportunity_score: float = Field(description="Overall opportunity score 0-1")
    recommendation: str = Field(description="Investment recommendation")
    confidence_level: str = Field(description="Analysis confidence level")


class BrandIdentity(BaseModel):
    brand_name: str = Field(description="Generated brand name")
    tagline: str = Field(description="Brand tagline")
    value_proposition: str = Field(description="Core value proposition")
    positioning_statement: str = Field(description="Market positioning")
    target_audience: str = Field(description="Primary target audience")
    domain_suggestions: List[str] = Field(description="Domain name suggestions")


class MarketingCopy(BaseModel):
    headlines: List[str] = Field(description="Marketing headlines")
    taglines: List[str] = Field(description="Alternative taglines")
    value_propositions: List[str] = Field(description="Value proposition variants")
    hero_headline: str = Field(description="Primary hero headline")
    hero_subheadline: str = Field(description="Supporting subheadline")


class LandingPageAsset(BaseModel):
    page_title: str = Field(description="Page title")
    meta_description: str = Field(description="SEO meta description")
    html_template: str = Field(description="Complete HTML template")
    css_styles: str = Field(description="CSS styling")
    javascript_code: str = Field(description="JavaScript functionality")
    deployment_ready: bool = Field(description="Ready for deployment")


class OpportunityScoring(BaseModel):
    overall_score: float = Field(description="Overall opportunity score 0-1")
    market_attractiveness: float = Field(description="Market attractiveness score")
    competitive_advantage: float = Field(description="Competitive advantage score")
    demand_strength: float = Field(description="Demand validation score")
    execution_feasibility: float = Field(description="Execution feasibility score")
    recommendation: str = Field(description="Strategic recommendation")
    confidence_level: str = Field(description="Scoring confidence")
    next_actions: List[str] = Field(description="Recommended next steps")
