"""
Tavily Search Tool - Production-ready web search for market research
"""

from typing import Dict, List, Any
from datetime import datetime
from tavily import TavilyClient
from google.adk.tools import FunctionTool
from cosm.settings import settings


# Initialize Tavily client
def get_tavily_client():
    """Get Tavily client with API key from environment"""
    api_key = settings.TAVI_API_KEY
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyClient(api_key=api_key)


def tavily_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_answer: bool = True,
    include_raw_content: bool = False,
    topic: str = "general",
) -> Dict[str, Any]:
    """
    Performs web search using Tavily API optimized for market research

    Args:
        query: Search query
        max_results: Maximum number of results to return
        search_depth: "basic" or "advanced" search depth
        include_answer: Whether to include AI-generated answer
        include_raw_content: Whether to include raw HTML content
        topic: Topic context for better search results

    Returns:
        Search results with metadata
    """
    search_results = {
        "query": query,
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "results": [],
        "answer": "",
        "search_metadata": {},
        "error": None,
    }

    try:
        client = get_tavily_client()

        # Perform search
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            topic=topic,
        )

        # Process results
        search_results["results"] = [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "published_date": result.get("published_date", ""),
                "raw_content": result.get("raw_content", "")
                if include_raw_content
                else None,
            }
            for result in response.get("results", [])
        ]

        # Add AI answer if available
        if include_answer and "answer" in response:
            search_results["answer"] = response["answer"]

        # Add search metadata
        search_results["search_metadata"] = {
            "search_depth": search_depth,
            "results_count": len(search_results["results"]),
            "total_available": response.get("total", 0),
            "search_time": response.get("search_time", 0),
        }

        return search_results

    except Exception as e:
        search_results["error"] = str(e)
        print(f"Tavily search error for query '{query}': {e}")
        return search_results


def tavily_market_research(
    keywords: List[str], research_type: str = "market_analysis"
) -> Dict[str, Any]:
    """
    Specialized market research using Tavily with optimized queries

    Args:
        keywords: List of keywords to research
        research_type: Type of research (market_analysis, competition, trends, demand)

    Returns:
        Comprehensive market research results
    """
    research_data = {
        "keywords": keywords,
        "research_type": research_type,
        "timestamp": datetime.now().isoformat(),
        "search_results": [],
        "aggregated_insights": {},
        "confidence_score": 0.0,
    }

    try:
        # Define search strategies based on research type
        search_strategies = {
            "market_analysis": [
                "{keyword} market size 2024 analysis",
                "{keyword} industry trends growth",
                "{keyword} market research report",
            ],
            "competition": [
                "{keyword} competitors market leaders",
                "best {keyword} alternatives comparison",
                "{keyword} competitive landscape analysis",
            ],
            "trends": [
                "{keyword} trends 2024 emerging",
                "{keyword} future predictions growth",
                "{keyword} innovation technology trends",
            ],
            "demand": [
                "{keyword} demand statistics usage",
                "{keyword} market adoption growth",
                "{keyword} user problems complaints",
            ],
            "pain_points": [
                "{keyword} problems frustrations users",
                "{keyword} limitations issues challenges",
                "{keyword} user complaints feedback",
            ],
        }

        queries = search_strategies.get(
            research_type, search_strategies["market_analysis"]
        )

        # Perform searches for each keyword
        for keyword in keywords[:3]:  # Limit to prevent API overuse
            keyword_results = []

            for query_template in queries:
                query = query_template.format(keyword=keyword)

                # Perform Tavily search
                search_result = tavily_search(
                    query=query,
                    max_results=3,
                    search_depth="advanced",
                    include_answer=True,
                    topic="business",
                )

                if not search_result.get("error"):
                    keyword_results.append(search_result)

            research_data["search_results"].extend(keyword_results)

        # Calculate confidence score
        research_data["confidence_score"] = calculate_research_confidence(research_data)

        return research_data

    except Exception as e:
        research_data["error"] = str(e)
        print(f"Market research error: {e}")
        return research_data


def tavily_competitive_intelligence(
    company_names: List[str], market_context: str = ""
) -> Dict[str, Any]:
    """
    Gather competitive intelligence using Tavily

    Args:
        company_names: List of competitor company names
        market_context: Market context for better search results

    Returns:
        Competitive intelligence data
    """
    competitive_data = {
        "companies": company_names,
        "market_context": market_context,
        "timestamp": datetime.now().isoformat(),
        "competitor_profiles": [],
        "market_positioning": {},
        "competitive_gaps": [],
    }

    try:
        for company in company_names[:5]:  # Limit API calls
            # Search for company information
            company_queries = [
                f"{company} business model revenue pricing",
                f"{company} market position competitive advantage",
                f"{company} customer reviews complaints limitations",
                f"{company} {market_context} features comparison",
            ]

            company_profile = {
                "name": company,
                "search_results": [],
                "key_insights": [],
            }

            for query in company_queries:
                search_result = tavily_search(
                    query=query,
                    max_results=2,
                    search_depth="advanced",
                    include_answer=True,
                    topic="business",
                )

                if not search_result.get("error"):
                    company_profile["search_results"].append(search_result)

            competitive_data["competitor_profiles"].append(company_profile)

        return competitive_data

    except Exception as e:
        competitive_data["error"] = str(e)
        print(f"Competitive intelligence error: {e}")
        return competitive_data


