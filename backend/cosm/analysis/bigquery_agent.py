"""
BigQuery Market Intelligence Agent
Integrates BigQuery with Tavily for enhanced market intelligence
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.cloud import bigquery
from google.genai import Client, types
from google.oauth2 import service_account
from typing import Dict, List, Any
import json
from datetime import datetime
import pandas as pd
from ..tools.tavily import tavily_market_research
from ..config import MODEL_CONFIG
from cosm.settings import settings

from litellm import completion

# Initialize clients
bq_client = bigquery.Client(
    credentials=service_account.Credentials.from_service_account_file(
        "service-account.json"
    ),
    project=settings.GOOGLE_CLOUD_PROJECT_ID,
)
genai_client = Client()

BIGQUERY_PROMPT = """
You are a BigQuery Market Intelligence Agent that combines web research with data analytics.

Your role:
1. Use Tavily to gather real-time market data
2. Store and analyze data in BigQuery for pattern recognition
3. Generate data-driven market insights
4. Provide quantified opportunity assessments

Focus on actionable insights backed by data analysis.
"""


def setup_bigquery_tables(dataset_id: str = "agentcosm_market"):
    """Setup BigQuery tables for market intelligence"""
    try:
        client = bigquery.Client(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            credentials=service_account.Credentials.from_service_account_file(
                "service-account.json"
            ),
        )

        # Create dataset
        dataset_id_full = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_id_full)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)

        signals_schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("keyword", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sentiment", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("relevance_score", "FLOAT", mode="REQUIRED"),
        ]

        # Search trends table (simplified)
        trends_schema = [
            bigquery.SchemaField("keyword", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("mention_count", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("avg_sentiment", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("source_diversity", "INTEGER", mode="REQUIRED"),
        ]

        # Create tables
        tables = [("market_signals", signals_schema), ("keyword_trends", trends_schema)]

        for table_name, schema in tables:
            table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{dataset_id}.{table_name}"
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table, exists_ok=True)
            print(f"✅ Table ready: {table_name}")

        return True

    except Exception as e:
        print(f"❌ BigQuery setup error: {e}")
        return False


def collect_and_analyze_market_data(
    keywords: List[str], dataset_id: str = "agentcosm_market"
) -> Dict[str, Any]:
    """
    Collect market data via Tavily and analyze with BigQuery
    """
    project_id = settings.GOOGLE_CLOUD_PROJECT_ID
    analysis_result = {
        "keywords": keywords,
        "timestamp": datetime.now().isoformat(),
        "data_collected": 0,
        "bigquery_analysis": {},
        "market_insights": {},
        "opportunity_score": 0.0,
        "trending_topics": [],
        "sentiment_analysis": {},
    }

    try:
        # Step 1: Collect data using Tavily
        print("🔍 Collecting market data with Tavily...")

        all_signals = []
        for keyword in keywords[:3]:  # Limit for mvp purposes
            # Use existing Tavily market research
            market_data = tavily_market_research(
                keywords=[keyword], research_type="market_analysis"
            )

            if not market_data.get("error"):
                for search_result in market_data.get("search_results", []):
                    for result in search_result.get("results", []):
                        signal = {
                            "id": f"{keyword}_{len(all_signals)}_{int(datetime.now().timestamp())}",
                            "timestamp": datetime.now(),
                            "keyword": keyword,
                            "title": result.get("title", ""),
                            "content": result.get("content", "")[
                                :1000
                            ],  # Limit for BigQuery
                            "url": result.get("url", ""),
                            "source": "tavily",
                            "sentiment": _calculate_simple_sentiment(
                                result.get("content", "")
                            ),
                            "relevance_score": result.get("score", 0.5),
                        }
                        all_signals.append(signal)

        analysis_result["data_collected"] = len(all_signals)

        if not all_signals:
            analysis_result["error"] = "No data collected"
            return analysis_result

        # Step 2: Store in BigQuery
        print(f"💾 Storing {len(all_signals)} signals in BigQuery...")

        df = pd.DataFrame(all_signals)
        table_id = f"{project_id}.{dataset_id}.market_signals"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
        )

        job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        # Step 3: Analyze with BigQuery
        print("📊 Running BigQuery analysis...")

        analysis_query = f"""
        WITH recent_signals AS (
            SELECT
                keyword,
                title,
                content,
                sentiment,
                relevance_score,
                timestamp
            FROM `{project_id}.{dataset_id}.market_signals`
            WHERE keyword IN UNNEST(@keywords)
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        ),
        keyword_stats AS (
            SELECT
                keyword,
                COUNT(*) as mention_count,
                AVG(sentiment) as avg_sentiment,
                AVG(relevance_score) as avg_relevance,
                COUNT(DISTINCT REGEXP_EXTRACT(url, r'https?://([^/]+)')) as source_diversity,
                ARRAY_AGG(title ORDER BY relevance_score DESC LIMIT 3) as top_titles
            FROM recent_signals
            GROUP BY keyword
        ),
        sentiment_distribution AS (
            SELECT
                keyword,
                COUNTIF(sentiment > 0.1) as positive_mentions,
                COUNTIF(sentiment < -0.1) as negative_mentions,
                COUNTIF(sentiment BETWEEN -0.1 AND 0.1) as neutral_mentions
            FROM recent_signals
            GROUP BY keyword
        )
        SELECT
            k.*,
            s.positive_mentions,
            s.negative_mentions,
            s.neural_mentions
        FROM keyword_stats k
        LEFT JOIN sentiment_distribution s ON k.keyword = s.keyword
        ORDER BY mention_count DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("keywords", "STRING", keywords),
            ]
        )

        query_results = bq_client.query(
            analysis_query, job_config=job_config
        ).to_dataframe()

        # Step 4: Process results
        bigquery_insights = {}
        trending_topics = []

        for _, row in query_results.iterrows():
            keyword_insight = {
                "keyword": row["keyword"],
                "mention_count": int(row["mention_count"]),
                "avg_sentiment": float(row["avg_sentiment"]),
                "avg_relevance": float(row["avg_relevance"]),
                "source_diversity": int(row["source_diversity"]),
                "positive_ratio": row["positive_mentions"] / row["mention_count"]
                if row["mention_count"] > 0
                else 0,
                "top_titles": row["top_titles"][:3] if row["top_titles"] else [],
            }
            bigquery_insights[row["keyword"]] = keyword_insight

            # Identify trending topics
            if row["mention_count"] > 5 and row["avg_relevance"] > 0.6:
                trending_topics.append(
                    {
                        "topic": row["keyword"],
                        "trend_strength": row["mention_count"] * row["avg_relevance"],
                        "sentiment": "positive"
                        if row["avg_sentiment"] > 0.1
                        else "negative"
                        if row["avg_sentiment"] < -0.1
                        else "neutral",
                    }
                )

        # Step 5: Calculate opportunity score
        opportunity_score = _calculate_opportunity_score(bigquery_insights)

        # Step 6: Generate insights with Gemini
        market_insights = _generate_bigquery_insights(bigquery_insights, keywords)

        analysis_result.update(
            {
                "bigquery_analysis": bigquery_insights,
                "market_insights": market_insights,
                "opportunity_score": opportunity_score,
                "trending_topics": sorted(
                    trending_topics, key=lambda x: x["trend_strength"], reverse=True
                )[:5],
                "sentiment_analysis": _analyze_overall_sentiment(bigquery_insights),
            }
        )

        # Step 7: Update trend tracking
        _update_trend_tracking(keywords, bigquery_insights, project_id, dataset_id)

        return analysis_result

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        analysis_result["error"] = str(e)
        return analysis_result


