"""
Adjacent Market Discovery Agent - Fixed Implementation
Uses parallel web search to discover markets adjacent to primary market for liminal connections
"""

from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool
from cosm.tools.parallel_search import parallel_adjacent_market_search
import json
from cosm.utils import robust_completion, ResilientLlmAgent

client = Client()
thread_local = threading.local()

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

        response = robust_completion(
            model=MODEL_CONFIG["market_explorer_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            return safe_json_loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error in AI analysis of adjacent connections: {e}")

    return {
        "connection_opportunities": [],
        "arbitrage_signals": [],
        "market_bridges": [],
    }


def analyze_upstream_market_with_ai(
    keyword: str, upstream_prompt: str
) -> Dict[str, Any]:
    """
    Analyze upstream markets using AI for a specific keyword
    """
    try:
        response = robust_completion(
            model=MODEL_CONFIG["market_explorer_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": upstream_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            result = safe_json_loads(response.choices[0].message.content)
            return {
                "keyword": keyword,
                "upstream_dependencies": result.get("upstream_dependencies", []),
                "prerequisites": result.get("prerequisites", []),
                "preparation_steps": result.get("preparation_steps", []),
                "enabling_services": result.get("enabling_services", []),
            }
    except Exception as e:
        print(f"❌ Error analyzing upstream market for {keyword}: {e}")

    return {
        "keyword": keyword,
        "upstream_dependencies": [],
        "prerequisites": [],
        "preparation_steps": [],
        "enabling_services": [],
    }


def analyze_downstream_market_with_ai(
    keyword: str, downstream_prompt: str
) -> Dict[str, Any]:
    """
    Analyze downstream markets using AI for a specific keyword
    """
    try:
        response = robust_completion(
            model=MODEL_CONFIG["market_explorer_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": downstream_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            result = safe_json_loads(response.choices[0].message.content)
            return {
                "keyword": keyword,
                "downstream_outcomes": result.get("downstream_outcomes", []),
                "next_steps": result.get("next_steps", []),
                "follow_up_services": result.get("follow_up_services", []),
                "completion_requirements": result.get("completion_requirements", []),
            }
    except Exception as e:
        print(f"❌ Error analyzing downstream market for {keyword}: {e}")

    return {
        "keyword": keyword,
        "downstream_outcomes": [],
        "next_steps": [],
        "follow_up_services": [],
        "completion_requirements": [],
    }


def find_upstream_downstream_flows(keywords: List[str]) -> Dict[str, Any]:
    """
    Find upstream and downstream market flows for workflow analysis using threading
    """
    flows = {
        "upstream_dependencies": [],
        "downstream_outcomes": [],
        "workflow_continuity_breaks": [],
        "integration_opportunities": [],
    }

    try:
        print(f"🔄 Analyzing upstream/downstream flows for {len(keywords)} keywords...")

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit upstream analysis tasks
            upstream_futures = []
            downstream_futures = []

            for keyword in keywords:
                # Upstream analysis
                upstream_prompt = f"""
                Based on market research, analyze what users typically do BEFORE using {keyword}.
                What tools, services, or processes do they need to complete first?
                What preparation or prerequisites are required?

                Return JSON:
                {{
                    "upstream_dependencies": ["step1", "step2", "step3"],
                    "prerequisites": ["requirement1", "requirement2"],
                    "preparation_steps": ["prep1", "prep2"],
                    "enabling_services": ["service1", "service2"]
                }}

                RETURN ONLY JSON AND NOTHING ELSE!!!!!!!!!!!!!
                """

                upstream_future = executor.submit(
                    analyze_upstream_market_with_ai, keyword, upstream_prompt
                )
                upstream_futures.append(upstream_future)

                # Downstream analysis
                downstream_prompt = f"""
                Based on market research, analyze what users typically do AFTER using {keyword}.
                What are the next steps in their workflow?
                What additional tools or services do they need?

                Return JSON:
                {{
                    "downstream_outcomes": ["outcome1", "outcome2", "outcome3"],
                    "next_steps": ["step1", "step2"],
                    "follow_up_services": ["service1", "service2"],
                    "completion_requirements": ["req1", "req2"]
                }}

                RETURN ONLY JSON AND NOTHING ELSE!!!!!!!!!!!!!
                """

                downstream_future = executor.submit(
                    analyze_downstream_market_with_ai, keyword, downstream_prompt
                )
                downstream_futures.append(downstream_future)

            # Collect upstream results
            for future in as_completed(upstream_futures):
                try:
                    result = future.result(timeout=30)
                    flows["upstream_dependencies"].append(result)
                except Exception as e:
                    print(f"❌ Upstream analysis failed: {e}")

            # Collect downstream results
            for future in as_completed(downstream_futures):
                try:
                    result = future.result(timeout=30)
                    flows["downstream_outcomes"].append(result)
                except Exception as e:
                    print(f"❌ Downstream analysis failed: {e}")

        # Analyze workflow breaks
        flows["workflow_continuity_breaks"] = identify_workflow_breaks(
            flows["upstream_dependencies"], flows["downstream_outcomes"]
        )

        # Identify integration opportunities
        flows["integration_opportunities"] = identify_integration_opportunities(
            flows["upstream_dependencies"], flows["downstream_outcomes"]
        )

        print("✅ Upstream/downstream analysis completed")
        return flows

    except Exception as e:
        flows["error"] = str(e)
        print(f"❌ Error in upstream/downstream analysis: {e}")
        return flows


def identify_workflow_breaks(
    upstream_data: List[Dict], downstream_data: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Identify breaks in workflow continuity between upstream and downstream processes
    """
    workflow_breaks = []

    try:
        # Analyze gaps between upstream outputs and downstream inputs
        for upstream_item in upstream_data:
            keyword = upstream_item.get("keyword", "")
            upstream_outputs = upstream_item.get("enabling_services", [])

            # Find corresponding downstream data
            downstream_item = next(
                (item for item in downstream_data if item.get("keyword") == keyword),
                None,
            )

            if downstream_item:
                downstream_inputs = downstream_item.get("next_steps", [])

                # Identify potential breaks
                for output in upstream_outputs:
                    if not any(
                        output.lower() in step.lower() for step in downstream_inputs
                    ):
                        workflow_breaks.append(
                            {
                                "keyword": keyword,
                                "break_type": "service_gap",
                                "upstream_output": output,
                                "missing_connection": f"No clear downstream usage of {output}",
                                "opportunity": f"Bridge {output} to downstream workflow",
                            }
                        )

    except Exception as e:
        print(f"❌ Error identifying workflow breaks: {e}")

    return workflow_breaks[:10]  # Limit results


def identify_integration_opportunities(
    upstream_data: List[Dict], downstream_data: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Identify opportunities for integrating upstream and downstream processes
    """
    opportunities = []

    try:
        # Look for automation opportunities
        for upstream_item in upstream_data:
            keyword = upstream_item.get("keyword", "")
            prerequisites = upstream_item.get("prerequisites", [])

            downstream_item = next(
                (item for item in downstream_data if item.get("keyword") == keyword),
                None,
            )

            if downstream_item:
                completion_reqs = downstream_item.get("completion_requirements", [])

                # Find automation opportunities
                for prereq in prerequisites:
                    for comp_req in completion_reqs:
                        if any(
                            word in prereq.lower() and word in comp_req.lower()
                            for word in ["data", "file", "report", "document"]
                        ):
                            opportunities.append(
                                {
                                    "keyword": keyword,
                                    "integration_type": "data_flow_automation",
                                    "upstream_requirement": prereq,
                                    "downstream_requirement": comp_req,
                                    "automation_potential": f"Automate {prereq} → {comp_req} flow",
                                    "value_proposition": "Eliminate manual data transfer",
                                }
                            )

    except Exception as e:
        print(f"❌ Error identifying integration opportunities: {e}")

    return opportunities[:10]  # Limit results


# Create the adjacent market agent
adjacent_market_agent = ResilientLlmAgent(
    name="adjacent_market_agent",
    model=MODEL_CONFIG["market_explorer"],
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
