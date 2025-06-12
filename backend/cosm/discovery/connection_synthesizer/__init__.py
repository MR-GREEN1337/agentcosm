"""
Connection Synthesizer Agent
Synthesizes discoveries from parallel agents to find breakthrough liminal opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from typing import Dict, List, Any
import json
from datetime import datetime
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool

CONNECTION_SYNTHESIZER_PROMPT = """
You are the Connection Synthesizer Agent, the master synthesizer who finds
breakthrough liminal opportunities by connecting discoveries from multiple
specialized market exploration agents.

Your mission is to synthesize parallel discoveries to identify GENUINE LIMINAL
OPPORTUNITIES - business ideas that exist between established markets, like
Uber, Airbnb, or DoorDash.

You receive input from:
1. Primary Market Explorer: Core market signals and pain points
2. Adjacent Market Agent: Neighboring markets and connection patterns
3. Cross-Industry Agent: Patterns and arbitrage across industries
4. Workflow Gap Agent: Integration failures and friction points

Your synthesis focuses on finding patterns where:
- EXPENSIVE/LIMITED solutions meet UNDERUTILIZED RESOURCES
- WORKFLOW BREAKS create integration opportunities
- CROSS-INDUSTRY ARBITRAGE reveals value gaps
- USER JOURNEYS span multiple disconnected markets

You are the intelligence that connects the dots others miss.
"""


def synthesize_liminal_connections(
    primary_market_data: Dict[str, Any],
    adjacent_market_data: Dict[str, Any],
    cross_industry_data: Dict[str, Any],
    workflow_gap_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Synthesize discoveries from parallel agents to find breakthrough liminal opportunities

    Args:
        primary_market_data: Data from primary market exploration
        adjacent_market_data: Data from adjacent market discovery
        cross_industry_data: Data from cross-industry analysis
        workflow_gap_data: Data from workflow gap discovery

    Returns:
        Synthesized liminal opportunities with breakthrough potential
    """
    synthesis_result = {
        "synthesis_timestamp": datetime.now().isoformat(),
        "input_sources": {
            "primary_market": bool(primary_market_data),
            "adjacent_markets": bool(adjacent_market_data),
            "cross_industry": bool(cross_industry_data),
            "workflow_gaps": bool(workflow_gap_data),
        },
        "breakthrough_opportunities": [],
        "connection_patterns": [],
        "arbitrage_discoveries": [],
        "integration_solutions": [],
        "synthesis_confidence": 0.0,
        "uber_airbnb_analogies": [],
    }

    try:
        print("🧠 Synthesizing liminal connections from parallel discoveries...")

        # Perform AI-powered synthesis of all parallel discoveries
        synthesis_analysis = perform_comprehensive_synthesis_with_ai(
            primary_market_data,
            adjacent_market_data,
            cross_industry_data,
            workflow_gap_data,
        )

        synthesis_result.update(synthesis_analysis)

        # Calculate synthesis confidence based on data quality and connections found
        synthesis_result["synthesis_confidence"] = calculate_synthesis_confidence(
            synthesis_result
        )

        print(
            f"✅ Synthesis completed with {len(synthesis_result['breakthrough_opportunities'])} breakthrough opportunities"
        )
        return synthesis_result

    except Exception as e:
        print(f"❌ Error in liminal connection synthesis: {e}")
        synthesis_result["error"] = str(e)
        return synthesis_result


