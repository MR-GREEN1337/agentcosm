"""
Market Explorer Agent - FIXED VERSION
Addresses JSON parsing issues and tool call problems
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool

# Import consolidated Tavily tools
from ...tools.tavily import (
    tavily_comprehensive_research,
    tavily_quick_search,
)


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


# Initialize client
client = Client()

EXPLORER_AGENT_PROMPT = """
You are the Market Explorer Agent with robust error handling capabilities.

Your mission is to discover opportunities in liminal market spaces by:
- Collecting authentic user frustrations using web research
- Analyzing trends and momentum with AI-powered insights
- Mapping signal connections to identify hidden gaps
- Finding underserved niches between established market categories

CRITICAL INSTRUCTIONS:
1. ONLY call ONE function at a time - never make parallel function calls
2. Always use the discover_comprehensive_market_signals function for market research
3. Provide clear, structured responses based on the collected data
4. If you encounter errors, acknowledge them and provide partial results where possible

When making function calls, ensure your arguments are valid JSON strings without extra characters.
"""


def robust_json_parser(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Ultra-robust JSON parser that handles multiple edge cases
    """
    if not json_string or not json_string.strip():
        return {}

    # Clean the string
    json_string = json_string.strip()

    try:
        # First attempt: standard parsing
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"⚠️  Primary JSON parse failed: {e}")

        # Second attempt: Handle "Extra data" error by finding first complete JSON
        if "Extra data" in str(e):
            try:
                # Use JSONDecoder to get the first valid object and its end position
                decoder = json.JSONDecoder()
                first_obj, end_idx = decoder.raw_decode(json_string)

                extra_chars = len(json_string) - end_idx
                print(
                    f"✅ Extracted first JSON object, ignored {extra_chars} extra characters"
                )
                return first_obj

            except json.JSONDecodeError as inner_e:
                print(f"⚠️  Failed to extract first JSON object: {inner_e}")

        # Third attempt: Fix common JSON issues
        try:
            # Remove potential trailing commas and fix common issues
            cleaned = json_string

            # Fix trailing commas before closing braces/brackets
            cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)

            # Ensure proper string escaping
            cleaned = (
                cleaned.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            )

            # Try to find the main JSON object if wrapped in extra text
            json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(1)

            return json.loads(cleaned)

        except json.JSONDecodeError as final_e:
            print(f"❌ All JSON parsing attempts failed: {final_e}")
            print(f"Problematic JSON (first 200 chars): {json_string[:200]}")
            return {}


def sanitize_query_for_llm(query: str) -> str:
    """
    Sanitize query to prevent JSON parsing issues in LLM responses
    """
    # Remove or escape problematic characters
    sanitized = query.replace('"', "'").replace("\n", " ").replace("\r", " ")
    # Limit length to prevent truncation issues
    return sanitized[:500] if len(sanitized) > 500 else sanitized


