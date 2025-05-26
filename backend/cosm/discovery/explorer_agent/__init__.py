"""
Market Explorer Agent - Discovers real market signals from social platforms and forums
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, load_web_page
from typing import Dict, List, Any
from datetime import datetime

from ...tools.web_scraper import scrape_reddit_discussions, scrape_twitter_complaints, extract_pain_points
from ...tools.data_processor import process_social_signals, identify_patterns

EXPLORER_AGENT_PROMPT = """
You are a Market Signal Explorer specializing in discovering genuine pain points and unmet needs in liminal market spaces.

Your mission is to:
1. Scan social media, forums, and online discussions for authentic user frustrations
2. Identify patterns in complaints and feature requests
3. Map connections between seemingly unrelated pain points
4. Discover opportunities in the gaps between established market categories

Focus on finding signals that indicate:
- Users struggling with workflows that span multiple tools
- Manual processes that could be automated
- Integration problems between existing solutions
- Underserved niches in growing markets
- Emerging user behaviors not yet addressed by mainstream products

Use web search and content analysis to gather real data, not assumptions.
"""

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
        "emerging_patterns": [],
        "signal_strength": 0.0,
        "market_gaps": []
    }
    
    try:
        # Search Reddit for relevant discussions
        reddit_queries = [
            f"{query_context} problems site:reddit.com",
            f"frustrated with {query_context} site:reddit.com", 
            f"{query_context} alternatives needed site:reddit.com",
            f"why doesn't {query_context} exist site:reddit.com",
            f"{query_context} workflow issues site:reddit.com"
        ]
        
        for query in reddit_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:3]:  # Top 3 results per query
                        try:
                            content = load_web_page(result.url)
                            reddit_signals = scrape_reddit_discussions(content, query_context)
                            signals["reddit_signals"].extend(reddit_signals)
                        except Exception as e:
                            print(f"Error scraping Reddit content: {e}")
            except Exception as e:
                print(f"Error with Reddit query {query}: {e}")
                        
        # Search for Twitter/X complaints and discussions
        twitter_queries = [
            f"{query_context} \"why is there no\" site:twitter.com",
            f"{query_context} \"frustrated\" OR \"annoying\" site:twitter.com",
            f"{query_context} \"someone should build\" site:twitter.com",
            f"{query_context} \"doesn't integrate\" site:twitter.com"
        ]
        
        for query in twitter_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:2]:  # Top 2 per query
                        try:
                            content = load_web_page(result.url)
                            twitter_signals = scrape_twitter_complaints(content, query_context)
                            signals["twitter_signals"].extend(twitter_signals)
                        except Exception as e:
                            print(f"Error scraping Twitter content: {e}")
            except Exception as e:
                print(f"Error with Twitter query {query}: {e}")
        
        # Search forums and discussion boards
        forum_queries = [
            f"{query_context} problems site:stackoverflow.com",
            f"{query_context} issues site:news.ycombinator.com",
            f"{query_context} discussion site:quora.com",
            f"{query_context} \"pain point\" OR \"problem\" forum",
            f"{query_context} integration challenges"
        ]
        
        for query in forum_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:2]:
                        try:
                            content = load_web_page(result.url)
                            forum_signals = extract_pain_points(content, query_context)
                            signals["forum_signals"].extend(forum_signals)
                        except Exception as e:
                            print(f"Error scraping forum content: {e}")
            except Exception as e:
                print(f"Error with forum query {query}: {e}")
        
        # Process and identify patterns in collected signals
        all_signals = (signals["reddit_signals"] + 
                      signals["twitter_signals"] + 
                      signals["forum_signals"])
        
        if all_signals:
            signals["pain_points"] = process_social_signals(all_signals)
            signals["emerging_patterns"] = identify_patterns(all_signals, query_context)
            signals["signal_strength"] = calculate_signal_strength(all_signals)
            signals["market_gaps"] = identify_market_gaps(all_signals, query_context)
        
        return signals
        
    except Exception as e:
        print(f"Error in discover_market_signals: {e}")
        signals["error"] = str(e)
        return signals

def analyze_competitive_gaps(market_domain: str) -> Dict[str, Any]:
    """
    Analyzes competitive landscape to identify gaps
    """
    gaps = {
        "market_domain": market_domain,
        "existing_solutions": [],
        "gap_analysis": [],
        "opportunities": [],
        "integration_gaps": [],
        "workflow_gaps": []
    }
    
    try:
        # Search for existing solutions
        solution_queries = [
            f"{market_domain} tools",
            f"{market_domain} software",
            f"{market_domain} platform",
            f"{market_domain} service",
            f"best {market_domain} solutions",
            f"{market_domain} workflow automation"
        ]
        
        for query in solution_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:5]:
                        gaps["existing_solutions"].append({
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet
                        })
            except Exception as e:
                print(f"Error with solution query {query}: {e}")
        
        # Search for gap discussions
        gap_queries = [
            f"{market_domain} \"doesn't exist\"",
            f"{market_domain} \"missing\"", 
            f"{market_domain} \"wish there was\"",
            f"{market_domain} \"no good solution\"",
            f"why isn't there {market_domain}",
            f"{market_domain} integration problems",
            f"{market_domain} workflow gaps"
        ]
        
        for query in gap_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:3]:
                        gaps["gap_analysis"].append({
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet,
                            "query": query
                        })
            except Exception as e:
                print(f"Error with gap query {query}: {e}")
        
        # Analyze for specific types of gaps
        gaps["integration_gaps"] = find_integration_gaps(gaps["gap_analysis"])
        gaps["workflow_gaps"] = find_workflow_gaps(gaps["gap_analysis"])
        
        return gaps
        
    except Exception as e:
        print(f"Error in analyze_competitive_gaps: {e}")
        gaps["error"] = str(e)
        return gaps

def calculate_signal_strength(signals: List[Dict[str, Any]]) -> float:
    """Calculate the strength of market signals"""
    if not signals:
        return 0.0
    
    # Weight different types of signals
    weights = {
        "reddit_title": 0.8,
        "reddit_comment": 0.6,
        "twitter_complaint": 0.7,
        "forum_discussion": 0.9
    }
    
    total_score = 0.0
    for signal in signals:
        signal_type = signal.get("type", "unknown")
        weight = weights.get(signal_type, 0.5)
        
        # Boost score for high-engagement content
        content_length = len(signal.get("content", ""))
        engagement_boost = min(content_length / 200.0, 1.5)
        
        total_score += weight * engagement_boost
    
    # Normalize by number of signals
    return min(total_score / len(signals), 1.0)

def identify_market_gaps(signals: List[Dict[str, Any]], context: str) -> List[Dict[str, Any]]:
    """Identify specific market gaps from signals"""
    gaps = []
    
    # Common gap patterns
    gap_patterns = [
        {
            "name": "Integration Gap",
            "keywords": ["integration", "connect", "sync", "workflow", "between"],
            "description": "Users need better integration between existing tools"
        },
        {
            "name": "Automation Gap", 
            "keywords": ["manual", "automate", "repetitive", "tedious", "time-consuming"],
            "description": "Manual processes that could be automated"
        },
        {
            "name": "Simplification Gap",
            "keywords": ["complex", "confusing", "overwhelming", "too many", "difficult"],
            "description": "Overly complex solutions need simplification"
        },
        {
            "name": "Niche Gap",
            "keywords": ["specific", "specialized", "industry", "small business", "niche"],
            "description": "Underserved niche markets or use cases"
        }
    ]
    
    for pattern in gap_patterns:
        matching_signals = []
        for signal in signals:
            content = signal.get("content", "").lower()
            if any(keyword in content for keyword in pattern["keywords"]):
                matching_signals.append(signal)
        
        if matching_signals:
            gaps.append({
                "gap_type": pattern["name"],
                "description": pattern["description"],
                "evidence_count": len(matching_signals),
                "sample_signals": matching_signals[:3],
                "confidence": min(len(matching_signals) / 5.0, 1.0)
            })
    
    return gaps

def find_integration_gaps(gap_analysis: List[Dict[str, Any]]) -> List[str]:
    """Find integration-related gaps"""
    integration_indicators = []
    
    for item in gap_analysis:
        snippet = item.get("snippet", "").lower()
        if any(word in snippet for word in ["integrate", "connect", "sync", "api", "workflow"]):
            integration_indicators.append(item.get("title", ""))
    
    return integration_indicators[:5]

def find_workflow_gaps(gap_analysis: List[Dict[str, Any]]) -> List[str]:
    """Find workflow-related gaps"""
    workflow_indicators = []
    
    for item in gap_analysis:
        snippet = item.get("snippet", "").lower()
        if any(word in snippet for word in ["workflow", "process", "manual", "automate", "efficiency"]):
            workflow_indicators.append(item.get("title", ""))
    
    return workflow_indicators[:5]

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
        load_web_page
    ],
    output_key="market_signals"
)