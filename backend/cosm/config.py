MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash-preview-05-20",
    "openai_model": "openai/gpt-4o-mini",
    "market_explorer": "gemini-2.0-flash",  # Market intelligence + trends + gaps
    "market_explorer_openai": "gpt-4.1-mini",  # Market intelligence + trends + gaps
    "brand_creator": "gpt-4.1-mini",  # Brand + copy creation
    "landing_builder": "gemini-2.5-pro-preview-05-06",  # Landing pages + dashboards
    "market_research": "gemini-2.0-flash",
    "discovery_agent": "gemini-2.0-flash",
    "discovery_agent_openai": "gpt-4.1-mini",
    "trend_tracker": "gpt-4.1-mini",
    "market_analyzer": "gemini-2.0-flash",
    "bigquery_agent": "gpt-4.1-mini",
    "data_intelligence": "gpt-4.1-mini",
    "code_executor": "gpt-4.1-mini",
    "market_analyzer_openai": "gpt-4.1-mini",
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
