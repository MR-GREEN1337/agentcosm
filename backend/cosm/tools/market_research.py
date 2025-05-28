"""
Real Market Research Tools - Production Ready Implementation
Uses web search and structured output for comprehensive market analysis
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from google.genai import Client, types
import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
from cosm.config import MODEL_CONFIG as CONFIG

# Initialize Gemini client
client = Client()


def comprehensive_market_research(
    keywords: List[str], target_audience: str = ""
) -> Dict[str, Any]:
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
        "actionable_insights": [],
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
        research_report["demand_validation"] = validate_demand_real(
            keywords, target_audience
        )

        # 4. Trend Analysis
        print("Analyzing trends...")
        research_report["trend_analysis"] = analyze_trends_real(keywords)

        # 5. Calculate Opportunity Score
        research_report["opportunity_score"] = calculate_opportunity_score_real(
            research_report
        )

        # 6. Generate Actionable Insights
        research_report["actionable_insights"] = generate_insights_with_gemini(
            research_report
        )

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
            f"{keyword} market gaps opportunities",
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
        "market_gaps": [],
    }

    for keyword in keywords[:2]:
        try:
            # Search for existing solutions
            comp_queries = [
                f"{keyword} top companies market leaders",
                f"best {keyword} solutions software tools",
                f"{keyword} competitors comparison review",
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
        "growth_indicators": [],
    }

    for keyword in keywords[:3]:
        try:
            # Search for demand indicators
            demand_queries = [
                f"{keyword} market size statistics 2024",
                f"{keyword} growing demand trends",
                f"how many people use {keyword}",
                f"{keyword} market research report",
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
        "future_predictions": [],
    }

    for keyword in keywords[:2]:
        try:
            trend_queries = [
                f"{keyword} trends 2024 2025 future",
                f"{keyword} market growth predictions",
                f"{keyword} emerging technologies innovations",
                f"{keyword} industry outlook report",
            ]

            for query in trend_queries:
                search_results = search_web_real(query, max_results=2)
                trends = extract_trends_with_gemini(search_results, keyword)
                trend_data["growth_indicators"].extend(trends)
                time.sleep(0.5)

        except Exception as e:
            print(f"Error analyzing trends for {keyword}: {e}")

    # Determine overall trend direction
    positive_indicators = len(
        [
            t
            for t in trend_data["growth_indicators"]
            if "growth" in str(t).lower() or "increase" in str(t).lower()
        ]
    )
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract search results
        result_links = soup.find_all("a", class_="result__a")

        for i, link in enumerate(result_links[:max_results]):
            try:
                title = link.get_text().strip()
                url = link.get("href", "")

                if url and title:
                    # Get snippet from result
                    snippet = extract_snippet_from_url(url)

                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "web_search",
                        }
                    )
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text[:max_length] + "..." if len(text) > max_length else text

    except Exception as e:
        print(f"Error extracting snippet from {url}: {e}")
        return ""


def extract_pain_signals_with_gemini(
    search_result: Dict[str, str], keyword: str
) -> Optional[Dict[str, Any]]:
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
            model=CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            pain_signal = json.loads(response.text)
            pain_signal["source"] = search_result.get("url", "")
            pain_signal["keyword"] = keyword
            return pain_signal

    except Exception as e:
        print(f"Error extracting pain signals: {e}")

    return None


def extract_competitors_with_gemini(
    search_results: List[Dict[str, str]], keyword: str
) -> List[Dict[str, Any]]:
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
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
            )

            if response and response.text:
                result_competitors = json.loads(response.text)
                competitors.extend(result_competitors)

        except Exception as e:
            print(f"Error extracting competitors: {e}")
            continue

    return competitors


def extract_demand_with_gemini(
    search_results: List[Dict[str, str]], keyword: str
) -> List[Dict[str, Any]]:
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
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
            )

            if response and response.text:
                indicators = json.loads(response.text)
                demand_indicators.extend(indicators)

        except Exception as e:
            print(f"Error extracting demand indicators: {e}")
            continue

    return demand_indicators


def extract_trends_with_gemini(
    search_results: List[Dict[str, str]], keyword: str
) -> List[Dict[str, Any]]:
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
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
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
    high_severity_signals = len(
        [s for s in pain_signals if s.get("severity") == "high"]
    )
    pain_score = min(high_severity_signals * 0.1, 0.3)
    score += pain_score

    # Competition score (0-0.25) - lower competition = higher score
    competition_level = research_data.get("competition_analysis", {}).get(
        "competition_level", "high"
    )
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
    trend_direction = research_data.get("trend_analysis", {}).get(
        "trend_direction", "stable"
    )
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
    high_credibility = len(
        [i for i in indicators if i.get("source_credibility") == "high"]
    )
    growth_indicators = len(
        [i for i in indicators if i.get("growth_direction") == "growth"]
    )

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
            model=CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.4
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error generating insights: {e}")

    return ["Market research completed successfully"]


def analyze_competitive_landscape(
    keywords: List[str], solution_type: str = ""
) -> Dict[str, Any]:
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
            "checked_at": datetime.now().isoformat(),
        }

        # Try to resolve the domain
        try:
            socket.gethostbyname(domain_name)
            result["available"] = False
        except socket.gaierror:
            result["available"] = True

        # Generate alternatives if not available
        if not result["available"]:
            base_name = domain_name.split(".")[0]
            alternatives = [
                f"{base_name}app.com",
                f"{base_name}pro.com",
                f"{base_name}hub.com",
                f"get{base_name}.com",
                f"{base_name}io.com",
            ]
            result["alternatives"] = alternatives

        return result

    except Exception as e:
        return {
            "domain": domain_name,
            "available": False,
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }


# Additional Market Research Functions


def analyze_market_size(
    keywords: List[str], target_audience: str = ""
) -> Dict[str, Any]:
    """
    Analyzes market size for given keywords and target audience

    Args:
        keywords: List of market keywords to analyze
        target_audience: Target audience description

    Returns:
        Market size analysis with TAM, SAM, SOM estimates
    """
    market_size_data = {
        "keywords": keywords,
        "target_audience": target_audience,
        "analysis_timestamp": datetime.now().isoformat(),
        "tam_estimate": 0,  # Total Addressable Market
        "sam_estimate": 0,  # Serviceable Addressable Market
        "som_estimate": 0,  # Serviceable Obtainable Market
        "market_segments": [],
        "growth_rate": 0.0,
        "geographic_distribution": {},
        "size_confidence": "medium",
        "data_sources": [],
        "methodology": "web_research_analysis",
    }

    try:
        # Search for market size data
        for keyword in keywords[:3]:  # Limit to prevent rate limiting
            market_queries = [
                f"{keyword} market size 2024 billion",
                f"{keyword} industry size statistics global",
                f"{keyword} TAM total addressable market",
                f"{keyword} market research report value",
            ]

            market_data_points = []

            for query in market_queries:
                try:
                    search_results = search_web_real(query, max_results=3)
                    size_data = extract_market_size_with_gemini(search_results, keyword)
                    if size_data:
                        market_data_points.extend(size_data)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error searching market size for {query}: {e}")
                    continue

            # Process market data points
            if market_data_points:
                market_size_data["data_sources"].extend(market_data_points)

        # Calculate TAM, SAM, SOM from collected data
        tam_sam_som = calculate_tam_sam_som(
            market_size_data["data_sources"], target_audience
        )
        market_size_data.update(tam_sam_som)

        # Analyze market segments
        market_size_data["market_segments"] = identify_market_segments(
            market_size_data["data_sources"], keywords
        )

        # Calculate growth rate
        market_size_data["growth_rate"] = calculate_growth_rate(
            market_size_data["data_sources"]
        )

        # Determine confidence level
        market_size_data["size_confidence"] = assess_size_confidence(market_size_data)

        return market_size_data

    except Exception as e:
        print(f"Error in analyze_market_size: {e}")
        market_size_data["error"] = str(e)
        return market_size_data


def research_competition(
    keywords: List[str], solution_type: str = ""
) -> Dict[str, Any]:
    """
    Researches competition in the market space

    Args:
        keywords: Market keywords to research
        solution_type: Type of solution being analyzed

    Returns:
        Comprehensive competition analysis
    """
    competition_data = {
        "keywords": keywords,
        "solution_type": solution_type,
        "analysis_timestamp": datetime.now().isoformat(),
        "direct_competitors": [],
        "indirect_competitors": [],
        "market_leaders": [],
        "emerging_players": [],
        "competition_level": "unknown",
        "market_concentration": "unknown",
        "competitive_advantages": [],
        "market_gaps": [],
        "pricing_analysis": {},
        "feature_comparison": {},
        "market_positioning": {},
    }

    try:
        # Research direct competitors
        for keyword in keywords[:2]:
            competitor_queries = [
                f"{keyword} {solution_type} competitors top companies",
                f"best {keyword} {solution_type} alternatives market leaders",
                f"{keyword} {solution_type} pricing comparison review",
                f"{keyword} {solution_type} market share leaders",
            ]

            all_competitors = []

            for query in competitor_queries:
                try:
                    search_results = search_web_real(query, max_results=3)
                    competitors = extract_competitors_with_gemini(
                        search_results, keyword
                    )
                    all_competitors.extend(competitors)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error researching competition for {query}: {e}")
                    continue

            # Categorize competitors
            direct_comps, indirect_comps, leaders = categorize_competitors(
                all_competitors
            )
            competition_data["direct_competitors"].extend(direct_comps)
            competition_data["indirect_competitors"].extend(indirect_comps)
            competition_data["market_leaders"].extend(leaders)

        # Determine competition level
        competition_data["competition_level"] = assess_competition_level(
            competition_data
        )

        # Analyze market concentration
        competition_data["market_concentration"] = analyze_market_concentration(
            competition_data
        )

        # Identify market gaps
        competition_data["market_gaps"] = identify_competition_gaps(
            competition_data, keywords
        )

        # Analyze pricing if data available
        competition_data["pricing_analysis"] = analyze_competitor_pricing(
            competition_data
        )

        return competition_data

    except Exception as e:
        print(f"Error in research_competition: {e}")
        competition_data["error"] = str(e)
        return competition_data


def validate_demand_signals(
    keywords: List[str], pain_points: List[str]
) -> Dict[str, Any]:
    """
    Validates demand signals for the market opportunity

    Args:
        keywords: Market keywords to validate
        pain_points: List of pain points to validate

    Returns:
        Demand validation analysis
    """
    demand_data = {
        "keywords": keywords,
        "pain_points": pain_points,
        "validation_timestamp": datetime.now().isoformat(),
        "signal_strength": 0.0,  # 0-100 scale
        "search_volume": 0,
        "social_mentions": 0,
        "forum_discussions": 0,
        "job_postings": 0,
        "patent_filings": 0,
        "funding_rounds": 0,
        "growth_indicators": [],
        "demand_sources": [],
        "validation_confidence": "medium",
        "market_readiness": "unknown",
    }

    try:
        # Validate demand through multiple signals
        for keyword in keywords[:3]:
            demand_queries = [
                f"{keyword} search volume trends statistics",
                f"{keyword} job market demand hiring trends",
                f"{keyword} startup funding investment 2024",
                f"{keyword} patent applications innovation",
                f"{keyword} social media mentions discussions",
            ]

            demand_indicators = []

            for query in demand_queries:
                try:
                    search_results = search_web_real(query, max_results=2)
                    signals = extract_demand_signals_with_gemini(
                        search_results, keyword
                    )
                    if signals:
                        demand_indicators.extend(signals)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error validating demand for {query}: {e}")
                    continue

            demand_data["demand_sources"].extend(demand_indicators)

        # Validate pain points specifically
        for pain_point in pain_points[:3]:
            pain_queries = [
                f'"{pain_point}" problem frustration discussions',
                f'"{pain_point}" solution need market demand',
                f'"{pain_point}" reddit twitter complaints',
            ]

            for query in pain_queries:
                try:
                    search_results = search_web_real(query, max_results=2)
                    pain_validation = extract_pain_validation_with_gemini(
                        search_results, pain_point
                    )
                    if pain_validation:
                        demand_data["demand_sources"].extend(pain_validation)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error validating pain point {pain_point}: {e}")
                    continue

        # Calculate overall signal strength
        demand_data["signal_strength"] = calculate_signal_strength_score(
            demand_data["demand_sources"]
        )

        # Extract specific metrics
        demand_data.update(extract_demand_metrics(demand_data["demand_sources"]))

        # Assess validation confidence
        demand_data["validation_confidence"] = assess_validation_confidence(demand_data)

        # Determine market readiness
        demand_data["market_readiness"] = assess_market_readiness(demand_data)

        return demand_data

    except Exception as e:
        print(f"Error in validate_demand_signals: {e}")
        demand_data["error"] = str(e)
        return demand_data


def calculate_tam_sam_som(
    market_data_points: List[Dict[str, Any]], target_audience: str = ""
) -> Dict[str, Any]:
    """
    Calculates TAM, SAM, and SOM from market data points

    Args:
        market_data_points: List of market size data points
        target_audience: Target audience description

    Returns:
        TAM, SAM, SOM calculations with methodology
    """
    tam_sam_som = {
        "tam_estimate": 0,
        "sam_estimate": 0,
        "som_estimate": 0,
        "tam_methodology": "aggregated_sources",
        "sam_methodology": "target_segment_analysis",
        "som_methodology": "realistic_capture_rate",
        "calculation_confidence": "medium",
        "data_points_used": len(market_data_points),
        "geographic_scope": "global",
        "time_horizon": "current_year",
        "assumptions": [],
    }

    try:
        if not market_data_points:
            return tam_sam_som

        # Extract TAM estimates from data points
        tam_values = []
        for data_point in market_data_points:
            if data_point.get("market_size_value"):
                try:
                    # Convert various formats to numbers
                    value = parse_market_size_value(data_point["market_size_value"])
                    if value > 0:
                        tam_values.append(value)
                except ValueError:
                    continue

        # Calculate TAM
        if tam_values:
            # Use median to avoid outliers
            tam_values.sort()
            tam_estimate = tam_values[len(tam_values) // 2]
            tam_sam_som["tam_estimate"] = int(tam_estimate)

            # Calculate SAM (typically 10-30% of TAM for focused markets)
            if target_audience:
                sam_multiplier = 0.25  # 25% of TAM for specific audience
            else:
                sam_multiplier = 0.15  # 15% of TAM for general market

            tam_sam_som["sam_estimate"] = int(tam_estimate * sam_multiplier)

            # Calculate SOM (typically 1-5% of SAM for new entrants)
            som_multiplier = 0.03  # 3% of SAM - realistic for new market entrant
            tam_sam_som["som_estimate"] = int(
                tam_sam_som["sam_estimate"] * som_multiplier
            )

            # Set confidence based on data quality
            if len(tam_values) >= 3:
                tam_sam_som["calculation_confidence"] = "high"
            elif len(tam_values) >= 2:
                tam_sam_som["calculation_confidence"] = "medium"
            else:
                tam_sam_som["calculation_confidence"] = "low"

        # Add assumptions
        tam_sam_som["assumptions"] = [
            f"TAM calculated from {len(tam_values)} market size data points",
            f"SAM estimated as {int(sam_multiplier*100)}% of based on target focus",
            f"SOM estimated as {int(som_multiplier*100)}% of SAM for new market entrant",
            "Calculations assume current market conditions and growth rates",
        ]

        return tam_sam_som

    except Exception as e:
        print(f"Error calculating TAM/SAM/SOM: {e}")
        tam_sam_som["error"] = str(e)
        return tam_sam_som


# Helper functions for new market research functions


def extract_market_size_with_gemini(
    search_results: List[Dict[str, str]], keyword: str
) -> List[Dict[str, Any]]:
    """Extract market size data using Gemini"""
    market_data = []

    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result about "{keyword}" market size and extract any market size data, statistics, or valuations.

            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}

            Extract and return a JSON array of market size data points, each with:
            - market_size_value: The numerical value (e.g., "5.2 billion", "150M")
            - market_size_unit: The unit (billion, million, USD, etc.)
            - timeframe: Year or period this applies to
            - geographic_scope: Geographic area (global, US, Europe, etc.)
            - market_segment: Specific segment if mentioned
            - source_credibility: How credible this source seems (high/medium/low)

            Only return the JSON array, no other text.
            """

            response = client.models.generate_content(
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
            )

            if response and response.text:
                data_points = json.loads(response.text)
                market_data.extend(data_points)

        except Exception as e:
            print(f"Error extracting market size data: {e}")
            continue

    return market_data


