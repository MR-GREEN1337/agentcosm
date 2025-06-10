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
from cosm.tools.search import search_tool

# Import consolidated Tavily tools
from ...tools.tavily import (
    tavily_comprehensive_research,
    tavily_quick_search,
)

# Initialize client
client = Client()

EXPLORER_AGENT_PROMPT = """
You are the unified Market Explorer Agent with enhanced capabilities. You combine:

1. MARKET SIGNAL DISCOVERY - Find authentic user frustrations and unmet needs
2. TREND ANALYSIS - Identify emerging market trends and patterns
3. GAP MAPPING - Map connections between signals to reveal liminal opportunities

Your mission is to efficiently discover opportunities in liminal market spaces by:
- Collecting authentic user frustrations using consolidated web research
- Analyzing trends and momentum with AI-powered insights
- Mapping signal connections to identify hidden gaps
- Finding underserved niches between established market categories

Use your consolidated tools to provide comprehensive market intelligence in a single pass.

IMPORTANT: Only call ONE function at a time to avoid JSON parsing issues.
"""


def safe_json_loads(json_string: str) -> dict:
    """
    Safely parse JSON with error handling for concatenated JSON objects
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        if "Extra data" in str(e):
            # Handle concatenated JSON objects (known ADK bug)
            print(
                "⚠️  Detected concatenated JSON, attempting to parse first valid object..."
            )
            try:
                # Find the end of the first JSON object
                decoder = json.JSONDecoder()
                first_obj, idx = decoder.raw_decode(json_string)
                print(
                    f"✅ Successfully parsed first JSON object, ignoring {len(json_string) - idx} extra characters"
                )
                return first_obj
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse concatenated JSON: {json_string[:100]}...")
                return {}
        else:
            print(f"❌ JSON parsing error: {e}")
            return {}


def discover_comprehensive_market_signals(query_context: str) -> Dict[str, Any]:
    """
    FIXED: Sequential execution to avoid parallel tool call issues
    """
    comprehensive_data = {
        "timestamp": datetime.now().isoformat(),
        "context": query_context,
        "market_signals": [],
        "trend_analysis": {},
        "gap_mapping": {},
        "liminal_opportunities": [],
        "consolidated_insights": {},
        "confidence_score": 0.0,
    }

    try:
        print(f"🔍 Comprehensive market discovery for: {query_context}")

        print("🔍 Phase 1: Pain point discovery...")
        pain_point_results = tavily_quick_search(query_context)

        print("🔍 Phase 2: Market research...")
        market_research_results = tavily_comprehensive_research([query_context])

        print("🔍 Phase 3: Competitive analysis...")
        competitive_results = tavily_comprehensive_research([query_context])

        all_content = []

        if not pain_point_results.get("error"):
            for signal in pain_point_results.get("pain_point_signals", []):
                for result in signal.get("results", []):
                    all_content.append(
                        {
                            "source": "pain_discovery",
                            "type": "user_frustration",
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[:1500],
                            "url": result.get("url", ""),
                            "score": result.get("score", 0.0),
                        }
                    )

        if not market_research_results.get("error"):
            for search_result in market_research_results.get("search_results", []):
                for result in search_result.get("results", []):
                    all_content.append(
                        {
                            "source": "market_research",
                            "type": "market_data",
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[:1500],
                            "url": result.get("url", ""),
                            "score": result.get("score", 0.0),
                        }
                    )

        if not competitive_results.get("error"):
            for profile in competitive_results.get("competitor_profiles", []):
                for search_result in profile.get("search_results", []):
                    for result in search_result.get("results", []):
                        all_content.append(
                            {
                                "source": "competitive_intel",
                                "type": "competition_data",
                                "title": result.get("title", ""),
                                "content": result.get("content", "")[:1500],
                                "url": result.get("url", ""),
                                "score": result.get("score", 0.0),
                            }
                        )

        comprehensive_data["raw_content_collected"] = len(all_content)

        if all_content:
            print(f"🤖 Analyzing {len(all_content)} pieces of content with AI...")
            comprehensive_data = analyze_comprehensive_signals_with_ai(
                all_content, query_context, comprehensive_data
            )

        return comprehensive_data

    except Exception as e:
        print(f"❌ Error in comprehensive market discovery: {e}")
        comprehensive_data["error"] = str(e)
        return comprehensive_data


def analyze_comprehensive_signals_with_ai(
    content_collection: List[Dict], query_context: str, base_data: Dict
) -> Dict[str, Any]:
    """
    FIXED: Enhanced error handling and JSON parsing
    """
    try:
        # Prepare content for analysis
        content_summary = "\n\n".join(
            [
                f"Source: {item['source']} | Type: {item['type']}\n"
                f"Title: {item['title']}\n"
                f"Content: {item['content'][:800]}\n"
                f"Score: {item.get('score', 0.0)}"
                for item in content_collection[:15]  # Limit for token efficiency
            ]
        )

        analysis_prompt = f"""
        Perform comprehensive market analysis for "{query_context}" combining signal discovery, trend analysis, and gap mapping.

        Content to analyze:
        {content_summary}

        Provide comprehensive analysis in JSON format. RETURN ONLY VALID JSON - NO MARKDOWN, NO EXPLANATIONS:
        {{
            "market_signals": [
                {{
                    "signal_type": "pain_point",
                    "description": "Clear description of the signal",
                    "strength": "high",
                    "frequency": "how often mentioned",
                    "affected_users": "who experiences this",
                    "evidence": "supporting evidence from content"
                }}
            ],
            "trend_analysis": {{
                "trend_direction": "growing",
                "momentum_indicators": ["specific momentum signals"],
                "emerging_technologies": ["technologies enabling change"],
                "market_timing": "optimal",
                "growth_drivers": ["key factors driving growth"]
            }},
            "gap_mapping": {{
                "workflow_gaps": ["specific workflow intersection problems"],
                "integration_failures": ["systems that don't connect well"],
                "technology_gaps": ["missing technological capabilities"],
                "market_positioning_gaps": ["underserved positioning spaces"]
            }},
            "liminal_opportunities": [
                {{
                    "opportunity_description": "specific liminal market opportunity",
                    "target_segment": "who would benefit most",
                    "solution_approach": "how to address this opportunity",
                    "market_readiness": "high",
                    "competitive_advantage": "why this would succeed"
                }}
            ],
            "consolidated_insights": {{
                "primary_pain_themes": ["main user frustration themes"],
                "market_momentum": "accelerating",
                "competitive_landscape": "fragmented",
                "technology_enablers": ["key technologies making solutions possible"],
                "timing_factors": ["factors affecting market timing"],
                "success_requirements": ["what would be needed to succeed"]
            }},
            "confidence_assessment": {{
                "data_quality": "high",
                "source_diversity": "high",
                "signal_consistency": "high",
                "overall_confidence": 0.8
            }},
            "strategic_recommendations": [
                "actionable recommendations for entrepreneurs"
            ]
        }}
        """

        # SOLUTION 3: Enhanced API call with retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = completion(
                    model=MODEL_CONFIG["market_explorer"],
                    api_key=settings.OPENAI_API_KEY,
                    messages=[{"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1,  # Lower temperature for more consistent JSON
                    max_tokens=2000,  # Limit response size
                )

                if response and response.choices[0].message.content:
                    # Use safe JSON parsing
                    ai_analysis = safe_json_loads(response.choices[0].message.content)

                    if ai_analysis:  # Only proceed if we got valid JSON
                        # Merge AI analysis into base data structure
                        base_data.update(ai_analysis)

                        # Extract confidence score safely
                        confidence_data = ai_analysis.get("confidence_assessment", {})
                        base_data["confidence_score"] = float(
                            confidence_data.get("overall_confidence", 0.5)
                        )

                        print("✅ AI analysis completed successfully")
                        return base_data
                    else:
                        print(
                            f"⚠️  Attempt {attempt + 1}: Invalid JSON received, retrying..."
                        )
                        if attempt == max_retries:
                            break
                        continue

            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    base_data["ai_analysis_error"] = str(e)
                    break
                continue

    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        base_data["ai_analysis_error"] = str(e)

    return base_data


def validate_signals_cross_platform(signals_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced cross-platform signal validation with consolidated data
    """
    validation = {
        "cross_platform_consistency": {},
        "signal_reliability": {},
        "confidence_boost_factors": [],
        "validation_score": 0.0,
    }

    try:
        # Analyze signal consistency across different sources
        market_signals = signals_data.get("market_signals", [])
        liminal_opportunities = signals_data.get("liminal_opportunities", [])

        # Count high-confidence signals
        high_confidence_signals = len(
            [s for s in market_signals if s.get("strength") == "high"]
        )
        ready_opportunities = len(
            [o for o in liminal_opportunities if o.get("market_readiness") == "high"]
        )

        # Calculate validation score
        if high_confidence_signals >= 3 and ready_opportunities >= 1:
            validation["validation_score"] = 0.9
            validation["cross_platform_consistency"] = "high"
        elif high_confidence_signals >= 2:
            validation["validation_score"] = 0.7
            validation["cross_platform_consistency"] = "medium"
        else:
            validation["validation_score"] = 0.4
            validation["cross_platform_consistency"] = "low"

        validation["confidence_boost_factors"] = [
            f"Found {high_confidence_signals} high-confidence signals",
            f"Identified {ready_opportunities} market-ready opportunities",
            f"Analyzed {len(market_signals)} total market signals",
        ]

        return validation

    except Exception as e:
        print(f"❌ Error in signal validation: {e}")
        validation["error"] = str(e)
        return validation


market_explorer_agent = LlmAgent(
    name="market_explorer_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["market_explorer"], api_key=settings.OPENAI_API_KEY
    ),
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "Optimized market intelligence agent that combines signal discovery, trend analysis, "
        "and gap mapping to efficiently identify liminal market opportunities. "
        "Fixed for ADK JSON parsing issues."
    ),
    tools=[
        FunctionTool(func=discover_comprehensive_market_signals),
        FunctionTool(func=validate_signals_cross_platform),
        search_tool,
    ],
    output_key="comprehensive_market_intelligence",
)
