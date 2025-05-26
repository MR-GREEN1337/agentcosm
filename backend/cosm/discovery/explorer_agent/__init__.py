"""
Market Explorer Agent - Discovers real market signals from social platforms and forums
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, web_fetch
from typing import Dict, List, Any
import json
import re
from datetime import datetime, timedelta

from ..tools.web_scraper import scrape_reddit_discussions, scrape_twitter_complaints
from ..tools.social_monitor import monitor_social_sentiment, extract_pain_points
from ..tools.data_processor import process_social_signals, identify_patterns
from ..prompts.explorer_prompts import EXPLORER_AGENT_PROMPT, SIGNAL_ANALYSIS_PROMPT

def discover_market_signals(query_context: str) -> Dict[str, Any]:
    """
    Discovers real market signals from multiple sources
    
    Args:
        query_context: The market domain or problem space to explore
        
    Returns:
        Dictionary containing discovered signals and pain points
    """
    signals = {
        "timestamp": datetime.now().isoformat(),
        "context": query_context,
        "reddit_signals": [],
        "twitter_signals": [],
        "forum_signals": [],
        "pain_points": [],
        "emerging_patterns": []
    }
    
    try:
        # Search Reddit for relevant discussions
        reddit_queries = [
            f"{query_context} problems site:reddit.com",
            f"frustrated with {query_context} site:reddit.com", 
            f"{query_context} alternatives needed site:reddit.com",
            f"why doesn't {query_context} exist site:reddit.com"
        ]
        
        for query in reddit_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:3]:  # Top 3 results per query
                    try:
                        content = web_fetch(result.url)
                        reddit_signals = scrape_reddit_discussions(content, query_context)
                        signals["reddit_signals"].extend(reddit_signals)
                    except Exception as e:
                        print(f"Error scraping Reddit content: {e}")
                        
        # Search for Twitter/X complaints and discussions
        twitter_queries = [
            f"{query_context} \"why is there no\" site:twitter.com",
            f"{query_context} \"frustrated\" OR \"annoying\" site:twitter.com",
            f"{query_context} \"someone should build\" site:twitter.com"
        ]
        
        for query in twitter_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:2]:  # Top 2 per query
                    try:
                        content = web_fetch(result.url)
                        twitter_signals = scrape_twitter_complaints(content, query_context)
                        signals["twitter_signals"].extend(twitter_signals)
                    except Exception as e:
                        print(f"Error scraping Twitter content: {e}")
        
        # Search forums and discussion boards
        forum_queries = [
            f"{query_context} problems site:stackoverflow.com",
            f"{query_context} issues site:news.ycombinator.com",
            f"{query_context} discussion site:quora.com",
            f"{query_context} \"pain point\" OR \"problem\" forum"
        ]
        
        for query in forum_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:2]:
                    try:
                        content = web_fetch(result.url)
                        forum_signals = extract_pain_points(content, query_context)
                        signals["forum_signals"].extend(forum_signals)
                    except Exception as e:
                        print(f"Error scraping forum content: {e}")
        
        # Process and identify patterns in collected signals
        all_signals = (signals["reddit_signals"] + 
                      signals["twitter_signals"] + 
                      signals["forum_signals"])
        
        if all_signals:
            signals["pain_points"] = process_social_signals(all_signals)
            signals["emerging_patterns"] = identify_patterns(all_signals, query_context)
        
        return signals
        
    except Exception as e:
        print(f"Error in discover_market_signals: {e}")
        return signals

def analyze_competitive_gaps(market_domain: str) -> Dict[str, Any]:
    """
    Analyzes competitive landscape to identify gaps
    """
    gaps = {
        "market_domain": market_domain,
        "existing_solutions": [],
        "gap_analysis": [],
        "opportunities": []
    }
    
    try:
        # Search for existing solutions
        solution_queries = [
            f"{market_domain} tools",
            f"{market_domain} software",
            f"{market_domain} platform",
            f"{market_domain} service",
            f"best {market_domain} solutions"
        ]
        
        for query in solution_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:5]:
                    gaps["existing_solutions"].append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet
                    })
        
        # Search for gap discussions
        gap_queries = [
            f"{market_domain} \"doesn't exist\"",
            f"{market_domain} \"missing\"", 
            f"{market_domain} \"wish there was\"",
            f"{market_domain} \"no good solution\"",
            f"why isn't there {market_domain}"
        ]
        
        for query in gap_queries:
            results = google_search(query)
            if results and hasattr(results, 'results'):
                for result in results.results[:3]:
                    gaps["gap_analysis"].append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "query": query
                    })
        
        return gaps
        
    except Exception as e:
        print(f"Error in analyze_competitive_gaps: {e}")
        return gaps

# Create the market explorer agent
market_explorer_agent = LlmAgent(
    name="market_explorer_agent",
    model="gemini-2.0-flash",
    instruction=EXPLORER_AGENT_PROMPT,
    description=(
        "Explores social media, forums, and online discussions to discover "
        "genuine market signals, pain points, and unmet needs in liminal spaces."
    ),
    tools=[
        FunctionTool(func=discover_market_signals),
        FunctionTool(func=analyze_competitive_gaps),
        google_search,
        web_fetch
    ],
    output_key="market_signals"
)