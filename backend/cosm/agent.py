"""
Market Opportunity Discovery Agent - Root Coordinator
Finds genuine liminal market spaces and builds testable business assets
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from google.genai import types
from datetime import datetime

from .discovery.explorer_agent import market_explorer_agent
from .discovery.trend_analyzer import trend_analyzer_agent  
from .discovery.gap_mapper import gap_mapper_agent
from .analysis import market_analyzer_agent
from .analysis.code_executor import code_executor_agent
from .analysis.opportunity_scorer import opportunity_scorer_agent
from .builder import brand_creator_agent, landing_builder_agent, copy_writer_agent
from .tools.market_research import comprehensive_market_research, analyze_competitive_landscape, check_domain_availability
from .prompts import ROOT_AGENT_PROMPT
from .config import MODEL_CONFIG
from .schemas import MarketValidation

def setup_market_context(callback_context: CallbackContext):
    """Setup market research context and shared state"""
    if "market_context" not in callback_context.state:
        callback_context.state["market_context"] = {
            "research_timestamp": datetime.now().isoformat(),
            "data_sources": [],
            "validation_criteria": {},
            "research_pipeline": {}
        }
    
    if "research_results" not in callback_context.state:
        callback_context.state["research_results"] = {
            "market_signals": [],
            "trend_analysis": {},
            "gap_analysis": {},
            "validation_data": {},
            "opportunity_scores": {},
            "business_assets": {}
        }

class MarketOpportunityAgent:
    """
    Root agent that orchestrates the discovery and validation of liminal market opportunities
    """
    
    def __init__(self):
        # Phase 1: Market Signal Discovery (Parallel)
        self.discovery_phase = ParallelAgent(
            name="market_discovery_phase",
            sub_agents=[
                market_explorer_agent,  # Scrapes social media, forums, reviews
                trend_analyzer_agent,   # Analyzes search trends, industry reports
                gap_mapper_agent       # Maps connections between signals
            ]
        )
        
        # Phase 2: Deep Analysis & Validation (Sequential)
        self.analysis_phase = SequentialAgent(
            name="market_analysis_phase", 
            sub_agents=[
                market_analyzer_agent,    # Market sizing and competitive analysis
                code_executor_agent,      # Data analysis and visualization
                opportunity_scorer_agent  # Scores and ranks opportunities
            ]
        )
        
        # Phase 3: Business Asset Creation (Parallel)
        self.builder_phase = ParallelAgent(
            name="business_builder_phase",
            sub_agents=[
                brand_creator_agent,   # Creates brand identity and positioning
                copy_writer_agent,     # Generates marketing copy
                landing_builder_agent  # Builds functional landing page
            ]
        )
        
        # Root orchestrator agent with enhanced ADK features
        self.root_agent = LlmAgent(
            name="market_opportunity_coordinator",
            model=MODEL_CONFIG["primary_model"],
            instruction=ROOT_AGENT_PROMPT,
            description=(
                "Discovers genuine liminal market opportunities by analyzing "
                "real-world signals, validates them through data analysis, "
                "and creates testable business assets for rapid validation."
            ),
            # ADK Enhanced Features
            before_agent_callback=setup_market_context,
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
                response_mime_type="application/json"
            ),
            output_key="market_opportunity_analysis",
            output_schema=MarketValidation,
            tools=[
                # Core research tools
                FunctionTool(func=comprehensive_market_research),
                FunctionTool(func=analyze_competitive_landscape),
                FunctionTool(func=check_domain_availability),
                
                # Agent orchestration tools
                AgentTool(agent=self.discovery_phase),
                AgentTool(agent=self.analysis_phase), 
                AgentTool(agent=self.builder_phase)
            ],
            sub_agents=[
                self.discovery_phase,
                self.analysis_phase,
                self.builder_phase
            ]
        )

# Create the root agent instance
root_agent = MarketOpportunityAgent().root_agent