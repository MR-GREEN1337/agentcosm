"""
Market Explorer Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any
from datetime import datetime
import json
from litellm import completion
from cosm.config import MODEL_CONFIG
from google.adk.models.lite_llm import LiteLlm
from cosm.settings import settings

# Import Tavily search tools
from ...tools.tavily import (
    tavily_search,
    tavily_market_research,
    tavily_pain_point_discovery,
    tavily_competitive_intelligence,
    tavily_market_research_tool,
    tavily_pain_point_discovery_tool,
    tavily_competitive_intelligence_tool,
    tavily_trend_analysis_tool,
)

# Initialize Gemini client
client = Client()

EXPLORER_AGENT_PROMPT = """
You are a Market Signal Explorer specializing in discovering genuine pain points and unmet needs in liminal market spaces.

Your mission is to discover opportunities that exist between established market categories by:
1. Collecting authentic user frustrations from social platforms and forums using Tavily search
2. Using AI to identify subtle patterns and connections in user complaints
3. Mapping workflow gaps and integration problems users experience
4. Finding underserved niches where mainstream solutions fail

Focus on liminal spaces where users fall through the cracks of existing solutions.
Use the Tavily search tools to gather real-time data from web sources.
"""


def discover_market_signals(query_context: str) -> Dict[str, Any]:
    """
    Enhanced approach: Tavily search + AI analysis for market signal discovery

    Args:
        query_context: The market domain or problem space to explore

    Returns:
        AI-analyzed market signals and opportunities
    """
    signals = {
        "timestamp": datetime.now().isoformat(),
        "context": query_context,
        "raw_content_collected": 0,
        "ai_analysis": {},
        "pain_point_clusters": [],
        "workflow_gaps": [],
        "integration_opportunities": [],
        "underserved_segments": [],
        "signal_confidence": 0.0,
    }

    try:
        # Phase 1: Collect raw content using Tavily search
        print(f"🔍 Collecting market signals for: {query_context}")
        collected_content = []

        # Use Tavily for pain point discovery
        pain_point_results = tavily_pain_point_discovery(
            market_keywords=[query_context],
            user_segments=["small business", "enterprise", "individual users"],
        )

        if not pain_point_results.get("error"):
            for signal in pain_point_results.get("pain_point_signals", []):
                for result in signal.get("results", []):
                    collected_content.append(
                        {
                            "source": "tavily_pain_discovery",
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[:2000],
                            "query_context": signal.get("query", ""),
                            "platform_type": "web_search",
                            "score": result.get("score", 0.0),
                        }
                    )

        # Use Tavily for market research
        market_research_results = tavily_market_research(
            keywords=[query_context], research_type="pain_points"
        )

        if not market_research_results.get("error"):
            for search_result in market_research_results.get("search_results", []):
                for result in search_result.get("results", []):
                    collected_content.append(
                        {
                            "source": "tavily_market_research",
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[:2000],
                            "query_context": search_result.get("query", ""),
                            "platform_type": "market_research",
                            "score": result.get("score", 0.0),
                        }
                    )

        # Additional targeted searches for specific pain points
        pain_point_queries = [
            f"{query_context} problems frustrated users",
            f"{query_context} doesn't work complaints",
            f"alternatives to {query_context} needed",
            f"{query_context} workflow integration issues",
        ]

        for query in pain_point_queries:
            search_result = tavily_search(
                query=query,
                max_results=3,
                search_depth="basic",
                include_answer=True,
                topic="general",
            )

            if not search_result.get("error"):
                for result in search_result.get("results", []):
                    collected_content.append(
                        {
                            "source": "tavily_direct_search",
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[:2000],
                            "query_context": query,
                            "platform_type": "direct_search",
                            "score": result.get("score", 0.0),
                        }
                    )

        signals["raw_content_collected"] = len(collected_content)

        # Phase 2: AI-powered analysis of collected content
        if collected_content:
            print(f"🤖 Analyzing {len(collected_content)} pieces of content with AI...")
            signals = analyze_signals_with_ai(collected_content, query_context, signals)

        return signals

    except Exception as e:
        print(f"Error in discover_market_signals: {e}")
        signals["error"] = str(e)
        return signals


def analyze_competitive_gaps(market_domain: str) -> Dict[str, Any]:
    """
    Enhanced competitive analysis using Tavily search + AI gap identification
    """
    gaps = {
        "market_domain": market_domain,
        "analysis_timestamp": datetime.now().isoformat(),
        "raw_data_collected": 0,
        "competitive_landscape": {},
        "identified_gaps": [],
        "market_opportunities": [],
        "positioning_strategies": [],
    }

    try:
        print(f"🔍 Analyzing competitive landscape for: {market_domain}")

        # Use Tavily for competitive intelligence
        competitive_data = tavily_competitive_intelligence(
            company_names=[],  # Will discover companies through search
            market_context=market_domain,
        )

        # Use Tavily for market research focused on competition
        market_data = tavily_market_research(
            keywords=[market_domain], research_type="competition"
        )

        # Direct searches for competitive gaps
        gap_queries = [
            f"{market_domain} market gaps opportunities",
            f"{market_domain} competitors limitations weaknesses",
            f"{market_domain} unserved market segments",
            f"why isn't there good {market_domain} solution",
        ]

        all_content = []

        # Collect competitive intelligence data
        if not competitive_data.get("error"):
            for profile in competitive_data.get("competitor_profiles", []):
                for search_result in profile.get("search_results", []):
                    for result in search_result.get("results", []):
                        all_content.append(
                            {
                                "type": "competitive_intelligence",
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "content": result.get("content", "")[:2000],
                                "company": profile.get("name", ""),
                                "score": result.get("score", 0.0),
                            }
                        )

        # Collect market research data
        if not market_data.get("error"):
            for search_result in market_data.get("search_results", []):
                for result in search_result.get("results", []):
                    all_content.append(
                        {
                            "type": "market_research",
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", "")[:2000],
                            "query": search_result.get("query", ""),
                            "score": result.get("score", 0.0),
                        }
                    )

        # Collect gap-specific data
        for query in gap_queries:
            search_result = tavily_search(
                query=query,
                max_results=3,
                search_depth="advanced",
                include_answer=True,
                topic="business",
            )

            if not search_result.get("error"):
                for result in search_result.get("results", []):
                    all_content.append(
                        {
                            "type": "gap_discussion",
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", "")[:1500],
                            "query": query,
                            "score": result.get("score", 0.0),
                        }
                    )

        gaps["raw_data_collected"] = len(all_content)

        # Phase 2: AI-powered competitive gap analysis
        if all_content:
            print("🤖 Analyzing competitive gaps with AI...")
            gaps = analyze_competitive_gaps_with_ai(all_content, market_domain, gaps)

        return gaps

    except Exception as e:
        print(f"Error in analyze_competitive_gaps: {e}")
        gaps["error"] = str(e)
        return gaps


def analyze_signals_with_ai(
    content_collection: List[Dict], query_context: str, signals: Dict
) -> Dict[str, Any]:
    """
    Use Gemini to analyze collected content for market signals and opportunities
    """
    try:
        # Prepare content for AI analysis
        content_summary = "\n\n".join(
            [
                f"Source: {item['source']} ({item.get('platform_type', 'unknown')})\n"
                f"Title: {item['title']}\n"
                f"Content: {item['content'][:800]}\n"
                f"Score: {item.get('score', 0.0)}"
                for item in content_collection[
                    :12
                ]  # Max 12 items to prevent token overflow
            ]
        )

        analysis_prompt = f"""
        Analyze this user-generated content about "{query_context}" to discover market signals and opportunities.

        Content to analyze:
        {content_summary}

        Provide comprehensive market signal analysis in JSON format:
        {{
            "ai_analysis": {{
                "overall_sentiment": "frustrated/neutral/satisfied",
                "primary_pain_themes": ["Main themes of user frustration"],
                "signal_strength": "strong/moderate/weak",
                "market_maturity": "early/growing/mature",
                "urgency_indicators": ["Signs that solutions are needed urgently"]
            }},
            "pain_point_clusters": [
                {{
                    "cluster_name": "Name for this pain point group",
                    "description": "What users are struggling with",
                    "frequency": "how_often_mentioned",
                    "severity": "high/medium/low",
                    "affected_users": "Who experiences this pain",
                    "current_workarounds": "How users currently cope",
                    "opportunity_size": "small/medium/large"
                }}
            ],
            "workflow_gaps": [
                {{
                    "gap_description": "Specific workflow breakdown",
                    "tools_involved": ["Tools/systems mentioned"],
                    "manual_processes": "What users do manually",
                    "integration_failures": "Where systems don't connect",
                    "time_impact": "How much time this wastes",
                    "automation_potential": "high/medium/low"
                }}
            ],
            "integration_opportunities": [
                {{
                    "integration_need": "What needs to be connected",
                    "systems_mentioned": ["Specific tools/platforms"],
                    "use_case": "Why users need this integration",
                    "current_alternatives": "Existing solutions mentioned",
                    "market_gap": "Why current solutions fail"
                }}
            ],
            "underserved_segments": [
                {{
                    "segment_description": "Who is underserved",
                    "specific_needs": "Their unique requirements",
                    "why_underserved": "Why mainstream solutions don't work",
                    "size_indicators": "Evidence of segment size",
                    "willingness_to_pay": "Signs they'd pay for solutions"
                }}
            ],
            "emerging_behaviors": [
                {{
                    "behavior": "New way users are working/acting",
                    "driver": "What's causing this behavior",
                    "tools_needed": "What tools would support this",
                    "trend_strength": "strong/emerging/weak"
                }}
            ],
            "solution_directions": [
                {{
                    "solution_type": "Type of solution needed",
                    "key_features": ["Must-have features mentioned"],
                    "integration_requirements": ["What it needs to work with"],
                    "user_priorities": ["What users care most about"],
                    "differentiation_opportunities": ["How to stand out"]
                }}
            ],
            "market_timing_signals": [
                {{
                    "signal": "Indicator about market timing",
                    "implication": "What this means for timing",
                    "urgency": "high/medium/low"
                }}
            ],
            "confidence_assessment": {{
                "data_quality": "high/medium/low",
                "source_diversity": "high/medium/low",
                "signal_consistency": "high/medium/low",
                "overall_confidence": "0.0-1.0 score"
            }},
            "key_insights": [
                "Most important discoveries for entrepreneurs"
            ]
        }}

        Focus on finding genuine market gaps and unmet needs, especially those that exist between established product categories.
        """

        response = completion(
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            ai_analysis = json.loads(response.choices[0].message.content)

            # Merge AI analysis into signals structure
            signals.update(ai_analysis)

            # Extract confidence score
            confidence_data = ai_analysis.get("confidence_assessment", {})
            signals["signal_confidence"] = float(
                confidence_data.get("overall_confidence", 0.5)
            )

            return signals

    except Exception as e:
        print(f"Error in AI analysis: {e}")
        signals["ai_analysis_error"] = str(e)

    return signals


def analyze_competitive_gaps_with_ai(
    content_collection: List[Dict], market_domain: str, gaps: Dict
) -> Dict[str, Any]:
    """
    Use AI to analyze competitive landscape and identify gaps
    """
    try:
        content_text = "\n\n".join(
            [
                f"Type: {item['type']}\n"
                f"Title: {item['title']}\n"
                f"Content: {item['content'][:700]}\n"
                f"Score: {item.get('score', 0.0)}"
                for item in content_collection[:10]
            ]
        )

        competitive_prompt = f"""
        Analyze the competitive landscape and market gaps for "{market_domain}".

        Research content:
        {content_text}

        Provide competitive gap analysis in JSON format:
        {{
            "competitive_landscape": {{
                "market_maturity": "early/growth/mature/declining",
                "dominant_players": ["Key market leaders identified"],
                "solution_categories": ["Types of solutions available"],
                "pricing_patterns": ["Pricing approaches mentioned"],
                "target_segments": ["Who current solutions serve"],
                "common_features": ["Features most solutions have"]
            }},
            "identified_gaps": [
                {{
                    "gap_type": "functionality/market/pricing/user_experience",
                    "gap_description": "Specific unmet need or limitation",
                    "evidence": "What proves this gap exists",
                    "affected_users": "Who experiences this gap",
                    "current_workarounds": "How users currently cope",
                    "opportunity_size": "large/medium/small"
                }}
            ],
            "market_opportunities": [
                {{
                    "opportunity": "Specific business opportunity",
                    "target_segment": "Who would benefit most",
                    "solution_approach": "How to address this opportunity",
                    "competitive_advantage": "Why this would work",
                    "market_entry_strategy": "How to enter this space",
                    "timing": "immediate/6_months/12_months"
                }}
            ],
            "positioning_strategies": [
                {{
                    "strategy": "How to position against competitors",
                    "differentiation": "Key differentiating factors",
                    "value_proposition": "Unique value to offer",
                    "messaging_direction": "How to communicate advantage"
                }}
            ],
            "underserved_niches": [
                {{
                    "niche_description": "Specific underserved market",
                    "why_underserved": "Why competitors ignore this",
                    "size_potential": "Evidence of market size",
                    "entry_barriers": "low/medium/high",
                    "solution_requirements": "What solution would need"
                }}
            ],
            "innovation_opportunities": [
                {{
                    "innovation_area": "Where innovation is needed",
                    "current_limitations": "What current solutions can't do",
                    "technology_enablers": "What makes innovation possible now",
                    "user_impact": "How this would help users"
                }}
            ],
            "key_insights": [
                "Most valuable insights for market entry strategy"
            ]
        }}

        Focus on finding genuine gaps where new solutions could create significant value.
        """

        response = completion(
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": competitive_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            analysis = json.loads(response.choices[0].message.content)
            gaps.update(analysis)
            return gaps

    except Exception as e:
        print(f"Error in competitive AI analysis: {e}")
        gaps["ai_analysis_error"] = str(e)

    return gaps


def validate_signals_cross_platform(signals_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cross-validate signals across different platforms for reliability
    """
    validation = {
        "cross_platform_consistency": {},
        "signal_reliability": {},
        "confidence_boost_factors": [],
        "validation_score": 0.0,
    }

    try:
        # This would use AI to compare signals across platforms
        # and assess consistency/reliability
        pain_clusters = signals_data.get("pain_point_clusters", [])

        if len(pain_clusters) >= 2:
            validation["cross_platform_consistency"] = "high"
            validation["validation_score"] = 0.8
        elif len(pain_clusters) >= 1:
            validation["cross_platform_consistency"] = "medium"
            validation["validation_score"] = 0.6
        else:
            validation["cross_platform_consistency"] = "low"
            validation["validation_score"] = 0.3

        return validation

    except Exception as e:
        print(f"Error in signal validation: {e}")
        return validation


# Create the hybrid market explorer agent
market_explorer_agent = LlmAgent(
    name="market_explorer_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["market_explorer"], api_key=settings.OPENAI_API_KEY
    ),
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "Hybrid market signal explorer that combines web scraping with AI-powered "
        "analysis to discover genuine opportunities in liminal market spaces."
    ),
    tools=[
        FunctionTool(func=discover_market_signals),
        FunctionTool(func=analyze_competitive_gaps),
        FunctionTool(func=validate_signals_cross_platform),
        tavily_market_research_tool,
        tavily_pain_point_discovery_tool,
        tavily_competitive_intelligence_tool,
        tavily_trend_analysis_tool,
        # google_search,
        # load_web_page,
    ],
    output_key="market_signals",
)