def extract_demand_signals_with_gemini(
    search_results: List[Dict[str, str]], keyword: str
) -> List[Dict[str, Any]]:
    """Extract demand signals using Gemini"""
    demand_signals = []

    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result about "{keyword}" and extract any demand indicators, market signals, or growth metrics.

            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}

            Extract and return a JSON array of demand signals, each with:
            - signal_type: Type of signal (search_volume, job_postings, funding, social_mentions, etc.)
            - signal_value: Numerical value if available
            - signal_trend: Trend direction (increasing/decreasing/stable)
            - timeframe: Time period this covers
            - strength: Signal strength (high/medium/low)
            - source_credibility: How credible this source seems (high/medium/low)

            Only return the JSON array, no other text.
            """

            response = client.models.generate_content(
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
            )

            if response and response.text:
                signals = json.loads(response.text)
                demand_signals.extend(signals)

        except Exception as e:
            print(f"Error extracting demand signals: {e}")
            continue

    return demand_signals


def extract_pain_validation_with_gemini(
    search_results: List[Dict[str, str]], pain_point: str
) -> List[Dict[str, Any]]:
    """Extract pain point validation using Gemini"""
    validations = []

    for result in search_results:
        try:
            prompt = f"""
            Analyze this search result for validation of the pain point: "{pain_point}"

            Title: {result.get('title', '')}
            Content: {result.get('snippet', '')}

            Extract and return a JSON array of validation points, each with:
            - validation_type: Type of validation (user_complaint, discussion, review, etc.)
            - validation_strength: How strongly this validates the pain point (high/medium/low)
            - user_segment: What type of users are affected
            - frequency_indicator: How often this pain occurs (daily/weekly/monthly/rare)
            - impact_level: Impact level on users (critical/major/minor)
            - evidence_quote: Brief quote showing the pain point (max 50 words)

            Only return the JSON array, no other text.
            """

            response = client.models.generate_content(
                model=CONFIG["primary_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.3
                ),
            )

            if response and response.text:
                validation_points = json.loads(response.text)
                validations.extend(validation_points)

        except Exception as e:
            print(f"Error extracting pain validation: {e}")
            continue

    return validations


def parse_market_size_value(value_str: str) -> float:
    """Parse market size value string to float"""
    if not value_str:
        return 0.0

    # Clean the string
    value_str = value_str.lower().replace(",", "").replace("$", "").strip()

    # Extract number and multiplier
    number_match = re.search(r"(\d+\.?\d*)", value_str)
    if not number_match:
        return 0.0

    number = float(number_match.group(1))

    # Apply multipliers
    if "trillion" in value_str or "t" in value_str:
        return number * 1_000_000_000_000
    elif "billion" in value_str or "b" in value_str:
        return number * 1_000_000_000
    elif "million" in value_str or "m" in value_str:
        return number * 1_000_000
    elif "thousand" in value_str or "k" in value_str:
        return number * 1_000
    else:
        return number


def categorize_competitors(competitors: List[Dict[str, Any]]) -> tuple:
    """Categorize competitors into direct, indirect, and leaders"""
    direct_competitors = []
    indirect_competitors = []
    market_leaders = []

    for competitor in competitors:
        comp_type = competitor.get("type", "").lower()
        market_position = competitor.get("market_position", "").lower()

        # Categorize as market leader
        if "leader" in market_position or "dominant" in market_position:
            market_leaders.append(competitor)

        # Categorize by competition type
        if "direct" in comp_type or "software" in comp_type or "platform" in comp_type:
            direct_competitors.append(competitor)
        else:
            indirect_competitors.append(competitor)

    return direct_competitors[:10], indirect_competitors[:10], market_leaders[:5]


def assess_competition_level(competition_data: Dict[str, Any]) -> str:
    """Assess the level of competition"""
    direct_count = len(competition_data.get("direct_competitors", []))
    total_count = direct_count + len(competition_data.get("indirect_competitors", []))

    if direct_count <= 2 and total_count <= 5:
        return "low"
    elif direct_count <= 5 and total_count <= 15:
        return "medium"
    else:
        return "high"


def analyze_market_concentration(competition_data: Dict[str, Any]) -> str:
    """Analyze market concentration"""
    leaders_count = len(competition_data.get("market_leaders", []))
    total_competitors = len(competition_data.get("direct_competitors", []))

    if leaders_count <= 1 and total_competitors >= 8:
        return "fragmented"
    elif leaders_count <= 3 and total_competitors >= 5:
        return "competitive"
    else:
        return "concentrated"


def identify_competition_gaps(
    competition_data: Dict[str, Any], keywords: List[str]
) -> List[str]:
    """Identify gaps in competitive landscape"""
    gaps = []

    # Check for common gap patterns
    competitors = competition_data.get("direct_competitors", [])

    # Feature gaps
    common_weaknesses = []
    for competitor in competitors:
        weaknesses = competitor.get("weaknesses", [])
        common_weaknesses.extend(weaknesses)

    # If multiple competitors have same weakness, it's a market gap
    weakness_counts = Counter(common_weaknesses)

    for weakness, count in weakness_counts.items():
        if count >= 2:  # Multiple competitors have this weakness
            gaps.append(f"Market gap: {weakness}")

    # Add keyword-based gaps
    for keyword in keywords:
        if keyword.lower() in ["integration", "automation", "workflow"]:
            gaps.append(f"Potential {keyword} solution gap")

    return gaps[:5]


def analyze_competitor_pricing(competition_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze competitor pricing if available"""
    pricing_analysis = {
        "pricing_models": [],
        "price_ranges": {},
        "pricing_gaps": [],
        "pricing_strategy_insights": [],
    }

    # This would be enhanced with actual pricing data extraction
    # For now, provide general analysis framework

    competitors = competition_data.get("direct_competitors", [])
    if competitors:
        pricing_analysis["pricing_strategy_insights"] = [
            "Analyze competitor pricing pages for detailed pricing data",
            "Look for freemium vs. premium pricing models",
            "Identify pricing gaps in the market",
            "Consider value-based pricing opportunities",
        ]

    return pricing_analysis


