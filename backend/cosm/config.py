# Model Configuration
MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash-preview-05-20",  # Keep for Opportunity Scorer
    "groq_model": "groq/llama3-70b-8192",
    "openai_model": "openai/gpt-4o-mini",
    # Agent routing
    "opportunity_scorer": "gemini-2.5-flash-preview-05-20",
    "market_explorer": "groq/llama3-70b-8192",
    "gap_mapper": "groq/llama3-70b-8192",
    "trend_analyzer": "groq/llama3-70b-8192",
    "trend_tracker": "groq/llama3-70b-8192",
    "builder_agents": "groq/llama3-70b-8192",
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
