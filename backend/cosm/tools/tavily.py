"""
Optimized Tavily Search Tools - Consolidated and deduplicated
Removed redundant wrapper functions and consolidated into efficient research suite
"""

from typing import Dict, List, Any
from datetime import datetime
from tavily import TavilyClient
from google.adk.tools import FunctionTool
from cosm.settings import settings


# Initialize Tavily client (consolidated)
def get_tavily_client():
    """Get Tavily client with API key from environment"""
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyClient(api_key=api_key)


def tavily_research_suite(
    query: str,
    research_type: str = "comprehensive",
    max_results: int = 5,
    search_depth: str = "advanced",
) -> Dict[str, Any]:
    """
    CONSOLIDATED Tavily research function replacing multiple specialized functions

    Args:
        query: Search query
        research_type: "market_analysis", "competition", "pain_points", "trends", or "comprehensive"
        max_results: Maximum results per search
        search_depth: "basic" or "advanced"

    Returns:
        Comprehensive research results optimized for market intelligence
    """
    research_results = {
        "query": query,
        "research_type": research_type,
        "timestamp": datetime.now().isoformat(),
        "search_results": [],
        "insights": {},
        "confidence_score": 0.0,
        "optimization_applied": "consolidated_tavily_suite",
    }

    try:
        client = get_tavily_client()

        # Define search strategies based on research type (OPTIMIZED - fewer queries)
        if research_type == "comprehensive":
            search_queries = [
                f"{query} market analysis opportunities",
                f"{query} problems user complaints",
                f"{query} competitors market leaders",
                f"{query} trends 2025 growth",
            ]
        elif research_type == "market_analysis":
            search_queries = [
                f"{query} market size analysis",
                f"{query} industry growth trends",
            ]
        elif research_type == "competition":
            search_queries = [
                f"{query} competitors market leaders",
                f"{query} competitive landscape",
            ]
        elif research_type == "pain_points":
            search_queries = [
                f"{query} problems user frustrations",
                f"{query} limitations complaints",
            ]
        elif research_type == "trends":
            search_queries = [
                f"{query} trends 2025 emerging",
                f"{query} growth predictions",
            ]
        else:
            search_queries = [query]  # Fallback to simple search

        # Execute consolidated searches (OPTIMIZED - parallel processing ready)
        all_results = []
        for search_query in search_queries[:3]:  # LIMIT: Max 3 queries for performance
            try:
                response = client.search(
                    query=search_query,
                    search_depth=search_depth,
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False,  # OPTIMIZED: Skip raw content for speed
                    topic="general",
                )

                # Process results
                search_result = {
                    "query": search_query,
                    "results": [
                        {
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", "")[
                                :1500
                            ],  # OPTIMIZED: Limit content length
                            "score": result.get("score", 0.0),
                            "published_date": result.get("published_date", ""),
                        }
                        for result in response.get("results", [])
                    ],
                    "ai_answer": response.get("answer", "")
                    if response.get("answer")
                    else "",
                }

                all_results.append(search_result)

            except Exception as e:
                print(f"Search error for '{search_query}': {e}")
                continue

        research_results["search_results"] = all_results

        # Calculate consolidated confidence score
        total_results = sum(len(sr.get("results", [])) for sr in all_results)
        answers_count = sum(1 for sr in all_results if sr.get("ai_answer"))

        confidence = min(total_results / 15.0, 1.0)  # OPTIMIZED: Lower threshold
        confidence += min(answers_count / 3.0, 0.2)  # Bonus for AI answers

        research_results["confidence_score"] = min(confidence, 1.0)

        # Generate consolidated insights
        research_results["insights"] = generate_consolidated_insights(
            all_results, research_type
        )

        return research_results

    except Exception as e:
        research_results["error"] = str(e)
        print(f"Tavily research suite error: {e}")
        return research_results


