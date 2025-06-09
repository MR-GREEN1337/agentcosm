MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash-preview-05-20",
    "openai_model": "openai/gpt-4o-mini",
    "market_explorer": "openai/gpt-4o-mini",  # Market intelligence + trends + gaps
    "brand_creator": "openai/gpt-4o-mini",  # Brand + copy creation
    "landing_builder": "gemini-2.5-pro-preview-05-06",  # Landing pages + dashboards
    "market_research": "openai/gpt-4o-mini",
    "discovery_agent": "openai/gpt-4o-mini",
    "trend_tracker": "openai/gpt-4o-mini",
    "market_analyzer": "openai/gpt-4o-mini",
    "bigquery_agent": "openai/gpt-4o-mini",
    "data_intelligence": "openai/gpt-4o-mini",
    "code_executor": "openai/gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 4096,
    "generation_config": {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 4096,
        "response_mime_type": "text/plain",
    },
}
