"""
Market Opportunity Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from google.genai import types

from .discovery.explorer_agent import (
    market_explorer_agent,
)  # Now includes trend analysis + gap mapping
from .analysis import market_analyzer_agent  # Now includes opportunity scoring
from .analysis.data_intelligence import (
    data_intelligence_agent,
)  # Now includes BigQuery functionality
from .builder import (
    brand_creator_agent,
    landing_builder_agent,
)  # Brand creator now includes copy writing

from .settings import settings
from .tools.market_research import (
    comprehensive_market_research,
    analyze_competitive_landscape,
    check_domain_availability,
)
from .prompts import ROOT_AGENT_PROMPT
from .config import MODEL_CONFIG


class MarketOpportunityAgent:
    """
    Root agent with streamlined 2-phase processing
    Reduced complexity while maintaining comprehensive market intelligence
    """

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID

        # PHASE 1: Market Intelligence (Parallel Processing)
        # Consolidated discovery + analysis for speed
        self.intelligence_phase = LlmAgent(
            name="market_intelligence_phase",
            model=MODEL_CONFIG["primary_model"],
            description="Consolidated market intelligence combining discovery, analysis, and validation",
            sub_agents=[
                market_explorer_agent,  # Now includes: explorer + trend analyzer + gap mapper
                market_analyzer_agent,  # Now includes: analyzer + opportunity scorer
                data_intelligence_agent,  # Now includes: BigQuery + code executor
            ],
        )

        # PHASE 2: Asset Creation (Parallel Processing)
        # Streamlined brand and deployment creation
        self.creation_phase = LlmAgent(
            name="asset_creation_phase",
            model=MODEL_CONFIG["primary_model"],
            description="Rapid creation of brand assets and deployable business validation tools",
            sub_agents=[
                brand_creator_agent,
                landing_builder_agent,
            ],
        )

        self.root_agent = LlmAgent(
            name="market_opportunity_coordinator",
            model=MODEL_CONFIG["primary_model"],
            instruction=(
                ROOT_AGENT_PROMPT
                + "\n\n for efficiency: You now orchestrate a streamlined 2-phase process that "
                "delivers comprehensive market intelligence and deployable business assets faster than ever. "
                "Each phase runs agents with consolidated capabilities, eliminating redundancy "
                "while maintaining analytical depth and strategic insight quality."
            ),
            description=(
                "Market opportunity coordinator that efficiently transforms market uncertainty "
                "into validated business opportunities using streamlined 2-phase processing with consolidated agents."
            ),
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
            ),
            tools=[
                FunctionTool(func=comprehensive_market_research),
                FunctionTool(func=analyze_competitive_landscape),
                FunctionTool(func=check_domain_availability),
                AgentTool(agent=self.intelligence_phase),
                AgentTool(agent=self.creation_phase),
            ],
            sub_agents=[self.intelligence_phase, self.creation_phase],
        )


# Export root agent
root_agent = MarketOpportunityAgent().root_agent