def discover_comprehensive_market_signals(query_context: str) -> Dict[str, Any]:
    """
    FIXED: Enhanced error handling and content validation
    """
    # Sanitize input to prevent downstream JSON issues
    sanitized_query = sanitize_query_for_llm(query_context)

    comprehensive_data = {
        "timestamp": datetime.now().isoformat(),
        "original_context": query_context,
        "sanitized_context": sanitized_query,
        "market_signals": [],
        "trend_analysis": {},
        "gap_mapping": {},
        "liminal_opportunities": [],
        "consolidated_insights": {},
        "confidence_score": 0.0,
        "processing_status": "starting",
        "errors": [],
    }

    try:
        print(f"🔍 Comprehensive market discovery for: {sanitized_query}")
        comprehensive_data["processing_status"] = "collecting_data"

        # Phase 1: Pain point discovery with error handling
        print("🔍 Phase 1: Pain point discovery...")
        try:
            pain_point_results = tavily_quick_search(sanitized_query)
            comprehensive_data["pain_point_collection_status"] = "success"
        except Exception as e:
            print(f"⚠️  Pain point discovery failed: {e}")
            pain_point_results = {"error": str(e), "pain_point_signals": []}
            comprehensive_data["errors"].append(f"Pain point discovery: {e}")

        # Phase 2: Market research with error handling
        print("🔍 Phase 2: Market research...")
        try:
            market_research_results = tavily_comprehensive_research([sanitized_query])
            comprehensive_data["market_research_status"] = "success"
        except Exception as e:
            print(f"⚠️  Market research failed: {e}")
            market_research_results = {"error": str(e), "search_results": []}
            comprehensive_data["errors"].append(f"Market research: {e}")

        # Collect and validate content
        all_content = []

        # Process pain point data
        if not pain_point_results.get("error"):
            for signal in pain_point_results.get("pain_point_signals", []):
                for result in signal.get("results", []):
                    content_item = {
                        "source": "pain_discovery",
                        "type": "user_frustration",
                        "title": str(result.get("title", ""))[
                            :200
                        ],  # Limit title length
                        "content": str(result.get("content", ""))[
                            :1000
                        ],  # Limit content length
                        "url": str(result.get("url", "")),
                        "score": float(result.get("score", 0.0))
                        if result.get("score")
                        else 0.0,
                    }
                    all_content.append(content_item)

        # Process market research data
        if not market_research_results.get("error"):
            for search_result in market_research_results.get("search_results", []):
                for result in search_result.get("results", []):
                    content_item = {
                        "source": "market_research",
                        "type": "market_data",
                        "title": str(result.get("title", ""))[:200],
                        "content": str(result.get("content", ""))[:1000],
                        "url": str(result.get("url", "")),
                        "score": float(result.get("score", 0.0))
                        if result.get("score")
                        else 0.0,
                    }
                    all_content.append(content_item)

        comprehensive_data["raw_content_collected"] = len(all_content)
        comprehensive_data["processing_status"] = "analyzing"

        # AI Analysis phase
        if all_content:
            print(f"🤖 Analyzing {len(all_content)} pieces of content with AI...")
            try:
                comprehensive_data = analyze_with_enhanced_ai(
                    all_content, sanitized_query, comprehensive_data
                )
                comprehensive_data["ai_analysis_status"] = "success"
            except Exception as e:
                print(f"⚠️  AI analysis failed: {e}")
                comprehensive_data["errors"].append(f"AI analysis: {e}")
                comprehensive_data["ai_analysis_status"] = "failed"
        else:
            print("⚠️  No content collected for analysis")
            comprehensive_data["ai_analysis_status"] = "skipped_no_content"

        comprehensive_data["processing_status"] = "completed"
        return comprehensive_data

    except Exception as e:
        print(f"❌ Critical error in comprehensive market discovery: {e}")
        comprehensive_data["processing_status"] = "failed"
        comprehensive_data["critical_error"] = str(e)
        return comprehensive_data


