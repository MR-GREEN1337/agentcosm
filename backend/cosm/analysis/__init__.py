"""
Market Analyzer Agent - Validates market opportunities with real data
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.load_web_page import load_web_page


from typing import Dict, Any
import re
from datetime import datetime

from ..tools.market_research import (
    analyze_market_size,
    research_competition,
    validate_demand_signals,
    assess_market_risks,
    calculate_opportunity_score_real,
    generate_recommendation,
)
from ..tools.trend_tracker import analyze_search_trends
from cosm.prompts import MARKET_ANALYZER_PROMPT


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
        "recommendation": "pending",
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
            validation_report["trend_analysis"],
        )

        # 6. Calculate Opportunity Score
        validation_report["opportunity_score"] = calculate_opportunity_score_real(
            validation_report
        )

        # 7. Generate Recommendation
        validation_report["recommendation"] = generate_recommendation(
            validation_report["opportunity_score"], validation_report["risk_assessment"]
        )

        return validation_report

    except Exception as e:
        print(f"Error in comprehensive_market_validation: {e}")
        validation_report["error"] = str(e)
        return validation_report


def research_market_demographics(
    target_market: str, geography: str = "global"
) -> Dict[str, Any]:
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
        "growth_projections": {},
    }

    try:
        # Search for demographic data
        demo_queries = [
            f"{target_market} demographics statistics",
            f"{target_market} market size {geography}",
            f"{target_market} consumer behavior research",
            f"{target_market} spending trends 2024",
        ]

        for query in demo_queries:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:3]:
                    try:
                        content = load_web_page(result.url)
                        # Extract demographic insights from content
                        insights = extract_demographic_insights(content, target_market)
                        demographics.update(insights)
                    except Exception:
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
            r"(\d+)[-–](\d+)\s*years?\s*old",
            r"age\s*(\d+)[-–](\d+)",
            r"(\d+)[-–](\d+)\s*age",
        ]

        for pattern in age_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                insights["age_ranges"] = matches[:3]  # Top 3 age ranges
                break

        # Look for income data
        income_patterns = [
            r"\$(\d+(?:,\d+)*)\s*(?:to|[-–])\s*\$(\d+(?:,\d+)*)",
            r"income.*?\$(\d+(?:,\d+)*)",
            r"\$(\d+(?:,\d+)*)\s*income",
        ]

        for pattern in income_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                insights["income_data"] = matches[:3]
                break

        return insights

    except Exception:
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
        load_web_page,
    ],
    output_key="market_validation",
)
