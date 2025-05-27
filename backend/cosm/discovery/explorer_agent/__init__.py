"""
Market Explorer Agent - Fixed import issue
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search

# Fix: Import the actual function, not the module
from google.adk.tools.load_web_page import load_web_page
from google.genai import Client, types
from typing import Dict, List, Any
from datetime import datetime
import json

# Initialize Gemini client
client = Client()

EXPLORER_AGENT_PROMPT = """
You are a Market Signal Explorer specializing in discovering genuine pain points and unmet needs in liminal market spaces.

Your mission is to discover opportunities that exist between established market categories by:
1. Collecting authentic user frustrations from social platforms and forums
2. Using AI to identify subtle patterns and connections in user complaints
3. Mapping workflow gaps and integration problems users experience
4. Finding underserved niches where mainstream solutions fail

Focus on liminal spaces where users fall through the cracks of existing solutions.
"""


def discover_market_signals(query_context: str) -> Dict[str, Any]:
    """
    Hybrid approach: Web scraping + AI analysis for market signal discovery

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
        # Phase 1: Collect raw content from multiple sources
        print(f"🔍 Collecting market signals for: {query_context}")
        collected_content = []

        # Reddit discussions
        reddit_content = collect_reddit_signals(query_context)
        collected_content.extend(reddit_content)

        # Twitter/X complaints
        twitter_content = collect_twitter_signals(query_context)
        collected_content.extend(twitter_content)

        # Forum discussions
        forum_content = collect_forum_signals(query_context)
        collected_content.extend(forum_content)

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


def collect_reddit_signals(query_context: str) -> List[Dict[str, Any]]:
    """Collect content from Reddit discussions"""
    reddit_content = []

    reddit_queries = [
        f"{query_context} problems frustrated site:reddit.com",
        f"{query_context} alternatives needed site:reddit.com",
        f"why doesn't {query_context} work site:reddit.com",
        f"{query_context} workflow integration issues site:reddit.com",
    ]

    for query in reddit_queries:
        try:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:3]:  # Top 3 per query
                    try:
                        content = load_web_page(result.url)
                        if content and len(content) > 200:
                            reddit_content.append(
                                {
                                    "source": "reddit",
                                    "url": result.url,
                                    "title": result.title,
                                    "content": content[:2000],  # Limit content length
                                    "query_context": query,
                                    "platform_type": "discussion_forum",
                                }
                            )
                    except Exception as e:
                        print(f"Error loading Reddit page: {e}")
        except Exception as e:
            print(f"Error with Reddit query: {e}")

    return reddit_content


def collect_twitter_signals(query_context: str) -> List[Dict[str, Any]]:
    """Collect content from Twitter/X complaints"""
    twitter_content = []

    twitter_queries = [
        f"{query_context} frustrated annoying site:twitter.com",
        f"{query_context} someone should build site:twitter.com",
        f"{query_context} doesn't integrate work site:twitter.com",
        f"{query_context} why is there no site:twitter.com",
    ]

    for query in twitter_queries:
        try:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:2]:  # Top 2 per query
                    try:
                        content = load_web_page(result.url)
                        if content and len(content) > 100:
                            twitter_content.append(
                                {
                                    "source": "twitter",
                                    "url": result.url,
                                    "title": result.title,
                                    "content": content[:1000],
                                    "query_context": query,
                                    "platform_type": "social_media",
                                }
                            )
                    except Exception as e:
                        print(f"Error loading Twitter page: {e}")
        except Exception as e:
            print(f"Error with Twitter query: {e}")

    return twitter_content


def collect_forum_signals(query_context: str) -> List[Dict[str, Any]]:
    """Collect content from forums and Q&A sites"""
    forum_content = []

    forum_queries = [
        f"{query_context} problems issues site:stackoverflow.com",
        f"{query_context} discussion site:news.ycombinator.com",
        f"{query_context} pain point problem site:quora.com",
        f"{query_context} integration challenges workflow",
    ]

    for query in forum_queries:
        try:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:2]:
                    try:
                        content = load_web_page(result.url)
                        if content and len(content) > 300:
                            forum_content.append(
                                {
                                    "source": "forum",
                                    "url": result.url,
                                    "title": result.title,
                                    "content": content[:1500],
                                    "query_context": query,
                                    "platform_type": "technical_forum",
                                }
                            )
                    except Exception as e:
                        print(f"Error loading forum page: {e}")
        except Exception as e:
            print(f"Error with forum query: {e}")

    return forum_content


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
                f"Source: {item['source']} ({item['platform_type']})\n"
                f"Title: {item['title']}\n"
                f"Content: {item['content'][:800]}"  # Limit per item
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=analysis_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            ai_analysis = json.loads(response.text)

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


def analyze_competitive_gaps(market_domain: str) -> Dict[str, Any]:
    """
    Hybrid competitive analysis: Web scraping + AI gap identification
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

        # Phase 1: Collect competitive intelligence
        competitive_content = collect_competitive_data(market_domain)
        gap_content = collect_gap_discussions(market_domain)

        all_content = competitive_content + gap_content
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


def collect_competitive_data(market_domain: str) -> List[Dict[str, Any]]:
    """Collect data about existing solutions"""
    competitive_content = []

    solution_queries = [
        f"best {market_domain} tools software 2024",
        f"{market_domain} platform comparison review",
        f"top {market_domain} solutions market leaders",
        f"{market_domain} startup competitors landscape",
    ]

    for query in solution_queries:
        try:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:3]:
                    try:
                        content = load_web_page(result.url)
                        if content and len(content) > 400:
                            competitive_content.append(
                                {
                                    "type": "competitive_intelligence",
                                    "title": result.title,
                                    "url": result.url,
                                    "content": content[:2000],
                                    "query": query,
                                }
                            )
                    except Exception:
                        continue
        except Exception:
            continue

    return competitive_content


def collect_gap_discussions(market_domain: str) -> List[Dict[str, Any]]:
    """Collect discussions about market gaps"""
    gap_content = []

    gap_queries = [
        f"{market_domain} doesn't exist missing solution",
        f"why isn't there good {market_domain} tool",
        f"{market_domain} market gap opportunity",
        f"{market_domain} limitations problems current solutions",
    ]

    for query in gap_queries:
        try:
            results = google_search(query)
            if results and hasattr(results, "results"):
                for result in results.results[:3]:
                    try:
                        content = load_web_page(result.url)
                        if content and len(content) > 300:
                            gap_content.append(
                                {
                                    "type": "gap_discussion",
                                    "title": result.title,
                                    "url": result.url,
                                    "content": content[:1500],
                                    "query": query,
                                }
                            )
                    except Exception:
                        continue
        except Exception:
            continue

    return gap_content


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
                f"Content: {item['content'][:700]}"
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=competitive_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            analysis = json.loads(response.text)
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
    model="gemini-2.0-flash",
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "Hybrid market signal explorer that combines web scraping with AI-powered "
        "analysis to discover genuine opportunities in liminal market spaces."
    ),
    tools=[
        FunctionTool(func=discover_market_signals),
        FunctionTool(func=analyze_competitive_gaps),
        FunctionTool(func=validate_signals_cross_platform),
        google_search,
        load_web_page,  # Fixed: Now properly imported as a function
    ],
    output_key="market_signals",
)