def analyze_with_enhanced_ai(
    content_collection: List[Dict], query_context: str, base_data: Dict
) -> Dict[str, Any]:
    """
    ENHANCED: Maximum robustness for AI analysis with JSON parsing
    """
    try:
        # Prepare content with strict length limits
        content_items = []
        for item in content_collection[:10]:  # Limit to 10 items for token efficiency
            safe_item = {
                "source": str(item.get("source", ""))[:50],
                "type": str(item.get("type", ""))[:50],
                "title": str(item.get("title", ""))[:150],
                "content": str(item.get("content", ""))[:600],  # Reduced for safety
                "score": float(item.get("score", 0.0)),
            }
            content_items.append(safe_item)

        # Create concise content summary
        content_summary = "\n\n".join(
            [
                f"[{item['source']}] {item['title']}\n{item['content'][:400]}"
                for item in content_items
            ]
        )

        # Simplified prompt to reduce JSON complexity
        analysis_prompt = f"""
Analyze market opportunities for: {query_context}

Content data:
{content_summary}

Return ONLY valid JSON with this exact structure:
{{
    "market_signals": [
        {{
            "description": "signal description",
            "strength": "high",
            "evidence": "supporting evidence"
        }}
    ],
    "trend_analysis": {{
        "direction": "growing",
        "momentum": "high",
        "timing": "optimal"
    }},
    "liminal_opportunities": [
        {{
            "opportunity": "specific opportunity description",
            "target": "target market",
            "readiness": "high"
        }}
    ],
    "confidence_score": 0.8
}}

NO markdown, NO explanations, ONLY JSON.
"""

        # Enhanced API call with multiple safety measures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🤖 AI analysis attempt {attempt + 1}/{max_retries}")

                response = completion(
                    model=MODEL_CONFIG["market_explorer_openai"],
                    api_key=settings.OPENAI_API_KEY,
                    messages=[{"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.0,  # Zero temperature for maximum consistency
                    max_tokens=1500,  # Conservative token limit
                    timeout=30,  # Add timeout to prevent hanging
                )

                if (
                    response
                    and response.choices
                    and response.choices[0].message.content
                ):
                    raw_content = response.choices[0].message.content.strip()

                    # Use robust JSON parser
                    ai_analysis = robust_json_parser(raw_content)

                    if ai_analysis and isinstance(ai_analysis, dict):
                        # Safely merge results
                        base_data.update(
                            {
                                "market_signals": ai_analysis.get("market_signals", []),
                                "trend_analysis": ai_analysis.get("trend_analysis", {}),
                                "liminal_opportunities": ai_analysis.get(
                                    "liminal_opportunities", []
                                ),
                                "confidence_score": float(
                                    ai_analysis.get("confidence_score", 0.5)
                                ),
                            }
                        )

                        print("✅ AI analysis completed successfully")
                        return base_data
                    else:
                        print(f"⚠️  Attempt {attempt + 1}: Invalid JSON structure")

                else:
                    print(f"⚠️  Attempt {attempt + 1}: Empty response from API")

            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {str(e)[:100]}")

                if attempt == max_retries - 1:
                    base_data["ai_analysis_error"] = (
                        f"All attempts failed. Last error: {str(e)[:200]}"
                    )
                    break

    except Exception as e:
        print(f"❌ Critical error in AI analysis: {e}")
        base_data["ai_analysis_error"] = f"Critical failure: {str(e)[:200]}"

    # Return base data even if AI analysis failed
    return base_data


def validate_signals_cross_platform(signals_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified and robust signal validation
    """
    validation = {
        "validation_timestamp": datetime.now().isoformat(),
        "validation_score": 0.0,
        "quality_metrics": {},
        "recommendations": [],
    }

    try:
        # Safe extraction of data
        market_signals = signals_data.get("market_signals", [])
        opportunities = signals_data.get("liminal_opportunities", [])
        confidence_score = float(signals_data.get("confidence_score", 0.0))

        # Simple scoring logic
        signal_count = len(market_signals)
        opportunity_count = len(opportunities)

        # Calculate validation score
        if signal_count >= 3 and opportunity_count >= 1 and confidence_score > 0.7:
            validation["validation_score"] = 0.9
            validation["quality_assessment"] = "high"
        elif signal_count >= 2 and confidence_score > 0.5:
            validation["validation_score"] = 0.7
            validation["quality_assessment"] = "medium"
        else:
            validation["validation_score"] = 0.4
            validation["quality_assessment"] = "low"

        validation["quality_metrics"] = {
            "signals_found": signal_count,
            "opportunities_identified": opportunity_count,
            "base_confidence": confidence_score,
        }

        # Generate recommendations
        if validation["validation_score"] > 0.7:
            validation["recommendations"].append(
                "High-quality signals detected - proceed with opportunity evaluation"
            )
        else:
            validation["recommendations"].append(
                "Consider additional research to strengthen signal quality"
            )

        return validation

    except Exception as e:
        print(f"❌ Error in signal validation: {e}")
        validation["error"] = str(e)
        validation["validation_score"] = 0.0
        return validation


# Create the enhanced agent with improved error handling
market_explorer_agent = LlmAgent(
    name="market_explorer_agent",
    model=MODEL_CONFIG["market_explorer"],
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "Robust market intelligence agent with comprehensive error handling. "
        "Fixes JSON parsing issues, handles API failures gracefully, and provides "
        "partial results when full analysis isn't possible."
    ),
    tools=[
        FunctionTool(func=discover_comprehensive_market_signals),
        FunctionTool(func=validate_signals_cross_platform),
        search_tool,
    ],
    output_key="comprehensive_market_intelligence",
)
