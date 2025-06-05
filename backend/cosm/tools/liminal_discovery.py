"""
Complete Liminal Discovery Tools
This will find breakthrough opportunities like Uber, Airbnb, DoorDash
"""

from typing import Dict, List, Any
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.tavily import tavily_quick_search


def synthesize_liminal_connections(
    primary_market: Dict[str, Any],
    adjacent_markets: Dict[str, Any],
    cross_industry: Dict[str, Any],
    workflow_gaps: Dict[str, Any],
) -> Dict[str, Any]:
    """
    BREAKTHROUGH SYNTHESIS: Finds genuine liminal opportunities like Uber/Airbnb
    """

    synthesis_result = {
        "synthesis_timestamp": datetime.now().isoformat(),
        "breakthrough_opportunities": [],
        "connection_patterns": [],
        "arbitrage_discoveries": [],
        "integration_solutions": [],
        "uber_airbnb_analogies": [],
    }

    try:
        print("🧠 SYNTHESIZING BREAKTHROUGH LIMINAL OPPORTUNITIES...")

        # Prepare comprehensive data for AI analysis
        synthesis_data = {
            "primary_signals": extract_key_signals(primary_market),
            "adjacent_opportunities": extract_key_signals(adjacent_markets),
            "cross_industry_patterns": extract_key_signals(cross_industry),
            "workflow_friction": extract_key_signals(workflow_gaps),
        }

        # CRITICAL: Use advanced AI to find breakthrough connections
        synthesis_prompt = f"""
        You are the BREAKTHROUGH OPPORTUNITY SYNTHESIZER. Find the next Uber, Airbnb, or DoorDash
        by synthesizing these market discoveries.

        SYNTHESIS DATA:
        {json.dumps(synthesis_data, indent=2)[:3000]}

        MISSION: Find GENUINE LIMINAL OPPORTUNITIES that exist between established markets.

        Look for these WINNING PATTERNS:
        1. EXPENSIVE/LIMITED solution + UNDERUTILIZED resource = Uber pattern
        2. FRAGMENTED market + UNIFIED platform = Airbnb pattern
        3. COMPLEX process + SIMPLE interface = Stripe pattern
        4. WORKFLOW BREAKS + SEAMLESS bridge = Zapier pattern

        BREAKTHROUGH EXAMPLES:
        - Uber: Taxis (expensive/limited) + Cars (underutilized) = On-demand rides
        - Airbnb: Hotels (expensive) + Homes (spare rooms) = Affordable stays
        - DoorDash: Restaurants + Delivery = Food on-demand
        - Stripe: Complex payments + Simple API = Developer payments

        Find opportunities with these characteristics:
        - CLEAR VALUE ARBITRAGE (obvious economic opportunity)
        - MARKET TIMING (technology/behavior ready)
        - SCALABLE MODEL (can grow exponentially)
        - NETWORK EFFECTS (gets better with more users)

        Return JSON with SPECIFIC, ACTIONABLE opportunities:
        {{
            "breakthrough_opportunities": [
                {{
                    "opportunity_name": "Clear, compelling business name",
                    "tagline": "Simple value proposition",
                    "liminal_position": "Specific gap between markets X and Y",
                    "expensive_side": "What users currently overpay for",
                    "underutilized_side": "What resources are sitting idle",
                    "value_arbitrage": "Specific economic value created",
                    "target_users": "Who would use this first",
                    "revenue_model": "How money is made",
                    "network_effect": "How it gets better with scale",
                    "implementation_mvp": "Simplest version to test",
                    "market_size_estimate": "TAM estimate with reasoning",
                    "uber_airbnb_analogy": "Detailed comparison to successful pattern",
                    "why_now": "Why this timing is perfect",
                    "competitive_moat": "What makes this defensible"
                }}
            ],
            "connection_patterns": [
                {{
                    "pattern_name": "Name of the connection pattern",
                    "pattern_description": "How two markets could connect",
                    "value_creation": "Economic value from connection",
                    "evidence": "Market signals supporting this"
                }}
            ],
            "arbitrage_discoveries": [
                {{
                    "arbitrage_type": "cost|time|quality|access|convenience",
                    "market_inefficiency": "Specific inefficiency discovered",
                    "value_capture_method": "How to profit from this gap",
                    "market_readiness": "Evidence market is ready"
                }}
            ]
        }}

        FOCUS: Find opportunities that entrepreneurs can actually build and scale.
        Make each opportunity SPECIFIC and ACTIONABLE with clear next steps.
        """

        response = completion(
            model=MODEL_CONFIG["primary_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": synthesis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.6,  # Higher for breakthrough creativity
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            ai_synthesis = json.loads(response.choices[0].message.content)
            synthesis_result.update(ai_synthesis)

            # Enhance each opportunity with additional analysis
            enhanced_opportunities = []
            for opp in synthesis_result.get("breakthrough_opportunities", []):
                enhanced_opp = enhance_opportunity_analysis(opp)
                enhanced_opportunities.append(enhanced_opp)

            synthesis_result["breakthrough_opportunities"] = enhanced_opportunities

        print(
            f"✅ SYNTHESIS COMPLETE: {len(synthesis_result['breakthrough_opportunities'])} breakthrough opportunities found"
        )

        return synthesis_result

    except Exception as e:
        print(f"❌ SYNTHESIS ERROR: {e}")
        synthesis_result["error"] = str(e)
        return synthesis_result


def extract_key_signals(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key signals from market data for synthesis"""
    if not market_data:
        return {}

    signals = {
        "pain_points": [],
        "market_gaps": [],
        "user_frustrations": [],
        "cost_inefficiencies": [],
        "workflow_breaks": [],
        "underutilized_resources": [],
    }

    # Extract signals from various data structures
    def extract_from_any(data, target_list, keywords):
        if isinstance(data, dict):
            for key, value in data.items():
                if any(kw in key.lower() for kw in keywords):
                    if isinstance(value, list):
                        target_list.extend(value[:3])  # Limit for performance
                    elif isinstance(value, str) and len(value) > 10:
                        target_list.append(value)
                extract_from_any(value, target_list, keywords)
        elif isinstance(data, list):
            for item in data[:5]:  # Limit list processing
                extract_from_any(item, target_list, keywords)

    # Extract different types of signals
    extract_from_any(
        market_data, signals["pain_points"], ["pain", "problem", "frustration", "issue"]
    )
    extract_from_any(
        market_data, signals["market_gaps"], ["gap", "missing", "need", "lack"]
    )
    extract_from_any(
        market_data,
        signals["cost_inefficiencies"],
        ["expensive", "cost", "price", "fee"],
    )
    extract_from_any(
        market_data,
        signals["workflow_breaks"],
        ["manual", "switch", "break", "friction"],
    )
    extract_from_any(
        market_data,
        signals["underutilized_resources"],
        ["unused", "idle", "underutilized", "spare"],
    )

    return signals


def enhance_opportunity_analysis(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance opportunity with deeper analysis"""

    enhanced = opportunity.copy()

    try:
        # Calculate opportunity score
        enhanced["opportunity_score"] = calculate_opportunity_score(opportunity)

        # Add implementation difficulty
        enhanced["implementation_difficulty"] = assess_implementation_difficulty(
            opportunity
        )

        # Add time to market
        enhanced["time_to_market"] = estimate_time_to_market(opportunity)

        # Add risk factors
        enhanced["risk_factors"] = identify_risk_factors(opportunity)

        # Add success indicators
        enhanced["success_indicators"] = identify_success_indicators(opportunity)

        return enhanced

    except Exception as e:
        enhanced["enhancement_error"] = str(e)
        return enhanced


def calculate_opportunity_score(opportunity: Dict[str, Any]) -> float:
    """Calculate overall opportunity score (0-1)"""

    # score = 0.0
    factors = []

    # Market size factor
    market_size = opportunity.get("market_size_estimate", "").lower()
    if "billion" in market_size:
        factors.append(0.9)
    elif "million" in market_size:
        factors.append(0.7)
    else:
        factors.append(0.5)

    # Value arbitrage factor
    arbitrage = opportunity.get("value_arbitrage", "").lower()
    if "high" in arbitrage or "significant" in arbitrage:
        factors.append(0.8)
    elif "medium" in arbitrage or "moderate" in arbitrage:
        factors.append(0.6)
    else:
        factors.append(0.4)

    # Market timing factor
    timing = opportunity.get("why_now", "").lower()
    if len(timing) > 100:  # Detailed timing explanation
        factors.append(0.8)
    else:
        factors.append(0.5)

    # Network effects factor
    network = opportunity.get("network_effect", "").lower()
    if "strong" in network or "viral" in network:
        factors.append(0.9)
    elif "moderate" in network:
        factors.append(0.6)
    else:
        factors.append(0.3)

    return sum(factors) / len(factors) if factors else 0.5


def assess_implementation_difficulty(opportunity: Dict[str, Any]) -> str:
    """Assess how difficult this would be to implement"""

    mvp = opportunity.get("implementation_mvp", "").lower()

    if any(word in mvp for word in ["simple", "basic", "existing", "api"]):
        return "low"
    elif any(word in mvp for word in ["moderate", "platform", "marketplace"]):
        return "medium"
    else:
        return "high"


def estimate_time_to_market(opportunity: Dict[str, Any]) -> str:
    """Estimate time to get to market"""

    difficulty = assess_implementation_difficulty(opportunity)

    if difficulty == "low":
        return "3-6 months"
    elif difficulty == "medium":
        return "6-12 months"
    else:
        return "12+ months"


def identify_risk_factors(opportunity: Dict[str, Any]) -> List[str]:
    """Identify key risk factors"""

    risks = []

    # Check for regulation risks
    if any(
        word in str(opportunity).lower()
        for word in ["regulated", "compliance", "legal"]
    ):
        risks.append("Regulatory complexity")

    # Check for network effect dependency
    if "network" in opportunity.get("revenue_model", "").lower():
        risks.append("Chicken-and-egg problem (needs both sides)")

    # Check for competition
    if "competitive" in str(opportunity).lower():
        risks.append("Competitive market entry")

    # Default risks
    risks.extend(
        [
            "Market adoption speed",
            "Technology execution risk",
            "Customer acquisition cost",
        ]
    )

    return risks[:5]


def identify_success_indicators(opportunity: Dict[str, Any]) -> List[str]:
    """Identify early success indicators to track"""

    indicators = [
        "User sign-up rate",
        "Transaction volume growth",
        "User retention rate",
        "Word-of-mouth referrals",
    ]

    # Add opportunity-specific indicators
    if "marketplace" in str(opportunity).lower():
        indicators.append("Supply-demand balance")

    if "subscription" in opportunity.get("revenue_model", "").lower():
        indicators.append("Monthly recurring revenue growth")

    return indicators


def validate_connection_strength(
    opportunity: Dict[str, Any],
) -> Dict[str, Any]:
    """
    VALIDATION ENGINE: Validates strength of liminal connections
    """

    validation = {
        "opportunity_name": opportunity.get("opportunity_name", "Unknown"),
        "validation_timestamp": datetime.now().isoformat(),
        "connection_strength": 0.0,
        "validation_factors": {},
        "go_no_go_recommendation": "analyze",
        "confidence_level": "medium",
        "validation_evidence": [],
    }

    try:
        print(f"🔍 VALIDATING: {opportunity.get('opportunity_name', 'Unknown')}")

        # Core validation factors
        factors = {
            "market_size_viability": validate_market_size(opportunity),
            "arbitrage_strength": validate_arbitrage(opportunity),
            "technical_feasibility": validate_technical_feasibility(opportunity),
            "market_timing": validate_market_timing(opportunity),
            "competitive_advantage": validate_competitive_advantage(opportunity),
            "scalability_potential": validate_scalability(opportunity),
        }

        validation["validation_factors"] = factors

        # Calculate overall connection strength
        validation["connection_strength"] = sum(factors.values()) / len(factors)

        # Generate recommendation
        if validation["connection_strength"] >= 0.75:
            validation["go_no_go_recommendation"] = "proceed"
            validation["confidence_level"] = "high"
        elif validation["connection_strength"] >= 0.6:
            validation["go_no_go_recommendation"] = "proceed_with_caution"
            validation["confidence_level"] = "medium"
        elif validation["connection_strength"] >= 0.4:
            validation["go_no_go_recommendation"] = "validate_further"
            validation["confidence_level"] = "low"
        else:
            validation["go_no_go_recommendation"] = "do_not_proceed"
            validation["confidence_level"] = "very_low"

        # Generate validation evidence
        validation["validation_evidence"] = generate_validation_evidence(
            opportunity, factors
        )

        print(
            f"✅ VALIDATION COMPLETE: {validation['connection_strength']:.2f} strength"
        )

        return validation

    except Exception as e:
        print(f"❌ VALIDATION ERROR: {e}")
        validation["error"] = str(e)
        return validation


def validate_market_size(opportunity: Dict[str, Any]) -> float:
    """Validate market size is large enough"""

    market_size = opportunity.get("market_size_estimate", "").lower()

    if "trillion" in market_size:
        return 1.0
    elif "billion" in market_size:
        if any(num in market_size for num in ["1", "2", "3", "4", "5"]):
            return 0.9
        else:
            return 0.8
    elif "million" in market_size:
        if "100" in market_size or "500" in market_size:
            return 0.7
        else:
            return 0.5
    else:
        return 0.3


def validate_arbitrage(opportunity: Dict[str, Any]) -> float:
    """Validate strength of value arbitrage"""

    arbitrage = opportunity.get("value_arbitrage", "").lower()
    expensive_side = opportunity.get("expensive_side", "").lower()
    underutilized_side = opportunity.get("underutilized_side", "").lower()

    score = 0.0

    # Check for clear arbitrage language
    if any(word in arbitrage for word in ["significant", "massive", "huge", "clear"]):
        score += 0.4
    elif any(word in arbitrage for word in ["good", "solid", "reasonable"]):
        score += 0.3
    else:
        score += 0.1

    # Check for specificity
    if len(expensive_side) > 20 and len(underutilized_side) > 20:
        score += 0.4
    else:
        score += 0.2

    return min(score, 1.0)


def validate_technical_feasibility(opportunity: Dict[str, Any]) -> float:
    """Validate technical feasibility"""

    mvp = opportunity.get("implementation_mvp", "").lower()

    if any(word in mvp for word in ["api", "existing", "simple", "basic"]):
        return 0.9
    elif any(word in mvp for word in ["platform", "marketplace", "moderate"]):
        return 0.7
    elif any(word in mvp for word in ["complex", "advanced", "difficult"]):
        return 0.4
    else:
        return 0.6


def validate_market_timing(opportunity: Dict[str, Any]) -> float:
    """Validate market timing is right"""

    timing = opportunity.get("why_now", "").lower()

    score = 0.5  # Base score

    # Check for timing indicators
    timing_signals = [
        "covid",
        "remote",
        "digital",
        "mobile",
        "ai",
        "technology",
        "behavior",
        "trend",
    ]

    signal_count = sum(1 for signal in timing_signals if signal in timing)
    score += min(signal_count * 0.1, 0.4)

    # Check for detailed explanation
    if len(timing) > 100:
        score += 0.1

    return min(score, 1.0)


def validate_competitive_advantage(opportunity: Dict[str, Any]) -> float:
    """Validate competitive advantage"""

    moat = opportunity.get("competitive_moat", "").lower()
    network = opportunity.get("network_effect", "").lower()

    score = 0.0

    # Network effects
    if "strong" in network or "viral" in network:
        score += 0.4
    elif "moderate" in network:
        score += 0.3
    else:
        score += 0.1

    # Other moats
    if any(word in moat for word in ["data", "scale", "brand", "switching"]):
        score += 0.3
    else:
        score += 0.2

    return min(score, 1.0)


def validate_scalability(opportunity: Dict[str, Any]) -> float:
    """Validate scalability potential"""

    revenue_model = opportunity.get("revenue_model", "").lower()
    network = opportunity.get("network_effect", "").lower()

    score = 0.5  # Base score

    # Revenue model scalability
    if any(
        word in revenue_model for word in ["commission", "subscription", "platform"]
    ):
        score += 0.3
    elif any(word in revenue_model for word in ["transaction", "usage"]):
        score += 0.2

    # Network effects boost scalability
    if "strong" in network:
        score += 0.2

    return min(score, 1.0)


def generate_validation_evidence(
    opportunity: Dict[str, Any], factors: Dict[str, float]
) -> List[str]:
    """Generate evidence supporting the validation"""

    evidence = []

    # Market size evidence
    if factors["market_size_viability"] >= 0.7:
        evidence.append(
            f"Large addressable market: {opportunity.get('market_size_estimate', 'TBD')}"
        )

    # Arbitrage evidence
    if factors["arbitrage_strength"] >= 0.7:
        evidence.append(
            f"Clear value arbitrage: {opportunity.get('value_arbitrage', 'TBD')}"
        )

    # Technical evidence
    if factors["technical_feasibility"] >= 0.7:
        evidence.append(
            f"Technically feasible MVP: {opportunity.get('implementation_mvp', 'TBD')}"
        )

    # Timing evidence
    if factors["market_timing"] >= 0.7:
        evidence.append("Market timing appears favorable based on current trends")

    return evidence


def rank_liminal_opportunities(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    RANKING ENGINE: Ranks opportunities by breakthrough potential
    """

    ranking = {
        "ranking_timestamp": datetime.now().isoformat(),
        "total_opportunities": len(opportunities),
        "ranked_opportunities": [],
        "top_tier_opportunities": [],
        "sleeper_opportunities": [],
        "ranking_methodology": {
            "factors": [
                "opportunity_score (40%)",
                "market_size (25%)",
                "implementation_feasibility (20%)",
                "timing_advantage (15%)",
            ]
        },
    }

    try:
        print(f"📊 RANKING {len(opportunities)} opportunities...")

        # Score each opportunity
        scored_opportunities = []

        for opp in opportunities:
            # Calculate composite score
            composite_score = calculate_composite_opportunity_score(opp)

            ranked_opp = {
                **opp,
                "composite_score": composite_score,
                "tier": classify_opportunity_tier(composite_score),
                "investment_recommendation": generate_investment_recommendation(
                    composite_score
                ),
            }

            scored_opportunities.append(ranked_opp)

        # Sort by composite score
        scored_opportunities.sort(key=lambda x: x["composite_score"], reverse=True)

        ranking["ranked_opportunities"] = scored_opportunities

        # Categorize opportunities
        ranking["top_tier_opportunities"] = [
            opp for opp in scored_opportunities if opp["tier"] == "top_tier"
        ]
        ranking["sleeper_opportunities"] = [
            opp for opp in scored_opportunities if opp["tier"] == "sleeper"
        ]

        print(
            f"✅ RANKING COMPLETE: {len(ranking['top_tier_opportunities'])} top-tier opportunities"
        )

        return ranking

    except Exception as e:
        print(f"❌ RANKING ERROR: {e}")
        ranking["error"] = str(e)
        return ranking


def calculate_composite_opportunity_score(opportunity: Dict[str, Any]) -> float:
    """Calculate composite score for ranking"""

    # Get individual scores
    opp_score = opportunity.get("opportunity_score", 0.5)

    # Market size score
    market_size = opportunity.get("market_size_estimate", "").lower()
    if "billion" in market_size:
        size_score = 0.9
    elif "million" in market_size:
        size_score = 0.6
    else:
        size_score = 0.3

    # Implementation feasibility score
    difficulty = opportunity.get("implementation_difficulty", "medium")
    if difficulty == "low":
        feasibility_score = 0.9
    elif difficulty == "medium":
        feasibility_score = 0.6
    else:
        feasibility_score = 0.3

    # Timing score
    timing = opportunity.get("why_now", "")
    timing_score = 0.8 if len(timing) > 100 else 0.5

    # Weighted composite score
    composite = (
        opp_score * 0.4  # 40% opportunity fundamentals
        + size_score * 0.25  # 25% market size
        + feasibility_score * 0.2  # 20% implementation feasibility
        + timing_score * 0.15  # 15% timing advantage
    )

    return composite


def classify_opportunity_tier(score: float) -> str:
    """Classify opportunity into tiers"""

    if score >= 0.8:
        return "top_tier"
    elif score >= 0.65:
        return "high_potential"
    elif score >= 0.5:
        return "sleeper"
    else:
        return "risky"


def generate_investment_recommendation(score: float) -> str:
    """Generate investment recommendation"""

    if score >= 0.8:
        return "immediate_action"
    elif score >= 0.65:
        return "strong_consider"
    elif score >= 0.5:
        return "validate_further"
    else:
        return "pass"


# PARALLEL EXECUTION FUNCTIONS
def execute_parallel_liminal_discovery(keywords: List[str]) -> Dict[str, Any]:
    """
    Execute complete liminal discovery using parallel threading
    """

    discovery_results = {
        "keywords": keywords,
        "discovery_timestamp": datetime.now().isoformat(),
        "parallel_execution": True,
        "results": {},
        "synthesis": {},
        "execution_time": 0.0,
    }

    start_time = time.time()

    try:
        print(f"🚀 STARTING PARALLEL LIMINAL DISCOVERY for: {', '.join(keywords)}")

        # Define discovery tasks
        discovery_tasks = [
            ("primary_market", discover_primary_market_parallel),
            ("adjacent_markets", discover_adjacent_markets_parallel),
            ("cross_industry", discover_cross_industry_parallel),
            ("workflow_gaps", discover_workflow_gaps_parallel),
        ]

        # Execute all discovery tasks in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_task = {
                executor.submit(task_func, keywords): task_name
                for task_name, task_func in discovery_tasks
            }

            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result(timeout=30)
                    results[task_name] = result
                    print(f"✅ {task_name} discovery completed")
                except Exception as e:
                    print(f"❌ {task_name} discovery failed: {e}")
                    results[task_name] = {"error": str(e)}

        discovery_results["results"] = results

        # Synthesize all results
        synthesis = synthesize_liminal_connections(
            results.get("primary_market", {}),
            results.get("adjacent_markets", {}),
            results.get("cross_industry", {}),
            results.get("workflow_gaps", {}),
        )

        discovery_results["synthesis"] = synthesis
        discovery_results["execution_time"] = time.time() - start_time

        print(
            f"🎯 PARALLEL DISCOVERY COMPLETE in {discovery_results['execution_time']:.2f}s"
        )

        return discovery_results

    except Exception as e:
        discovery_results["error"] = str(e)
        discovery_results["execution_time"] = time.time() - start_time
        return discovery_results


def discover_primary_market_parallel(keywords: List[str]) -> Dict[str, Any]:
    """Parallel primary market discovery"""
    return parallel_search_execution(keywords, "primary_market")


def discover_adjacent_markets_parallel(keywords: List[str]) -> Dict[str, Any]:
    """Parallel adjacent markets discovery"""
    return parallel_search_execution(keywords, "adjacent_markets")


def discover_cross_industry_parallel(keywords: List[str]) -> Dict[str, Any]:
    """Parallel cross-industry discovery"""
    return parallel_search_execution(keywords, "cross_industry")


def discover_workflow_gaps_parallel(keywords: List[str]) -> Dict[str, Any]:
    """Parallel workflow gaps discovery"""
    return parallel_search_execution(keywords, "workflow_gaps")


def parallel_search_execution(
    keywords: List[str], discovery_type: str
) -> Dict[str, Any]:
    """Execute parallel searches for any discovery type"""

    search_queries = generate_search_queries(keywords, discovery_type)

    results = {
        "discovery_type": discovery_type,
        "keywords": keywords,
        "search_results": [],
        "processed_signals": [],
    }

    try:
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(tavily_quick_search, query, 2)
                for query in search_queries[:6]  # Limit for performance
            ]

            for future in as_completed(futures):
                try:
                    search_result = future.result(timeout=10)
                    if search_result and not search_result.get("error"):
                        results["search_results"].append(search_result)
                except Exception as e:
                    print(f"Search failed: {e}")

        # Process results to extract signals
        results["processed_signals"] = process_search_results_for_signals(
            results["search_results"], discovery_type
        )

        return results

    except Exception as e:
        results["error"] = str(e)
        return results


def generate_search_queries(keywords: List[str], discovery_type: str) -> List[str]:
    """Generate targeted search queries based on discovery type"""

    queries = []

    for keyword in keywords[:2]:  # Limit keywords for performance
        if discovery_type == "primary_market":
            queries.extend(
                [
                    f"{keyword} user problems complaints reddit",
                    f"{keyword} market size statistics",
                    f"{keyword} customer pain points reviews",
                ]
            )

        elif discovery_type == "adjacent_markets":
            queries.extend(
                [
                    f"what do people use before {keyword}",
                    f"what happens after using {keyword}",
                    f"alternatives to {keyword} people combine",
                ]
            )

        elif discovery_type == "cross_industry":
            queries.extend(
                [
                    f"how {keyword} works in different industries",
                    f"{keyword} healthcare vs finance vs retail",
                    f"{keyword} cost differences across sectors",
                ]
            )

        elif discovery_type == "workflow_gaps":
            queries.extend(
                [
                    f"{keyword} integration problems challenges",
                    f"manual steps required with {keyword}",
                    f"switching between {keyword} and other tools",
                ]
            )

    return queries


def process_search_results_for_signals(
    search_results: List[Dict], discovery_type: str
) -> List[Dict[str, Any]]:
    """Process search results to extract relevant signals"""

    signals = []

    for result in search_results:
        if result.get("search_results"):
            for search_data in result["search_results"]:
                if search_data.get("results"):
                    for item in search_data["results"][:2]:  # Limit processing
                        signal = {
                            "signal_type": discovery_type,
                            "title": item.get("title", ""),
                            "content": item.get("content", "")[:500],  # Limit content
                            "url": item.get("url", ""),
                            "relevance_score": item.get("score", 0.5),
                        }

                        if signal["title"] and signal["content"]:
                            signals.append(signal)

    return signals[:10]  # Limit for performance