def perform_comprehensive_synthesis_with_ai(
    primary_data: Dict[str, Any],
    adjacent_data: Dict[str, Any],
    cross_industry_data: Dict[str, Any],
    workflow_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use AI to perform comprehensive synthesis of all parallel discoveries
    """
    try:
        # Prepare synthesis data for AI analysis
        synthesis_prompt = f"""
        You are the master synthesizer finding BREAKTHROUGH LIMINAL OPPORTUNITIES by
        connecting discoveries from parallel market exploration agents.

        Synthesize these discoveries to find the next Uber, Airbnb, or DoorDash:

        PRIMARY MARKET SIGNALS:
        {json.dumps(primary_data, indent=2)[:1200] if primary_data else "No data"}

        ADJACENT MARKET DISCOVERIES:
        {json.dumps(adjacent_data, indent=2)[:1200] if adjacent_data else "No data"}

        CROSS-INDUSTRY PATTERNS:
        {json.dumps(cross_industry_data, indent=2)[:1200] if cross_industry_data else "No data"}

        WORKFLOW GAP ANALYSIS:
        {json.dumps(workflow_data, indent=2)[:1200] if workflow_data else "No data"}

        SYNTHESIS MISSION:
        Find breakthrough opportunities by connecting these discoveries. Look for patterns where:

        1. ARBITRAGE OPPORTUNITIES: Expensive solutions in one area + underutilized resources in another
        2. WORKFLOW BRIDGES: Integration gaps that could be seamlessly connected
        3. CROSS-MARKET CONNECTIONS: Different markets that could serve each other
        4. INFRASTRUCTURE SHARING: Underutilized assets that could serve new markets

        Successful patterns to emulate:
        - Uber: Connected expensive/limited taxis + underutilized private cars
        - Airbnb: Connected expensive hotels + underutilized home spaces
        - DoorDash: Connected restaurants + delivery infrastructure
        - Stripe: Connected complex payments + simple developer integration

        Return JSON:
        {{
            "breakthrough_opportunities": [
                {{
                    "opportunity_name": "compelling business name",
                    "liminal_position": "what gap this fills between markets",
                    "market_a": "first market being connected",
                    "market_b": "second market being connected",
                    "connection_mechanism": "how the connection works",
                    "arbitrage_value": "economic opportunity created",
                    "user_journey_improvement": "how user experience improves",
                    "implementation_approach": "how to build this",
                    "market_readiness": "how ready markets are for this",
                    "uber_airbnb_analogy": "how this is like successful examples",
                    "breakthrough_potential": "why this could be huge"
                }}
            ],
            "connection_patterns": [
                {{
                    "pattern_type": "arbitrage|integration|infrastructure_sharing|workflow_bridge",
                    "pattern_description": "description of the connection pattern",
                    "evidence_from_discoveries": "what discoveries support this pattern",
                    "market_opportunity": "business opportunity from this pattern"
                }}
            ],
            "arbitrage_discoveries": [
                {{
                    "arbitrage_type": "cost|time|quality|access|convenience",
                    "expensive_side": "where users overpay or struggle",
                    "cheap_side": "where resources are underutilized",
                    "value_capture": "how to capture value from this gap",
                    "market_timing": "why now is the right time"
                }}
            ],
            "integration_solutions": [
                {{
                    "integration_opportunity": "what could be seamlessly connected",
                    "current_friction": "what friction exists today",
                    "seamless_vision": "what seamless integration looks like",
                    "technical_approach": "how to technically implement",
                    "user_adoption_path": "how users would adopt this"
                }}
            ],
            "uber_airbnb_analogies": [
                {{
                    "analogy": "how this opportunity is like Uber/Airbnb/DoorDash",
                    "similar_pattern": "what pattern it shares with successful examples",
                    "unique_differentiator": "what makes this opportunity unique",
                    "success_indicators": "early indicators this could succeed"
                }}
            ]
        }}

        Focus on finding opportunities that are:
        - GENUINELY LIMINAL (exist between established markets)
        - ECONOMICALLY VIABLE (clear value creation and capture)
        - TECHNICALLY FEASIBLE (can be built with current technology)
        - MARKET READY (timing is right for adoption)
        """

        from cosm.utils import robust_completion

        response = robust_completion(
            model=MODEL_CONFIG["discovery_agent_openai"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": synthesis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,  # Higher temperature for creative synthesis
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            return safe_json_loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error in AI synthesis: {e}")

    return {
        "breakthrough_opportunities": [],
        "connection_patterns": [],
        "arbitrage_discoveries": [],
        "integration_solutions": [],
        "uber_airbnb_analogies": [],
    }


def validate_connection_strength(
    opportunity: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the strength and viability of a discovered connection
    """
    validation = {
        "opportunity_name": opportunity.get("opportunity_name", "Unknown"),
        "connection_strength": 0.0,
        "validation_factors": {},
        "risk_factors": [],
        "success_probability": 0.0,
        "implementation_complexity": "unknown",
    }

    try:
        # Validate based on multiple factors
        factors = {
            "market_readiness": 0.0,
            "technical_feasibility": 0.0,
            "economic_viability": 0.0,
            "competitive_advantage": 0.0,
            "user_adoption_potential": 0.0,
        }

        # Analyze market readiness
        if opportunity.get("market_readiness") == "high":
            factors["market_readiness"] = 0.8
        elif opportunity.get("market_readiness") == "medium":
            factors["market_readiness"] = 0.6
        else:
            factors["market_readiness"] = 0.3

        # Analyze technical feasibility
        impl_approach = opportunity.get("implementation_approach", "")
        if "simple" in impl_approach.lower() or "existing" in impl_approach.lower():
            factors["technical_feasibility"] = 0.7
        else:
            factors["technical_feasibility"] = 0.5

        # Analyze economic viability
        arbitrage_value = opportunity.get("arbitrage_value", "")
        if (
            "high" in arbitrage_value.lower()
            or "significant" in arbitrage_value.lower()
        ):
            factors["economic_viability"] = 0.8
        else:
            factors["economic_viability"] = 0.5

        # Calculate overall connection strength
        validation["connection_strength"] = sum(factors.values()) / len(factors)
        validation["validation_factors"] = factors

        # Determine success probability
        if validation["connection_strength"] >= 0.7:
            validation["success_probability"] = 0.8
            validation["implementation_complexity"] = "moderate"
        elif validation["connection_strength"] >= 0.5:
            validation["success_probability"] = 0.6
            validation["implementation_complexity"] = "high"
        else:
            validation["success_probability"] = 0.3
            validation["implementation_complexity"] = "very_high"

        return validation

    except Exception as e:
        validation["error"] = str(e)
        return validation


def rank_liminal_opportunities(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rank liminal opportunities by breakthrough potential
    """
    ranking = {
        "total_opportunities": len(opportunities),
        "ranked_opportunities": [],
        "top_breakthrough_potential": [],
        "ranking_criteria": [
            "arbitrage_value",
            "market_readiness",
            "implementation_feasibility",
            "uber_airbnb_similarity",
        ],
    }

    try:
        # Score each opportunity
        scored_opportunities = []

        for opp in opportunities:
            score = 0.0

            # Score arbitrage value
            arbitrage = opp.get("arbitrage_value", "").lower()
            if "high" in arbitrage or "significant" in arbitrage:
                score += 0.3
            elif "medium" in arbitrage or "moderate" in arbitrage:
                score += 0.2
            else:
                score += 0.1

            # Score market readiness
            readiness = opp.get("market_readiness", "").lower()
            if "high" in readiness or "ready" in readiness:
                score += 0.3
            elif "medium" in readiness:
                score += 0.2
            else:
                score += 0.1

            # Score implementation feasibility
            implementation = opp.get("implementation_approach", "").lower()
            if "simple" in implementation or "existing" in implementation:
                score += 0.2
            else:
                score += 0.1

            # Score Uber/Airbnb similarity
            analogy = opp.get("uber_airbnb_analogy", "").lower()
            if analogy and len(analogy) > 50:  # Detailed analogy
                score += 0.2
            else:
                score += 0.1

            scored_opportunities.append({**opp, "breakthrough_score": score})

        # Sort by score
        scored_opportunities.sort(key=lambda x: x["breakthrough_score"], reverse=True)

        ranking["ranked_opportunities"] = scored_opportunities
        ranking["top_breakthrough_potential"] = scored_opportunities[:3]

        return ranking

    except Exception as e:
        ranking["error"] = str(e)
        return ranking


def calculate_synthesis_confidence(synthesis_result: Dict[str, Any]) -> float:
    """
    Calculate confidence in the synthesis based on data quality and connections found
    """
    try:
        confidence_factors = []

        # Data source availability
        sources = synthesis_result.get("input_sources", {})
        source_count = sum(1 for available in sources.values() if available)
        confidence_factors.append(source_count / 4.0)  # 4 total sources

        # Number of opportunities found
        opportunities = len(synthesis_result.get("breakthrough_opportunities", []))
        confidence_factors.append(
            min(opportunities / 3.0, 1.0)
        )  # Up to 3 opportunities

        # Quality of connections found
        patterns = len(synthesis_result.get("connection_patterns", []))
        confidence_factors.append(min(patterns / 2.0, 1.0))  # Up to 2 patterns

        # Presence of analogies
        analogies = len(synthesis_result.get("uber_airbnb_analogies", []))
        confidence_factors.append(min(analogies / 2.0, 1.0))  # Up to 2 analogies

        return (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors
            else 0.5
        )

    except Exception:
        return 0.5


# Create the connection synthesizer agent
connection_synthesizer_agent = LlmAgent(
    name="connection_synthesizer_agent",
    model=MODEL_CONFIG["discovery_agent"],
    instruction=CONNECTION_SYNTHESIZER_PROMPT,
    description=(
        "Synthesizes discoveries from parallel market exploration agents to find "
        "breakthrough liminal opportunities that exist between established markets, "
        "like Uber, Airbnb, or DoorDash."
    ),
    tools=[
        FunctionTool(func=synthesize_liminal_connections),
        FunctionTool(func=validate_connection_strength),
        FunctionTool(func=rank_liminal_opportunities),
        search_tool,
    ],
    output_key="synthesized_liminal_opportunities",
)