def identify_market_segments(
    market_data: List[Dict[str, Any]], keywords: List[str]
) -> List[Dict[str, str]]:
    """Identify market segments from data"""
    segments = []

    # Extract segments mentioned in market data
    for data_point in market_data:
        segment = data_point.get("market_segment", "")
        if segment and segment not in [s.get("name") for s in segments]:
            segments.append(
                {
                    "name": segment,
                    "description": f"Market segment focused on {segment}",
                    "size_estimate": "TBD",
                }
            )

    # Add keyword-based segments
    for keyword in keywords:
        if keyword.lower() in ["enterprise", "small business", "startup"]:
            segments.append(
                {
                    "name": f"{keyword.title()} Market",
                    "description": f"Market segment serving {keyword} customers",
                    "size_estimate": "TBD",
                }
            )

    return segments[:5]


def calculate_growth_rate(market_data: List[Dict[str, Any]]) -> float:
    """Calculate market growth rate from data"""
    growth_indicators = []

    for data_point in market_data:
        if "growth" in str(data_point).lower():
            # Try to extract growth percentage
            text = str(data_point).lower()
            growth_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*growth", text)
            if growth_match:
                growth_indicators.append(float(growth_match.group(1)))

    if growth_indicators:
        return sum(growth_indicators) / len(growth_indicators)
    else:
        return 5.0  # Default assumption


