# Model Configuration
MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash-preview-05-20",  # Keep for Opportunity Scorer
    "groq_model": "llama-3.3-70b-versatile",
    "openai_model": "openai/gpt-4o-mini",
    # Agent routing
    "opportunity_scorer": "gemini-2.5-flash-preview-05-20",
    "market_explorer": "llama-3.3-70b-versatile",
    "gap_mapper": "llama-3.3-70b-versatile",
    "trend_analyzer": "llama-3.3-70b-versatile",
    "trend_tracker": "llama-3.3-70b-versatile",
    "builder_agents": "llama-3.3-70b-versatile",
    "market_research": "openai/gpt-4o-mini",
    "bigquery_agent": "openai/gpt-4o-mini",
    "code_executor": "openai/gpt-4o-mini",
    "backup_model": "gemini-1.5-pro",
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
