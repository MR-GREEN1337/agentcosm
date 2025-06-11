"""
Cross-Industry Pattern Discovery Agent - Fixed Implementation
Uses parallel search to find patterns across different industries for arbitrage opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from typing import Dict, List, Any
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool
from cosm.tools.parallel_search import parallel_cross_industry_search

thread_local = threading.local()

CROSS_INDUSTRY_PROMPT = """
You are the Cross-Industry Pattern Discovery Agent, specialized in finding patterns,
solutions, and opportunities that exist across different industries.

Your mission is to discover arbitrage opportunities where solutions that work well
in one industry could be applied to another industry, or where different industries
could be connected in novel ways.

You use parallel web search to efficiently discover:
1. INDUSTRY-SPECIFIC SOLUTIONS: How different industries solve similar problems
2. CROSS-INDUSTRY ARBITRAGE: Expensive solutions in one industry vs cheap in another
3. TECHNOLOGY TRANSFER: Solutions that could move between industries
4. REGULATORY ARBITRAGE: Different rules/costs across industries
5. INFRASTRUCTURE SHARING: Underutilized resources in one industry serving another

Focus on finding patterns like:
- How finance industry solutions could serve healthcare
- How retail infrastructure could serve manufacturing
- How gig economy patterns could apply to B2B services
"""


def discover_cross_industry_patterns_parallel(
    primary_keywords: List[str],
) -> Dict[str, Any]:
    """
    Discovers cross-industry patterns using parallel web search

    Args:
        primary_keywords: Keywords representing the primary market

    Returns:
        Dictionary containing cross-industry pattern discoveries
    """
    cross_industry_data = {
        "primary_keywords": primary_keywords,
        "timestamp": datetime.now().isoformat(),
        "discovery_method": "parallel_cross_industry_search",
        "industry_patterns": {},
        "arbitrage_opportunities": [],
        "technology_transfer_opportunities": [],
        "infrastructure_sharing_opportunities": [],
        "regulatory_arbitrage_signals": [],
    }

    try:
        print(
            f"🏭 Discovering cross-industry patterns in parallel for: {', '.join(primary_keywords)}"
        )

        # Execute parallel search across industries
        search_results = parallel_cross_industry_search(primary_keywords)
        cross_industry_data["industry_patterns"] = search_results

        # Analyze results with AI to find arbitrage opportunities
        if search_results:
            arbitrage_analysis = analyze_cross_industry_arbitrage_with_ai(
                search_results, primary_keywords
            )
            cross_industry_data.update(arbitrage_analysis)

        print(
            f"✅ Cross-industry discovery completed across {len(search_results.get('industry_patterns', {}))} industries"
        )
        return cross_industry_data

    except Exception as e:
        print(f"❌ Error in cross-industry pattern discovery: {e}")
        cross_industry_data["error"] = str(e)
        return cross_industry_data


def analyze_cross_industry_arbitrage_with_ai(
    search_results: Dict[str, Any], primary_keywords: List[str]
) -> Dict[str, Any]:
    """
    Use AI to analyze cross-industry patterns for arbitrage opportunities
    """
    try:
        analysis_prompt = f"""
        Analyze these cross-industry search results to find ARBITRAGE OPPORTUNITIES
        where solutions, resources, or approaches from one industry could create
        value in another industry.

        Primary Keywords: {primary_keywords}

        Cross-Industry Search Results:
        {json.dumps(search_results, indent=2)[:2500]}

        Look for arbitrage patterns like:
        1. EXPENSIVE in Industry A, CHEAP in Industry B
        2. COMMON in Industry A, NOVEL in Industry B
        3. REGULATED in Industry A, UNREGULATED in Industry B
        4. UNDERUTILIZED RESOURCES in Industry A that could serve Industry B
        5. PROVEN SOLUTIONS in Industry A that could transform Industry B

        Examples of successful cross-industry arbitrage:
        - Uber: Applied taxi model using private car infrastructure
        - Airbnb: Applied hotel model using residential infrastructure
        - Amazon: Applied retail logistics to cloud infrastructure

        Return JSON:
        {{
            "arbitrage_opportunities": [
                {{
                    "opportunity_name": "descriptive name",
                    "source_industry": "industry with the solution/resource",
                    "target_industry": "industry that could benefit",
                    "arbitrage_type": "cost|regulatory|technology|infrastructure",
                    "value_creation": "what value this arbitrage creates",
                    "implementation_barriers": "what barriers exist",
                    "market_readiness": "how ready the target market is"
                }}
            ],
            "technology_transfer_opportunities": [
                {{
                    "technology": "specific technology or approach",
                    "current_industry": "where it's currently used",
                    "target_industry": "where it could be applied",
                    "adaptation_required": "what changes would be needed"
                }}
            ],
            "infrastructure_sharing_opportunities": [
                {{
                    "infrastructure": "type of infrastructure",
                    "current_use": "how it's currently used",
                    "alternative_use": "how else it could be used",
                    "value_unlock": "economic value of sharing"
                }}
            ],
            "regulatory_arbitrage_signals": [
                {{
                    "regulation_gap": "difference in regulations",
                    "industries": "industries with different rules",
                    "opportunity": "business opportunity from gap"
                }}
            ]
        }}
        """

        response = completion(
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
        print(f"❌ Error in AI analysis of cross-industry arbitrage: {e}")

    return {
        "arbitrage_opportunities": [],
        "technology_transfer_opportunities": [],
        "infrastructure_sharing_opportunities": [],
        "regulatory_arbitrage_signals": [],
    }


def analyze_cost_disparities_with_ai(
    keyword: str, cost_analysis_prompt: str
) -> Dict[str, Any]:
    """
    Analyze cost disparities across industries using AI
    """
    try:
        response = completion(
            model=MODEL_CONFIG["market_explorer_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": cost_analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            result = safe_json_loads(response.choices[0].message.content)
            return {
                "keyword": keyword,
                "cost_disparities": result.get("cost_disparities", []),
                "price_arbitrage": result.get("price_arbitrage", []),
                "efficiency_gaps": result.get("efficiency_gaps", []),
                "cost_drivers": result.get("cost_drivers", []),
            }
    except Exception as e:
        print(f"❌ Error analyzing cost disparities for {keyword}: {e}")

    return {
        "keyword": keyword,
        "cost_disparities": [],
        "price_arbitrage": [],
        "efficiency_gaps": [],
        "cost_drivers": [],
    }


def analyze_asset_utilization_with_ai(
    keyword: str, asset_analysis_prompt: str
) -> Dict[str, Any]:
    """
    Analyze underutilized assets across industries using AI
    """
    try:
        response = completion(
            model=MODEL_CONFIG["market_explorer_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": asset_analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            result = safe_json_loads(response.choices[0].message.content)
            return {
                "keyword": keyword,
                "underutilized_assets": result.get("underutilized_assets", []),
                "idle_resources": result.get("idle_resources", []),
                "sharing_opportunities": result.get("sharing_opportunities", []),
                "utilization_rates": result.get("utilization_rates", []),
            }
    except Exception as e:
        print(f"❌ Error analyzing asset utilization for {keyword}: {e}")

    return {
        "keyword": keyword,
        "underutilized_assets": [],
        "idle_resources": [],
        "sharing_opportunities": [],
        "utilization_rates": [],
    }


def find_industry_cost_disparities(keywords: List[str]) -> Dict[str, Any]:
    """
    Find cost disparities across industries for the same solutions/needs using threading
    """
    disparities = {
        "cost_gaps": [],
        "price_arbitrage_opportunities": [],
        "efficiency_gaps": [],
        "resource_utilization_differences": [],
    }

    try:
        print(
            f"💰 Analyzing cost disparities across industries for {len(keywords)} keywords..."
        )

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []

            for keyword in keywords:
                cost_analysis_prompt = f"""
                Analyze cost structures for {keyword} across different industries.
                Where are there significant price differences for similar solutions?
                Which industries overpay while others have efficient alternatives?

                Return JSON:
                {{
                    "cost_disparities": [
                        {{
                            "expensive_industry": "industry name",
                            "cheap_industry": "industry name",
                            "cost_difference": "percentage or amount",
                            "reason": "why the difference exists"
                        }}
                    ],
                    "price_arbitrage": [
                        {{
                            "opportunity": "arbitrage opportunity description",
                            "source_industry": "where it's cheap",
                            "target_industry": "where it's expensive",
                            "potential_savings": "estimated savings"
                        }}
                    ],
                    "efficiency_gaps": [
                        {{
                            "inefficient_industry": "industry with inefficiency",
                            "efficient_industry": "industry with better approach",
                            "efficiency_gain": "potential improvement"
                        }}
                    ],
                    "cost_drivers": ["factor1", "factor2", "factor3"]
                }}
                """

                future = executor.submit(
                    analyze_cost_disparities_with_ai, keyword, cost_analysis_prompt
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    disparities["cost_gaps"].append(result)

                    # Extract specific data
                    if result.get("cost_disparities"):
                        disparities["price_arbitrage_opportunities"].extend(
                            result.get("price_arbitrage", [])
                        )
                    if result.get("efficiency_gaps"):
                        disparities["efficiency_gaps"].extend(
                            result.get("efficiency_gaps", [])
                        )

                except Exception as e:
                    print(f"❌ Cost analysis failed: {e}")

        print("✅ Cost disparity analysis completed")
        return disparities

    except Exception as e:
        disparities["error"] = str(e)
        print(f"❌ Error in cost disparity analysis: {e}")
        return disparities


def identify_underutilized_industry_assets(keywords: List[str]) -> Dict[str, Any]:
    """
    Identify underutilized assets in different industries using threading
    """
    assets = {
        "underutilized_infrastructure": [],
        "idle_resources": [],
        "excess_capacity": [],
        "cross_industry_opportunities": [],
    }

    try:
        print(
            f"🏗️ Analyzing underutilized assets across industries for {len(keywords)} keywords..."
        )

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []

            for keyword in keywords:
                asset_analysis_prompt = f"""
                What infrastructure, resources, or capacity related to {keyword} is
                underutilized in different industries? How could these assets serve
                other industries or markets?

                Return JSON:
                {{
                    "underutilized_assets": [
                        {{
                            "asset_type": "type of asset",
                            "industry": "industry with underutilized asset",
                            "utilization_rate": "current utilization percentage",
                            "potential_uses": ["use1", "use2", "use3"]
                        }}
                    ],
                    "idle_resources": [
                        {{
                            "resource": "specific resource",
                            "industry": "industry with idle resource",
                            "idle_capacity": "amount or percentage idle",
                            "alternative_applications": ["app1", "app2"]
                        }}
                    ],
                    "sharing_opportunities": [
                        {{
                            "shared_asset": "what could be shared",
                            "source_industry": "industry that has excess",
                            "target_industry": "industry that needs it",
                            "sharing_model": "how sharing would work"
                        }}
                    ],
                    "utilization_rates": [
                        {{
                            "industry": "industry name",
                            "asset": "asset type",
                            "current_rate": "utilization percentage",
                            "optimal_rate": "target utilization"
                        }}
                    ]
                }}
                """

                future = executor.submit(
                    analyze_asset_utilization_with_ai, keyword, asset_analysis_prompt
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    assets["underutilized_infrastructure"].append(result)

                    # Extract specific data
                    if result.get("underutilized_assets"):
                        assets["idle_resources"].extend(
                            result.get("idle_resources", [])
                        )
                    if result.get("sharing_opportunities"):
                        assets["cross_industry_opportunities"].extend(
                            result.get("sharing_opportunities", [])
                        )

                except Exception as e:
                    print(f"❌ Asset analysis failed: {e}")

        print("✅ Asset utilization analysis completed")
        return assets

    except Exception as e:
        assets["error"] = str(e)
        print(f"❌ Error in asset utilization analysis: {e}")
        return assets


# Create the cross-industry pattern agent
cross_industry_agent = LlmAgent(
    name="cross_industry_agent",
    model=MODEL_CONFIG["market_explorer"],
    instruction=CROSS_INDUSTRY_PROMPT,
    description=(
        "Discovers patterns, solutions, and arbitrage opportunities across different "
        "industries using parallel web search to find cost disparities, technology "
        "transfer opportunities, and underutilized resources."
    ),
    tools=[
        FunctionTool(func=discover_cross_industry_patterns_parallel),
        FunctionTool(func=find_industry_cost_disparities),
        FunctionTool(func=identify_underutilized_industry_assets),
        search_tool,
    ],
    output_key="cross_industry_intelligence",
)