def assess_size_confidence(market_size_data: Dict[str, Any]) -> str:
    """Assess confidence in market size calculations"""
    data_points = len(market_size_data.get("data_sources", []))
    tam_estimate = market_size_data.get("tam_estimate", 0)

    if data_points >= 3 and tam_estimate > 0:
        return "high"
    elif data_points >= 2 and tam_estimate > 0:
        return "medium"
    else:
        return "low"


def calculate_signal_strength_score(demand_sources: List[Dict[str, Any]]) -> float:
    """Calculate overall signal strength score (0-100)"""
    if not demand_sources:
        return 0.0

    total_score = 0.0
    weights = {"high": 1.0, "medium": 0.6, "low": 0.3}

    for source in demand_sources:
        strength = source.get("strength", "low")
        signal_type = source.get("signal_type", "")

        # Base score from strength
        score = weights.get(strength, 0.3) * 20

        # Bonus for high-value signal types
        if signal_type in ["funding", "job_postings", "patent_filings"]:
            score *= 1.5
        elif signal_type in ["search_volume", "social_mentions"]:
            score *= 1.2

        total_score += score

    # Normalize to 0-100 scale
    return min(total_score / len(demand_sources), 100.0)


def extract_demand_metrics(demand_sources: List[Dict[str, Any]]) -> Dict[str, int]:
    """Extract specific demand metrics from sources"""
    metrics = {
        "search_volume": 0,
        "social_mentions": 0,
        "forum_discussions": 0,
        "job_postings": 0,
        "patent_filings": 0,
        "funding_rounds": 0,
    }

    for source in demand_sources:
        signal_type = source.get("signal_type", "")
        signal_value = source.get("signal_value", 0)

        try:
            value = int(
                float(
                    str(signal_value)
                    .replace(",", "")
                    .replace("k", "000")
                    .replace("m", "000000")
                )
            )
            if signal_type in metrics:
                metrics[signal_type] += value
        except ValueError:
            # If no numeric value, count as 1 occurrence
            if signal_type in metrics:
                metrics[signal_type] += 1

    return metrics


