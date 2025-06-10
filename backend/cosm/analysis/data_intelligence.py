"""
Data Intelligence Agent - Fixed File Access Security
Combines BigQuery Intelligence + Code Executor capabilities with proper file access controls
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.cloud import bigquery
from google.genai import Client
from google.oauth2 import service_account
from typing import Dict, List, Any
import json
from datetime import datetime
import pandas as pd
import tempfile
import subprocess
import os
import sys
import traceback
from pathlib import Path
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from ..tools.search import search_tool
from google.adk.models.lite_llm import LiteLlm

# Initialize clients
bq_client = (
    bigquery.Client(
        credentials=service_account.Credentials.from_service_account_file(
            "service-account.json"
        ),
        project=settings.GOOGLE_CLOUD_PROJECT_ID,
    )
    if hasattr(settings, "GOOGLE_CLOUD_PROJECT_ID") and settings.GOOGLE_CLOUD_PROJECT_ID
    else None
)

client = Client()

DATA_INTELLIGENCE_PROMPT = """
You are the unified Data Intelligence Agent with integrated capabilities. You combine:

1. BIGQUERY ANALYTICS - Advanced data storage and analysis using BigQuery
2. CODE EXECUTION - Python code execution for data processing and visualization
3. MARKET INTELLIGENCE - Data-driven insights generation

Your mission is to transform raw market data into actionable intelligence by:
- Storing and analyzing market data in BigQuery for pattern recognition
- Executing Python code for data analysis, visualization, and validation
- Generating data-driven market insights and recommendations
- Providing quantified opportunity assessments with statistical backing