def tavily_trend_analysis(topics: List[str], timeframe: str = "2024") -> Dict[str, Any]:
    """
    Analyze trends using Tavily search

    Args:
        topics: List of topics to analyze trends for
        timeframe: Timeframe for trend analysis

    Returns:
        Trend analysis data
    """
    trend_data = {
        "topics": topics,
        "timeframe": timeframe,
        "timestamp": datetime.now().isoformat(),
        "trend_results": [],
        "emerging_patterns": [],
        "growth_indicators": [],
    }

    try:
        for topic in topics[:3]:  # Limit API calls
            trend_queries = [
                f"{topic} trends {timeframe} growth statistics",
                f"{topic} market growth predictions future",
                f"{topic} emerging trends innovation {timeframe}",
                f"{topic} adoption rates user behavior {timeframe}",
            ]

            topic_trends = {"topic": topic, "search_results": []}

            for query in trend_queries:
                search_result = tavily_search(
                    query=query,
                    max_results=3,
                    search_depth="advanced",
                    include_answer=True,
                    topic="business",
                )

                if not search_result.get("error"):
                    topic_trends["search_results"].append(search_result)

            trend_data["trend_results"].append(topic_trends)

        return trend_data

    except Exception as e:
        trend_data["error"] = str(e)
        print(f"Trend analysis error: {e}")
        return trend_data


def tavily_pain_point_discovery(
    market_keywords: List[str], user_segments: List[str]
) -> Dict[str, Any]:
    """
    Discover user pain points using Tavily search

    Args:
        market_keywords: Keywords related to the market
        user_segments: Specific user segments to focus on

    Returns:
        Pain point discovery results
    """
    pain_point_data = {
        "market_keywords": market_keywords,
        "user_segments": user_segments or [],
        "timestamp": datetime.now().isoformat(),
        "pain_point_signals": [],
        "frustration_indicators": [],
        "unmet_needs": [],
    }

    try:
        pain_queries = []

        # Generate pain point queries
        for keyword in market_keywords[:3]:
            pain_queries.extend(
                [
                    f"{keyword} problems frustrations users complaints",
                    f"{keyword} limitations doesn't work issues",
                    f"{keyword} user feedback negative reviews",
                    f"why {keyword} fails problems users face",
                    f"{keyword} alternatives needed better solution",
                ]
            )

        # Add user segment specific queries
        for segment in (user_segments or [])[:2]:
            for keyword in market_keywords[:2]:
                pain_queries.append(f"{segment} {keyword} problems challenges")

        # Perform searches
        for query in pain_queries[:15]:  # Limit total queries
            search_result = tavily_search(
                query=query,
                max_results=3,
                search_depth="basic",
                include_answer=True,
                topic="general",
            )

            if not search_result.get("error"):
                pain_point_data["pain_point_signals"].append(search_result)

        return pain_point_data

    except Exception as e:
        pain_point_data["error"] = str(e)
        print(f"Pain point discovery error: {e}")
        return pain_point_data


def calculate_research_confidence(research_data: Dict[str, Any]) -> float:
    """Calculate confidence score for research results"""
    try:
        search_results = research_data.get("search_results", [])
        if not search_results:
            return 0.0

        total_results = sum(len(sr.get("results", [])) for sr in search_results)

        # Base confidence on number of results and sources
        confidence = min(total_results / 20.0, 1.0)  # Max confidence at 20+ results

        # Boost confidence if we have AI answers
        answers_count = sum(1 for sr in search_results if sr.get("answer"))
        confidence += min(answers_count / 10.0, 0.2)  # Up to 20% boost

        return min(confidence, 1.0)

    except Exception:
        return 0.5  # Default moderate confidence


# Create FunctionTool instances for use in agents
tavily_search_tool = FunctionTool(func=tavily_search)
tavily_market_research_tool = FunctionTool(func=tavily_market_research)
tavily_competitive_intelligence_tool = FunctionTool(
    func=tavily_competitive_intelligence
)
tavily_trend_analysis_tool = FunctionTool(func=tavily_trend_analysis)
tavily_pain_point_discovery_tool = FunctionTool(func=tavily_pain_point_discovery)
