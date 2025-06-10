"""
Parallel Web Search Tools using Threading for Enhanced Performance
Optimized for liminal market discovery across multiple dimensions
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from dataclasses import dataclass
from queue import Queue

from ..tools.tavily import tavily_research_suite, tavily_quick_search
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from litellm import completion


@dataclass
class SearchTask:
    """Represents a single search task for parallel execution"""

    query: str
    search_type: str  # 'tavily', 'google', 'comprehensive'
    market_dimension: str  # 'primary', 'adjacent', 'cross_industry', etc.
    priority: int = 1  # Higher number = higher priority
    max_results: int = 3
    timeout: int = 15


@dataclass
class SearchResult:
    """Container for search results with metadata"""

    task: SearchTask
    results: Dict[str, Any]
    success: bool
    execution_time: float
    error: Optional[str] = None


class ParallelSearchEngine:
    """
    Thread-safe parallel web search engine for liminal market discovery
    """

    def __init__(self, max_workers: int = 8, request_delay: float = 0.5):
        self.max_workers = max_workers
        self.request_delay = request_delay  # Rate limiting between requests
        self.results_queue = Queue()
        self.lock = threading.Lock()

    def execute_search_task(self, task: SearchTask) -> SearchResult:
        """
        Execute a single search task with error handling and timing
        """
        start_time = time.time()

        try:
            # Rate limiting
            time.sleep(self.request_delay)

            if task.search_type == "tavily":
                results = tavily_research_suite(
                    query=task.query,
                    research_type="comprehensive",
                    max_results=task.max_results,
                    search_depth="basic",
                )
            elif task.search_type == "tavily_quick":
                results = tavily_quick_search(
                    query=task.query, max_results=task.max_results
                )
            else:
                # Fallback to basic search
                results = {"query": task.query, "results": [], "source": "fallback"}

            execution_time = time.time() - start_time

            return SearchResult(
                task=task, results=results, success=True, execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Search task failed: {task.query} - {str(e)}")

            return SearchResult(
                task=task,
                results={},
                success=False,
                execution_time=execution_time,
                error=str(e),
            )

    def execute_parallel_searches(self, tasks: List[SearchTask]) -> List[SearchResult]:
        """
        Execute multiple search tasks in parallel using ThreadPoolExecutor
        """
        print(f"🚀 Starting parallel execution of {len(tasks)} search tasks...")

        results = []
        successful_searches = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.execute_search_task, task): task for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task, timeout=30):
                try:
                    result = future.result()
                    results.append(result)

                    if result.success:
                        successful_searches += 1
                        print(
                            f"✅ Completed: {result.task.query} ({result.execution_time:.2f}s)"
                        )
                    else:
                        print(f"❌ Failed: {result.task.query}")

                except Exception as e:
                    task = future_to_task[future]
                    print(f"❌ Exception in task {task.query}: {str(e)}")
                    results.append(
                        SearchResult(
                            task=task,
                            results={},
                            success=False,
                            execution_time=0,
                            error=str(e),
                        )
                    )

        print(
            f"🎯 Parallel search completed: {successful_searches}/{len(tasks)} successful"
        )
        return results


def create_liminal_search_tasks(keywords: List[str]) -> List[SearchTask]:
    """
    Create comprehensive search tasks for liminal market discovery
    """
    tasks = []

    for keyword in keywords[:2]:  # Limit primary keywords for performance
        # PRIMARY MARKET EXPLORATION
        tasks.extend(
            [
                SearchTask(
                    query=f"{keyword} user problems complaints reddit",
                    search_type="tavily_quick",
                    market_dimension="primary_pain_points",
                    priority=3,
                    max_results=4,
                ),
                SearchTask(
                    query=f"{keyword} market size industry analysis",
                    search_type="tavily",
                    market_dimension="primary_market_size",
                    priority=2,
                    max_results=3,
                ),
            ]
        )

        # ADJACENT MARKET DISCOVERY
        tasks.extend(
            [
                SearchTask(
                    query=f"what do people use before {keyword}",
                    search_type="tavily_quick",
                    market_dimension="upstream_markets",
                    priority=3,
                    max_results=3,
                ),
                SearchTask(
                    query=f"what happens after using {keyword}",
                    search_type="tavily_quick",
                    market_dimension="downstream_markets",
                    priority=3,
                    max_results=3,
                ),
                SearchTask(
                    query=f"alternatives to {keyword} that people combine",
                    search_type="tavily_quick",
                    market_dimension="complementary_markets",
                    priority=2,
                    max_results=3,
                ),
            ]
        )

        # CROSS-INDUSTRY PATTERNS
        tasks.extend(
            [
                SearchTask(
                    query=f"how {keyword} works in different industries",
                    search_type="tavily",
                    market_dimension="cross_industry_patterns",
                    priority=2,
                    max_results=3,
                ),
                SearchTask(
                    query=f"{keyword} integration challenges across sectors",
                    search_type="tavily_quick",
                    market_dimension="integration_failures",
                    priority=2,
                    max_results=3,
                ),
            ]
        )

        # WORKFLOW GAP DISCOVERY
        tasks.extend(
            [
                SearchTask(
                    query=f"workflow breaks with {keyword} manual steps",
                    search_type="tavily_quick",
                    market_dimension="workflow_gaps",
                    priority=3,
                    max_results=3,
                ),
                SearchTask(
                    query=f"switching between {keyword} and other tools friction",
                    search_type="tavily_quick",
                    market_dimension="tool_switching_friction",
                    priority=2,
                    max_results=3,
                ),
            ]
        )

        # ARBITRAGE OPPORTUNITIES
        tasks.extend(
            [
                SearchTask(
                    query=f"{keyword} expensive alternatives cheap underutilized",
                    search_type="tavily_quick",
                    market_dimension="arbitrage_opportunities",
                    priority=2,
                    max_results=3,
                ),
            ]
        )

    # Sort by priority (higher first)
    tasks.sort(key=lambda x: x.priority, reverse=True)

    return tasks


def parallel_liminal_discovery(keywords: List[str]) -> Dict[str, Any]:
    """
    Main function for parallel liminal market discovery

    Args:
        keywords: Primary market keywords to explore

    Returns:
        Comprehensive liminal market intelligence from parallel searches
    """
    discovery_data = {
        "keywords": keywords,
        "timestamp": datetime.now().isoformat(),
        "search_strategy": "parallel_liminal_discovery",
        "market_dimensions": {},
        "execution_stats": {},
        "liminal_signals": [],
    }

    try:
        # Create search tasks
        search_tasks = create_liminal_search_tasks(keywords)
        print(f"📋 Created {len(search_tasks)} parallel search tasks")

        # Execute parallel searches
        search_engine = ParallelSearchEngine(max_workers=6, request_delay=0.3)
        start_time = time.time()

        results = search_engine.execute_parallel_searches(search_tasks)

        total_time = time.time() - start_time

        # Organize results by market dimension
        dimension_results = {}
        successful_results = [r for r in results if r.success]

        for result in successful_results:
            dimension = result.task.market_dimension
            if dimension not in dimension_results:
                dimension_results[dimension] = []
            dimension_results[dimension].append(result.results)

        discovery_data["market_dimensions"] = dimension_results
        discovery_data["execution_stats"] = {
            "total_tasks": len(search_tasks),
            "successful_tasks": len(successful_results),
            "failed_tasks": len(results) - len(successful_results),
            "total_execution_time": total_time,
            "average_task_time": sum(r.execution_time for r in results) / len(results)
            if results
            else 0,
            "parallel_efficiency": f"{len(search_tasks) * min(r.execution_time for r in results if r.success) / total_time:.1f}x"
            if successful_results
            else "0x",
        }

        # Extract liminal signals using AI analysis
        discovery_data["liminal_signals"] = (
            extract_liminal_signals_from_parallel_results(dimension_results, keywords)
        )

        print(f"✅ Parallel liminal discovery completed in {total_time:.2f}s")
        print(
            f"📊 Efficiency: {discovery_data['execution_stats']['parallel_efficiency']} speedup"
        )

        return discovery_data

    except Exception as e:
        print(f"❌ Error in parallel liminal discovery: {e}")
        discovery_data["error"] = str(e)
        return discovery_data


def extract_liminal_signals_from_parallel_results(
    dimension_results: Dict[str, List[Dict]], keywords: List[str]
) -> List[Dict[str, Any]]:
    """
    Use AI to extract liminal opportunity signals from parallel search results
    """
    try:
        # Prepare data for AI analysis
        analysis_data = {
            "keywords": keywords,
            "market_dimensions": {
                k: v[:2] for k, v in dimension_results.items()
            },  # Limit for token efficiency
        }

        liminal_analysis_prompt = f"""
        Analyze these parallel market search results to identify LIMINAL OPPORTUNITY SIGNALS
        - opportunities that exist between established markets, like Uber, Airbnb, DoorDash.

        Search Results by Market Dimension:
        {json.dumps(analysis_data, indent=2)[:3000]}

        Find signals indicating:
        1. WORKFLOW BREAKS: Where users switch between different services
        2. ARBITRAGE GAPS: Expensive solutions + underutilized resources
        3. INTEGRATION FAILURES: Systems that should connect but don't
        4. CROSS-INDUSTRY PATTERNS: Similar problems across different sectors

        Return JSON array of liminal signals:
        [
            {{
                "signal_type": "workflow_break|arbitrage_gap|integration_failure|cross_industry",
                "opportunity_description": "specific liminal opportunity",
                "market_a": "first market/industry",
                "market_b": "second market/industry",
                "connection_gap": "what gap exists between them",
                "user_pain": "specific user frustration",
                "arbitrage_potential": "economic opportunity",
                "evidence": "supporting evidence from search results",
                "uber_airbnb_analogy": "how this is like existing successes"
            }}
        ]
        """

        response = completion(
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": liminal_analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            result = safe_json_loads(response.choices[0].message.content)
            return result.get("liminal_signals", [])

    except Exception as e:
        print(f"❌ Error extracting liminal signals: {e}")

    return []


# Specialized parallel search functions for each agent


def parallel_adjacent_market_search(keywords: List[str]) -> Dict[str, Any]:
    """Parallel search specialized for adjacent market discovery"""

    tasks = []
    for keyword in keywords[:2]:
        tasks.extend(
            [
                SearchTask(
                    f"what do people use before {keyword}",
                    "tavily_quick",
                    "upstream",
                    3,
                ),
                SearchTask(
                    f"what happens after {keyword}", "tavily_quick", "downstream", 3
                ),
                SearchTask(
                    f"alternatives to {keyword} people combine",
                    "tavily_quick",
                    "complementary",
                    2,
                ),
                SearchTask(
                    f"workarounds for {keyword} limitations",
                    "tavily_quick",
                    "substitutes",
                    2,
                ),
            ]
        )

    engine = ParallelSearchEngine(max_workers=4, request_delay=0.4)
    results = engine.execute_parallel_searches(tasks)

    return organize_adjacent_market_results(results)


def parallel_cross_industry_search(keywords: List[str]) -> Dict[str, Any]:
    """Parallel search specialized for cross-industry pattern discovery"""

    tasks = []
    industries = ["healthcare", "finance", "retail", "manufacturing", "education"]

    for keyword in keywords[:2]:
        for industry in industries[:3]:  # Limit for performance
            tasks.append(
                SearchTask(
                    f"how {keyword} works in {industry} industry",
                    "tavily_quick",
                    f"{industry}_patterns",
                    2,
                )
            )

    engine = ParallelSearchEngine(max_workers=6, request_delay=0.3)
    results = engine.execute_parallel_searches(tasks)

    return organize_cross_industry_results(results)


def parallel_workflow_gap_search(keywords: List[str]) -> Dict[str, Any]:
    """Parallel search specialized for workflow gap discovery"""

    tasks = []
    for keyword in keywords[:2]:
        tasks.extend(
            [
                SearchTask(
                    f"{keyword} integration challenges problems",
                    "tavily_quick",
                    "integration_gaps",
                    3,
                ),
                SearchTask(
                    f"manual steps required with {keyword}",
                    "tavily_quick",
                    "manual_friction",
                    3,
                ),
                SearchTask(
                    f"switching between {keyword} and other tools",
                    "tavily_quick",
                    "tool_switching",
                    2,
                ),
                SearchTask(
                    f"{keyword} workflow breaks interruptions",
                    "tavily_quick",
                    "workflow_breaks",
                    2,
                ),
            ]
        )

    engine = ParallelSearchEngine(max_workers=4, request_delay=0.4)
    results = engine.execute_parallel_searches(tasks)

    return organize_workflow_gap_results(results)


def organize_adjacent_market_results(results: List[SearchResult]) -> Dict[str, Any]:
    """Organize results specifically for adjacent market analysis"""
    organized = {
        "upstream_markets": [],
        "downstream_markets": [],
        "complementary_markets": [],
        "substitute_markets": [],
        "connection_opportunities": [],
    }

    for result in results:
        if result.success:
            dimension = result.task.market_dimension
            if dimension in organized:
                organized[dimension].append(result.results)

    return organized


def organize_cross_industry_results(results: List[SearchResult]) -> Dict[str, Any]:
    """Organize results specifically for cross-industry analysis"""
    organized = {
        "industry_patterns": {},
        "cross_industry_opportunities": [],
        "arbitrage_potential": [],
    }

    for result in results:
        if result.success:
            industry = result.task.market_dimension.replace("_patterns", "")
            if industry not in organized["industry_patterns"]:
                organized["industry_patterns"][industry] = []
            organized["industry_patterns"][industry].append(result.results)

    return organized


def organize_workflow_gap_results(results: List[SearchResult]) -> Dict[str, Any]:
    """Organize results specifically for workflow gap analysis"""
    organized = {
        "integration_gaps": [],
        "manual_friction_points": [],
        "tool_switching_costs": [],
        "workflow_break_patterns": [],
        "automation_opportunities": [],
    }

    for result in results:
        if result.success:
            dimension = result.task.market_dimension
            if "integration" in dimension:
                organized["integration_gaps"].append(result.results)
            elif "manual" in dimension:
                organized["manual_friction_points"].append(result.results)
            elif "switching" in dimension:
                organized["tool_switching_costs"].append(result.results)
            elif "workflow" in dimension:
                organized["workflow_break_patterns"].append(result.results)

    return organized