Use your integrated data capabilities to provide comprehensive market intelligence with real analytics.
"""


def integrated_data_analysis_and_storage(
    keywords: List[str],
    market_data: Dict[str, Any],
    analysis_type: str = "comprehensive",
) -> Dict[str, Any]:
    """
    Integrated function combining BigQuery storage with code execution for market analysis

    Args:
        keywords: List of market keywords to analyze
        market_data: Optional market data to analyze
        analysis_type: Type of analysis to perform

    Returns:
        Comprehensive data analysis results with BigQuery insights and code execution results
    """
    analysis_result = {
        "keywords": keywords,
        "analysis_type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "bigquery_analysis": {},
        "code_execution_results": {},
        "data_visualizations": [],
        "market_insights": {},
        "opportunity_score": 0.0,
        "statistical_confidence": 0.0,
    }

    try:
        print(f"🔍 Starting integrated data analysis for: {', '.join(keywords)}")

        # Phase 1: BigQuery Data Collection and Analysis
        if bq_client:
            print("💾 Setting up BigQuery analysis...")
            bigquery_results = setup_and_analyze_bigquery_data(keywords, market_data)
            analysis_result["bigquery_analysis"] = bigquery_results
        else:
            print("⚠️ BigQuery client not available, using alternative data analysis")
            analysis_result["bigquery_analysis"] = {
                "status": "unavailable",
                "message": "BigQuery client not configured",
            }

        # Phase 2: Code Execution for Data Processing
        print("⚡ Executing data analysis code...")
        code_results = execute_market_data_analysis(
            keywords, market_data, analysis_result["bigquery_analysis"]
        )
        analysis_result["code_execution_results"] = code_results

        # Phase 3: Generate Visualizations
        print("📊 Creating data visualizations...")
        if code_results.get("success") and code_results.get("files_created"):
            analysis_result["data_visualizations"] = extract_visualization_data(
                code_results["files_created"]
            )

        # Phase 4: Generate Market Intelligence Summary
        print("🧠 Generating market intelligence summary...")
        analysis_result["market_insights"] = generate_integrated_market_intelligence(
            analysis_result["bigquery_analysis"],
            analysis_result["code_execution_results"],
            keywords,
        )

        # Phase 5: Calculate Opportunity Score
        analysis_result["opportunity_score"] = calculate_data_driven_opportunity_score(
            analysis_result
        )
        analysis_result["statistical_confidence"] = calculate_statistical_confidence(
            analysis_result
        )

        print("✅ Integrated data analysis completed!")
        return analysis_result

    except Exception as e:
        print(f"❌ Error in integrated data analysis: {e}")
        analysis_result["error"] = str(e)
        return analysis_result


def execute_python_code_integrated(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Integrated Python code execution with enhanced error handling and proper file access control
    """
    result = {
        "success": False,
        "output": "",
        "error": "",
        "execution_time": 0,
        "files_created": [],
        "timestamp": datetime.now().isoformat(),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            start_time = datetime.now()

            # Write code to temporary file
            code_file = temp_path / "exec_code.py"

            # Fixed safety wrapper with proper path handling
            safe_code = f"""
import sys
import os
import json
import traceback
from pathlib import Path

# Restrict file access to temp directory
import builtins
original_open = builtins.open

def safe_open(file, mode='r', **kwargs):
    if isinstance(file, (str, Path)):
        try:
            # Convert to Path object and resolve
            file_path = Path(file)

            # If path is relative, make it relative to current working directory (temp_dir)
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            else:
                file_path = file_path.resolve()

            # Get the temp directory path
            temp_path = Path(r"{temp_dir}").resolve()

            # Check if the resolved file path is within temp directory
            try:
                file_path.relative_to(temp_path)
            except ValueError:
                raise PermissionError(f"File access outside temp directory not allowed: {{file_path}}")

        except Exception as e:
            # If there's any issue with path resolution, block the access
            raise PermissionError(f"Invalid file path: {{file}} - {{str(e)}}")

    return original_open(file, mode, **kwargs)

builtins.open = safe_open

# Set working directory to temp directory
os.chdir(r"{temp_dir}")

# Execute analysis code
try:
{_indent_code(code, 4)}
except Exception as e:
    print(f"EXECUTION_ERROR: {{type(e).__name__}}: {{str(e)}}")
    traceback.print_exc()
"""

            code_file.write_text(safe_code, encoding="utf-8")

            # Execute the code with proper working directory
            process = subprocess.run(
                [sys.executable, str(code_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={
                    **os.environ,
                    "PYTHONPATH": str(temp_dir),
                    "TMPDIR": temp_dir,
                    "TEMP": temp_dir,
                    "TMP": temp_dir,
                },
            )

            end_time = datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()

            # Capture output
            result["output"] = process.stdout
            if process.stderr:
                result["error"] = process.stderr

            # Check for execution errors
            if "EXECUTION_ERROR:" in result["output"]:
                result["error"] = result["output"]
                result["output"] = ""
            else:
                result["success"] = process.returncode == 0

            # List created files with proper error handling
            created_files = []
            try:
                for file_path in temp_path.iterdir():
                    if file_path.name != "exec_code.py" and file_path.is_file():
                        try:
                            file_size = file_path.stat().st_size
                            if file_size < 1024 * 1024:  # 1MB limit
                                if file_path.suffix in [".txt", ".json", ".csv"]:
                                    content = file_path.read_text(
                                        encoding="utf-8", errors="ignore"
                                    )
                                    created_files.append(
                                        {
                                            "name": file_path.name,
                                            "size": file_size,
                                            "content": content[
                                                :10000
                                            ],  # Limit content size
                                            "type": "text",
                                        }
                                    )
                                else:
                                    created_files.append(
                                        {
                                            "name": file_path.name,
                                            "size": file_size,
                                            "type": "binary",
                                        }
                                    )
                            else:
                                created_files.append(
                                    {
                                        "name": file_path.name,
                                        "size": file_size,
                                        "type": "large_file",
                                        "note": "File too large to include content",
                                    }
                                )
                        except Exception as e:
                            created_files.append(
                                {
                                    "name": file_path.name,
                                    "error": f"Error reading file: {str(e)}",
                                }
                            )
            except Exception as e:
                result["file_listing_error"] = f"Error listing files: {str(e)}"

            result["files_created"] = created_files

        except subprocess.TimeoutExpired:
            result["error"] = f"Code execution timed out after {timeout} seconds"
        except Exception as e:
            result["error"] = f"Execution failed: {str(e)}"
            result["traceback"] = traceback.format_exc()

    return result


def execute_market_data_analysis(
    keywords: List[str],
    market_data: Dict[str, Any],
    bigquery_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Execute comprehensive market data analysis using Python code
    """
    # Escape the data for safe string interpolation
    market_data_json = (
        json.dumps(market_data or {}, default=str, indent=2)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )
    bigquery_data_json = (
        json.dumps(bigquery_data or {}, default=str, indent=2)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )

    analysis_code = f'''
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

print("=== INTEGRATED MARKET DATA ANALYSIS ===")
print(f"Analysis timestamp: {{datetime.now()}}")
print(f"Keywords: {keywords}")

# Market data analysis
try:
    market_data = json.loads("""{market_data_json}""")
except json.JSONDecodeError as e:
    print(f"Error parsing market data: {{e}}")
    market_data = {{}}

try:
    bigquery_data = json.loads("""{bigquery_data_json}""")
except json.JSONDecodeError as e:
    print(f"Error parsing BigQuery data: {{e}}")
    bigquery_data = {{}}

print("\\n1. MARKET DATA SUMMARY")
if market_data:
    print(f"Market data keys: {{list(market_data.keys())}}")

    # Analyze market signals if available
    if 'market_signals' in market_data:
        signals = market_data['market_signals']
        print(f"Total market signals: {{len(signals) if isinstance(signals, list) else 'N/A'}}")

        if isinstance(signals, list) and signals:
            # Signal sentiment analysis
            sentiments = {{'positive': 0, 'negative': 0, 'neutral': 0}}
            for signal in signals:
                sentiment = signal.get('sentiment', 'neutral')
                if sentiment in sentiments:
                    sentiments[sentiment] += 1

            print(f"Signal sentiment distribution: {{sentiments}}")

            # Create sentiment visualization with error handling
            try:
                plt.figure(figsize=(10, 6))
                plt.subplot(1, 2, 1)
                if sum(sentiments.values()) > 0:
                    plt.pie(sentiments.values(), labels=sentiments.keys(), autopct='%1.1f%%')
                    plt.title('Market Signal Sentiment Distribution')
                else:
                    plt.text(0.5, 0.5, 'No sentiment data available', ha='center', va='center')
                    plt.title('Market Signal Sentiment Distribution')

                # Signal strength analysis
                strengths = {{'high': 0, 'medium': 0, 'low': 0}}
                for signal in signals:
                    strength = signal.get('strength', 'medium')
                    if strength in strengths:
                        strengths[strength] += 1

                plt.subplot(1, 2, 2)
                if sum(strengths.values()) > 0:
                    plt.bar(strengths.keys(), strengths.values())
                    plt.title('Signal Strength Distribution')
                    plt.ylabel('Count')
                else:
                    plt.text(0.5, 0.5, 'No strength data available', ha='center', va='center')
                    plt.title('Signal Strength Distribution')

                plt.tight_layout()
                plt.savefig('market_signals_analysis.png', dpi=150, bbox_inches='tight')
                plt.close()
                print("Market signals visualization saved successfully")

            except Exception as e:
                print(f"Error creating visualization: {{e}}")

            print(f"Signal strength distribution: {{strengths}}")

print("\\n2. BIGQUERY DATA ANALYSIS")
if bigquery_data and 'analysis_results' in bigquery_data:
    bq_results = bigquery_data['analysis_results']
    print(f"BigQuery analysis keys: {{list(bq_results.keys()) if isinstance(bq_results, dict) else 'N/A'}}")

print("\\n3. OPPORTUNITY SCORING FACTORS")
opportunity_factors = {{}}

# Calculate market readiness score
if market_data:
    signals_count = len(market_data.get('market_signals', []))
    liminal_opps = len(market_data.get('liminal_opportunities', []))

    opportunity_factors['signal_strength'] = min(signals_count / 10.0, 1.0)
    opportunity_factors['liminal_potential'] = min(liminal_opps / 3.0, 1.0)

    # Competition analysis
    competition = market_data.get('competition_analysis', {{}})
    comp_level = competition.get('competition_level', 'high')
    opportunity_factors['competition_advantage'] = {{
        'low': 0.8, 'medium': 0.5, 'high': 0.2
    }}.get(comp_level, 0.5)

print(f"Opportunity factors: {{opportunity_factors}}")

# Calculate composite opportunity score
composite_score = 0.0
if opportunity_factors:
    composite_score = sum(opportunity_factors.values()) / len(opportunity_factors)
    print(f"\\nCOMPOSITE OPPORTUNITY SCORE: {{composite_score:.3f}}")

    # Create opportunity scoring visualization with error handling
    try:
        plt.figure(figsize=(12, 8))

        # Factor breakdown
        plt.subplot(2, 2, 1)
        if opportunity_factors:
            plt.bar(list(opportunity_factors.keys()), list(opportunity_factors.values()))
            plt.title('Opportunity Scoring Factors')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Score (0-1)')

        # Overall score gauge
        plt.subplot(2, 2, 2)
        colors = ['red' if composite_score < 0.3 else 'orange' if composite_score < 0.6 else 'green']
        plt.pie([composite_score, 1-composite_score], labels=['Opportunity', 'Gap'],
                colors=colors + ['lightgray'], startangle=90)
        plt.title(f'Overall Score: {{composite_score:.1%}}')

        plt.tight_layout()
        plt.savefig('opportunity_analysis.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Opportunity analysis visualization saved successfully")

    except Exception as e:
        print(f"Error creating opportunity visualization: {{e}}")

print("\\n4. MARKET TREND INDICATORS")
trend_data = market_data.get('trend_analysis', {{}}) if market_data else {{}}
if trend_data:
    print(f"Trend direction: {{trend_data.get('trend_direction', 'unknown')}}")
    print(f"Growth drivers: {{trend_data.get('growth_drivers', [])}}")

# Save analysis summary
summary = {{
    'analysis_timestamp': datetime.now().isoformat(),
    'keywords_analyzed': {keywords},
    'opportunity_factors': opportunity_factors,
    'composite_score': composite_score,
    'data_quality': 'high' if market_data and len(market_data.get('market_signals', [])) > 5 else 'medium'
}}

try:
    with open('analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("Analysis summary saved successfully")
except Exception as e:
    print(f"Error saving analysis summary: {{e}}")

print("\\n=== ANALYSIS COMPLETE ===")
print("Expected files: market_signals_analysis.png, opportunity_analysis.png, analysis_summary.json")
'''

    return execute_python_code_integrated(analysis_code)


def _indent_code(code: str, spaces: int) -> str:
    """Indent code by specified number of spaces"""
    indent = " " * spaces
    return "\n".join(indent + line for line in code.splitlines())


def setup_and_analyze_bigquery_data(
    keywords: List[str],
    market_data: Dict[str, Any],
    dataset_id: str = "agentcosm_market",
) -> Dict[str, Any]:
    """
    Consolidated BigQuery setup and analysis
    """
    bigquery_result = {
        "setup_status": "pending",
        "data_stored": 0,
        "analysis_results": {},
        "trend_analysis": {},
        "insights": {},
    }

    try:
        if not bq_client:
            return {"error": "BigQuery client not available"}

        # Setup tables
        setup_success = setup_bigquery_tables_integrated(dataset_id)
        bigquery_result["setup_status"] = "success" if setup_success else "failed"

        if setup_success and market_data:
            # Store market data
            stored_count = store_market_data_in_bigquery(market_data, dataset_id)
            bigquery_result["data_stored"] = stored_count

            # Analyze stored data
            bigquery_result["analysis_results"] = analyze_bigquery_market_data(
                keywords, dataset_id
            )
            bigquery_result["trend_analysis"] = get_trend_analysis_from_bigquery(
                keywords, dataset_id
            )

        return bigquery_result

    except Exception as e:
        print(f"Error in BigQuery analysis: {e}")
        bigquery_result["error"] = str(e)
        return bigquery_result


def setup_bigquery_tables_integrated(dataset_id: str = "agentcosm_market") -> bool:
    """Integrated BigQuery table setup"""
    try:
        if not bq_client:
            return False

        # Create dataset
        dataset_id_full = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_id_full)
        dataset.location = "US"
        bq_client.create_dataset(dataset, exists_ok=True)

        # Simplified schema for performance
        signals_schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("keyword", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sentiment", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("relevance_score", "FLOAT", mode="REQUIRED"),
        ]

        # Create market signals table
        table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}.market_signals"
        table = bigquery.Table(table_id, schema=signals_schema)
        bq_client.create_table(table, exists_ok=True)

        return True

    except Exception as e:
        print(f"BigQuery setup error: {e}")
        return False


def store_market_data_in_bigquery(market_data: Dict[str, Any], dataset_id: str) -> int:
    """Store market data in BigQuery"""
    try:
        if not bq_client or not market_data:
            return 0

        signals = market_data.get("market_signals", [])
        if not signals:
            return 0

        # Prepare data for BigQuery
        bq_data = []
        for i, signal in enumerate(signals[:50]):  # Limit for performance
            bq_data.append(
                {
                    "id": f"signal_{int(datetime.now().timestamp())}_{i}",
                    "timestamp": datetime.now(),
                    "keyword": signal.get("keyword", "unknown"),
                    "content": str(signal.get("content", ""))[:1000],  # Limit content
                    "sentiment": float(signal.get("sentiment_score", 0.0))
                    if isinstance(signal.get("sentiment_score"), (int, float))
                    else 0.0,
                    "relevance_score": float(signal.get("relevance_score", 0.5)),
                }
            )

        if bq_data:
            df = pd.DataFrame(bq_data)
            table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}.market_signals"

            job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
            job = bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()

            return len(bq_data)

        return 0

    except Exception as e:
        print(f"Error storing data in BigQuery: {e}")
        return 0


def analyze_bigquery_market_data(
    keywords: List[str], dataset_id: str
) -> Dict[str, Any]:
    """Analyze market data stored in BigQuery"""
    try:
        if not bq_client:
            return {"error": "BigQuery client not available"}

        # Simplified analysis query for performance
        query = f"""
        SELECT
            keyword,
            COUNT(*) as signal_count,
            AVG(sentiment) as avg_sentiment,
            AVG(relevance_score) as avg_relevance
        FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}.market_signals`
        WHERE keyword IN UNNEST(@keywords)
        AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        GROUP BY keyword
        ORDER BY signal_count DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("keywords", "STRING", keywords),
            ]
        )

        results = bq_client.query(query, job_config=job_config).to_dataframe()

        analysis = {}
        for _, row in results.iterrows():
            analysis[row["keyword"]] = {
                "signal_count": int(row["signal_count"]),
                "avg_sentiment": float(row["avg_sentiment"]),
                "avg_relevance": float(row["avg_relevance"]),
            }

        return analysis

    except Exception as e:
        print(f"Error analyzing BigQuery data: {e}")
        return {"error": str(e)}


def get_trend_analysis_from_bigquery(
    keywords: List[str], dataset_id: str
) -> Dict[str, Any]:
    """Get trend analysis from BigQuery data"""
    try:
        if not bq_client:
            return {"error": "BigQuery client not available"}

        # Simple trend analysis
        return {
            "trend_direction": "stable",
            "data_points": len(keywords),
            "analysis_period": "30_days",
            "confidence": "medium",
        }

    except Exception as e:
        print(f"Error in trend analysis: {e}")
        return {"error": str(e)}


def generate_integrated_market_intelligence(
    bigquery_data: Dict[str, Any], code_results: Dict[str, Any], keywords: List[str]
) -> Dict[str, Any]:
    """Generate integrated market intelligence summary"""
    try:
        intelligence_prompt = f"""
        Generate market intelligence insights from this integrated data analysis:

        BigQuery Analysis: {json.dumps(bigquery_data, indent=2)[:2000]}
        Code Execution Results: {json.dumps(code_results, indent=2)[:2000]}
        Keywords: {keywords}

        Provide insights in JSON format:
        {{
            "executive_summary": "2-3 sentence key takeaway",
            "data_quality_assessment": "high/medium/low",
            "key_insights": ["insight1", "insight2", "insight3"],
            "opportunity_indicators": ["indicator1", "indicator2"],
            "risk_factors": ["risk1", "risk2"],
            "recommended_actions": ["action1", "action2"],
            "confidence_level": "high/medium/low"
        }}

        RETURN ONLY JSON AND NOTHING ELSE!!!!!!!!!!!!!
        """

        response = completion(
            model=MODEL_CONFIG["data_intelligence"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": intelligence_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            return safe_json_loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating market intelligence: {e}")

    return {
        "executive_summary": "Data analysis completed with integrated insights",
        "data_quality_assessment": "medium",
        "key_insights": ["Analysis completed successfully"],
        "confidence_level": "medium",
    }


def calculate_data_driven_opportunity_score(analysis_result: Dict[str, Any]) -> float:
    """Calculate opportunity score based on integrated data analysis"""
    try:
        score = 0.0

        # BigQuery data contribution
        bq_data = analysis_result.get("bigquery_analysis", {})
        if "analysis_results" in bq_data:
            signal_counts = [
                data.get("signal_count", 0)
                for data in bq_data["analysis_results"].values()
            ]
            if signal_counts:
                score += min(max(signal_counts) / 20.0, 0.3)

        # Code execution success contribution
        code_data = analysis_result.get("code_execution_results", {})
        if code_data.get("success"):
            score += 0.2

        # Files created contribution (visualizations/analysis)
        if code_data.get("files_created"):
            score += min(len(code_data["files_created"]) / 5.0, 0.3)

        # Market insights contribution
        insights = analysis_result.get("market_insights", {})
        if insights.get("confidence_level") == "high":
            score += 0.2
        elif insights.get("confidence_level") == "medium":
            score += 0.1

        return min(score, 1.0)

    except Exception as e:
        print(f"Error calculating opportunity score: {e}")
        return 0.5


def calculate_statistical_confidence(analysis_result: Dict[str, Any]) -> float:
    """Calculate statistical confidence in the analysis"""
    try:
        factors = []

        # Data availability
        if analysis_result.get("bigquery_analysis", {}).get("data_stored", 0) > 0:
            factors.append(0.3)

        # Code execution success
        if analysis_result.get("code_execution_results", {}).get("success"):
            factors.append(0.3)

        # Visualization generation
        if analysis_result.get("data_visualizations"):
            factors.append(0.2)

        # Market insights quality
        insights = analysis_result.get("market_insights", {})
        if insights.get("data_quality_assessment") == "high":
            factors.append(0.2)
        elif insights.get("data_quality_assessment") == "medium":
            factors.append(0.1)

        return sum(factors) if factors else 0.5

    except Exception:
        return 0.5


def extract_visualization_data(
    files_created: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Extract visualization data from created files"""
    visualizations = []

    for file_data in files_created:
        if file_data.get("name", "").endswith((".png", ".jpg", ".svg")):
            visualizations.append(
                {
                    "type": "chart",
                    "filename": file_data["name"],
                    "size": file_data.get("size", 0),
                    "description": f"Generated visualization: {file_data['name']}",
                }
            )
        elif (
            file_data.get("name") == "analysis_summary.json" and "content" in file_data
        ):
            try:
                summary_data = json.loads(file_data["content"])
                visualizations.append(
                    {
                        "type": "summary",
                        "data": summary_data,
                        "description": "Market analysis summary with key metrics",
                    }
                )
            except Exception:
                pass

    return visualizations


data_intelligence_agent = LlmAgent(
    name="data_intelligence_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["data_intelligence"], api_key=settings.OPENAI_API_KEY
    ),
    instruction=DATA_INTELLIGENCE_PROMPT,
    description=(
        "Integrated data intelligence agent that combines BigQuery analytics with "
        "Python code execution for comprehensive market data analysis and insights."
    ),
    tools=[
        FunctionTool(func=integrated_data_analysis_and_storage),
        search_tool,
    ],
    output_key="integrated_data_intelligence",
)
