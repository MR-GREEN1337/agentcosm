"""
Market Analyzer Agent - Validates market opportunities with real data
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, web_fetch
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

from ..tools.market_research import (
    analyze_market_size, research_competition, 
    validate_demand_signals, calculate_tam_sam_som
)
from ..tools.trend_tracker import (
    analyze_search_trends, track_industry_momentum,
    identify_growth_patterns
)
from ..prompts import MARKET_ANALYZER_PROMPT

def comprehensive_market_validation(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs comprehensive market validation using real data sources
    
    Args:
        opportunity_data: Dictionary containing the market opportunity to validate
        
    Returns:
        Comprehensive market validation report
    """
    validation_report = {
        "opportunity_id": opportunity_data.get("id", datetime.now().isoformat()),
        "market_name": opportunity_data.get("market_name", "Unknown"),
        "validation_timestamp": datetime.now().isoformat(),
        "market_size": {},
        "competition_analysis": {},
        "demand_validation": {},
        "trend_analysis": {},
        "risk_assessment": {},
        "opportunity_score": 0.0,
        "recommendation": "pending"
    }
    
    try:
        market_keywords = opportunity_data.get("keywords", [])
        target_audience = opportunity_data.get("target_audience", "")
        
        # 1. Market Size Analysis
        print("Analyzing market size...")
        validation_report["market_size"] = analyze_market_size(
            market_keywords, target_audience
        )
        
        # 2. Competition Analysis  
        print("Analyzing competition...")
        validation_report["competition_analysis"] = research_competition(
            market_keywords, opportunity_data.get("solution_type", "")
        )
        
        # 3. Demand Validation
        print("Validating demand signals...")
        validation_report["demand_validation"] = validate_demand_signals(
            market_keywords, opportunity_data.get("pain_points", [])
        )
        
        # 4. Trend Analysis
        print("Analyzing market trends...")
        validation_report["trend_analysis"] = analyze_search_trends(market_keywords)
        
        # 5. Risk Assessment
        print("Assessing risks...")
        validation_report["risk_assessment"] = assess_market_risks(
            validation_report["competition_analysis"],
            validation_report["trend_analysis"]
        )
        
        # 6. Calculate Opportunity Score
        validation_report["opportunity_score"] = calculate_opportunity_score(
            validation_report
        )
        
        # 7. Generate Recommendation
        validation_report["recommendation"] = generate_recommendation(
            validation_report["opportunity_score"],
            validation_report["risk_assessment"]
        )
        
        return validation_report
        
    except Exception as e:
        print(f"Error in comprehensive_market_validation: {e}")
        validation_report["error"] = str(e)
        return validation_report

def assess_market_risks(competition_data: Dict, trend_data: Dict) -> Dict[str, Any]:
    """
    Assesses market risks based on competition and trend analysis
    """
    risks = {
        "competition_risk": "low",
        "trend_risk": "low", 
        "market_saturation": "low",
        "timing_risk": "low",
        "overall_risk": "low",
        "risk_factors": [],
        "mitigation_strategies": []
    }
    
    try:
        # Analyze competition risk
        num_competitors = len(competition_data.get("direct_competitors", []))
        if num_competitors > 10:
            risks["competition_risk"] = "high"
            risks["risk_factors"].append("High number of direct competitors")
        elif num_competitors > 5:
            risks["competition_risk"] = "medium"
            risks["risk_factors"].append("Moderate competition exists")
        
        # Analyze trend risk
        trend_direction = trend_data.get("trend_direction", "stable")
        if trend_direction == "declining":
            risks["trend_risk"] = "high"
            risks["risk_factors"].append("Market trend is declining")
        elif trend_direction == "volatile":
            risks["trend_risk"] = "medium"
            risks["risk_factors"].append("Market trend is volatile")
        
        # Market saturation analysis
        search_volume = trend_data.get("search_volume", 0)
        if search_volume > 100000:  # High search volume might indicate saturation
            risks["market_saturation"] = "high"
            risks["risk_factors"].append("High search volume may indicate market saturation")
        
        # Calculate overall risk
        risk_levels = [risks["competition_risk"], risks["trend_risk"], 
                      risks["market_saturation"], risks["timing_risk"]]
        high_risks = risk_levels.count("high")
        medium_risks = risk_levels.count("medium")
        
        if high_risks >= 2:
            risks["overall_risk"] = "high"
        elif high_risks >= 1 or medium_risks >= 2:
            risks["overall_risk"] = "medium"
        
        # Generate mitigation strategies
        if risks["competition_risk"] in ["medium", "high"]:
            risks["mitigation_strategies"].append("Focus on unique value proposition and niche differentiation")
        
        if risks["trend_risk"] in ["medium", "high"]:
            risks["mitigation_strategies"].append("Monitor trend closely and pivot strategy if needed")
        
        return risks
        
    except Exception as e:
        print(f"Error assessing market risks: {e}")
        return risks

