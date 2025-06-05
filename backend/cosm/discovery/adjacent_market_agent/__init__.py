"""
Adjacent Market Discovery Agent
Uses parallel web search to discover markets adjacent to primary market for liminal connections
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from google.adk.models.lite_llm import LiteLlm
from typing import Dict, List, Any
import json
from datetime import datetime
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool
from cosm.tools.parallel_search import parallel_adjacent_market_search

client = Client()

ADJACENT_MARKET_PROMPT = """
You are the Adjacent Market Discovery Agent, specialized in finding markets that are
adjacent, complementary, or connected to a primary market space using parallel web search.

Your mission is to discover the "neighboring" markets that could create liminal
opportunities when connected to the primary market - like how Uber connected
taxis (expensive/limited) with private cars (underutilized).

You use parallel web search to efficiently discover:
1. UPSTREAM MARKETS: What people use before the primary market
2. DOWNSTREAM MARKETS: What people use after the primary market
3. COMPLEMENTARY MARKETS: What people use alongside the primary market
4. SUBSTITUTE MARKETS: What people use instead of the primary market
5. ENABLING INFRASTRUCTURE: What services/infrastructure enable the primary market

Focus on finding connection patterns that reveal arbitrage opportunities between
expensive/limited solutions and underutilized resources.
"""


def discover_adjacent_markets_parallel(primary_keywords: List[str]) -> Dict[str, Any]:
    """
    Discovers markets adjacent to primary market using parallel web search

    Args:
        primary_keywords: Keywords representing the primary market

    Returns:
        Dictionary containing adjacent market discoveries
    """
    adjacent_data = {
        "primary_keywords": primary_keywords,
        "timestamp": datetime.now().isoformat(),
        "discovery_method": "parallel_web_search",
        "adjacent_markets": {},
        "connection_opportunities": [],
        "arbitrage_signals": [],
        "market_bridges": [],
    }

    try:
        print(
            f"🔍 Discovering adjacent markets in parallel for: {', '.join(primary_keywords)}"
        )

        # Execute parallel search for adjacent markets
        search_results = parallel_adjacent_market_search(primary_keywords)
        adjacent_data["adjacent_markets"] = search_results

        # Analyze results with AI to find connection opportunities
        if search_results:
            connection_analysis = analyze_adjacent_connections_with_ai(
                search_results, primary_keywords
            )
            adjacent_data.update(connection_analysis)

        print(
            f"✅ Adjacent market discovery completed with {len(search_results)} market dimensions"
        )
        return adjacent_data

    except Exception as e:
        print(f"❌ Error in adjacent market discovery: {e}")
        adjacent_data["error"] = str(e)
        return adjacent_data


def analyze_adjacent_connections_with_ai(
    search_results: Dict[str, Any], primary_keywords: List[str]
) -> Dict[str, Any]:
    """
    Use AI to analyze adjacent market search results for connection opportunities
    """
    try:
        analysis_prompt = f"""
        Analyze these adjacent market search results to find CONNECTION OPPORTUNITIES
        that could create liminal businesses like Uber, Airbnb, or DoorDash.

        Primary Keywords: {primary_keywords}

        Adjacent Market Search Results:
        {json.dumps(search_results, indent=2)[:2500]}

        Look for patterns where:
        1. EXPENSIVE/LIMITED solutions in one market
        2. UNDERUTILIZED RESOURCES in adjacent markets
        3. WORKFLOW BREAKS between markets
        4. USER JOURNEYS that span multiple markets

        Find connection opportunities like:
        - Uber: Taxis (expensive) + Private Cars (underutilized)
        - Airbnb: Hotels (expensive) + Homes (spare rooms)
        - DoorDash: Restaurants + Delivery Infrastructure

        Return JSON:
        {{
            "connection_opportunities": [
                {{
                    "opportunity_name": "descriptive name",
                    "expensive_market": "market with expensive/limited solutions",
                    "underutilized_market": "market with underutilized resources",
                    "connection_value": "what value the connection creates",
                    "user_journey": "how users currently experience friction",
                    "arbitrage_potential": "economic opportunity",
                    "implementation_approach": "how to bridge the markets"
                }}
            ],
            "arbitrage_signals": [
                {{
                    "signal": "specific arbitrage opportunity",
                    "market_gap": "gap between markets",
                    "evidence": "supporting evidence from search results"
                }}
            ],
            "market_bridges": [
                {{
                    "bridge_concept": "how to connect the markets",
                    "technical_feasibility": "how technically feasible",
                    "market_readiness": "how ready the markets are"
                }}
            ]
        }}
        """

        response = completion(
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error in AI analysis of adjacent connections: {e}")

    return {
        "connection_opportunities": [],
        "arbitrage_signals": [],
        "market_bridges": [],
    }


def find_upstream_downstream_flows(keywords: List[str]) -> Dict[str, Any]:
    """
    Find upstream and downstream market flows for workflow analysis
    """
    flows = {
        "upstream_dependencies": [],
        "downstream_outcomes": [],
        "workflow_continuity_breaks": [],
        "integration_opportunities": [],
    }

    try:
        # This would use the parallel search results to map user workflow flows
        # and identify where workflows break between different markets

        for keyword in keywords:
            # Analyze upstream dependencies
            upstream_prompt = f"""
            Based on market research, what are the typical steps users take BEFORE using {keyword}?
            What tools, services, or processes do they need to complete first?
            What preparation or prerequisites are required?
            """  # noqa: F841

            # Analyze downstream outcomes
            downstream_prompt = f"""
            Based on market research, what do users typically do AFTER using {keyword}?
            What are the next steps in their workflow?
            What additional tools or services do they need?
            """  # noqa: F841

            # These could be executed in parallel as well using ThreadPoolExecutor

        return flows

    except Exception as e:
        flows["error"] = str(e)
        return flows


# Create the adjacent market agent
adjacent_market_agent = LlmAgent(
    name="adjacent_market_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["market_explorer"], api_key=settings.OPENAI_API_KEY
    ),
    instruction=ADJACENT_MARKET_PROMPT,
    description=(
        "Discovers markets adjacent to primary market using parallel web search "
        "to find liminal connection opportunities between expensive/limited solutions "
        "and underutilized resources."
    ),
    tools=[
        FunctionTool(func=discover_adjacent_markets_parallel),
        FunctionTool(func=find_upstream_downstream_flows),
        search_tool,
    ],
    output_key="adjacent_market_intelligence",
)
