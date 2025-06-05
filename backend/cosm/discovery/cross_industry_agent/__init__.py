"""
Cross-Industry Pattern Discovery Agent
Uses parallel search to find patterns across different industries for arbitrage opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from typing import Dict, List, Any
import json
from datetime import datetime
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool
from cosm.tools.parallel_search import parallel_cross_industry_search

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
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error in AI analysis of cross-industry arbitrage: {e}")

    return {
        "arbitrage_opportunities": [],
        "technology_transfer_opportunities": [],
        "infrastructure_sharing_opportunities": [],
        "regulatory_arbitrage_signals": [],
    }


def find_industry_cost_disparities(keywords: List[str]) -> Dict[str, Any]:
    """
    Find cost disparities across industries for the same solutions/needs
    """
    disparities = {
        "cost_gaps": [],
        "price_arbitrage_opportunities": [],
        "efficiency_gaps": [],
        "resource_utilization_differences": [],
    }

    try:
        for keyword in keywords:
            # This could use parallel search to find pricing in different industries
            # and identify where the same solution costs vastly different amounts

            cost_analysis_prompt = f"""
            Analyze cost structures for {keyword} across different industries.
            Where are there significant price differences for similar solutions?
            Which industries overpay while others have efficient alternatives?
            """  # noqa: F841

            # Implementation would use parallel search results

        return disparities

    except Exception as e:
        disparities["error"] = str(e)
        return disparities


def identify_underutilized_industry_assets(keywords: List[str]) -> Dict[str, Any]:
    """
    Identify underutilized assets in different industries that could serve other markets
    """
    assets = {
        "underutilized_infrastructure": [],
        "idle_resources": [],
        "excess_capacity": [],
        "cross_industry_opportunities": [],
    }

    try:
        for keyword in keywords:
            # Analyze which industries have excess capacity or underutilized resources
            # that could be repurposed to serve other industries

            asset_analysis_prompt = f"""
            What infrastructure, resources, or capacity related to {keyword} is
            underutilized in different industries? How could these assets serve
            other industries or markets?
            """  # noqa: F841

            # Implementation would analyze parallel search results for asset utilization

        return assets

    except Exception as e:
        assets["error"] = str(e)
        return assets


# Create the cross-industry pattern agent
cross_industry_agent = LlmAgent(
    name="cross_industry_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["market_explorer"], api_key=settings.OPENAI_API_KEY
    ),
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