def calculate_opportunity_score(validation_data: Dict[str, Any]) -> float:
    """
    Calculates an overall opportunity score (0-1) based on validation data
    """
    try:
        score_components = {
            "market_size": 0.0,
            "demand": 0.0, 
            "competition": 0.0,
            "trends": 0.0,
            "risks": 0.0
        }
        
        # Market size score (0-0.3)
        tam = validation_data.get("market_size", {}).get("tam_estimate", 0)
        if tam > 1000000000:  # $1B+ TAM
            score_components["market_size"] = 0.3
        elif tam > 100000000:  # $100M+ TAM
            score_components["market_size"] = 0.2
        elif tam > 10000000:   # $10M+ TAM
            score_components["market_size"] = 0.15
        elif tam > 1000000:    # $1M+ TAM
            score_components["market_size"] = 0.1
        
        # Demand score (0-0.25)
        demand_signals = validation_data.get("demand_validation", {}).get("signal_strength", 0)
        score_components["demand"] = min(demand_signals / 100.0 * 0.25, 0.25)
        
        # Competition score (0-0.2) - lower competition = higher score
        competition_level = validation_data.get("competition_analysis", {}).get("competition_level", "high")
        if competition_level == "low":
            score_components["competition"] = 0.2
        elif competition_level == "medium":
            score_components["competition"] = 0.1
        else:
            score_components["competition"] = 0.05
        
        # Trends score (0-0.15)
        trend_direction = validation_data.get("trend_analysis", {}).get("trend_direction", "stable")
        if trend_direction == "growing":
            score_components["trends"] = 0.15
        elif trend_direction == "stable":
            score_components["trends"] = 0.1
        else:
            score_components["trends"] = 0.05
        
        # Risk penalty (0-0.1 deduction)
        overall_risk = validation_data.get("risk_assessment", {}).get("overall_risk", "medium")
        if overall_risk == "low":
            score_components["risks"] = 0.1
        elif overall_risk == "medium":
            score_components["risks"] = 0.05
        else:
            score_components["risks"] = 0.0
        
        total_score = sum(score_components.values())
        return min(total_score, 1.0)
        
    except Exception as e:
        print(f"Error calculating opportunity score: {e}")
        return 0.0

def generate_recommendation(opportunity_score: float, risk_assessment: Dict) -> str:
    """
    Generates actionable recommendation based on opportunity score and risks
    """
    if opportunity_score >= 0.7:
        return "STRONG PURSUE: High-potential opportunity with favorable market conditions"
    elif opportunity_score >= 0.5:
        return "CAUTIOUS PURSUE: Moderate opportunity, validate further before major investment"
    elif opportunity_score >= 0.3:
        return "INVESTIGATE: Weak signals, requires significant validation and risk mitigation"
    else:
        return "AVOID: Poor market opportunity with high risks and low potential"

def research_market_demographics(target_market: str, geography: str = "global") -> Dict[str, Any]:
    """
    Researches detailed market demographics and user behavior
    """
    demographics = {
        "target_market": target_market,
        "geography": geography,
        "age_distribution": {},
        "income_levels": {},
        "behavior_patterns": {},
        "spending_power": {},
        "growth_projections": {}
    }
    
    try:
        # Search for demographic data
        demo_queries = [
            f"{target_market} demographics statistics",
            f"{target_market} market size {geography}",
            f"{target_market} consumer behavior research",
            f"{target_market} spending trends 2024"
        ]
        
        for query in demo_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:3]:
                    try:
                        content = web_fetch(result.url)
                        # Extract demographic insights from content
                        insights = extract_demographic_insights(content, target_market)
                        demographics.update(insights)
                    except Exception as e:
                        continue
        
        return demographics
        
    except Exception as e:
        print(f"Error researching market demographics: {e}")
        return demographics

def extract_demographic_insights(content: str, target_market: str) -> Dict[str, Any]:
    """
    Extracts demographic insights from web content using pattern matching
    """
    insights = {}
    
    try:
        # Look for age-related data
        age_patterns = [
            r'(\d+)[-–](\d+)\s*years?\s*old',
            r'age\s*(\d+)[-–](\d+)',
            r'(\d+)[-–](\d+)\s*age'
        ]
        
        for pattern in age_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                insights["age_ranges"] = matches[:3]  # Top 3 age ranges
                break
        
        # Look for income data
        income_patterns = [
            r'\$(\d+(?:,\d+)*)\s*(?:to|[-–])\s*\$(\d+(?:,\d+)*)',
            r'income.*?\$(\d+(?:,\d+)*)',
            r'\$(\d+(?:,\d+)*)\s*income'
        ]
        
        for pattern in income_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                insights["income_data"] = matches[:3]
                break
        
        return insights
        
    except Exception as e:
        return {}

# Create the market analyzer agent
market_analyzer_agent = LlmAgent(
    name="market_analyzer_agent",
    model="gemini-2.0-flash",
    instruction=MARKET_ANALYZER_PROMPT,
    description=(
        "Validates market opportunities through comprehensive analysis of "
        "market size, competition, demand signals, and trend data using real sources."
    ),
    tools=[
        FunctionTool(func=comprehensive_market_validation),
        FunctionTool(func=research_market_demographics),
        google_search,
        web_fetch
    ],
    output_key="market_validation"
)