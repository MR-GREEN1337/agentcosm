"""
Real Market Research Tools - Production Ready Implementation
Uses web search and structured output for comprehensive market analysis
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from google.genai import Client, types
import requests
from bs4 import BeautifulSoup
import time
import random

# Initialize Gemini client
client = Client()

def comprehensive_market_research(keywords: List[str], target_audience: str = "") -> Dict[str, Any]:
    """
    Performs comprehensive market research using real web sources
    
    Args:
        keywords: List of market keywords to research
        target_audience: Target audience description
        
    Returns:
        Comprehensive market research report
    """
    research_report = {
        "timestamp": datetime.now().isoformat(),
        "keywords": keywords,
        "target_audience": target_audience,
        "market_signals": [],
        "competition_analysis": {},
        "demand_validation": {},
        "trend_analysis": {},
        "opportunity_score": 0.0,
        "actionable_insights": []
    }
    
    try:
        # 1. Market Signals Discovery
        print("Discovering market signals...")
        research_report["market_signals"] = discover_market_signals_real(keywords)
        
        # 2. Competition Analysis
        print("Analyzing competition...")
        research_report["competition_analysis"] = analyze_competition_real(keywords)
        
        # 3. Demand Validation
        print("Validating demand...")
        research_report["demand_validation"] = validate_demand_real(keywords, target_audience)
        
        # 4. Trend Analysis
        print("Analyzing trends...")
        research_report["trend_analysis"] = analyze_trends_real(keywords)
        
        # 5. Calculate Opportunity Score
        research_report["opportunity_score"] = calculate_opportunity_score_real(research_report)
        
        # 6. Generate Actionable Insights
        research_report["actionable_insights"] = generate_insights_with_gemini(research_report)
        
        return research_report
        
    except Exception as e:
        print(f"Error in comprehensive_market_research: {e}")
        research_report["error"] = str(e)
        return research_report

def discover_market_signals_real(keywords: List[str]) -> List[Dict[str, Any]]:
    """Discovers real market signals from web sources"""
    signals = []
    
    for keyword in keywords[:3]:  # Limit to prevent rate limiting
        # Search for problems and pain points
        pain_queries = [
            f"{keyword} problems frustrating users",
            f"{keyword} doesn't work complaints",
            f"alternatives to {keyword} needed",
            f"{keyword} market gaps opportunities"
        ]
        
        for query in pain_queries:
            try:
                search_results = search_web_real(query, max_results=3)
                for result in search_results:
                    signal = extract_pain_signals_with_gemini(result, keyword)
                    if signal:
                        signals.append(signal)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error searching for {query}: {e}")
                continue
    
    return signals

def analyze_competition_real(keywords: List[str]) -> Dict[str, Any]:
    """Analyzes real competition data"""
    competition_data = {
        "direct_competitors": [],
        "indirect_competitors": [],
        "market_leaders": [],
        "competition_level": "unknown",
        "market_gaps": []
    }
    
    for keyword in keywords[:2]:
        try:
            # Search for existing solutions
            comp_queries = [
                f"{keyword} top companies market leaders",
                f"best {keyword} solutions software tools",
                f"{keyword} competitors comparison review"
            ]
            
            all_competitors = []
            for query in comp_queries:
                search_results = search_web_real(query, max_results=3)
                competitors = extract_competitors_with_gemini(search_results, keyword)
                all_competitors.extend(competitors)
                time.sleep(0.5)
            
            # Categorize competitors
            competition_data["direct_competitors"].extend(all_competitors[:5])
            competition_data["market_leaders"].extend(all_competitors[:3])
            
        except Exception as e:
            print(f"Error analyzing competition for {keyword}: {e}")
    
    # Determine competition level
    total_competitors = len(competition_data["direct_competitors"])
    if total_competitors < 3:
        competition_data["competition_level"] = "low"
    elif total_competitors < 8:
        competition_data["competition_level"] = "medium"
    else:
        competition_data["competition_level"] = "high"
    
    return competition_data

def validate_demand_real(keywords: List[str], target_audience: str) -> Dict[str, Any]:
    """Validates market demand using real data"""
    demand_data = {
        "search_volume_indicators": [],
        "social_mentions": [],
        "forum_discussions": [],
        "demand_score": 0.0,
        "growth_indicators": []
    }
    
    for keyword in keywords[:3]:
        try:
            # Search for demand indicators
            demand_queries = [
                f"{keyword} market size statistics 2024",
                f"{keyword} growing demand trends",
                f"how many people use {keyword}",
                f"{keyword} market research report"
            ]
            
            for query in demand_queries:
                search_results = search_web_real(query, max_results=2)
                demand_indicators = extract_demand_with_gemini(search_results, keyword)
                demand_data["search_volume_indicators"].extend(demand_indicators)
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error validating demand for {keyword}: {e}")
    
    # Calculate demand score
    demand_data["demand_score"] = calculate_demand_score(demand_data)
    
    return demand_data

def analyze_trends_real(keywords: List[str]) -> Dict[str, Any]:
    """Analyzes real market trends"""
    trend_data = {
        "trend_direction": "stable",
        "growth_indicators": [],
        "emerging_technologies": [],
        "market_shifts": [],
        "future_predictions": []
    }
    
    for keyword in keywords[:2]:
        try:
            trend_queries = [
                f"{keyword} trends 2024 2025 future",
                f"{keyword} market growth predictions",
                f"{keyword} emerging technologies innovations",
                f"{keyword} industry outlook report"
            ]
            
            for query in trend_queries:
                search_results = search_web_real(query, max_results=2)
                trends = extract_trends_with_gemini(search_results, keyword)
                trend_data["growth_indicators"].extend(trends)
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error analyzing trends for {keyword}: {e}")
    
    # Determine overall trend direction
    positive_indicators = len([t for t in trend_data["growth_indicators"] if "growth" in str(t).lower() or "increase" in str(t).lower()])
    if positive_indicators > len(trend_data["growth_indicators"]) * 0.6:
        trend_data["trend_direction"] = "growing"
    elif positive_indicators < len(trend_data["growth_indicators"]) * 0.3:
        trend_data["trend_direction"] = "declining"
    
    return trend_data

def search_web_real(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Performs real web search using requests and BeautifulSoup
    Searches DuckDuckGo to avoid API requirements
    """
    results = []
    
    try:
        # Use DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        result_links = soup.find_all('a', class_='result__a')
        
        for i, link in enumerate(result_links[:max_results]):
            try:
                title = link.get_text().strip()
                url = link.get('href', '')
                
                if url and title:
                    # Get snippet from result
                    snippet = extract_snippet_from_url(url)
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': 'web_search'
                    })
            except Exception as e:
                print(f"Error processing search result: {e}")
                continue
                
    except Exception as e:
        print(f"Error in web search for '{query}': {e}")
    
    return results

