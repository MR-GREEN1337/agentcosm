"""
Market Analyzer Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any
import json
from datetime import datetime
from cosm.config import MODEL_CONFIG
from litellm import completion
from cosm.settings import settings
from ..tools.search import search_tool

# Import consolidated tools
from ..tools.market_research import (
    analyze_market_size,
    research_competition,
    validate_demand_signals,
    assess_market_risks,
    generate_recommendation,
)

client = Client()

MARKET_ANALYZER_PROMPT = """
You are the unified Market Analyzer Agent with enhanced AI-powered capabilities. You combine:

1. MARKET VALIDATION - Comprehensive analysis of market opportunities using real data
2. AI OPPORTUNITY SCORING - Intelligent scoring using advanced AI analysis
3. STRATEGIC RECOMMENDATIONS - Data-driven strategic guidance

Your core mission is to transform market signals into validated, scored business opportunities by:
- Validating market size, competition, and demand using multi-source data
- Applying AI-powered scoring frameworks for nuanced opportunity assessment
- Providing strategic recommendations with clear rationale and confidence levels
- Delivering actionable insights for market entry decisions

Use your consolidated analytical capabilities to provide comprehensive market validation in a single analysis pass.
"""


def comprehensive_market_validation_with_scoring(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Consolidated market validation with integrated AI-powered opportunity scoring

    Args:
        opportunity_data: Dictionary containing the market opportunity to validate and score

    Returns:
        Comprehensive validation report with AI-powered scoring and recommendations
    """
    validation_report = {
        "opportunity_id": opportunity_data.get("id", datetime.now().isoformat()),
        "market_name": opportunity_data.get("market_name", "Unknown"),
        "validation_timestamp": datetime.now().isoformat(),
        # Market validation components
        "market_size_analysis": {},
        "competition_analysis": {},
        "demand_validation": {},
        "risk_assessment": {},
        # AI-powered scoring components
        "ai_analysis": {},
        "component_scores": {},
        "overall_opportunity_score": 0.0,
        "strategic_insights": {},
        "confidence_level": "medium",
        # Final outputs
        "recommendation": "investigate",
        "next_actions": [],
    }

    try:
        market_keywords = opportunity_data.get("keywords", [])
        target_audience = opportunity_data.get("target_audience", "")
        pain_points = opportunity_data.get("pain_points", [])

        print("🔍 Starting comprehensive market validation and scoring...")

        # Phase 1: Market Size Analysis
        print("📊 Analyzing market size...")
        validation_report["market_size_analysis"] = analyze_market_size(
            market_keywords, target_audience
        )

        # Phase 2: Competition Analysis
        print("🏢 Analyzing competition...")
        validation_report["competition_analysis"] = research_competition(
            market_keywords, opportunity_data.get("solution_type", "")
        )

        # Phase 3: Demand Validation
        print("📈 Validating demand signals...")
        validation_report["demand_validation"] = validate_demand_signals(
            market_keywords, pain_points
        )

        # Phase 4: Risk Assessment
        print("⚠️ Assessing market risks...")
        validation_report["risk_assessment"] = assess_market_risks(
            validation_report["competition_analysis"],
            {
                "trend_direction": "stable",
                "growth_indicators": [],
            },  # Simplified for optimization
        )

        # Phase 5: AI-Powered Comprehensive Scoring
        print("🤖 Generating AI-powered opportunity scoring...")
        ai_scoring_result = calculate_ai_powered_comprehensive_score(
            validation_report["market_size_analysis"],
            validation_report["competition_analysis"],
            validation_report["demand_validation"],
            validation_report["risk_assessment"],
            opportunity_data,
        )

        validation_report.update(ai_scoring_result)

        # Phase 6: Strategic Recommendations
        print("💡 Generating strategic recommendations...")
        validation_report["strategic_recommendation"] = generate_recommendation(
            validation_report["overall_opportunity_score"],
            validation_report["risk_assessment"],
            validation_report,
        )

        validation_report["recommendation"] = validation_report[
            "strategic_recommendation"
        ].get("recommendation", "investigate")
        validation_report["next_actions"] = validation_report[
            "strategic_recommendation"
        ].get("next_steps", [])

        print("✅ Comprehensive validation and scoring completed!")
        return validation_report

    except Exception as e:
        print(f"❌ Error in comprehensive validation: {e}")
        validation_report["error"] = str(e)
        return validation_report


