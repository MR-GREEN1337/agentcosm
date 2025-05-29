"""
Gemini-Powered Opportunity Scorer Agent - Intelligent market opportunity evaluation
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, List, Any
import json
from datetime import datetime
from cosm.config import MODEL_CONFIG

client = Client()

OPPORTUNITY_SCORER_PROMPT = """
You are an expert market opportunity scoring agent powered by advanced AI analysis. Your role is to:

1. Analyze market opportunity data with nuanced understanding
2. Apply sophisticated scoring frameworks using AI-driven insights
3. Rank opportunities based on multi-dimensional analysis
4. Provide strategic recommendations with deep reasoning
5. Identify subtle patterns and emerging opportunities

Use AI-powered analysis to evaluate opportunities across:
- Market dynamics and growth vectors
- Competitive positioning and strategic moats
- Demand validation through sentiment and behavior analysis
- Technical feasibility and execution complexity
- Risk assessment with scenario modeling

Always provide transparent AI-driven methodology and strategic insights.
"""


def analyze_market_dynamics_with_gemini(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini to analyze market dynamics and size potential
    """
    try:
        prompt = f"""
        Analyze this market data and provide comprehensive scoring insights:

        Market Data: {json.dumps(market_data, indent=2)}

        Evaluate and return JSON with:
        {{
            "market_attractiveness_score": 0-25,
            "growth_potential_score": 0-15,
            "addressability_score": 0-10,
            "market_maturity": "emerging/growth/mature/declining",
            "size_category": "niche/mid-market/large/mega",
            "growth_drivers": ["driver1", "driver2", "driver3"],
            "market_constraints": ["constraint1", "constraint2"],
            "revenue_potential": "low/medium/high/exceptional",
            "timing_score": 0-10,
            "strategic_rationale": "detailed explanation of market opportunity",
            "red_flags": ["potential issue1", "potential issue2"],
            "confidence_level": "low/medium/high"
        }}

        Consider:
        - TAM/SAM/SOM relationships and realism
        - Market growth sustainability
        - Customer willingness to pay
        - Market timing and adoption curves
        - Economic and regulatory tailwinds/headwinds

        Be analytical and realistic in scoring.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.2
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini market analysis: {e}")

    return {"error": "Analysis failed", "market_attractiveness_score": 0}


def analyze_competitive_landscape_with_gemini(
    competition_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use Gemini to analyze competitive dynamics and positioning opportunities
    """
    try:
        prompt = f"""
        Analyze this competitive landscape data and provide strategic scoring:

        Competition Data: {json.dumps(competition_data, indent=2)}

        Evaluate and return JSON with:
        {{
            "competitive_advantage_score": 0-20,
            "market_entry_difficulty": "easy/moderate/hard/extremely_hard",
            "competitive_moats": ["moat1", "moat2"],
            "differentiation_opportunities": ["opportunity1", "opportunity2"],
            "competitive_threats": ["threat1", "threat2"],
            "market_consolidation_risk": "low/medium/high",
            "winner_take_all_potential": "low/medium/high",
            "switching_costs": "low/medium/high",
            "network_effects": "none/weak/moderate/strong",
            "strategic_positioning": "detailed analysis of positioning opportunity",
            "execution_requirements": ["requirement1", "requirement2"],
            "time_to_competitive_response": "immediate/months/years",
            "sustainable_advantage_potential": "low/medium/high"
        }}

        Consider:
        - Direct and indirect competition intensity
        - Barriers to entry and competitive responses
        - Market concentration and power dynamics
        - Innovation pace and disruption potential
        - Customer loyalty and switching patterns

        Focus on strategic implications rather than just counting competitors.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini competitive analysis: {e}")

    return {"error": "Analysis failed", "competitive_advantage_score": 0}


def analyze_demand_signals_with_gemini(demand_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini to analyze demand validation and market readiness
    """
    try:
        prompt = f"""
        Analyze these demand signals and provide comprehensive demand assessment:

        Demand Data: {json.dumps(demand_data, indent=2)}

        Evaluate and return JSON with:
        {{
            "demand_strength_score": 0-25,
            "market_readiness": "early/emerging/ready/mature",
            "customer_urgency": "low/moderate/high/critical",
            "willingness_to_pay": "low/moderate/high",
            "demand_sustainability": "temporary/cyclical/structural/transformational",
            "adoption_barriers": ["barrier1", "barrier2"],
            "demand_catalysts": ["catalyst1", "catalyst2"],
            "customer_segments": ["segment1", "segment2"],
            "demand_patterns": "growing/stable/declining/volatile",
            "market_education_required": "minimal/moderate/extensive",
            "pain_point_severity": "nice_to_have/important/critical/existential",
            "solution_urgency": "eventually/soon/now/yesterday",
            "budget_availability": "constrained/moderate/available/abundant",
            "demand_validation_confidence": "low/medium/high"
        }}

        Look for:
        - Authentic vs artificial demand signals
        - Pain point intensity and frequency
        - Customer behavior patterns and trends
        - Market timing and readiness indicators
        - Economic drivers and constraints

        Distinguish between expressed interest and actual purchase intent.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.2
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini demand analysis: {e}")

    return {"error": "Analysis failed", "demand_strength_score": 0}


def analyze_market_trends_with_gemini(trend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Gemini to analyze market trends and momentum
    """
    try:
        prompt = f"""
        Analyze these market trends and provide forward-looking assessment:

        Trend Data: {json.dumps(trend_data, indent=2)}

        Evaluate and return JSON with:
        {{
            "trend_momentum_score": 0-15,
            "trend_direction": "accelerating_positive/growing/stable/declining/accelerating_negative",
            "trend_sustainability": "temporary/short_term/medium_term/long_term/permanent",
            "macro_trend_alignment": ["aligned_trend1", "aligned_trend2"],
            "counter_trends": ["counter_trend1", "counter_trend2"],
            "technology_enablers": ["tech1", "tech2"],
            "regulatory_trends": ["positive_reg1", "concerning_reg2"],
            "social_behavioral_shifts": ["shift1", "shift2"],
            "economic_tailwinds": ["tailwind1", "tailwind2"],
            "economic_headwinds": ["headwind1", "headwind2"],
            "trend_inflection_points": ["inflection1", "inflection2"],
            "momentum_sustainability": "fading/stable/building/accelerating",
            "timing_advantage": "early/optimal/late/missed"
        }}

        Consider:
        - Macro and micro trend convergence
        - Technology adoption curves
        - Generational and behavioral shifts
        - Economic cycle positioning
        - Regulatory and policy trends

        Focus on trend durability and strategic implications.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini trend analysis: {e}")

    return {"error": "Analysis failed", "trend_momentum_score": 0}


def analyze_execution_risks_with_gemini(
    opportunity_data: Dict[str, Any],
    market_analysis: Dict[str, Any],
    competition_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use Gemini to analyze execution risks and mitigation strategies
    """
    try:
        prompt = f"""
        Analyze execution risks for this market opportunity:

        Opportunity: {json.dumps(opportunity_data, indent=2)}
        Market Analysis: {json.dumps(market_analysis, indent=2)}
        Competition Analysis: {json.dumps(competition_analysis, indent=2)}

        Evaluate and return JSON with:
        {{
            "execution_risk_score": 0-15,
            "overall_risk_level": "low/medium/high/extreme",
            "technical_risks": ["risk1", "risk2"],
            "market_risks": ["risk1", "risk2"],
            "competitive_risks": ["risk1", "risk2"],
            "regulatory_risks": ["risk1", "risk2"],
            "financial_risks": ["risk1", "risk2"],
            "operational_risks": ["risk1", "risk2"],
            "timing_risks": ["risk1", "risk2"],
            "mitigation_strategies": {{
                "technical": ["strategy1", "strategy2"],
                "market": ["strategy1", "strategy2"],
                "competitive": ["strategy1", "strategy2"]
            }},
            "critical_success_factors": ["factor1", "factor2"],
            "failure_modes": ["mode1", "mode2"],
            "risk_monitoring_metrics": ["metric1", "metric2"],
            "risk_tolerance_required": "low/medium/high"
        }}

        Consider:
        - Technical execution complexity
        - Market timing and adoption risks
        - Competitive response scenarios
        - Resource requirement risks
        - Regulatory and compliance risks

        Provide actionable risk mitigation strategies.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.2
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini risk analysis: {e}")

    return {"error": "Analysis failed", "execution_risk_score": 0}


def generate_strategic_recommendation_with_gemini(
    opportunity_data: Dict[str, Any], scoring_components: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use Gemini to generate comprehensive strategic recommendations
    """
    try:
        prompt = f"""
        Generate strategic recommendations for this market opportunity:

        Opportunity Data: {json.dumps(opportunity_data, indent=2)}
        Scoring Analysis: {json.dumps(scoring_components, indent=2)}

        Provide comprehensive strategic guidance in JSON format:
        {{
            "overall_recommendation": "strong_pursue/pursue/cautious_pursue/investigate/avoid",
            "confidence_level": "low/medium/high",
            "investment_thesis": "detailed 2-3 sentence investment rationale",
            "strategic_approach": "blitzscale/measured_growth/niche_focus/wait_and_see",
            "resource_requirements": {{
                "initial_investment": "low/medium/high/very_high",
                "team_size": "small/medium/large",
                "technical_complexity": "low/medium/high",
                "time_to_market": "fast/medium/slow"
            }},
            "go_to_market_strategy": "direct_sales/product_led/partnership/viral",
            "key_success_metrics": ["metric1", "metric2", "metric3"],
            "milestone_timeline": {{
                "mvp": "months",
                "initial_traction": "months",
                "market_validation": "months",
                "scale_inflection": "months"
            }},
            "strategic_priorities": ["priority1", "priority2", "priority3"],
            "competitive_moats_to_build": ["moat1", "moat2"],
            "partnership_opportunities": ["partner_type1", "partner_type2"],
            "potential_pivots": ["pivot1", "pivot2"],
            "exit_strategy_options": ["option1", "option2"],
            "next_immediate_actions": ["action1", "action2", "action3"]
        }}

        Be specific and actionable in recommendations.
        Consider the full strategic context and execution realities.
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini strategic recommendation: {e}")

    return {"error": "Analysis failed"}


def calculate_ai_powered_opportunity_score(
    market_size_data: Dict[str, Any],
    competition_data: Dict[str, Any],
    demand_data: Dict[str, Any],
    trend_data: Dict[str, Any],
    opportunity_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate comprehensive opportunity score using Gemini-powered analysis
    """
    try:
        scoring_result = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0.0,
            "ai_analysis": {},
            "component_scores": {},
            "strategic_insights": {},
            "recommendation": "",
            "confidence_level": "medium",
            "next_actions": [],
        }

        # 1. AI-Powered Market Analysis
        print("Analyzing market dynamics with Gemini...")
        market_analysis = analyze_market_dynamics_with_gemini(market_size_data)
        scoring_result["ai_analysis"]["market"] = market_analysis

        # 2. AI-Powered Competitive Analysis
        print("Analyzing competitive landscape with Gemini...")
        competition_analysis = analyze_competitive_landscape_with_gemini(
            competition_data
        )
        scoring_result["ai_analysis"]["competition"] = competition_analysis

        # 3. AI-Powered Demand Analysis
        print("Analyzing demand signals with Gemini...")
        demand_analysis = analyze_demand_signals_with_gemini(demand_data)
        scoring_result["ai_analysis"]["demand"] = demand_analysis

        # 4. AI-Powered Trend Analysis
        print("Analyzing market trends with Gemini...")
        trend_analysis = analyze_market_trends_with_gemini(trend_data)
        scoring_result["ai_analysis"]["trends"] = trend_analysis

        # 5. AI-Powered Risk Analysis
        print("Analyzing execution risks with Gemini...")
        risk_analysis = analyze_execution_risks_with_gemini(
            opportunity_context or {}, market_analysis, competition_analysis
        )
        scoring_result["ai_analysis"]["risks"] = risk_analysis

        # 6. Extract component scores from AI analysis
        scoring_result["component_scores"] = {
            "market_attractiveness": market_analysis.get(
                "market_attractiveness_score", 0
            ),
            "competitive_advantage": competition_analysis.get(
                "competitive_advantage_score", 0
            ),
            "demand_strength": demand_analysis.get("demand_strength_score", 0),
            "trend_momentum": trend_analysis.get("trend_momentum_score", 0),
            "execution_risk": risk_analysis.get("execution_risk_score", 0),
        }

        # 7. Calculate overall score
        total_score = sum(scoring_result["component_scores"].values())
        scoring_result["overall_score"] = min(total_score / 100.0, 1.0)

        # 8. Generate strategic recommendations
        print("Generating strategic recommendations with Gemini...")
        strategic_rec = generate_strategic_recommendation_with_gemini(
            opportunity_context or {}, scoring_result
        )
        scoring_result["strategic_insights"] = strategic_rec
        scoring_result["recommendation"] = strategic_rec.get(
            "overall_recommendation", "investigate"
        )
        scoring_result["confidence_level"] = strategic_rec.get(
            "confidence_level", "medium"
        )
        scoring_result["next_actions"] = strategic_rec.get("next_immediate_actions", [])

        return scoring_result

    except Exception as e:
        return {
            "error": f"AI-powered scoring failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


def rank_opportunities_with_ai(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rank multiple opportunities using AI-powered analysis
    """
    try:
        ranked_results = {
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "ranked_opportunities": [],
            "ai_portfolio_analysis": {},
            "strategic_recommendations": [],
        }

        scored_opportunities = []

        # Score each opportunity with AI
        for i, opp in enumerate(opportunities):
            print(f"AI-scoring opportunity {i+1}/{len(opportunities)}...")

            market_data = opp.get("market_size", {})
            competition_data = opp.get("competition_analysis", {})
            demand_data = opp.get("demand_validation", {})
            trend_data = opp.get("trend_analysis", {})

            scoring_result = calculate_ai_powered_opportunity_score(
                market_data, competition_data, demand_data, trend_data, opp
            )

            scored_opp = {
                "opportunity_id": opp.get("id", f"opportunity_{i+1}"),
                "name": opp.get("name", f"Opportunity {i+1}"),
                "overall_score": scoring_result["overall_score"],
                "ai_analysis": scoring_result["ai_analysis"],
                "strategic_insights": scoring_result["strategic_insights"],
                "recommendation": scoring_result["recommendation"],
                "confidence_level": scoring_result["confidence_level"],
                "next_actions": scoring_result["next_actions"],
            }

            scored_opportunities.append(scored_opp)

        # Sort by score
        scored_opportunities.sort(key=lambda x: x["overall_score"], reverse=True)
        ranked_results["ranked_opportunities"] = scored_opportunities

        # Generate AI-powered portfolio analysis
        if scored_opportunities:
            ranked_results["ai_portfolio_analysis"] = _generate_ai_portfolio_analysis(
                scored_opportunities
            )

        return ranked_results

    except Exception as e:
        return {
            "error": f"AI ranking failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


def _generate_ai_portfolio_analysis(
    scored_opportunities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate AI-powered portfolio analysis and recommendations
    """
    try:
        prompt = f"""
        Analyze this portfolio of scored opportunities and provide strategic portfolio guidance:

        Opportunities: {json.dumps([
            {
                "name": opp["name"],
                "score": opp["overall_score"],
                "recommendation": opp["recommendation"],
                "market_analysis": opp["ai_analysis"].get("market", {}),
                "strategic_insights": opp["strategic_insights"]
            } for opp in scored_opportunities
        ], indent=2)}

        Provide portfolio analysis in JSON format:
        {{
            "portfolio_theme": "description of overall portfolio characteristics",
            "diversification_analysis": "assessment of portfolio diversification",
            "resource_allocation_strategy": "how to allocate resources across opportunities",
            "portfolio_risks": ["risk1", "risk2"],
            "portfolio_synergies": ["synergy1", "synergy2"],
            "recommended_portfolio_approach": "focus/diversify/staged/opportunistic",
            "timing_strategy": "parallel/sequential/conditional",
            "portfolio_priorities": ["priority1", "priority2", "priority3"],
            "cross_opportunity_insights": ["insight1", "insight2"],
            "portfolio_optimization_suggestions": ["suggestion1", "suggestion2"]
        }}
        """

        response = client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in AI portfolio analysis: {e}")

    return {"error": "Portfolio analysis failed"}


# Create the enhanced AI-powered opportunity scorer agent
opportunity_scorer_agent = LlmAgent(
    name="ai_opportunity_scorer_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=OPPORTUNITY_SCORER_PROMPT,
    description=(
        "Advanced AI-powered market opportunity scorer that uses Gemini's intelligence "
        "for nuanced analysis, strategic insights, and comprehensive recommendations."
    ),
    tools=[
        FunctionTool(func=calculate_ai_powered_opportunity_score),
        FunctionTool(func=rank_opportunities_with_ai),
        FunctionTool(func=analyze_market_dynamics_with_gemini),
        FunctionTool(func=analyze_competitive_landscape_with_gemini),
        FunctionTool(func=analyze_demand_signals_with_gemini),
        FunctionTool(func=analyze_market_trends_with_gemini),
        FunctionTool(func=generate_strategic_recommendation_with_gemini),
    ],
    output_key="ai_opportunity_scoring",
)
