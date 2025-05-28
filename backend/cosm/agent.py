"""
Market Opportunity Discovery Agent
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from google.genai import types
from datetime import datetime

# Import existing agents
from .discovery.explorer_agent import market_explorer_agent
from .discovery.trend_analyzer import trend_analyzer_agent
from .discovery.gap_mapper import gap_mapper_agent
from .analysis import market_analyzer_agent
from .analysis.code_executor import code_executor_agent
from .analysis.opportunity_scorer import opportunity_scorer_agent
from .builder import brand_creator_agent, landing_builder_agent, copy_writer_agent

# Import BigQuery agen
from .analysis.bigquery_agent import create_bigquery_agent

from .settings import settings

from .tools.market_research import (
    comprehensive_market_research,
    analyze_competitive_landscape,
    check_domain_availability,
)
from .prompts import ROOT_AGENT_PROMPT
from .config import MODEL_CONFIG


def setup_market_context(callback_context: CallbackContext):
    """Setup market research context and shared state"""
    if "market_context" not in callback_context.state:
        callback_context.state["market_context"] = {
            "research_timestamp": datetime.now().isoformat(),
            "data_sources": [],
            "validation_criteria": {},
            "research_pipeline": {},
            "bigquery_enabled": True,  # NEW: Enable BigQuery features
        }

    if "research_results" not in callback_context.state:
        callback_context.state["research_results"] = {
            "market_signals": [],
            "trend_analysis": {},
            "gap_analysis": {},
            "validation_data": {},
            "opportunity_scores": {},
            "business_assets": {},
            "bigquery_insights": {},  # NEW: Store BigQuery results
        }


class MarketOpportunityAgent:
    """
    Root agent with BigQuery intelligence
    """

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID

        # Create BigQuery agent
        self.bigquery_agent = create_bigquery_agent()

        # Phase 1: Discovery (Parallel)
        self.discovery_phase = LlmAgent(
            name="market_discovery_phase",
            model=MODEL_CONFIG["primary_model"],
            description="Discovers market signals from multiple sources in parallel",
            sub_agents=[
                market_explorer_agent,
                trend_analyzer_agent,
                gap_mapper_agent,
            ],
        )

        # Phase 2: Enhanced Analysis with BigQuery (Sequential)
        self.analysis_phase = SequentialAgent(
            name="market_analysis_phase",
            description="Performs deep analysis including BigQuery intelligence",
            sub_agents=[
                market_analyzer_agent,
                self.bigquery_agent,
                code_executor_agent,
                opportunity_scorer_agent,
            ],
        )

        # Phase 3: Business Asset Creation (Parallel)
        self.builder_phase = LlmAgent(
            name="business_builder_phase",
            model=MODEL_CONFIG["primary_model"],
            description="Creates business assets for rapid market validation",
            sub_agents=[
                brand_creator_agent,
                copy_writer_agent,
                landing_builder_agent,
            ],
        )

        # Root orchestrator
        self.root_agent = LlmAgent(
            name="market_opportunity_coordinator",  # Keep internal name
            model=MODEL_CONFIG["primary_model"],
            instruction=(
                ROOT_AGENT_PROMPT
                + "\n\nYou are a strategic co-founder helping the user discover and build their next billion-dollar idea. "
                "Use advanced data and insights without revealing internal tools or technical details."
            ),
            description=(
                "Acts as a co-founder that helps the user uncover high-potential ideas and turn them into testable ventures, "
                "leveraging deep data signals without surfacing implementation specifics."
            ),
            before_agent_callback=setup_market_context,
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
            ),
            tools=[
                FunctionTool(func=comprehensive_market_research),
                FunctionTool(func=analyze_competitive_landscape),
                FunctionTool(func=check_domain_availability),
                AgentTool(agent=self.discovery_phase),
                AgentTool(agent=self.analysis_phase),
                AgentTool(agent=self.builder_phase),
            ],
            sub_agents=[self.discovery_phase, self.analysis_phase, self.builder_phase],
        )


root_agent = MarketOpportunityAgent().root_agent
