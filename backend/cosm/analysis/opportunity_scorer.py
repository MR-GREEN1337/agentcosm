"""
Opportunity Scorer Agent - Scores and ranks market opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, List, Any, Optional
import json
import math
from datetime import datetime

client = Client()

OPPORTUNITY_SCORER_PROMPT = """
You are an expert market opportunity scoring agent. Your role is to:

1. Analyze market opportunity data objectively
2. Apply scoring frameworks to evaluate potential
3. Rank opportunities based on multiple criteria
4. Provide clear recommendations with reasoning
5. Identify risks and mitigation strategies

Use data-driven approaches to score opportunities across dimensions like:
- Market size and growth potential
- Competition levels and barriers to entry
- Demand validation and trend analysis
- Technical feasibility and resource requirements
- Risk factors and market timing

Always provide transparent scoring methodology and actionable insights.
"""

def calculate_opportunity_score(
    market_size_data: Dict[str, Any],
    competition_data: Dict[str, Any], 
    demand_data: Dict[str, Any],
    trend_data: Dict[str, Any],
    risk_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate comprehensive opportunity score based on multiple factors
    
    Args:
        market_size_data: Market size and TAM/SAM data
        competition_data: Competitive landscape analysis
        demand_data: Demand validation signals
        trend_data: Market trend analysis
        risk_data: Risk assessment data
        
    Returns:
        Comprehensive scoring results with breakdown
    """
    try:
        scoring_result = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0.0,
            "component_scores": {},
            "score_breakdown": {},
            "recommendation": "",
            "confidence_level": "medium",
            "key_strengths": [],
            "key_weaknesses": [],
            "risk_factors": [],
            "next_steps": []
        }
        
        # 1. Market Size Score (0-25 points)
        market_score = _calculate_market_size_score(market_size_data)
        scoring_result["component_scores"]["market_size"] = market_score
        
        # 2. Competition Score (0-20 points)
        competition_score = _calculate_competition_score(competition_data)
        scoring_result["component_scores"]["competition"] = competition_score
        
        # 3. Demand Score (0-25 points)
        demand_score = _calculate_demand_score(demand_data)
        scoring_result["component_scores"]["demand"] = demand_score
        
        # 4. Trend Score (0-15 points)
        trend_score = _calculate_trend_score(trend_data)
        scoring_result["component_scores"]["trends"] = trend_score
        
        # 5. Risk Score (0-15 points penalty reduction)
        risk_score = _calculate_risk_score(risk_data)
        scoring_result["component_scores"]["risk_mitigation"] = risk_score
        
        # Calculate overall score
        total_score = market_score + competition_score + demand_score + trend_score + risk_score
        scoring_result["overall_score"] = min(total_score / 100.0, 1.0)  # Normalize to 0-1
        
        # Generate detailed breakdown
        scoring_result["score_breakdown"] = {
            "market_size": {"score": market_score, "weight": "25%", "rationale": _get_market_size_rationale(market_size_data)},
            "competition": {"score": competition_score, "weight": "20%", "rationale": _get_competition_rationale(competition_data)},
            "demand": {"score": demand_score, "weight": "25%", "rationale": _get_demand_rationale(demand_data)},
            "trends": {"score": trend_score, "weight": "15%", "rationale": _get_trend_rationale(trend_data)},
            "risk_mitigation": {"score": risk_score, "weight": "15%", "rationale": _get_risk_rationale(risk_data)}
        }
        
        # Generate recommendation
        scoring_result["recommendation"] = _generate_recommendation(scoring_result["overall_score"])
        
        # Determine confidence level
        scoring_result["confidence_level"] = _calculate_confidence_level(
            market_size_data, competition_data, demand_data, trend_data, risk_data
        )
        
        # Extract key insights
        scoring_result["key_strengths"] = _extract_strengths(market_size_data, competition_data, demand_data, trend_data)
        scoring_result["key_weaknesses"] = _extract_weaknesses(market_size_data, competition_data, demand_data, trend_data)
        scoring_result["risk_factors"] = _extract_risk_factors(risk_data)
        scoring_result["next_steps"] = _generate_next_steps(scoring_result["overall_score"], scoring_result["key_weaknesses"])
        
        return scoring_result
        
    except Exception as e:
        return {
            "error": f"Scoring calculation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def _calculate_market_size_score(market_data: Dict[str, Any]) -> float:
    """Calculate market size component score (0-25 points)"""
    try:
        tam = market_data.get("tam_estimate", 0)
        growth_rate = market_data.get("growth_rate", 0)
        addressable_percentage = market_data.get("addressable_percentage", 10)
        
        # TAM scoring (0-15 points)
        if tam >= 1000000000:  # $1B+
            tam_score = 15
        elif tam >= 100000000:  # $100M+
            tam_score = 12
        elif tam >= 10000000:   # $10M+
            tam_score = 8
        elif tam >= 1000000:    # $1M+
            tam_score = 4
        else:
            tam_score = 1
        
        # Growth rate scoring (0-5 points)
        growth_score = min(growth_rate / 20.0 * 5, 5)  # 20% growth = full points
        
        # Addressable market scoring (0-5 points)
        addressable_score = min(addressable_percentage / 20.0 * 5, 5)  # 20% addressable = full points
        
        return tam_score + growth_score + addressable_score
        
    except Exception:
        return 0.0

def _calculate_competition_score(competition_data: Dict[str, Any]) -> float:
    """Calculate competition component score (0-20 points)"""
    try:
        competition_level = competition_data.get("competition_level", "high")
        direct_competitors = len(competition_data.get("direct_competitors", []))
        market_gaps = len(competition_data.get("market_gaps", []))
        
        # Competition level scoring (0-12 points)
        if competition_level == "low":
            comp_score = 12
        elif competition_level == "medium":
            comp_score = 8
        else:  # high competition
            comp_score = 3
        
        # Number of competitors penalty (0-4 points deduction)
        if direct_competitors <= 2:
            competitor_penalty = 0
        elif direct_competitors <= 5:
            competitor_penalty = 2
        else:
            competitor_penalty = 4
        
        # Market gaps bonus (0-4 points)
        gap_bonus = min(market_gaps * 1.5, 4)
        
        return max(comp_score - competitor_penalty + gap_bonus, 0)
        
    except Exception:
        return 0.0

def _calculate_demand_score(demand_data: Dict[str, Any]) -> float:
    """Calculate demand component score (0-25 points)"""
    try:
        signal_strength = demand_data.get("signal_strength", 0)
        search_volume = demand_data.get("search_volume", 0)
        growth_indicators = len(demand_data.get("growth_indicators", []))
        validation_sources = len(demand_data.get("validation_sources", []))
        
        # Signal strength scoring (0-10 points)
        signal_score = min(signal_strength / 100.0 * 10, 10)
        
        # Search volume scoring (0-8 points)
        if search_volume >= 100000:
            volume_score = 8
        elif search_volume >= 10000:
            volume_score = 6
        elif search_volume >= 1000:
            volume_score = 4
        else:
            volume_score = 1
        
        # Growth indicators (0-4 points)
        growth_score = min(growth_indicators * 1.5, 4)
        
        # Validation sources (0-3 points)
        validation_score = min(validation_sources, 3)
        
        return signal_score + volume_score + growth_score + validation_score
        
    except Exception:
        return 0.0

def _calculate_trend_score(trend_data: Dict[str, Any]) -> float:
    """Calculate trend component score (0-15 points)"""
    try:
        trend_direction = trend_data.get("trend_direction", "stable")
        momentum_score = trend_data.get("momentum_score", 0.5)
        emerging_tech = len(trend_data.get("emerging_technologies", []))
        
        # Trend direction scoring (0-8 points)
        if trend_direction == "growing":
            direction_score = 8
        elif trend_direction == "stable":
            direction_score = 5
        else:  # declining
            direction_score = 1
        
        # Momentum scoring (0-4 points)
        momentum_points = momentum_score * 4
        
        # Emerging tech bonus (0-3 points)
        tech_bonus = min(emerging_tech * 1.5, 3)
        
        return direction_score + momentum_points + tech_bonus
        
    except Exception:
        return 0.0

def _calculate_risk_score(risk_data: Dict[str, Any]) -> float:
    """Calculate risk mitigation score (0-15 points)"""
    try:
        overall_risk = risk_data.get("overall_risk", "medium")
        risk_factors = len(risk_data.get("risk_factors", []))
        mitigation_strategies = len(risk_data.get("mitigation_strategies", []))
        
        # Base risk scoring (0-10 points)
        if overall_risk == "low":
            base_score = 10
        elif overall_risk == "medium":
            base_score = 6
        else:  # high risk
            base_score = 2
        
        # Risk factor penalty
        risk_penalty = min(risk_factors * 1.5, 5)
        
        # Mitigation bonus
        mitigation_bonus = min(mitigation_strategies * 2, 5)
        
        return max(base_score - risk_penalty + mitigation_bonus, 0)
        
    except Exception:
        return 0.0

def _get_market_size_rationale(market_data: Dict[str, Any]) -> str:
    """Generate rationale for market size scoring"""
    tam = market_data.get("tam_estimate", 0)
    if tam >= 1000000000:
        return "Large addressable market ($1B+) with significant revenue potential"
    elif tam >= 100000000:
        return "Substantial market size ($100M+) supporting viable business case"
    elif tam >= 10000000:
        return "Moderate market size ($10M+) requiring focused execution"
    else:
        return "Limited market size requiring niche positioning and efficiency"

def _get_competition_rationale(competition_data: Dict[str, Any]) -> str:
    """Generate rationale for competition scoring"""
    level = competition_data.get("competition_level", "high")
    competitors = len(competition_data.get("direct_competitors", []))
    
    if level == "low" and competitors <= 2:
        return "Low competition provides clear market entry opportunity"
    elif level == "medium":
        return "Moderate competition requires differentiation strategy"
    else:
        return "High competition demands strong value proposition and execution"

def _get_demand_rationale(demand_data: Dict[str, Any]) -> str:
    """Generate rationale for demand scoring"""
    strength = demand_data.get("signal_strength", 0)
    if strength >= 80:
        return "Strong demand signals indicate clear market need"
    elif strength >= 50:
        return "Moderate demand signals suggest viable market opportunity"
    else:
        return "Weak demand signals require additional validation"

def _get_trend_rationale(trend_data: Dict[str, Any]) -> str:
    """Generate rationale for trend scoring"""
    direction = trend_data.get("trend_direction", "stable")
    if direction == "growing":
        return "Positive market trends support opportunity timing"
    elif direction == "stable":
        return "Stable market trends provide predictable environment"
    else:
        return "Declining trends present timing and adoption challenges"

def _get_risk_rationale(risk_data: Dict[str, Any]) -> str:
    """Generate rationale for risk scoring"""
    risk_level = risk_data.get("overall_risk", "medium")
    strategies = len(risk_data.get("mitigation_strategies", []))
    
    if risk_level == "low" and strategies >= 3:
        return "Low risk profile with strong mitigation strategies"
    elif risk_level == "medium":
        return "Moderate risk requiring careful planning and execution"
    else:
        return "High risk necessitates comprehensive risk management approach"

def _generate_recommendation(score: float) -> str:
    """Generate recommendation based on overall score"""
    if score >= 0.8:
        return "STRONG PURSUE: Exceptional opportunity with high success potential"
    elif score >= 0.6:
        return "PURSUE: Strong opportunity worth investment and development"
    elif score >= 0.4:
        return "CAUTIOUS PURSUE: Moderate opportunity requiring careful validation"
    elif score >= 0.2:
        return "INVESTIGATE: Weak opportunity needing significant improvements"
    else:
        return "AVOID: Poor opportunity with high failure risk"

def _calculate_confidence_level(market_data, competition_data, demand_data, trend_data, risk_data) -> str:
    """Calculate confidence level based on data quality and completeness"""
    data_quality_score = 0
    
    # Check data completeness and quality
    if market_data.get("tam_estimate", 0) > 0:
        data_quality_score += 1
    if competition_data.get("direct_competitors"):
        data_quality_score += 1
    if demand_data.get("signal_strength", 0) > 0:
        data_quality_score += 1
    if trend_data.get("trend_direction"):
        data_quality_score += 1
    if risk_data.get("risk_factors"):
        data_quality_score += 1
    
    if data_quality_score >= 4:
        return "high"
    elif data_quality_score >= 2:
        return "medium"
    else:
        return "low"

def _extract_strengths(market_data, competition_data, demand_data, trend_data) -> List[str]:
    """Extract key strengths from the opportunity analysis"""
    strengths = []
    
    if market_data.get("tam_estimate", 0) >= 100000000:
        strengths.append("Large addressable market with significant revenue potential")
    
    if competition_data.get("competition_level") == "low":
        strengths.append("Low competitive pressure enables market capture")
    
    if demand_data.get("signal_strength", 0) >= 70:
        strengths.append("Strong demand signals validate market need")
    
    if trend_data.get("trend_direction") == "growing":
        strengths.append("Positive market trends support growth opportunity")
    
    if len(competition_data.get("market_gaps", [])) >= 2:
        strengths.append("Multiple market gaps provide differentiation opportunities")
    
    return strengths

def _extract_weaknesses(market_data, competition_data, demand_data, trend_data) -> List[str]:
    """Extract key weaknesses from the opportunity analysis"""
    weaknesses = []
    
    if market_data.get("tam_estimate", 0) < 10000000:
        weaknesses.append("Limited market size constrains revenue potential")
    
    if competition_data.get("competition_level") == "high":
        weaknesses.append("High competition increases market entry difficulty")
    
    if demand_data.get("signal_strength", 0) < 40:
        weaknesses.append("Weak demand signals indicate uncertain market need")
    
    if trend_data.get("trend_direction") == "declining":
        weaknesses.append("Declining market trends present adoption challenges")
    
    if len(competition_data.get("direct_competitors", [])) > 10:
        weaknesses.append("Saturated competitive landscape limits differentiation")
    
    return weaknesses

def _extract_risk_factors(risk_data: Dict[str, Any]) -> List[str]:
    """Extract main risk factors"""
    risk_factors = risk_data.get("risk_factors", [])
    if isinstance(risk_factors, list):
        return risk_factors[:5]  # Top 5 risks
    return []

def _generate_next_steps(score: float, weaknesses: List[str]) -> List[str]:
    """Generate recommended next steps based on score and weaknesses"""
    next_steps = []
    
    if score >= 0.6:
        next_steps.append("Develop detailed business plan and go-to-market strategy")
        next_steps.append("Secure initial funding or resource allocation")
        next_steps.append("Build minimum viable product for market testing")
    elif score >= 0.4:
        next_steps.append("Conduct additional market validation research")
        next_steps.append("Analyze competitive positioning in detail")
        next_steps.append("Develop risk mitigation strategies")
    else:
        next_steps.append("Reassess market opportunity and consider pivoting")
        next_steps.append("Strengthen value proposition and differentiation")
        next_steps.append("Gather more comprehensive market data")
    
    # Add specific steps based on weaknesses
    for weakness in weaknesses[:3]:  # Address top 3 weaknesses
        if "market size" in weakness.lower():
            next_steps.append("Explore adjacent markets or expand target segments")
        elif "competition" in weakness.lower():
            next_steps.append("Develop unique competitive advantages and barriers")
        elif "demand" in weakness.lower():
            next_steps.append("Conduct customer interviews and demand validation studies")
    
    return next_steps

def rank_opportunities(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rank multiple opportunities by their calculated scores
    
    Args:
        opportunities: List of opportunity data dictionaries
        
    Returns:
        Ranked opportunities with comparative analysis
    """
    try:
        ranked_results = {
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "ranked_opportunities": [],
            "top_opportunity": None,
            "comparative_analysis": {},
            "portfolio_recommendations": []
        }
        
        scored_opportunities = []
        
        # Score each opportunity
        for i, opp in enumerate(opportunities):
            try:
                # Extract scoring components
                market_data = opp.get("market_size", {})
                competition_data = opp.get("competition_analysis", {})
                demand_data = opp.get("demand_validation", {})
                trend_data = opp.get("trend_analysis", {})
                risk_data = opp.get("risk_assessment", {})
                
                # Calculate score
                scoring_result = calculate_opportunity_score(
                    market_data, competition_data, demand_data, trend_data, risk_data
                )
                
                scored_opp = {
                    "opportunity_id": opp.get("id", f"opportunity_{i+1}"),
                    "name": opp.get("name", f"Opportunity {i+1}"),
                    "overall_score": scoring_result["overall_score"],
                    "recommendation": scoring_result["recommendation"],
                    "key_strengths": scoring_result["key_strengths"],
                    "key_weaknesses": scoring_result["key_weaknesses"],
                    "risk_factors": scoring_result["risk_factors"],
                    "confidence_level": scoring_result["confidence_level"],
                    "component_scores": scoring_result["component_scores"],
                    "original_data": opp
                }
                
                scored_opportunities.append(scored_opp)
                
            except Exception as e:
                print(f"Error scoring opportunity {i}: {e}")
                continue
        
        # Sort by score (highest first)
        scored_opportunities.sort(key=lambda x: x["overall_score"], reverse=True)
        
        ranked_results["ranked_opportunities"] = scored_opportunities
        
        if scored_opportunities:
            ranked_results["top_opportunity"] = scored_opportunities[0]
            
            # Generate comparative analysis
            ranked_results["comparative_analysis"] = _generate_comparative_analysis(scored_opportunities)
            
            # Generate portfolio recommendations
            ranked_results["portfolio_recommendations"] = _generate_portfolio_recommendations(scored_opportunities)
        
        return ranked_results
        
    except Exception as e:
        return {
            "error": f"Ranking failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def _generate_comparative_analysis(scored_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comparative analysis between opportunities"""
    if len(scored_opportunities) < 2:
        return {"note": "Need at least 2 opportunities for comparison"}
    
    analysis = {
        "score_range": {
            "highest": scored_opportunities[0]["overall_score"],
            "lowest": scored_opportunities[-1]["overall_score"],
            "spread": scored_opportunities[0]["overall_score"] - scored_opportunities[-1]["overall_score"]
        },
        "strength_patterns": {},
        "common_weaknesses": {},
        "risk_distribution": {}
    }
    
    # Analyze common patterns
    all_strengths = []
    all_weaknesses = []
    all_risks = []
    
    for opp in scored_opportunities:
        all_strengths.extend(opp.get("key_strengths", []))
        all_weaknesses.extend(opp.get("key_weaknesses", []))
        all_risks.extend(opp.get("risk_factors", []))
    
    # Count frequency of strengths/weaknesses/risks
    from collections import Counter
    
    analysis["strength_patterns"] = dict(Counter(all_strengths).most_common(5))
    analysis["common_weaknesses"] = dict(Counter(all_weaknesses).most_common(5))
    analysis["risk_distribution"] = dict(Counter(all_risks).most_common(5))
    
    return analysis

def _generate_portfolio_recommendations(scored_opportunities: List[Dict[str, Any]]) -> List[str]:
    """Generate portfolio-level recommendations"""
    recommendations = []
    
    high_score_count = len([opp for opp in scored_opportunities if opp["overall_score"] >= 0.6])
    medium_score_count = len([opp for opp in scored_opportunities if 0.4 <= opp["overall_score"] < 0.6])
    
    if high_score_count >= 2:
        recommendations.append("Focus resources on top 2-3 high-scoring opportunities")
        recommendations.append("Consider parallel development of strongest opportunities")
    elif high_score_count == 1:
        recommendations.append("Prioritize single high-scoring opportunity while improving others")
    
    if medium_score_count >= 3:
        recommendations.append("Investigate medium-scoring opportunities for improvement potential")
    
    if len(scored_opportunities) > 5:
        recommendations.append("Consider portfolio pruning to focus on top performers")
    
    return recommendations

def generate_scoring_report(opportunity_data: Dict[str, Any]) -> str:
    """
    Generate a comprehensive scoring report using AI
    
    Args:
        opportunity_data: Complete opportunity analysis data
        
    Returns:
        Formatted scoring report as string
    """
    try:
        prompt = f"""
        Generate a comprehensive market opportunity scoring report based on this data:
        
        {json.dumps(opportunity_data, indent=2)}
        
        Include:
        1. Executive Summary with key findings
        2. Detailed scoring breakdown by component
        3. Strengths and opportunities analysis
        4. Risk assessment and mitigation recommendations
        5. Next steps and action items
        6. Investment recommendation with rationale
        
        Make the report professional, data-driven, and actionable.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        
        if response and response.text:
            return response.text
        else:
            return "Failed to generate scoring report"
            
    except Exception as e:
        return f"Report generation failed: {str(e)}"

# Create the opportunity scorer agent
opportunity_scorer_agent = LlmAgent(
    name="opportunity_scorer_agent", 
    model="gemini-2.0-flash",
    instruction=OPPORTUNITY_SCORER_PROMPT,
    description=(
        "Analyzes and scores market opportunities using comprehensive "
        "multi-factor evaluation frameworks and provides actionable recommendations."
    ),
    tools=[
        FunctionTool(func=calculate_opportunity_score),
        FunctionTool(func=rank_opportunities),
        FunctionTool(func=generate_scoring_report)
    ],
    output_key="opportunity_scoring"
)