MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash-preview-05-20",
    "openai_model": "openai/gpt-4o-mini",
    "market_explorer": "openai/gpt-4o-mini",  # Market intelligence + trends + gaps
    "market_analyzer": "gemini-2.5-flash-preview-05-20",  # Analysis + scoring
    "data_intelligence": "gemini-2.5-flash-preview-05-20",  # BigQuery + code execution
    "brand_creator": "openai/gpt-4o-mini",  # Brand + copy creation
    "landing_builder": "openai/gpt-4o-mini",  # Landing pages + dashboards
    "market_research": "openai/gpt-4o-mini",
    "trend_tracker": "openai/gpt-4o-mini",
    "bigquery_agent": "gemini-2.5-flash-preview-05-20",
    "code_executor": "gemini-2.5-flash-preview-05-20",
    "builder_agents": "openai/gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 4096,
    "generation_config": {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 4096,
        "response_mime_type": "text/plain",
    },
    "optimization_enabled": True,
    "model_reduction": "4_to_2_models",
    "estimated_cost_savings": "35%",
    "estimated_latency_improvement": "50%",
}