def generate_consolidated_insights(
    search_results: List[Dict[str, Any]], research_type: str
) -> Dict[str, Any]:
    """
    Generate consolidated insights from search results (OPTIMIZED)
    """
    insights = {
        "key_themes": [],
        "opportunity_indicators": [],
        "risk_factors": [],
        "market_signals": [],
    }

    try:
        # Extract themes from all results
        all_content = []
        for search_result in search_results:
            for result in search_result.get("results", []):
                content = result.get("content", "")
                if content and len(content) > 100:  # Quality filter
                    all_content.append(content[:500])  # Limit for processing

        # Simple theme extraction (OPTIMIZED - no external AI calls)
        if research_type == "pain_points":
            pain_keywords = [
                "problem",
                "issue",
                "frustration",
                "difficulty",
                "challenge",
            ]
            insights["key_themes"] = [
                kw
                for kw in pain_keywords
                if any(kw in content.lower() for content in all_content)
            ]

        elif research_type == "competition":
            comp_keywords = ["leader", "competitor", "market share", "dominant"]
            insights["key_themes"] = [
                kw
                for kw in comp_keywords
                if any(kw in content.lower() for content in all_content)
            ]

        elif research_type == "trends":
            trend_keywords = [
                "growth",
                "increasing",
                "emerging",
                "future",
                "innovation",
            ]
            insights["key_themes"] = [
                kw
                for kw in trend_keywords
                if any(kw in content.lower() for content in all_content)
            ]

        # Opportunity indicators based on content analysis
        high_score_results = []
        for search_result in search_results:
            high_score_results.extend(
                [r for r in search_result.get("results", []) if r.get("score", 0) > 0.7]
            )

        insights["opportunity_indicators"] = [
            f"Found {len(high_score_results)} high-relevance results",
            f"Research type: {research_type}",
            "Content analysis completed",
        ]

        return insights

    except Exception as e:
        print(f"Error generating insights: {e}")
        return insights


def tavily_quick_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    OPTIMIZED quick search function for simple queries
    """
    return tavily_research_suite(
        query=query,
        research_type="simple",
        max_results=max_results,
        search_depth="basic",
    )


def tavily_comprehensive_research(keywords: List[str]) -> Dict[str, Any]:
    """
    OPTIMIZED comprehensive research for multiple keywords
    """
    if not keywords:
        return {"error": "No keywords provided"}

    # Process up to 3 keywords for performance
    consolidated_results = {
        "keywords": keywords[:3],
        "timestamp": datetime.now().isoformat(),
        "research_results": [],
        "consolidated_insights": {},
        "optimization_note": "Limited to 3 keywords for performance",
    }

    try:
        for keyword in keywords[:3]:  # PERFORMANCE LIMIT
            keyword_research = tavily_research_suite(
                query=keyword,
                research_type="comprehensive",
                max_results=3,  # REDUCED from 5
                search_depth="basic",  # OPTIMIZED: Use basic for speed
            )
            consolidated_results["research_results"].append(keyword_research)

        # Generate cross-keyword insights
        all_themes = []
        all_opportunities = []

        for research in consolidated_results["research_results"]:
            insights = research.get("insights", {})
            all_themes.extend(insights.get("key_themes", []))
            all_opportunities.extend(insights.get("opportunity_indicators", []))

        consolidated_results["consolidated_insights"] = {
            "common_themes": list(set(all_themes)),
            "total_opportunities": len(all_opportunities),
            "research_confidence": sum(
                r.get("confidence_score", 0)
                for r in consolidated_results["research_results"]
            )
            / len(consolidated_results["research_results"])
            if consolidated_results["research_results"]
            else 0,
        }

        return consolidated_results

    except Exception as e:
        consolidated_results["error"] = str(e)
        return consolidated_results


tavily_research_tool = FunctionTool(func=tavily_research_suite)
tavily_quick_search_tool = FunctionTool(func=tavily_quick_search)
tavily_comprehensive_research_tool = FunctionTool(func=tavily_comprehensive_research)

__all__ = [
    "tavily_research_suite",
    "tavily_quick_search",
    "tavily_comprehensive_research",
    "tavily_research_tool",
    "tavily_quick_search_tool",
    "tavily_comprehensive_research_tool",
]