def get_historical_trend_analysis(
    keywords: List[str],
    dataset_id: str = "agentcosm_market",
    days_back: int = 30,
) -> Dict[str, Any]:
    """
    Analyze historical trends from BigQuery data
    """
    project_id = settings.GOOGLE_CLOUD_PROJECT_ID
    try:
        trend_query = f"""
        WITH daily_trends AS (
            SELECT
                keyword,
                DATE(timestamp) as date,
                COUNT(*) as daily_mentions,
                AVG(sentiment) as daily_sentiment,
                AVG(relevance_score) as daily_relevance
            FROM `{project_id}.{dataset_id}.market_signals`
            WHERE keyword IN UNNEST(@keywords)
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days_back DAY)
            GROUP BY keyword, DATE(timestamp)
        ),
        trend_analysis AS (
            SELECT
                keyword,
                AVG(daily_mentions) as avg_mentions,
                STDDEV(daily_mentions) as mention_volatility,
                CORR(UNIX_DATE(date), daily_mentions) as trend_correlation,
                AVG(daily_sentiment) as avg_sentiment_trend,
                COUNT(DISTINCT date) as data_points
            FROM daily_trends
            GROUP BY keyword
        )
        SELECT * FROM trend_analysis
        ORDER BY avg_mentions DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("keywords", "STRING", keywords),
                bigquery.ScalarQueryParameter("days_back", "INT64", days_back),
            ]
        )

        results = bq_client.query(trend_query, job_config=job_config).to_dataframe()

        trend_analysis = {}
        for _, row in results.iterrows():
            trend_analysis[row["keyword"]] = {
                "avg_daily_mentions": float(row["avg_mentions"]),
                "volatility": float(row["mention_volatility"])
                if row["mention_volatility"]
                else 0,
                "trend_direction": "growing"
                if row["trend_correlation"] > 0.3
                else "declining"
                if row["trend_correlation"] < -0.3
                else "stable",
                "trend_strength": abs(float(row["trend_correlation"]))
                if row["trend_correlation"]
                else 0,
                "sentiment_trend": float(row["avg_sentiment_trend"]),
                "data_quality": min(float(row["data_points"]) / days_back, 1.0),
            }

        return {
            "keywords": keywords,
            "analysis_period_days": days_back,
            "trend_analysis": trend_analysis,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ Trend analysis error: {e}")
        return {"error": str(e)}


def generate_market_intelligence_summary(
    current_analysis: Dict[str, Any], historical_trends: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate executive summary combining current and historical data
    """
    try:
        summary_prompt = f"""
        Generate a concise market intelligence summary based on this data:

        Current Analysis: {json.dumps(current_analysis, default=str)[:3000]}
        Historical Trends: {json.dumps(historical_trends, default=str)[:2000]}

        Return JSON with:
        {{
            "executive_summary": "2-3 sentence key takeaway",
            "market_momentum": "accelerating/stable/declining",
            "opportunity_level": "high/medium/low",
            "key_insights": ["insight1", "insight2", "insight3"],
            "recommended_action": "specific next step",
            "confidence_score": "0-100 score",
            "data_freshness": "description of data recency"
        }}
        """

        response = genai_client.models.generate_content(
            model=MODEL_CONFIG["primary_model"],
            contents=summary_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

        return {"error": "Failed to generate summary"}

    except Exception as e:
        print(f"❌ Summary generation error: {e}")
        return {"error": str(e)}


# Helper functions


def _calculate_simple_sentiment(text: str) -> float:
    """Simple sentiment calculation"""
    positive_words = [
        "good",
        "great",
        "excellent",
        "amazing",
        "love",
        "best",
        "awesome",
        "fantastic",
        "perfect",
        "outstanding",
    ]
    negative_words = [
        "bad",
        "terrible",
        "awful",
        "hate",
        "worst",
        "horrible",
        "disappointing",
        "frustrating",
        "useless",
        "broken",
    ]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count + neg_count == 0:
        return 0.0

    return (pos_count - neg_count) / (pos_count + neg_count)


def _calculate_opportunity_score(bigquery_insights: Dict[str, Any]) -> float:
    """Calculate opportunity score from BigQuery analysis"""
    if not bigquery_insights:
        return 0.0

    scores = []
    for keyword, data in bigquery_insights.items():
        # Simple scoring based on mentions, sentiment, and diversity
        mention_score = min(
            data["mention_count"] / 20.0, 1.0
        )  # Normalize to max 20 mentions
        sentiment_score = (data["avg_sentiment"] + 1) / 2  # Convert -1,1 to 0,1
        diversity_score = min(
            data["source_diversity"] / 10.0, 1.0
        )  # Normalize to max 10 sources

        keyword_score = (
            mention_score * 0.4 + sentiment_score * 0.3 + diversity_score * 0.3
        )
        scores.append(keyword_score)

    return sum(scores) / len(scores) if scores else 0.0


def _generate_bigquery_insights(
    bigquery_insights: Dict[str, Any], keywords: List[str]
) -> Dict[str, Any]:
    """Generate market insights from BigQuery analysis"""
    try:
        insights_prompt = f"""
        Analyze this BigQuery market data and provide insights:

        Data: {json.dumps(bigquery_insights, indent=2)}

        Return JSON with:
        {{
            "market_size_indicators": "assessment of market size",
            "competitive_landscape": "competition level assessment",
            "user_sentiment": "overall user sentiment analysis",
            "growth_opportunities": ["opportunity1", "opportunity2"],
            "risk_factors": ["risk1", "risk2"],
            "market_timing": "assessment of market timing"
        }}
        """

        response = completion(
            model=MODEL_CONFIG["bigquery_agent"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": insights_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Insights generation error: {e}")

    return {"error": "Failed to generate insights"}


def _analyze_overall_sentiment(bigquery_insights: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze overall sentiment across keywords"""
    if not bigquery_insights:
        return {}

    sentiments = [data["avg_sentiment"] for data in bigquery_insights.values()]
    avg_sentiment = sum(sentiments) / len(sentiments)

    return {
        "overall_sentiment": avg_sentiment,
        "sentiment_classification": "positive"
        if avg_sentiment > 0.1
        else "negative"
        if avg_sentiment < -0.1
        else "neutral",
        "sentiment_consistency": "high"
        if max(sentiments) - min(sentiments) < 0.5
        else "low",
        "keywords_analyzed": len(sentiments),
    }


def _update_trend_tracking(
    keywords: List[str], insights: Dict[str, Any], dataset_id: str = "agentcosm_market"
):
    """Update trend tracking table"""
    project_id = settings.GOOGLE_CLOUD_PROJECT_ID
    try:
        trend_records = []
        current_date = datetime.now().date()

        for keyword, data in insights.items():
            trend_records.append(
                {
                    "keyword": keyword,
                    "date": current_date,
                    "mention_count": data["mention_count"],
                    "avg_sentiment": data["avg_sentiment"],
                    "source_diversity": data["source_diversity"],
                }
            )

        if trend_records:
            df = pd.DataFrame(trend_records)
            table_id = f"{project_id}.{dataset_id}.keyword_trends"

            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
            )

            job = bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()
            print(f"✅ Updated trend tracking for {len(trend_records)} keywords")

    except Exception as e:
        print(f"❌ Trend tracking update error: {e}")


def create_bigquery_agent() -> LlmAgent:
    """Create BigQuery agent"""

    return LlmAgent(
        name="bigquery_market_agent",
        model=MODEL_CONFIG["primary_model"],
        instruction=BIGQUERY_PROMPT,
        description=(
            "BigQuery market intelligence agent that combines Tavily web research "
            "with BigQuery analytics for enhanced market insights and trend analysis."
        ),
        tools=[
            FunctionTool(func=collect_and_analyze_market_data),
            FunctionTool(func=get_historical_trend_analysis),
            FunctionTool(func=generate_market_intelligence_summary),
            FunctionTool(func=setup_bigquery_tables),
        ],
        output_key="bigquery_market_intelligence",
    )