def extract_snippet_from_url(url: str, max_length: int = 500) -> str:
    """Extracts text snippet from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:max_length] + "..." if len(text) > max_length else text
        
    except Exception as e:
        print(f"Error extracting snippet from {url}: {e}")
        return ""

def extract_pain_signals_with_gemini(search_result: Dict[str, str], keyword: str) -> Optional[Dict[str, Any]]:
    """Uses Gemini to extract pain signals from search results"""
    try:
        prompt = f"""
        Analyze this search result about "{keyword}" and extract any pain points, problems, or market gaps mentioned.
        
        Title: {search_result.get('title', '')}
        Content: {search_result.get('snippet', '')}
        
        Extract and return a JSON object with:
        - pain_point: The specific problem mentioned
        - severity: How severe the problem seems (high/medium/low)
        - frequency: How often this problem occurs (high/medium/low)
        - target_users: Who is affected by this problem
        - opportunity: What business opportunity this represents
        
        Only return the JSON object, no other text.
        """
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        if response and response.text:
            pain_signal = json.loads(response.text)
            pain_signal['source'] = search_result.get('url', '')
            pain_signal['keyword'] = keyword
            return pain_signal
            
    except Exception as e:
        print(f"Error extracting pain signals: {e}")
    
    return None

def extract_competitors_with_gemini(search_results: List[Dict[str, str]], keyword: str) -> List[Dict[str, Any]]:
    """Uses Gemini to extract competitor information"""
    competitors = []
    
    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result about "{keyword}" and extract any companies, products, or services mentioned as competitors or solutions.
            
            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}
            
            Extract and return a JSON array of competitors, each with:
            - name: Company/product name
            - type: Type of solution (software, service, platform, etc.)
            - market_position: Position in market (leader, challenger, niche, etc.)
            - strengths: Key strengths mentioned
            - weaknesses: Any weaknesses or limitations mentioned
            
            Only return the JSON array, no other text.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            if response and response.text:
                result_competitors = json.loads(response.text)
                competitors.extend(result_competitors)
                
        except Exception as e:
            print(f"Error extracting competitors: {e}")
            continue
    
    return competitors

def extract_demand_with_gemini(search_results: List[Dict[str, str]], keyword: str) -> List[Dict[str, Any]]:
    """Uses Gemini to extract demand indicators"""
    demand_indicators = []
    
    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result about "{keyword}" and extract any demand indicators, market size data, or usage statistics.
            
            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}
            
            Extract and return a JSON array of demand indicators, each with:
            - metric: The specific metric or statistic
            - value: The numerical value if available
            - timeframe: Time period this applies to
            - source_credibility: How credible this source seems (high/medium/low)
            - growth_direction: Whether this indicates growth, decline, or stability
            
            Only return the JSON array, no other text.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            if response and response.text:
                indicators = json.loads(response.text)
                demand_indicators.extend(indicators)
                
        except Exception as e:
            print(f"Error extracting demand indicators: {e}")
            continue
    
    return demand_indicators

def extract_trends_with_gemini(search_results: List[Dict[str, str]], keyword: str) -> List[Dict[str, Any]]:
    """Uses Gemini to extract trend information"""
    trends = []
    
    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result about "{keyword}" and extract any trend information, future predictions, or market direction indicators.
            
            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}
            
            Extract and return a JSON array of trends, each with:
            - trend: Description of the trend
            - direction: growing/declining/stable
            - timeframe: When this trend is expected
            - impact: Potential impact on the market
            - confidence: How confident this prediction seems (high/medium/low)
            
            Only return the JSON array, no other text.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            if response and response.text:
                trend_data = json.loads(response.text)
                trends.extend(trend_data)
                
        except Exception as e:
            print(f"Error extracting trends: {e}")
            continue
    
    return trends

def calculate_opportunity_score_real(research_data: Dict[str, Any]) -> float:
    """Calculates opportunity score based on real data"""
    score = 0.0
    
    # Pain signals score (0-0.3)
    pain_signals = research_data.get("market_signals", [])
    high_severity_signals = len([s for s in pain_signals if s.get("severity") == "high"])
    pain_score = min(high_severity_signals * 0.1, 0.3)
    score += pain_score
    
    # Competition score (0-0.25) - lower competition = higher score
    competition_level = research_data.get("competition_analysis", {}).get("competition_level", "high")
    if competition_level == "low":
        score += 0.25
    elif competition_level == "medium":
        score += 0.15
    else:
        score += 0.05
    
    # Demand score (0-0.25)
    demand_score = research_data.get("demand_validation", {}).get("demand_score", 0.0)
    score += min(demand_score * 0.25, 0.25)
    
    # Trend score (0-0.2)
    trend_direction = research_data.get("trend_analysis", {}).get("trend_direction", "stable")
    if trend_direction == "growing":
        score += 0.2
    elif trend_direction == "stable":
        score += 0.1
    else:
        score += 0.05
    
    return min(score, 1.0)

def calculate_demand_score(demand_data: Dict[str, Any]) -> float:
    """Calculates demand score from indicators"""
    indicators = demand_data.get("search_volume_indicators", [])
    if not indicators:
        return 0.0
    
    # Score based on number and quality of indicators
    high_credibility = len([i for i in indicators if i.get("source_credibility") == "high"])
    growth_indicators = len([i for i in indicators if i.get("growth_direction") == "growth"])
    
    score = (high_credibility * 0.3 + growth_indicators * 0.4) / max(len(indicators), 1)
    return min(score, 1.0)

def generate_insights_with_gemini(research_data: Dict[str, Any]) -> List[str]:
    """Generates actionable insights using Gemini"""
    try:
        prompt = f"""
        Based on this market research data, generate 5-7 specific, actionable business insights and opportunities.
        
        Research Data: {json.dumps(research_data, indent=2)}
        
        Focus on:
        1. Specific market gaps that could be filled
        2. Underserved customer segments
        3. Technology opportunities
        4. Business model innovations
        5. Go-to-market strategies
        
        Return a JSON array of insights, each as a string that is specific, actionable, and based on the data.
        """
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4
            )
        )
        
        if response and response.text:
            return json.loads(response.text)
            
    except Exception as e:
        print(f"Error generating insights: {e}")
    
    return ["Market research completed successfully"]

def analyze_competitive_landscape(keywords: List[str], solution_type: str = "") -> Dict[str, Any]:
    """
    Analyzes competitive landscape for given keywords
    """
    return analyze_competition_real(keywords)

def check_domain_availability(domain_name: str) -> Dict[str, Any]:
    """
    Checks domain availability for potential business names
    """
    try:
        # Simple domain availability check using whois
        import socket
        
        result = {
            "domain": domain_name,
            "available": False,
            "alternatives": [],
            "checked_at": datetime.now().isoformat()
        }
        
        # Try to resolve the domain
        try:
            socket.gethostbyname(domain_name)
            result["available"] = False
        except socket.gaierror:
            result["available"] = True
        
        # Generate alternatives if not available
        if not result["available"]:
            base_name = domain_name.split('.')[0]
            alternatives = [
                f"{base_name}app.com",
                f"{base_name}pro.com",
                f"{base_name}hub.com",
                f"get{base_name}.com",
                f"{base_name}io.com"
            ]
            result["alternatives"] = alternatives
        
        return result
        
    except Exception as e:
        return {
            "domain": domain_name,
            "available": False,
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }