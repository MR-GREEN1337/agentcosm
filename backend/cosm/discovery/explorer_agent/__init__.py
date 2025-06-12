"""
Market Explorer Agent
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
import asyncio
import concurrent.futures
from functools import partial
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
You are the Market Explorer Agent with robust error handling capabilities and parallel processing.

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


def execute_pain_point_discovery(sanitized_query: str) -> Dict[str, Any]:
    """
    Isolated function for pain point discovery - suitable for parallel execution
    """
    try:
        print(f"🔍 Starting pain point discovery for: {sanitized_query}")
        results = tavily_quick_search(sanitized_query)
        print("✅ Pain point discovery completed")
        return {"status": "success", "data": results, "error": None}
    except Exception as e:
        print(f"⚠️  Pain point discovery failed: {e}")
        return {"status": "failed", "data": {"pain_point_signals": []}, "error": str(e)}


def execute_market_research(sanitized_query: str) -> Dict[str, Any]:
    """
    Isolated function for market research - suitable for parallel execution
    """
    try:
        print(f"🔍 Starting market research for: {sanitized_query}")
        results = tavily_comprehensive_research([sanitized_query])
        print("✅ Market research completed")
        return {"status": "success", "data": results, "error": None}
    except Exception as e:
        print(f"⚠️  Market research failed: {e}")
        return {"status": "failed", "data": {"search_results": []}, "error": str(e)}


def execute_additional_context_search(sanitized_query: str) -> Dict[str, Any]:
    """
    Additional context gathering - can run in parallel with main research
    """
    try:
        # Search for related trends and competitor analysis
        trend_query = f"{sanitized_query} trends market analysis 2024 2025"
        print(f"🔍 Starting trend analysis for: {trend_query}")
        results = tavily_quick_search(trend_query)
        print("✅ Trend analysis completed")
        return {"status": "success", "data": results, "error": None}
    except Exception as e:
        print(f"⚠️  Trend analysis failed: {e}")
        return {"status": "failed", "data": {"pain_point_signals": []}, "error": str(e)}


async def run_research_tasks_parallel(sanitized_query: str) -> Dict[str, Any]:
    """
    Execute multiple research tasks in parallel using asyncio and ThreadPoolExecutor
    """
    print("🚀 Starting parallel research execution...")

    # Create a thread pool for I/O bound operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()

        # Create partial functions with the query pre-filled
        pain_point_task = partial(execute_pain_point_discovery, sanitized_query)
        market_research_task = partial(execute_market_research, sanitized_query)
        trend_analysis_task = partial(
            execute_additional_context_search, sanitized_query
        )

        # Submit all tasks to the thread pool
        futures = [
            loop.run_in_executor(executor, pain_point_task),
            loop.run_in_executor(executor, market_research_task),
            loop.run_in_executor(executor, trend_analysis_task),
        ]

        # Wait for all tasks to complete
        results = await asyncio.gather(*futures, return_exceptions=True)

        # Process results and handle any exceptions
        pain_point_result = (
            results[0]
            if not isinstance(results[0], Exception)
            else {
                "status": "failed",
                "data": {"pain_point_signals": []},
                "error": str(results[0]),
            }
        )

        market_research_result = (
            results[1]
            if not isinstance(results[1], Exception)
            else {
                "status": "failed",
                "data": {"search_results": []},
                "error": str(results[1]),
            }
        )

        trend_analysis_result = (
            results[2]
            if not isinstance(results[2], Exception)
            else {
                "status": "failed",
                "data": {"pain_point_signals": []},
                "error": str(results[2]),
            }
        )

        print(
            f"✅ Parallel research completed - Pain: {pain_point_result['status']}, Market: {market_research_result['status']}, Trends: {trend_analysis_result['status']}"
        )

        return {
            "pain_point_discovery": pain_point_result,
            "market_research": market_research_result,
            "trend_analysis": trend_analysis_result,
        }


def discover_comprehensive_market_signals(query_context: str) -> Dict[str, Any]:
    """
    PARALLELIZED: Enhanced error handling with concurrent processing for better performance
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
        "performance_metrics": {
            "parallel_execution": True,
            "start_time": datetime.now().isoformat(),
        },
    }

    try:
        print(f"🔍 Comprehensive parallel market discovery for: {sanitized_query}")
        comprehensive_data["processing_status"] = "collecting_data_parallel"

        # Execute research tasks in parallel
        try:
            # Run the parallel research tasks
            if asyncio.get_event_loop().is_running():
                # If we're already in an event loop, we need to use a different approach
                print("⚠️  Already in event loop, using synchronous fallback")
                research_results = run_synchronous_fallback(sanitized_query)
            else:
                # Run parallel tasks
                research_results = asyncio.run(
                    run_research_tasks_parallel(sanitized_query)
                )

            comprehensive_data["performance_metrics"][
                "parallel_execution_completed"
            ] = datetime.now().isoformat()

        except Exception as e:
            print(f"⚠️  Parallel execution failed, falling back to synchronous: {e}")
            research_results = run_synchronous_fallback(sanitized_query)
            comprehensive_data["performance_metrics"]["fallback_used"] = True

        # Process results from parallel execution
        pain_point_results = research_results["pain_point_discovery"]["data"]
        market_research_results = research_results["market_research"]["data"]
        trend_analysis_results = research_results["trend_analysis"]["data"]

        # Collect errors from parallel execution
        for task_name, task_result in research_results.items():
            if task_result["error"]:
                comprehensive_data["errors"].append(
                    f"{task_name}: {task_result['error']}"
                )

        # Collect and validate content from all sources
        all_content = []

        # Process pain point data
        if research_results["pain_point_discovery"]["status"] == "success":
            for signal in pain_point_results.get("pain_point_signals", []):
                for result in signal.get("results", []):
                    content_item = {
                        "source": "pain_discovery",
                        "type": "user_frustration",
                        "title": str(result.get("title", ""))[:200],
                        "content": str(result.get("content", ""))[:1000],
                        "url": str(result.get("url", "")),
                        "score": float(result.get("score", 0.0))
                        if result.get("score")
                        else 0.0,
                    }
                    all_content.append(content_item)

        # Process market research data
        if research_results["market_research"]["status"] == "success":
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

        # Process trend analysis data
        if research_results["trend_analysis"]["status"] == "success":
            for signal in trend_analysis_results.get("pain_point_signals", []):
                for result in signal.get("results", []):
                    content_item = {
                        "source": "trend_analysis",
                        "type": "trend_data",
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
        comprehensive_data["performance_metrics"]["data_collection_completed"] = (
            datetime.now().isoformat()
        )

        # AI Analysis phase
        if all_content:
            print(f"🤖 Analyzing {len(all_content)} pieces of content with AI...")
            try:
                comprehensive_data = analyze_with_enhanced_ai(
                    all_content, sanitized_query, comprehensive_data
                )
                comprehensive_data["ai_analysis_status"] = "success"
                comprehensive_data["performance_metrics"]["ai_analysis_completed"] = (
                    datetime.now().isoformat()
                )
            except Exception as e:
                print(f"⚠️  AI analysis failed: {e}")
                comprehensive_data["errors"].append(f"AI analysis: {e}")
                comprehensive_data["ai_analysis_status"] = "failed"
        else:
            print("⚠️  No content collected for analysis")
            comprehensive_data["ai_analysis_status"] = "skipped_no_content"

        comprehensive_data["processing_status"] = "completed"
        comprehensive_data["performance_metrics"]["total_completion_time"] = (
            datetime.now().isoformat()
        )

        # Calculate performance improvement
        if comprehensive_data["performance_metrics"].get("parallel_execution"):
            print("✅ Parallel execution completed successfully")

        return comprehensive_data

    except Exception as e:
        print(f"❌ Critical error in comprehensive market discovery: {e}")
        comprehensive_data["processing_status"] = "failed"
        comprehensive_data["critical_error"] = str(e)
        return comprehensive_data


def run_synchronous_fallback(sanitized_query: str) -> Dict[str, Any]:
    """
    Synchronous fallback when parallel execution fails
    """
    print("🔄 Running synchronous fallback...")
    return {
        "pain_point_discovery": execute_pain_point_discovery(sanitized_query),
        "market_research": execute_market_research(sanitized_query),
        "trend_analysis": execute_additional_context_search(sanitized_query),
    }


def analyze_with_enhanced_ai(
    content_collection: List[Dict], query_context: str, base_data: Dict
) -> Dict[str, Any]:
    """
    ENHANCED: Maximum robustness for AI analysis with JSON parsing
    Enhanced with better content categorization from parallel sources
    """
    try:
        # Categorize content by source for better analysis
        pain_points = [
            item
            for item in content_collection
            if item.get("source") == "pain_discovery"
        ]
        market_data = [
            item
            for item in content_collection
            if item.get("source") == "market_research"
        ]
        trend_data = [
            item
            for item in content_collection
            if item.get("source") == "trend_analysis"
        ]

        print(
            f"📊 Content breakdown: {len(pain_points)} pain points, {len(market_data)} market data, {len(trend_data)} trend insights"
        )

        # Prepare content with strict length limits, prioritizing diverse sources
        content_items = []

        # Take top items from each category
        for category, items in [
            ("pain", pain_points[:4]),
            ("market", market_data[:4]),
            ("trend", trend_data[:2]),
        ]:
            for item in items:
                safe_item = {
                    "source": str(item.get("source", ""))[:50],
                    "type": str(item.get("type", ""))[:50],
                    "title": str(item.get("title", ""))[:150],
                    "content": str(item.get("content", ""))[:600],
                    "score": float(item.get("score", 0.0)),
                    "category": category,
                }
                content_items.append(safe_item)

        # Create enhanced content summary with source categorization
        content_summary = "\n\n".join(
            [
                f"[{item['category']}-{item['source']}] {item['title']}\n{item['content'][:400]}"
                for item in content_items
            ]
        )

        # Enhanced prompt leveraging parallel data collection
        analysis_prompt = f"""
Analyze market opportunities for: {query_context}

Multi-source content data (collected in parallel):
{content_summary}

Return ONLY valid JSON with this exact structure:
{{
    "market_signals": [
        {{
            "description": "signal description",
            "strength": "high",
            "evidence": "supporting evidence",
            "source_diversity": "multiple_sources"
        }}
    ],
    "trend_analysis": {{
        "direction": "growing",
        "momentum": "high",
        "timing": "optimal",
        "cross_validation": "confirmed"
    }},
    "liminal_opportunities": [
        {{
            "opportunity": "specific opportunity description",
            "target": "target market",
            "readiness": "high",
            "confidence": "validated"
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

                from cosm.utils import robust_completion

                response = robust_completion(
                    model=MODEL_CONFIG["market_explorer_openai"],
                    api_key=settings.OPENAI_API_KEY,
                    messages=[{"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                    max_tokens=1500,
                    timeout=30,
                )

                if (
                    response
                    and response.choices
                    and response.choices[0].message.content
                ):
                    raw_content = response.choices[0].message.content.strip()
                    ai_analysis = robust_json_parser(raw_content)

                    if ai_analysis and isinstance(ai_analysis, dict):
                        # Safely merge results with enhanced metadata
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
                                "analysis_metadata": {
                                    "sources_analyzed": len(
                                        set(item["source"] for item in content_items)
                                    ),
                                    "content_diversity": {
                                        "pain_points": len(pain_points),
                                        "market_data": len(market_data),
                                        "trend_data": len(trend_data),
                                    },
                                },
                            }
                        )

                        print(
                            "✅ AI analysis completed successfully with parallel data"
                        )
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

    return base_data


def validate_signals_cross_platform(signals_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced signal validation that accounts for parallel data collection
    """
    validation = {
        "validation_timestamp": datetime.now().isoformat(),
        "validation_score": 0.0,
        "quality_metrics": {},
        "recommendations": [],
        "parallel_processing_quality": {},
    }

    try:
        # Safe extraction of data
        market_signals = signals_data.get("market_signals", [])
        opportunities = signals_data.get("liminal_opportunities", [])
        confidence_score = float(signals_data.get("confidence_score", 0.0))

        # Check for parallel processing metadata
        analysis_metadata = signals_data.get("analysis_metadata", {})
        sources_analyzed = analysis_metadata.get("sources_analyzed", 0)
        content_diversity = analysis_metadata.get("content_diversity", {})

        # Enhanced scoring logic that rewards source diversity
        signal_count = len(market_signals)
        opportunity_count = len(opportunities)

        # Base quality score
        base_score = 0.0
        if signal_count >= 3 and opportunity_count >= 1 and confidence_score > 0.7:
            base_score = 0.8
        elif signal_count >= 2 and confidence_score > 0.5:
            base_score = 0.6
        else:
            base_score = 0.3

        # Bonus for source diversity (from parallel collection)
        diversity_bonus = 0.0
        if sources_analyzed >= 3:
            diversity_bonus = 0.1
        elif sources_analyzed >= 2:
            diversity_bonus = 0.05

        # Final validation score
        validation["validation_score"] = min(1.0, base_score + diversity_bonus)

        if validation["validation_score"] > 0.8:
            validation["quality_assessment"] = "high"
        elif validation["validation_score"] > 0.6:
            validation["quality_assessment"] = "medium"
        else:
            validation["quality_assessment"] = "low"

        validation["quality_metrics"] = {
            "signals_found": signal_count,
            "opportunities_identified": opportunity_count,
            "base_confidence": confidence_score,
            "sources_analyzed": sources_analyzed,
            "content_diversity": content_diversity,
        }

        validation["parallel_processing_quality"] = {
            "multi_source_validation": sources_analyzed >= 2,
            "data_triangulation": len(content_diversity) >= 2,
            "quality_enhancement": diversity_bonus > 0,
        }

        # Enhanced recommendations
        if validation["validation_score"] > 0.8:
            validation["recommendations"].append(
                "Excellent signal quality with multi-source validation - high confidence for opportunity evaluation"
            )
        elif validation["validation_score"] > 0.6:
            validation["recommendations"].append(
                "Good signal quality detected - proceed with cautious opportunity evaluation"
            )
        else:
            validation["recommendations"].append(
                "Consider additional research with broader source coverage to strengthen signals"
            )

        if validation["parallel_processing_quality"]["multi_source_validation"]:
            validation["recommendations"].append(
                "Multi-source validation successful - signals are cross-verified"
            )

        return validation

    except Exception as e:
        print(f"❌ Error in signal validation: {e}")
        validation["error"] = str(e)
        validation["validation_score"] = 0.0
        return validation


# Create the enhanced agent with parallel processing capabilities
market_explorer_agent = LlmAgent(
    name="market_explorer_agent",
    model=MODEL_CONFIG["market_explorer"],
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "High-performance market intelligence agent with parallel processing capabilities. "
        "Features concurrent data collection, robust error handling, and enhanced signal validation. "
        "Delivers faster insights while maintaining data quality and reliability."
    ),
    tools=[
        FunctionTool(func=discover_comprehensive_market_signals),
        FunctionTool(func=validate_signals_cross_platform),
        search_tool,
    ],
    output_key="comprehensive_market_intelligence",
)
