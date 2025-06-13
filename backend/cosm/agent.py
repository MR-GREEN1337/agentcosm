"""
Enhanced Market Opportunity Agent with True Liminal Discovery
Uses ADK Multi-Agent Patterns for Breakthrough Opportunity Finding
"""

from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool, LongRunningFunctionTool
from google.genai import types

from cosm.utils import ResilientLlmAgent

from .discovery import (
    market_explorer_agent,
    adjacent_market_agent,
    cross_industry_agent,
    connection_synthesizer_agent,
)

from .analysis import market_analyzer_agent
from .analysis.data_intelligence import data_intelligence_agent

from .builder import (
    brand_creator_agent,
    landing_builder_agent,
)

from cosm.startup_pitch import startup_pitch_agent
from .tools.market_research import (
    comprehensive_market_research,
    analyze_competitive_landscape,
    check_domain_availability,
)
from .tools.liminal_discovery import (
    synthesize_liminal_connections,
    validate_connection_strength,
    rank_liminal_opportunities,
)
from .prompts import ROOT_AGENT_PROMPT
from .config import MODEL_CONFIG

from .tools.search import search_tool


class MarketOpportunityAgent:
    """
    Enhanced root agent with true liminal market discovery using ADK multi-agent patterns.

    Architecture:
    1. PARALLEL LIMINAL DISCOVERY: Multiple agents explore different market dimensions simultaneously
    2. CONNECTION SYNTHESIS: Specialized agent finds breakthrough connections between markets
    3. VALIDATION & SCORING: Analysis agents validate and score discovered opportunities
    4. ASSET CREATION: Builder agents create deployable business validation tools

    This finds Uber/Airbnb-style opportunities that exist between established markets.
    """

    def __init__(self):
        # PHASE 1: PARALLEL LIMINAL DISCOVERY
        # Uses ADK ParallelAgent to explore multiple market dimensions simultaneously
        self.liminal_discovery_phase = ParallelAgent(
            name="liminal_discovery_phase",
            description="Parallel exploration of market dimensions to find liminal opportunities",
            sub_agents=[
                market_explorer_agent,  # Primary market signals & pain points
                adjacent_market_agent,  # Adjacent/complementary markets
                cross_industry_agent,  # Cross-industry patterns & arbitrage
                connection_synthesizer_agent,  # Synthesize parallel discoveries
            ],
        )

        # PHASE 2: CONNECTION SYNTHESIS
        # Specialized agent that finds breakthrough connections between parallel discoveries
        self.connection_synthesis_phase = ResilientLlmAgent(
            name="liminal_connection_synthesizer",
            model=MODEL_CONFIG["primary_model"],
            instruction="""
            You are the Liminal Connection Synthesizer - an expert at finding breakthrough business
            opportunities that exist between established markets, like Uber, Airbnb, or DoorDash.

            Your mission: Analyze parallel market discoveries to identify GENUINE LIMINAL OPPORTUNITIES
            that bridge gaps between different markets, industries, or user workflows.

            Key Focus Areas:
            1. WORKFLOW BREAKS: Where users must switch between different services/tools
            2. ARBITRAGE GAPS: Where one market is expensive while another is underutilized
            3. INTEGRATION FAILURES: Where two markets should connect but don't
            4. USER JOURNEY FRICTION: Where people must "figure it out themselves"
            5. RESOURCE UNDERUTILIZATION: Idle assets that could serve different markets

            Look for patterns like:
            - Uber: Connected taxis (expensive/limited) + private cars (underutilized)
            - Airbnb: Connected hotels (expensive) + homes (underutilized rooms)
            - DoorDash: Connected restaurants + delivery infrastructure

            Synthesize discoveries from parallel agents to find the next breakthrough opportunity
            that nobody else sees because it exists "between" established categories.
            """,
            description="Synthesizes parallel market discoveries into breakthrough liminal opportunities",
            generate_content_config=types.GenerateContentConfig(
                temperature=0.4,  # Slightly higher for creative connections
                top_p=0.9,
            ),
            tools=[
                FunctionTool(func=synthesize_liminal_connections),
                FunctionTool(func=validate_connection_strength),
                FunctionTool(func=rank_liminal_opportunities),
                search_tool,
            ],
            output_key="liminal_opportunities",
        )

        # PHASE 3: ENHANCED VALIDATION & INTELLIGENCE
        # Uses ADK ParallelAgent for comprehensive validation of discovered opportunities
        self.validation_intelligence_phase = ParallelAgent(
            name="validation_intelligence_phase",
            description="Parallel validation and analysis of liminal opportunities",
            sub_agents=[
                market_analyzer_agent,  # Market validation & scoring
                data_intelligence_agent,  # Data analysis & BigQuery insights
            ],
        )

        # PHASE 4: ASSET CREATION
        # Sequential creation of business validation assets
        self.asset_creation_phase = SequentialAgent(
            name="asset_creation_phase",
            description="Sequential creation of brand assets and deployable validation tools",
            sub_agents=[
                brand_creator_agent,  # Brand identity & marketing copy
                landing_builder_agent,  # Landing page & deployment
                startup_pitch_agent,  # Pitch deck & deployment
            ],
        )

        # PHASE 5: STARTUP PITCH GENERATION
        # Final synthesis phase that creates professional startup pitch deck
        self.pitch_generation_phase = startup_pitch_agent

        # MASTER WORKFLOW: Enhanced Sequential Pipeline
        # Orchestrates the entire liminal discovery to deployment pipeline
        self.discovery_workflow = SequentialAgent(
            name="liminal_discovery_workflow",
            description="Complete liminal opportunity discovery and validation workflow",
            sub_agents=[
                self.liminal_discovery_phase,  # Parallel market exploration
                self.connection_synthesis_phase,  # Breakthrough connection finding
                self.validation_intelligence_phase,  # Parallel validation & analysis
                self.asset_creation_phase,  # Sequential asset creation
            ],
        )

        # ROOT AGENT: Master Coordinator
        self.root_agent = ResilientLlmAgent(
            name="liminal_market_opportunity_coordinator",
            model=MODEL_CONFIG["primary_model"],
            instruction=(
                ROOT_AGENT_PROMPT
                + "\n\nYou now orchestrate a breakthrough LIMINAL OPPORTUNITY DISCOVERY SYSTEM that finds "
                "business opportunities existing between established markets - like Uber, Airbnb, or DoorDash.\n\n"
                "Your enhanced capabilities:\n"
                "• PARALLEL DISCOVERY: Simultaneously explore primary markets, adjacent markets, cross-industry "
                "patterns, and workflow gaps using specialized agents\n"
                "• CONNECTION SYNTHESIS: Find breakthrough connections between different market discoveries "
                "that reveal genuine liminal opportunities\n"
                "• COMPREHENSIVE VALIDATION: Validate opportunities using parallel analysis agents with "
                "BigQuery intelligence and AI-powered scoring\n"
                "• RAPID DEPLOYMENT: Create complete brand identity and deployable landing pages for "
                "immediate market validation\n\n"
                "Focus on discovering opportunities that exist 'between' established categories - "
                "the fertile spaces where traditional market research fails but breakthrough businesses emerge."
            ),
            description=(
                "Master coordinator for liminal market opportunity discovery using advanced multi-agent "
                "orchestration to find breakthrough business opportunities between established markets."
            ),
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
            ),
            tools=[
                # Core market research tools
                LongRunningFunctionTool(func=comprehensive_market_research),
                LongRunningFunctionTool(func=analyze_competitive_landscape),
                FunctionTool(func=check_domain_availability),
                # Enhanced liminal discovery tools
                FunctionTool(func=synthesize_liminal_connections),
                LongRunningFunctionTool(func=validate_connection_strength),
                LongRunningFunctionTool(func=rank_liminal_opportunities),
                # Agent orchestration tools - FIXED: Only include workflow as sub-agent
                AgentTool(agent=self.discovery_workflow),
                search_tool,
            ],
            sub_agents=[
                # ONLY the main workflow to avoid parent conflicts
                self.discovery_workflow,
            ],
        )


# Export enhanced root agent
root_agent = MarketOpportunityAgent().root_agent