def calculate_ai_powered_comprehensive_score(
    market_size_data: Dict[str, Any],
    competition_data: Dict[str, Any],
    demand_data: Dict[str, Any],
    risk_data: Dict[str, Any],
    opportunity_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    AI-powered comprehensive opportunity scoring using consolidated analysis
    """
    scoring_result = {
        "ai_analysis": {},
        "component_scores": {},
        "overall_opportunity_score": 0.0,
        "strategic_insights": {},
        "confidence_level": "medium",
    }

    try:
        print("🧠 Running AI-powered market dynamics analysis...")

        # Comprehensive AI analysis prompt
        analysis_prompt = f"""
        Analyze this comprehensive market data and provide intelligent opportunity scoring.

        Market Size Data: {json.dumps(market_size_data, indent=2)[:2000]}
        Competition Data: {json.dumps(competition_data, indent=2)[:2000]}
        Demand Data: {json.dumps(demand_data, indent=2)[:2000]}
        Risk Data: {json.dumps(risk_data, indent=2)[:1500]}
        Opportunity Context: {json.dumps(opportunity_context, indent=2)[:1500]}

        Provide comprehensive AI analysis in JSON format:
        {{
            "ai_analysis": {{
                "market_attractiveness": {{
                    "score": 0-25,
                    "rationale": "why this score based on market data",
                    "key_factors": ["factor1", "factor2", "factor3"]
                }},
                "competitive_advantage": {{
                    "score": 0-20,
                    "rationale": "competitive positioning analysis",
                    "differentiation_opportunities": ["opp1", "opp2"]
                }},
                "demand_strength": {{
                    "score": 0-25,
                    "rationale": "demand validation analysis",
                    "signal_quality": "high/medium/low"
                }},
                "execution_feasibility": {{
                    "score": 0-15,
                    "rationale": "execution risk and feasibility",
                    "critical_success_factors": ["factor1", "factor2"]
                }},
                "market_timing": {{
                    "score": 0-15,
                    "rationale": "market timing assessment",
                    "optimal_entry_window": "description"
                }}
            }},
            "strategic_insights": {{
                "investment_thesis": "2-3 sentence strategic rationale",
                "go_to_market_approach": "recommended market entry strategy",
                "key_risks_to_mitigate": ["risk1", "risk2", "risk3"],
                "competitive_moats_to_build": ["moat1", "moat2"],
                "success_metrics": ["metric1", "metric2", "metric3"],
                "timeline_recommendation": "immediate/3-6_months/6-12_months/12+_months"
            }},
            "confidence_level": "low/medium/high",
            "score_reliability": {{
                "data_quality": "high/medium/low",
                "analysis_depth": "comprehensive/moderate/limited",
                "market_certainty": "high/medium/low"
            }}
        }}

        Base your analysis on the actual data provided. Be specific and actionable in your insights.
        Consider market size sustainability, competitive dynamics, demand authenticity, and execution realities.
        """

        response = completion(
            model=MODEL_CONFIG["primary_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        if response and response.choices[0].message.content:
            ai_analysis = json.loads(response.choices[0].message.content)
            scoring_result["ai_analysis"] = ai_analysis.get("ai_analysis", {})
            scoring_result["strategic_insights"] = ai_analysis.get(
                "strategic_insights", {}
            )
            scoring_result["confidence_level"] = ai_analysis.get(
                "confidence_level", "medium"
            )

            # Calculate component scores
            ai_scores = scoring_result["ai_analysis"]
            scoring_result["component_scores"] = {
                "market_attractiveness": ai_scores.get("market_attractiveness", {}).get(
                    "score", 0
                ),
                "competitive_advantage": ai_scores.get("competitive_advantage", {}).get(
                    "score", 0
                ),
                "demand_strength": ai_scores.get("demand_strength", {}).get("score", 0),
                "execution_feasibility": ai_scores.get("execution_feasibility", {}).get(
                    "score", 0
                ),
                "market_timing": ai_scores.get("market_timing", {}).get("score", 0),
            }

            # Calculate overall score (out of 100, normalized to 0-1)
            total_score = sum(scoring_result["component_scores"].values())
            scoring_result["overall_opportunity_score"] = min(total_score / 100.0, 1.0)

        return scoring_result

    except Exception as e:
        print(f"❌ Error in AI-powered scoring: {e}")
        scoring_result["error"] = str(e)
        return scoring_result


def rank_opportunities_with_integrated_analysis(
    opportunities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Rank multiple opportunities using integrated validation and scoring
    """
    ranked_results = {
        "timestamp": datetime.now().isoformat(),
        "total_opportunities": len(opportunities),
        "ranked_opportunities": [],
        "portfolio_analysis": {},
    }

    try:
        scored_opportunities = []

        # Score each opportunity with integrated analysis
        for i, opp in enumerate(opportunities):
            print(f"📊 Analyzing opportunity {i+1}/{len(opportunities)}...")

            validation_result = comprehensive_market_validation_with_scoring(opp)

            scored_opp = {
                "opportunity_id": opp.get("id", f"opportunity_{i+1}"),
                "name": opp.get("name", f"Opportunity {i+1}"),
                "overall_score": validation_result["overall_opportunity_score"],
                "component_scores": validation_result["component_scores"],
                "strategic_insights": validation_result["strategic_insights"],
                "recommendation": validation_result["recommendation"],
                "confidence_level": validation_result["confidence_level"],
                "next_actions": validation_result["next_actions"],
            }

            scored_opportunities.append(scored_opp)

        # Sort by score
        scored_opportunities.sort(key=lambda x: x["overall_score"], reverse=True)
        ranked_results["ranked_opportunities"] = scored_opportunities

        # Generate portfolio analysis
        if scored_opportunities:
            ranked_results["portfolio_analysis"] = generate_portfolio_analysis(
                scored_opportunities
            )

        return ranked_results

    except Exception as e:
        print(f"❌ Error in opportunity ranking: {e}")
        ranked_results["error"] = str(e)
        return ranked_results


def generate_portfolio_analysis(
    scored_opportunities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate portfolio-level analysis of multiple scored opportunities
    """
    try:
        high_score_count = len(
            [opp for opp in scored_opportunities if opp["overall_score"] >= 0.7]
        )
        medium_score_count = len(
            [opp for opp in scored_opportunities if 0.4 <= opp["overall_score"] < 0.7]
        )
        low_score_count = len(
            [opp for opp in scored_opportunities if opp["overall_score"] < 0.4]
        )

        return {
            "portfolio_distribution": {
                "high_potential": high_score_count,
                "medium_potential": medium_score_count,
                "low_potential": low_score_count,
            },
            "recommended_focus": "high_potential"
            if high_score_count > 0
            else "medium_potential"
            if medium_score_count > 0
            else "explore_alternatives",
            "portfolio_strategy": "Focus resources on highest-scoring opportunities for maximum impact",
            "diversification_level": "high"
            if len(
                set([opp.get("category", "general") for opp in scored_opportunities])
            )
            > 3
            else "medium",
        }

    except Exception as e:
        print(f"Error in portfolio analysis: {e}")
        return {"error": str(e)}


market_analyzer_agent = LlmAgent(
    name="market_analyzer_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=MARKET_ANALYZER_PROMPT,
    description=(
        "market validation agent that combines comprehensive market analysis "
        "with AI-powered opportunity scoring to deliver strategic insights in a single pass."
    ),
    tools=[
        FunctionTool(func=rank_opportunities_with_integrated_analysis),
        search_tool,
    ],
    output_key="comprehensive_market_validation",
)