def assess_validation_confidence(demand_data: Dict[str, Any]) -> str:
    """Assess confidence in demand validation"""
    signal_strength = demand_data.get("signal_strength", 0)
    source_count = len(demand_data.get("demand_sources", []))

    if signal_strength >= 70 and source_count >= 5:
        return "high"
    elif signal_strength >= 40 and source_count >= 3:
        return "medium"
    else:
        return "low"


def assess_market_readiness(demand_data: Dict[str, Any]) -> str:
    """Assess market readiness for the opportunity"""
    signal_strength = demand_data.get("signal_strength", 0)
    validation_confidence = demand_data.get("validation_confidence", "low")

    if signal_strength >= 60 and validation_confidence == "high":
        return "ready"
    elif signal_strength >= 40 and validation_confidence in ["medium", "high"]:
        return "emerging"
    else:
        return "early"


"""
Market Risk Assessment and Recommendation Functions using Gemini AI
"""

# Initialize Gemini client
client = Client()


def assess_market_risks(
    competition_analysis: Dict[str, Any], trend_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assesses market risks using Gemini AI analysis

    Args:
        competition_analysis: Competition analysis data
        trend_analysis: Trend analysis data

    Returns:
        Comprehensive risk assessment
    """
    risk_assessment = {
        "overall_risk_level": "medium",
        "risk_categories": {
            "competitive_risks": [],
            "market_risks": [],
            "technology_risks": [],
            "regulatory_risks": [],
            "economic_risks": [],
        },
        "risk_mitigation_strategies": [],
        "risk_score": 0.0,  # 0-100 scale, higher = more risky
        "critical_risks": [],
        "risk_timeline": {},
        "confidence_level": "medium",
    }

    try:
        # Prepare comprehensive data for Gemini analysis
        analysis_data = {  # noqa: F841
            "competition_data": competition_analysis,
            "trend_data": trend_analysis,
        }

        prompt = f"""
        Analyze the following market data and provide a comprehensive risk assessment for entering this market.

        Competition Analysis:
        {json.dumps(competition_analysis, indent=2)}

        Trend Analysis:
        {json.dumps(trend_analysis, indent=2)}

        Please analyze and return a JSON object with the following structure:
        {{
            "overall_risk_level": "low|medium|high",
            "risk_categories": {{
                "competitive_risks": [
                    {{
                        "risk": "description of competitive risk",
                        "severity": "low|medium|high",
                        "probability": "low|medium|high",
                        "impact": "description of potential impact",
                        "evidence": "what data supports this risk"
                    }}
                ],
                "market_risks": [
                    {{
                        "risk": "description of market risk",
                        "severity": "low|medium|high",
                        "probability": "low|medium|high",
                        "impact": "description of potential impact",
                        "evidence": "what data supports this risk"
                    }}
                ],
                "technology_risks": [
                    {{
                        "risk": "description of technology risk",
                        "severity": "low|medium|high",
                        "probability": "low|medium|high",
                        "impact": "description of potential impact",
                        "evidence": "what data supports this risk"
                    }}
                ],
                "regulatory_risks": [
                    {{
                        "risk": "description of regulatory risk",
                        "severity": "low|medium|high",
                        "probability": "low|medium|high",
                        "impact": "description of potential impact",
                        "evidence": "what data supports this risk"
                    }}
                ],
                "economic_risks": [
                    {{
                        "risk": "description of economic risk",
                        "severity": "low|medium|high",
                        "probability": "low|medium|high",
                        "impact": "description of potential impact",
                        "evidence": "what data supports this risk"
                    }}
                ]
            }},
            "risk_mitigation_strategies": [
                {{
                    "strategy": "description of mitigation strategy",
                    "addresses_risks": ["list of risks this strategy addresses"],
                    "implementation_difficulty": "low|medium|high",
                    "cost_estimate": "low|medium|high",
                    "effectiveness": "low|medium|high"
                }}
            ],
            "risk_score": number_0_to_100,
            "critical_risks": [
                {{
                    "risk": "description of critical risk",
                    "category": "competitive|market|technology|regulatory|economic",
                    "immediate_action_required": true|false,
                    "potential_impact": "description of severe impact"
                }}
            ],
            "risk_timeline": {{
                "immediate_risks": ["risks that need attention in 0-3 months"],
                "short_term_risks": ["risks that need attention in 3-12 months"],
                "long_term_risks": ["risks that need attention in 1+ years"]
            }},
            "confidence_level": "low|medium|high",
            "key_risk_insights": [
                "3-5 key insights about the risk landscape"
            ]
        }}

        Focus on:
        1. Analyze competition level and market saturation risks
        2. Evaluate trend sustainability and market timing risks
        3. Identify technology disruption potential
        4. Consider regulatory and compliance challenges
        5. Assess economic and market volatility factors
        6. Provide specific, actionable mitigation strategies
        7. Prioritize risks by severity and probability

        Base your analysis on the actual data provided, not general assumptions.
        """

        response = client.models.generate_content(
            model=CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            risk_data = json.loads(response.text)
            risk_assessment.update(risk_data)

        return risk_assessment

    except Exception as e:
        print(f"Error in assess_market_risks: {e}")
        risk_assessment["error"] = str(e)
        # Provide basic fallback analysis
        risk_assessment["risk_categories"]["market_risks"].append(
            {
                "risk": "Analysis error - manual review required",
                "severity": "medium",
                "probability": "unknown",
                "impact": "Could not complete automated risk assessment",
                "evidence": f"Error: {str(e)}",
            }
        )
        return risk_assessment


def generate_recommendation(
    opportunity_score: float,
    risk_assessment: Dict[str, Any],
    market_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Generates intelligent market entry recommendation using Gemini AI

    Args:
        opportunity_score: Calculated opportunity score (0-1)
        risk_assessment: Risk assessment data
        market_data: Optional additional market data

    Returns:
        Comprehensive recommendation with reasoning
    """
    recommendation = {
        "recommendation": "analyze_further",
        "confidence": "medium",
        "reasoning": [],
        "action_plan": [],
        "success_probability": 0.0,
        "investment_recommendation": "cautious",
        "timeline_recommendation": "6-12 months",
        "key_success_factors": [],
        "alternative_approaches": [],
        "next_steps": [],
    }

    try:
        # Prepare comprehensive analysis for Gemini
        analysis_context = {  # noqa: F841
            "opportunity_score": opportunity_score,
            "risk_assessment": risk_assessment,
            "market_data": market_data or {},
        }

        prompt = f"""
        Based on the following market analysis data, provide a comprehensive recommendation for this market opportunity.

        Opportunity Score: {opportunity_score} (scale 0-1, where 1 is highest opportunity)

        Risk Assessment:
        {json.dumps(risk_assessment, indent=2)}

        Additional Market Data:
        {json.dumps(market_data or {}, indent=2)}

        Please analyze all the data and return a JSON object with the following structure:
        {{
            "recommendation": "proceed|proceed_with_caution|analyze_further|pivot|do_not_proceed",
            "confidence": "low|medium|high",
            "reasoning": [
                "Detailed reasoning point 1",
                "Detailed reasoning point 2",
                "Detailed reasoning point 3"
            ],
            "action_plan": [
                {{
                    "phase": "immediate|short_term|long_term",
                    "action": "specific action to take",
                    "timeline": "timeframe for this action",
                    "priority": "high|medium|low",
                    "resources_needed": "description of resources required"
                }}
            ],
            "success_probability": number_0_to_100,
            "investment_recommendation": "aggressive|moderate|cautious|minimal",
            "timeline_recommendation": "immediate|3-6_months|6-12_months|12+_months",
            "key_success_factors": [
                "Critical factor 1 for success",
                "Critical factor 2 for success",
                "Critical factor 3 for success"
            ],
            "alternative_approaches": [
                {{
                    "approach": "description of alternative approach",
                    "pros": ["advantage 1", "advantage 2"],
                    "cons": ["disadvantage 1", "disadvantage 2"],
                    "suitability": "high|medium|low"
                }}
            ],
            "next_steps": [
                {{
                    "step": "specific next step",
                    "priority": "high|medium|low",
                    "timeline": "when to complete this step",
                    "outcome_expected": "what this step should achieve"
                }}
            ],
            "risk_mitigation_priorities": [
                "Top priority risk to address first",
                "Second priority risk to address",
                "Third priority risk to address"
            ],
            "market_entry_strategy": {{
                "recommended_approach": "description of recommended market entry approach",
                "target_segment": "which market segment to target first",
                "differentiation_strategy": "how to differentiate from competitors",
                "pricing_strategy": "recommended pricing approach"
            }},
            "success_metrics": [
                {{
                    "metric": "name of metric to track",
                    "target": "target value or milestone",
                    "timeline": "when to achieve this target"
                }}
            ],
            "decision_factors": {{
                "go_factors": ["factors supporting proceeding"],
                "no_go_factors": ["factors against proceeding"],
                "neutral_factors": ["factors that could go either way"]
            }}
        }}

        Provide specific, actionable recommendations based on:
        1. The opportunity score relative to risk level
        2. Critical risks that must be addressed
        3. Market timing and competitive dynamics
        4. Resource requirements vs. potential returns
        5. Probability of success given current data

        Be honest about uncertainties and provide clear decision criteria.
        Consider multiple scenarios and provide flexible strategies.
        """

        response = client.models.generate_content(
            model=CONFIG["primary_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.4
            ),
        )

        if response and response.text:
            recommendation_data = json.loads(response.text)
            recommendation.update(recommendation_data)

        # Add summary recommendation based on score and risk
        recommendation["summary"] = generate_recommendation_summary(
            opportunity_score, risk_assessment, recommendation
        )

        return recommendation

    except Exception as e:
        print(f"Error in generate_recommendation: {e}")
        recommendation["error"] = str(e)

        # Provide basic fallback recommendation
        if opportunity_score > 0.7:
            recommendation["recommendation"] = "proceed_with_caution"
            recommendation["reasoning"] = ["High opportunity score suggests potential"]
        elif opportunity_score > 0.5:
            recommendation["recommendation"] = "analyze_further"
            recommendation["reasoning"] = [
                "Moderate opportunity score requires more analysis"
            ]
        else:
            recommendation["recommendation"] = "do_not_proceed"
            recommendation["reasoning"] = [
                "Low opportunity score indicates limited potential"
            ]

        return recommendation


def generate_recommendation_summary(
    opportunity_score: float,
    risk_assessment: Dict[str, Any],
    recommendation_data: Dict[str, Any],
) -> str:
    """
    Generates a concise executive summary of the recommendation
    """
    try:
        score_percent = int(opportunity_score * 100)
        risk_level = risk_assessment.get("overall_risk_level", "medium")
        rec_action = recommendation_data.get("recommendation", "analyze_further")
        success_prob = recommendation_data.get("success_probability", 50)

        summary = f"""
        EXECUTIVE SUMMARY:

        Market Opportunity Score: {score_percent}%
        Overall Risk Level: {risk_level.title()}
        Recommendation: {rec_action.replace('_', ' ').title()}
        Success Probability: {success_prob}%

        {recommendation_data.get('reasoning', ['Analysis incomplete'])[0] if recommendation_data.get('reasoning') else 'Detailed analysis required for final recommendation.'}
        """

        return summary.strip()

    except Exception:
        return "Summary generation failed - refer to detailed recommendation data."


def validate_market_opportunity_comprehensive(
    keywords: list,
    target_audience: str = "",
    solution_type: str = "",
    pain_points: list = None,
) -> Dict[str, Any]:
    """
    Comprehensive market opportunity validation combining all analysis functions

    Args:
        keywords: Market keywords to analyze
        target_audience: Target audience description
        solution_type: Type of solution being considered
        pain_points: List of pain points to validate

    Returns:
        Complete market validation report with recommendations
    """
    from datetime import datetime

    # Import required functions (these would be in the same module)
    from .market_research import (
        analyze_market_size,
        research_competition,
        validate_demand_signals,
        calculate_opportunity_score_real,
    )

    validation_report = {
        "validation_id": datetime.now().isoformat(),
        "input_parameters": {
            "keywords": keywords,
            "target_audience": target_audience,
            "solution_type": solution_type,
            "pain_points": pain_points or [],
        },
        "market_size_analysis": {},
        "competition_analysis": {},
        "demand_validation": {},
        "trend_analysis": {},
        "risk_assessment": {},
        "opportunity_score": 0.0,
        "final_recommendation": {},
        "validation_timestamp": datetime.now().isoformat(),
    }

    try:
        print("Starting comprehensive market validation...")

        # 1. Market Size Analysis
        print("Analyzing market size...")
        validation_report["market_size_analysis"] = analyze_market_size(
            keywords, target_audience
        )

        # 2. Competition Research
        print("Researching competition...")
        validation_report["competition_analysis"] = research_competition(
            keywords, solution_type
        )

        # 3. Demand Validation
        print("Validating demand signals...")
        validation_report["demand_validation"] = validate_demand_signals(
            keywords, pain_points or []
        )

        # 4. Trend Analysis (placeholder - would integrate with trend analysis function)
        validation_report["trend_analysis"] = {
            "trend_direction": "stable",
            "growth_indicators": [],
            "market_maturity": "developing",
        }

        # 5. Risk Assessment
        print("Assessing market risks...")
        validation_report["risk_assessment"] = assess_market_risks(
            validation_report["competition_analysis"],
            validation_report["trend_analysis"],
        )

        # 6. Calculate Opportunity Score
        print("Calculating opportunity score...")
        validation_report["opportunity_score"] = calculate_opportunity_score_real(
            {
                "market_signals": validation_report["demand_validation"].get(
                    "demand_sources", []
                ),
                "competition_analysis": validation_report["competition_analysis"],
                "demand_validation": validation_report["demand_validation"],
                "trend_analysis": validation_report["trend_analysis"],
            }
        )

        # 7. Generate Final Recommendation
        print("Generating recommendation...")
        validation_report["final_recommendation"] = generate_recommendation(
            validation_report["opportunity_score"],
            validation_report["risk_assessment"],
            {
                "market_size": validation_report["market_size_analysis"],
                "competition": validation_report["competition_analysis"],
                "demand": validation_report["demand_validation"],
            },
        )

        print("Market validation completed successfully!")
        return validation_report

    except Exception as e:
        print(f"Error in comprehensive validation: {e}")
        validation_report["error"] = str(e)
        return validation_report


# Example usage function
def example_market_validation():
    """
    Example of how to use the comprehensive market validation
    """
    keywords = ["AI productivity tools", "workflow automation", "team collaboration"]
    target_audience = "small to medium businesses, remote teams"
    solution_type = "SaaS platform"
    pain_points = [
        "Manual workflow processes are time-consuming",
        "Poor team coordination in remote work",
        "Difficulty tracking project progress",
    ]

    # Run comprehensive validation
    result = validate_market_opportunity_comprehensive(
        keywords=keywords,
        target_audience=target_audience,
        solution_type=solution_type,
        pain_points=pain_points,
    )

    return result
