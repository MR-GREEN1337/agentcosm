"""
Market Analyzer Agent with Advanced Performance Optimizations
Combines comprehensive market analysis with AI-powered scoring using concurrent execution
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
from dataclasses import dataclass
from functools import wraps
import threading

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from cosm.config import MODEL_CONFIG
from litellm import completion
from cosm.settings import settings

from ..tools.market_research import (
    analyze_market_size,
    research_competition,
    validate_demand_signals,
    assess_market_risks,
    generate_recommendation,
)

client = Client()


@dataclass
class ValidationTask:
    """Represents a validation task for parallel execution"""

    task_id: str
    task_type: str
    function: callable
    args: tuple
    kwargs: dict
    priority: int = 1
    timeout: int = 30


@dataclass
class ValidationResult:
    """Container for validation results with metadata"""

    task_id: str
    task_type: str
    result: Dict[str, Any]
    execution_time: float
    success: bool
    error: Optional[str] = None


class ParallelMarketAnalyzer:
    """
    Advanced parallel market analyzer with optimized concurrent execution
    """

    def __init__(self, max_workers: int = 6, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.results_cache = {}
        self.lock = threading.Lock()

    def performance_monitor(func):
        """Decorator to monitor function performance"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                print(f"⚡ {func.__name__} completed in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {func.__name__} failed after {execution_time:.2f}s: {e}")
                raise

        return wrapper

    @performance_monitor
    async def comprehensive_market_validation_parallel(
        self, opportunity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        PARALLELIZED comprehensive market validation with integrated AI scoring

        This version runs all validation phases concurrently for maximum performance
        """
        validation_report = {
            "opportunity_id": opportunity_data.get("id", datetime.now().isoformat()),
            "market_name": opportunity_data.get("market_name", "Unknown"),
            "validation_timestamp": datetime.now().isoformat(),
            "execution_method": "parallel_optimization",
            "performance_metrics": {},
            # Market validation components (populated in parallel)
            "market_size_analysis": {},
            "competition_analysis": {},
            "demand_validation": {},
            "risk_assessment": {},
            # AI-powered scoring components
            "ai_analysis": {},
            "component_scores": {},
            "overall_opportunity_score": 0.0,
            "strategic_insights": {},
            "confidence_level": "medium",
            # Final outputs
            "recommendation": "investigate",
            "next_actions": [],
        }

        start_time = time.time()

        try:
            market_keywords = opportunity_data.get("keywords", [])
            target_audience = opportunity_data.get("target_audience", "")
            pain_points = opportunity_data.get("pain_points", [])
            solution_type = opportunity_data.get("solution_type", "")

            print("🚀 Starting PARALLEL comprehensive market validation...")

            # PHASE 1: PARALLEL MARKET VALIDATION
            validation_tasks = [
                ValidationTask(
                    task_id="market_size",
                    task_type="market_analysis",
                    function=analyze_market_size,
                    args=(market_keywords, target_audience),
                    kwargs={},
                    priority=3,
                    timeout=30,
                ),
                ValidationTask(
                    task_id="competition",
                    task_type="competition_analysis",
                    function=research_competition,
                    args=(market_keywords, solution_type),
                    kwargs={},
                    priority=3,
                    timeout=30,
                ),
                ValidationTask(
                    task_id="demand",
                    task_type="demand_validation",
                    function=validate_demand_signals,
                    args=(market_keywords, pain_points),
                    kwargs={},
                    priority=2,
                    timeout=25,
                ),
            ]

            # Execute validation tasks in parallel
            validation_results = await self.execute_validation_tasks_parallel(
                validation_tasks
            )

            # Process results
            for result in validation_results:
                if result.success:
                    if result.task_id == "market_size":
                        validation_report["market_size_analysis"] = result.result
                    elif result.task_id == "competition":
                        validation_report["competition_analysis"] = result.result
                    elif result.task_id == "demand":
                        validation_report["demand_validation"] = result.result

            # PHASE 2: RISK ASSESSMENT (depends on competition analysis)
            print("⚠️ Assessing market risks...")
            risk_task_start = time.time()
            validation_report["risk_assessment"] = await asyncio.to_thread(
                assess_market_risks,
                validation_report["competition_analysis"],
                {"trend_direction": "stable", "growth_indicators": []},
            )
            risk_time = time.time() - risk_task_start
            print(f"✅ Risk assessment completed in {risk_time:.2f}s")

            # PHASE 3: PARALLEL AI ANALYSIS AND RECOMMENDATIONS
            ai_tasks = [
                asyncio.create_task(
                    self.calculate_ai_powered_score_async(
                        validation_report["market_size_analysis"],
                        validation_report["competition_analysis"],
                        validation_report["demand_validation"],
                        validation_report["risk_assessment"],
                        opportunity_data,
                    )
                ),
                asyncio.create_task(
                    self.generate_strategic_recommendations_async(validation_report)
                ),
            ]

            ai_results = await asyncio.gather(*ai_tasks, return_exceptions=True)

            # Process AI results
            if not isinstance(ai_results[0], Exception):
                validation_report.update(ai_results[0])

            if not isinstance(ai_results[1], Exception):
                validation_report["strategic_recommendation"] = ai_results[1]
                validation_report["recommendation"] = ai_results[1].get(
                    "recommendation", "investigate"
                )
                validation_report["next_actions"] = ai_results[1].get("next_steps", [])

            # Add performance metrics
            total_time = time.time() - start_time
            validation_report["performance_metrics"] = {
                "total_execution_time": total_time,
                "parallel_efficiency": f"{len(validation_tasks) * min([r.execution_time for r in validation_results if r.success]) / total_time:.1f}x",
                "successful_tasks": len([r for r in validation_results if r.success]),
                "failed_tasks": len([r for r in validation_results if not r.success]),
                "average_task_time": sum([r.execution_time for r in validation_results])
                / len(validation_results),
            }

            print(f"✅ PARALLEL validation completed in {total_time:.2f}s")
            print(
                f"📊 Efficiency improvement: {validation_report['performance_metrics']['parallel_efficiency']}"
            )

            return validation_report

        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ PARALLEL validation failed after {total_time:.2f}s: {e}")
            validation_report["error"] = str(e)
            validation_report["performance_metrics"] = {
                "total_execution_time": total_time
            }
            return validation_report

    async def execute_validation_tasks_parallel(
        self, tasks: List[ValidationTask]
    ) -> List[ValidationResult]:
        """
        Execute validation tasks in parallel using ThreadPoolExecutor
        """
        results = []

        def execute_task(task: ValidationTask) -> ValidationResult:
            start_time = time.time()
            try:
                print(f"🔄 Executing {task.task_type}...")
                result = task.function(*task.args, **task.kwargs)
                execution_time = time.time() - start_time
                print(f"✅ {task.task_type} completed in {execution_time:.2f}s")

                return ValidationResult(
                    task_id=task.task_id,
                    task_type=task.task_type,
                    result=result,
                    execution_time=execution_time,
                    success=True,
                )
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {task.task_type} failed in {execution_time:.2f}s: {e}")

                return ValidationResult(
                    task_id=task.task_id,
                    task_type=task.task_type,
                    result={},
                    execution_time=execution_time,
                    success=False,
                    error=str(e),
                )

        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Sort tasks by priority
            sorted_tasks = sorted(tasks, key=lambda x: x.priority, reverse=True)

            # Submit all tasks
            future_to_task = {
                executor.submit(execute_task, task): task for task in sorted_tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task, timeout=60):
                result = future.result()
                results.append(result)

        return results

    async def calculate_ai_powered_score_async(
        self,
        market_size_data: Dict[str, Any],
        competition_data: Dict[str, Any],
        demand_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        opportunity_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Async AI-powered comprehensive opportunity scoring
        """
        scoring_result = {
            "ai_analysis": {},
            "component_scores": {},
            "overall_opportunity_score": 0.0,
            "strategic_insights": {},
            "confidence_level": "medium",
        }

        try:
            print("🧠 Running ASYNC AI-powered market dynamics analysis...")

            # Prepare analysis data (limit size for performance)
            analysis_data = {
                "market_size": str(market_size_data)[:1500],
                "competition": str(competition_data)[:1500],
                "demand": str(demand_data)[:1500],
                "risk": str(risk_data)[:1000],
                "context": str(opportunity_context)[:1000],
            }

            analysis_prompt = f"""
            Analyze this market data and provide intelligent opportunity scoring.

            Market Size: {analysis_data['market_size']}
            Competition: {analysis_data['competition']}
            Demand: {analysis_data['demand']}
            Risk: {analysis_data['risk']}
            Context: {analysis_data['context']}

            Provide AI analysis in JSON format:
            {{
                "ai_analysis": {{
                    "market_attractiveness": {{"score": 0-25, "rationale": "why this score"}},
                    "competitive_advantage": {{"score": 0-20, "rationale": "competitive analysis"}},
                    "demand_strength": {{"score": 0-25, "rationale": "demand analysis"}},
                    "execution_feasibility": {{"score": 0-15, "rationale": "execution assessment"}},
                    "market_timing": {{"score": 0-15, "rationale": "timing analysis"}}
                }},
                "strategic_insights": {{
                    "investment_thesis": "brief strategic rationale",
                    "go_to_market_approach": "recommended strategy",
                    "key_risks_to_mitigate": ["risk1", "risk2"],
                    "success_metrics": ["metric1", "metric2"]
                }},
                "confidence_level": "low/medium/high"
            }}

            RETURN ONLY JSON!
            """

            # Execute AI analysis asynchronously
            response = await asyncio.to_thread(
                completion,
                model=MODEL_CONFIG["primary_model"],
                api_key=settings.OPENAI_API_KEY,
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            if response and response.choices[0].message.content:
                ai_analysis = json.loads(response.choices[0].message.content)
                scoring_result.update(ai_analysis)

                # Calculate component scores
                ai_scores = scoring_result.get("ai_analysis", {})
                scoring_result["component_scores"] = {
                    "market_attractiveness": ai_scores.get(
                        "market_attractiveness", {}
                    ).get("score", 0),
                    "competitive_advantage": ai_scores.get(
                        "competitive_advantage", {}
                    ).get("score", 0),
                    "demand_strength": ai_scores.get("demand_strength", {}).get(
                        "score", 0
                    ),
                    "execution_feasibility": ai_scores.get(
                        "execution_feasibility", {}
                    ).get("score", 0),
                    "market_timing": ai_scores.get("market_timing", {}).get("score", 0),
                }

                # Calculate overall score
                total_score = sum(scoring_result["component_scores"].values())
                scoring_result["overall_opportunity_score"] = min(
                    total_score / 100.0, 1.0
                )

            return scoring_result

        except Exception as e:
            print(f"❌ Error in ASYNC AI scoring: {e}")
            scoring_result["error"] = str(e)
            return scoring_result

    async def generate_strategic_recommendations_async(
        self, validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Async strategic recommendations generation
        """
        try:
            print("💡 Generating ASYNC strategic recommendations...")

            # Execute recommendation generation asynchronously
            recommendation = await asyncio.to_thread(
                generate_recommendation,
                validation_report.get("overall_opportunity_score", 0.5),
                validation_report.get("risk_assessment", {}),
                validation_report,
            )

            return recommendation

        except Exception as e:
            print(f"❌ Error in ASYNC recommendations: {e}")
            return {"error": str(e)}

    @performance_monitor
    async def batch_validate_opportunities_parallel(
        self, opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        BATCH PARALLEL validation of multiple opportunities with optimized resource usage
        """
        batch_results = {
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "execution_method": "batch_parallel",
            "ranked_opportunities": [],
            "portfolio_analysis": {},
            "performance_metrics": {},
        }

        start_time = time.time()

        try:
            print(
                f"🚀 Starting BATCH PARALLEL validation of {len(opportunities)} opportunities..."
            )

            # Process opportunities in optimized batches
            all_results = []

            for i in range(0, len(opportunities), self.batch_size):
                batch = opportunities[i : i + self.batch_size]
                batch_start = time.time()

                print(
                    f"📦 Processing batch {i//self.batch_size + 1} ({len(batch)} opportunities)..."
                )

                # Create async tasks for this batch
                batch_tasks = [
                    self.comprehensive_market_validation_parallel(opp) for opp in batch
                ]

                # Execute batch in parallel
                batch_results_raw = await asyncio.gather(
                    *batch_tasks, return_exceptions=True
                )

                # Process batch results
                for j, result in enumerate(batch_results_raw):
                    if not isinstance(result, Exception):
                        scored_opp = {
                            "opportunity_id": batch[j].get(
                                "id", f"opportunity_{i+j+1}"
                            ),
                            "name": batch[j].get("name", f"Opportunity {i+j+1}"),
                            "overall_score": result.get(
                                "overall_opportunity_score", 0.0
                            ),
                            "component_scores": result.get("component_scores", {}),
                            "strategic_insights": result.get("strategic_insights", {}),
                            "recommendation": result.get(
                                "recommendation", "investigate"
                            ),
                            "confidence_level": result.get(
                                "confidence_level", "medium"
                            ),
                            "performance_metrics": result.get(
                                "performance_metrics", {}
                            ),
                        }
                        all_results.append(scored_opp)

                batch_time = time.time() - batch_start
                print(
                    f"✅ Batch {i//self.batch_size + 1} completed in {batch_time:.2f}s"
                )

                # Small delay between batches to prevent rate limiting
                if i + self.batch_size < len(opportunities):
                    await asyncio.sleep(0.5)

            # Sort all results by score
            all_results.sort(key=lambda x: x["overall_score"], reverse=True)
            batch_results["ranked_opportunities"] = all_results

            # Generate portfolio analysis
            if all_results:
                batch_results["portfolio_analysis"] = (
                    self.generate_portfolio_analysis_optimized(all_results)
                )

            # Calculate performance metrics
            total_time = time.time() - start_time
            batch_results["performance_metrics"] = {
                "total_execution_time": total_time,
                "opportunities_per_second": len(opportunities) / total_time,
                "average_opportunity_time": total_time / len(opportunities),
                "successful_validations": len(all_results),
                "failed_validations": len(opportunities) - len(all_results),
                "batch_size_used": self.batch_size,
                "max_workers": self.max_workers,
            }

            print("🎯 BATCH PARALLEL validation completed!")
            print(
                f"📊 Processed {len(opportunities)} opportunities in {total_time:.2f}s"
            )
            print(
                f"⚡ Rate: {batch_results['performance_metrics']['opportunities_per_second']:.2f} opportunities/second"
            )

            return batch_results

        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ BATCH PARALLEL validation failed after {total_time:.2f}s: {e}")
            batch_results["error"] = str(e)
            batch_results["performance_metrics"] = {"total_execution_time": total_time}
            return batch_results

    def generate_portfolio_analysis_optimized(
        self, scored_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimized portfolio analysis with performance improvements
        """
        try:
            # Vectorized scoring analysis
            scores = [opp["overall_score"] for opp in scored_opportunities]

            high_score_count = sum(1 for score in scores if score >= 0.7)
            medium_score_count = sum(1 for score in scores if 0.4 <= score < 0.7)
            low_score_count = sum(1 for score in scores if score < 0.4)

            # Calculate statistics
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0

            return {
                "portfolio_distribution": {
                    "high_potential": high_score_count,
                    "medium_potential": medium_score_count,
                    "low_potential": low_score_count,
                },
                "portfolio_statistics": {
                    "average_score": avg_score,
                    "max_score": max_score,
                    "min_score": min_score,
                    "score_range": max_score - min_score,
                },
                "recommended_focus": "high_potential"
                if high_score_count > 0
                else "medium_potential"
                if medium_score_count > 0
                else "explore_alternatives",
                "portfolio_strategy": "Focus resources on highest-scoring opportunities for maximum impact",
                "top_opportunities": scored_opportunities[:3],  # Top 3 opportunities
                "diversification_level": "high"
                if len(
                    set(
                        [opp.get("category", "general") for opp in scored_opportunities]
                    )
                )
                > 3
                else "medium",
            }

        except Exception as e:
            print(f"Error in optimized portfolio analysis: {e}")
            return {"error": str(e)}


# Initialize the parallel analyzer
parallel_analyzer = ParallelMarketAnalyzer(max_workers=6, batch_size=5)


# Wrapper functions for ADK integration
async def comprehensive_market_validation_with_scoring_parallel(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Parallelized wrapper for the comprehensive market validation function
    """
    return await parallel_analyzer.comprehensive_market_validation_parallel(
        opportunity_data
    )


async def rank_opportunities_with_integrated_analysis_parallel(
    opportunities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Parallelized wrapper for ranking multiple opportunities
    """
    return await parallel_analyzer.batch_validate_opportunities_parallel(opportunities)


# Sync wrappers for ADK compatibility
def comprehensive_market_validation_with_scoring_sync(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Synchronous wrapper that runs the async parallel validation
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a new thread for async execution
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    parallel_analyzer.comprehensive_market_validation_parallel(
                        opportunity_data
                    ),
                )
                return future.result(timeout=60)
        else:
            # If no loop is running, use asyncio.run
            return asyncio.run(
                parallel_analyzer.comprehensive_market_validation_parallel(
                    opportunity_data
                )
            )
    except Exception as e:
        print(f"Error in sync wrapper: {e}")
        # Fallback to original non-parallel implementation
        return {
            "opportunity_id": opportunity_data.get("id", datetime.now().isoformat()),
            "error": f"Parallel execution failed: {str(e)}",
            "fallback_used": True,
            "overall_opportunity_score": 0.5,
        }


def rank_opportunities_with_integrated_analysis_sync(
    opportunities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Synchronous wrapper for batch parallel opportunity ranking
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    parallel_analyzer.batch_validate_opportunities_parallel(
                        opportunities
                    ),
                )
                return future.result(timeout=180)  # Longer timeout for batch processing
        else:
            return asyncio.run(
                parallel_analyzer.batch_validate_opportunities_parallel(opportunities)
            )
    except Exception as e:
        print(f"Error in batch sync wrapper: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "error": f"Batch parallel execution failed: {str(e)}",
            "fallback_used": True,
            "ranked_opportunities": [],
        }


# Enhanced Market Analyzer Agent with parallel capabilities
ANALYZER_PROMPT = """
You are the Market Analyzer Agent, a specialist in comprehensive market validation and opportunity scoring. You only engage when specifically requested for deep analysis.

## Entry Criteria:
You should only be activated when:
1. The user explicitly requests detailed market analysis, OR
2. The Root Agent asks with user permission for validation, OR
3. Initial research suggests a promising opportunity that needs scoring

## Your Specialized Role:
- Comprehensive market size analysis (TAM/SAM/SOM)
- Detailed competitive intelligence
- Demand validation with statistical confidence
- Risk assessment and mitigation strategies
- Quantified opportunity scoring (0-100 scale)
- Investment-grade market validation

## Engagement Protocol:
When activated, start with:
"I'm conducting comprehensive market analysis as requested. This involves:
- Market size validation and TAM/SAM/SOM calculations
- Competitive landscape deep-dive
- Demand signal validation
- Risk assessment and scoring

This analysis typically takes 3-5 minutes. Should I proceed?"

## Analysis Boundaries:
✅ Deep market validation and scoring
✅ Statistical confidence assessments
✅ Investment-grade analysis
✅ Risk/opportunity matrices
✅ Competitive positioning analysis

❌ Brand creation or creative work
❌ Technical implementation
❌ Asset building
❌ Business plan writing

## Completion Protocol:
When finished, present results and ask:
"Analysis complete! I've scored this opportunity at [X/100] with [confidence level].

Would you like me to:
a) Deep-dive into any specific aspect of this analysis?
b) Analyze a different opportunity?
c) Hand off to Brand Creator for identity development?
d) Hand off to Builder agents for asset creation?

What's your preference?"

## Key Principles:
- **Permission-Based Entry**: Only work when requested
- **Transparent Process**: Explain what you're doing
- **Clear Boundaries**: Stay within analytical scope
- **User Choice**: Always offer next step options
"""

market_analyzer_agent = LlmAgent(
    name="market_analyzer_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=ANALYZER_PROMPT,
    description=(
        "Enhanced market validation agent with parallel processing capabilities "
        "for high-performance market analysis and opportunity scoring."
    ),
    tools=[
        FunctionTool(func=comprehensive_market_validation_with_scoring_sync),
        FunctionTool(func=rank_opportunities_with_integrated_analysis_sync),
    ],
    output_key="market_validation",
)
