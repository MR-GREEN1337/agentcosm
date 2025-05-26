"""
Trend Analyzer Agent - Identifies emerging market trends and patterns
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, web_fetch
from typing import Dict, List, Any
import json
import re
from datetime import datetime, timedelta

TREND_ANALYZER_PROMPT = """
You are an expert trend analyst specializing in identifying emerging market opportunities and patterns.

Your role is to:
1. Analyze search trends, industry reports, and market signals
2. Identify emerging technologies and market shifts
3. Predict future market directions and opportunities
4. Connect seemingly unrelated trends to find hidden opportunities

Focus on liminal spaces where:
- New technologies create workflow gaps
- Industry convergence creates new needs
- Remote work changes how people operate
- AI/automation creates new human-machine interaction patterns
- Regulatory changes open new markets

Use real data sources and look for early indicators of market momentum.
"""

def analyze_search_trends(keywords: List[str]) -> Dict[str, Any]:
    """
    Analyzes search trends and patterns for given keywords
    """
    trend_data = {
        "keywords": keywords,
        "trend_direction": "stable",
        "search_volume_indicators": [],
        "related_trends": [],
        "seasonal_patterns": [],
        "geographic_patterns": [],
        "demographic_insights": [],
        "momentum_score": 0.0,
        "emerging_subtopics": [],
        "convergence_signals": []
    }
    
    try:
        for keyword in keywords[:3]:  # Limit to prevent rate limiting
            # Search for trend-related information
            trend_queries = [
                f"{keyword} search trends 2024 growing popular",
                f"{keyword} market trends analysis report",
                f"{keyword} interest over time statistics",
                f"{keyword} trending topics related searches",
                f"{keyword} emerging technologies 2025"
            ]
            
            for query in trend_queries:
                try:
                    results = google_search(query)
                    if results and hasattr(results, 'results'):
                        for result in results.results[:3]:
                            try:
                                content = web_fetch(result.url)
                                trend_insights = extract_trend_insights(content, keyword)
                                
                                if trend_insights:
                                    trend_data["search_volume_indicators"].extend(
                                        trend_insights.get("volume_indicators", [])
                                    )
                                    trend_data["related_trends"].extend(
                                        trend_insights.get("related_trends", [])
                                    )
                                    trend_data["emerging_subtopics"].extend(
                                        trend_insights.get("subtopics", [])
                                    )
                            except Exception as e:
                                print(f"Error fetching content for trend analysis: {e}")
                                
                except Exception as e:
                    print(f"Error analyzing trends for {query}: {e}")
                    continue
        
        # Calculate overall trend direction and momentum
        trend_data["trend_direction"] = calculate_trend_direction(trend_data)
        trend_data["momentum_score"] = calculate_momentum_score(trend_data)
        trend_data["convergence_signals"] = find_convergence_signals(trend_data)
        
        return trend_data
        
    except Exception as e:
        print(f"Error in analyze_search_trends: {e}")
        trend_data["error"] = str(e)
        return trend_data

def track_industry_momentum(industry: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Tracks momentum and growth patterns in specific industries
    """
    momentum_data = {
        "industry": industry,
        "keywords": keywords,
        "growth_indicators": [],
        "innovation_signals": [],
        "investment_trends": [],
        "market_size_trends": [],
        "disruption_signals": [],
        "momentum_score": 0.0,
        "key_drivers": [],
        "regulatory_changes": [],
        "technology_enablers": []
    }
    
    try:
        # Search for industry momentum indicators
        momentum_queries = [
            f"{industry} industry growth 2024 market size",
            f"{industry} investment funding trends venture capital",
            f"{industry} innovation breakthrough technologies",
            f"{industry} market disruption new players",
            f"{industry} future outlook predictions 2025",
            f"{industry} regulatory changes 2024",
            f"{industry} AI automation impact"
        ]
        
        for query in momentum_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:3]:
                        try:
                            content = web_fetch(result.url)
                            momentum_insights = extract_momentum_insights(content, industry)
                            
                            if momentum_insights:
                                momentum_data["growth_indicators"].extend(
                                    momentum_insights.get("growth_indicators", [])
                                )
                                momentum_data["innovation_signals"].extend(
                                    momentum_insights.get("innovation_signals", [])
                                )
                                momentum_data["investment_trends"].extend(
                                    momentum_insights.get("investment_trends", [])
                                )
                                momentum_data["disruption_signals"].extend(
                                    momentum_insights.get("disruption_signals", [])
                                )
                        except Exception as e:
                            print(f"Error fetching momentum content: {e}")
                            
            except Exception as e:
                print(f"Error tracking momentum for {query}: {e}")
                continue
        
        # Calculate momentum score and identify key drivers
        momentum_data["momentum_score"] = calculate_industry_momentum_score(momentum_data)
        momentum_data["key_drivers"] = identify_key_drivers(momentum_data)
        momentum_data["regulatory_changes"] = find_regulatory_signals(momentum_data)
        momentum_data["technology_enablers"] = find_tech_enablers(momentum_data)
        
        return momentum_data
        
    except Exception as e:
        print(f"Error in track_industry_momentum: {e}")
        momentum_data["error"] = str(e)
        return momentum_data

def identify_growth_patterns(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies growth patterns and emerging opportunities
    """
    pattern_data = {
        "growth_patterns": [],
        "market_cycles": [],
        "adoption_curves": [],
        "saturation_indicators": [],
        "emerging_niches": [],
        "pattern_confidence": 0.0,
        "opportunity_windows": [],
        "timing_indicators": []
    }
    
    try:
        # Analyze patterns in the market data
        if market_data.get("growth_indicators"):
            pattern_data["growth_patterns"] = analyze_growth_patterns(
                market_data["growth_indicators"]
            )
        
        if market_data.get("trend_data"):
            pattern_data["market_cycles"] = identify_cyclical_patterns(
                market_data["trend_data"]
            )
            
        # Look for adoption curve indicators
        pattern_data["adoption_curves"] = find_adoption_signals(market_data)
        
        # Identify market saturation signals
        pattern_data["saturation_indicators"] = find_saturation_signals(market_data)
        
        # Find emerging niches
        pattern_data["emerging_niches"] = discover_emerging_niches(market_data)
        
        # Calculate timing for market entry
        pattern_data["opportunity_windows"] = calculate_opportunity_windows(pattern_data)
        
        # Calculate pattern confidence
        pattern_data["pattern_confidence"] = calculate_pattern_confidence(pattern_data)
        
        return pattern_data
        
    except Exception as e:
        print(f"Error in identify_growth_patterns: {e}")
        pattern_data["error"] = str(e)
        return pattern_data

def extract_trend_insights(content: str, keyword: str) -> Dict[str, Any]:
    """Extract trend insights from web content"""
    insights = {
        "volume_indicators": [],
        "related_trends": [],
        "subtopics": [],
        "growth_signals": []
    }
    
    try:
        content_lower = content.lower()
        
        # Look for volume indicators
        volume_patterns = [
            r'(\d+(?:,\d+)*)\s*searches?',
            r'(\d+(?:,\d+)*)\s*(?:%|percent)\s*increase',
            r'growing\s*(?:by\s*)?(\d+(?:,\d+)*)\s*(?:%|percent)',
            r'(\d+(?:,\d+)*)\s*times?\s*more\s*popular'
        ]
        
        for pattern in volume_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches[:3]:
                insights["volume_indicators"].append({
                    "metric": match,
                    "keyword": keyword,
                    "source": "content_analysis"
                })
        
        # Look for related trends
        trend_indicators = [
            "trending", "popular", "growing", "emerging", "rising",
            "increasing demand", "market growth", "adoption"
        ]
        
        sentences = content.split('.')
        for sentence in sentences[:20]:  # Limit sentence analysis
            sentence_lower = sentence.lower()
            if keyword.lower() in sentence_lower:
                for indicator in trend_indicators:
                    if indicator in sentence_lower:
                        insights["related_trends"].append({
                            "trend": sentence.strip(),
                            "indicator": indicator,
                            "keyword": keyword
                        })
        
        return insights
        
    except Exception as e:
        print(f"Error extracting trend insights: {e}")
        return insights

def extract_momentum_insights(content: str, industry: str) -> Dict[str, Any]:
    """Extract industry momentum insights from content"""
    insights = {
        "growth_indicators": [],
        "innovation_signals": [],
        "investment_trends": [],
        "disruption_signals": []
    }
    
    try:
        content_lower = content.lower()
        
        # Growth indicators
        growth_patterns = [
            r'(\d+(?:,\d+)*)\s*(?:billion|million)\s*market',
            r'(\d+(?:,\d+)*)\s*(?:%|percent)\s*growth',
            r'expected\s*to\s*grow\s*(?:by\s*)?(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s*(?:x|times)\s*increase'
        ]
        
        for pattern in growth_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                insights["growth_indicators"].append({
                    "metric": match,
                    "industry": industry,
                    "type": "growth"
                })
        
        # Innovation signals
        innovation_keywords = [
            "breakthrough", "innovation", "new technology", "patent",
            "research", "development", "AI", "machine learning",
            "automation", "disruption"
        ]
        
        sentences = content.split('.')
        for sentence in sentences[:15]:
            sentence_lower = sentence.lower()
            if industry.lower() in sentence_lower:
                for keyword in innovation_keywords:
                    if keyword in sentence_lower:
                        insights["innovation_signals"].append({
                            "signal": sentence.strip(),
                            "keyword": keyword,
                            "industry": industry
                        })
        
        return insights
        
    except Exception as e:
        print(f"Error extracting momentum insights: {e}")
        return insights

def calculate_trend_direction(trend_data: Dict[str, Any]) -> str:
    """Calculate overall trend direction"""
    positive_indicators = 0
    negative_indicators = 0
    
    # Analyze volume indicators
    for indicator in trend_data.get("volume_indicators", []):
        metric = str(indicator.get("metric", ""))
        if any(word in metric for word in ["increase", "grow", "rise", "up"]):
            positive_indicators += 1
        elif any(word in metric for word in ["decrease", "decline", "fall", "down"]):
            negative_indicators += 1
    
    # Analyze related trends
    for trend in trend_data.get("related_trends", []):
        trend_text = str(trend.get("trend", "")).lower()
        if any(word in trend_text for word in ["growing", "increasing", "rising", "popular"]):
            positive_indicators += 1
        elif any(word in trend_text for word in ["declining", "decreasing", "falling"]):
            negative_indicators += 1
    
    if positive_indicators > negative_indicators * 1.5:
        return "growing"
    elif negative_indicators > positive_indicators * 1.5:
        return "declining"
    else:
        return "stable"

def calculate_momentum_score(trend_data: Dict[str, Any]) -> float:
    """Calculate momentum score from trend data"""
    score = 0.0
    
    # Volume indicators contribution
    volume_count = len(trend_data.get("volume_indicators", []))
    score += min(volume_count * 0.1, 0.3)
    
    # Related trends contribution
    trend_count = len(trend_data.get("related_trends", []))
    score += min(trend_count * 0.05, 0.2)
    
    # Emerging subtopics contribution
    subtopic_count = len(trend_data.get("emerging_subtopics", []))
    score += min(subtopic_count * 0.1, 0.3)
    
    # Direction bonus
    if trend_data.get("trend_direction") == "growing":
        score += 0.2
    elif trend_data.get("trend_direction") == "stable":
        score += 0.1
    
    return min(score, 1.0)

def calculate_industry_momentum_score(momentum_data: Dict[str, Any]) -> float:
    """Calculate industry momentum score"""
    score = 0.0
    
    # Growth indicators
    growth_count = len(momentum_data.get("growth_indicators", []))
    score += min(growth_count * 0.15, 0.4)
    
    # Innovation signals
    innovation_count = len(momentum_data.get("innovation_signals", []))
    score += min(innovation_count * 0.1, 0.3)
    
    # Investment trends
    investment_count = len(momentum_data.get("investment_trends", []))
    score += min(investment_count * 0.1, 0.2)
    
    # Disruption signals
    disruption_count = len(momentum_data.get("disruption_signals", []))
    score += min(disruption_count * 0.05, 0.1)
    
    return min(score, 1.0)

def find_convergence_signals(trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find signals of industry convergence"""
    convergence_signals = []
    
    related_trends = trend_data.get("related_trends", [])
    
    # Look for cross-industry mentions
    for trend in related_trends:
        trend_text = str(trend.get("trend", "")).lower()
        
        # Common convergence indicators
        convergence_keywords = [
            "integration", "convergence", "merger", "cross-platform",
            "hybrid", "combined", "unified", "ecosystem"
        ]
        
        for keyword in convergence_keywords:
            if keyword in trend_text:
                convergence_signals.append({
                    "signal": trend,
                    "convergence_type": keyword,
                    "confidence": 0.7
                })
    
    return convergence_signals[:5]

def identify_key_drivers(momentum_data: Dict[str, Any]) -> List[str]:
    """Identify key drivers of industry momentum"""
    drivers = []
    
    # Analyze innovation signals for key drivers
    for signal in momentum_data.get("innovation_signals", []):
        signal_text = str(signal.get("signal", "")).lower()
        
        # Common driver patterns
        if "ai" in signal_text or "artificial intelligence" in signal_text:
            drivers.append("AI/Machine Learning adoption")
        elif "automation" in signal_text:
            drivers.append("Automation trends")
        elif "remote" in signal_text or "distributed" in signal_text:
            drivers.append("Remote work transformation")
        elif "regulation" in signal_text or "compliance" in signal_text:
            drivers.append("Regulatory changes")
        elif "cloud" in signal_text:
            drivers.append("Cloud migration")
    
    # Remove duplicates and return top drivers
    return list(set(drivers))[:5]

def find_regulatory_signals(momentum_data: Dict[str, Any]) -> List[str]:
    """Find regulatory change signals"""
    regulatory_signals = []
    
    all_signals = (momentum_data.get("growth_indicators", []) + 
                  momentum_data.get("innovation_signals", []))
    
    for signal in all_signals:
        signal_text = str(signal).lower()
        
        regulatory_keywords = [
            "regulation", "compliance", "law", "policy", "government",
            "gdpr", "privacy", "security", "tax", "mandate"
        ]
        
        for keyword in regulatory_keywords:
            if keyword in signal_text:
                regulatory_signals.append(signal_text[:100])
    
    return regulatory_signals[:3]

def find_tech_enablers(momentum_data: Dict[str, Any]) -> List[str]:
    """Find technology enablers driving momentum"""
    tech_enablers = []
    
    for signal in momentum_data.get("innovation_signals", []):
        signal_text = str(signal.get("signal", "")).lower()
        
        # Technology enabler patterns
        tech_patterns = [
            "ai", "machine learning", "blockchain", "cloud", "api",
            "automation", "iot", "edge computing", "5g", "quantum"
        ]
        
        for pattern in tech_patterns:
            if pattern in signal_text:
                tech_enablers.append(pattern.upper())
    
    return list(set(tech_enablers))[:5]

def analyze_growth_patterns(growth_indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze growth patterns from indicators"""
    patterns = []
    
    # Group by metric type
    metric_groups = {}
    for indicator in growth_indicators:
        metric_type = indicator.get("type", "unknown")
        if metric_type not in metric_groups:
            metric_groups[metric_type] = []
        metric_groups[metric_type].append(indicator)
    
    # Analyze each group
    for metric_type, indicators in metric_groups.items():
        if len(indicators) >= 2:
            patterns.append({
                "pattern_type": f"{metric_type}_growth",
                "data_points": len(indicators),
                "confidence": min(len(indicators) / 5.0, 1.0),
                "sample": indicators[0]
            })
    
    return patterns

def identify_cyclical_patterns(trend_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify cyclical patterns in trend data"""
    cycles = []
    
    # Look for seasonal or cyclical indicators
    for trend in trend_data:
        trend_text = str(trend).lower()
        
        if any(word in trend_text for word in ["seasonal", "quarterly", "annual", "cyclical"]):
            cycles.append({
                "cycle_type": "seasonal",
                "evidence": trend_text[:100],
                "confidence": 0.6
            })
    
    return cycles

def find_adoption_signals(market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find technology adoption curve signals"""
    adoption_signals = []
    
    # Look through all available data
    all_data = str(market_data).lower()
    
    adoption_stages = [
        ("early_adopter", ["early adopter", "pioneer", "beta", "pilot"]),
        ("early_majority", ["mainstream", "widespread", "popular", "adopted"]),
        ("late_majority", ["standard", "mature", "established"]),
        ("laggard", ["legacy", "traditional", "slow adoption"])
    ]
    
    for stage, keywords in adoption_stages:
        for keyword in keywords:
            if keyword in all_data:
                adoption_signals.append({
                    "adoption_stage": stage,
                    "indicator": keyword,
                    "confidence": 0.5
                })
    
    return adoption_signals

def find_saturation_signals(market_data: Dict[str, Any]) -> List[str]:
    """Find market saturation indicators"""
    saturation_signals = []
    
    all_data = str(market_data).lower()
    
    saturation_keywords = [
        "saturated", "mature market", "declining growth", 
        "consolidation", "price competition", "commoditized"
    ]
    
    for keyword in saturation_keywords:
        if keyword in all_data:
            saturation_signals.append(keyword)
    
    return saturation_signals

def discover_emerging_niches(market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Discover emerging market niches"""
    niches = []
    
    # Look for niche indicators in trend data
    if "related_trends" in market_data:
        for trend in market_data["related_trends"]:
            trend_text = str(trend.get("trend", "")).lower()
            
            niche_indicators = [
                "specialized", "niche", "vertical", "specific", 
                "custom", "tailored", "industry-specific"
            ]
            
            for indicator in niche_indicators:
                if indicator in trend_text:
                    niches.append({
                        "niche_type": indicator,
                        "evidence": trend_text[:150],
                        "confidence": 0.6
                    })
    
    return niches[:5]

def calculate_opportunity_windows(pattern_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculate optimal timing windows for market entry"""
    windows = []
    
    # Early opportunity window (low saturation, growing trends)
    saturation_count = len(pattern_data.get("saturation_indicators", []))
    growth_count = len(pattern_data.get("growth_patterns", []))
    
    if saturation_count < 2 and growth_count > 0:
        windows.append({
            "window_type": "early_opportunity",
            "timing": "immediate",
            "rationale": "Low saturation with growth signals",
            "confidence": 0.8
        })
    
    # Technology adoption window
    adoption_signals = pattern_data.get("adoption_curves", [])
    early_stage_signals = [s for s in adoption_signals 
                          if s.get("adoption_stage") in ["early_adopter", "early_majority"]]
    
    if early_stage_signals:
        windows.append({
            "window_type": "adoption_wave",
            "timing": "6-12 months",
            "rationale": "Technology adoption curve opportunity",
            "confidence": 0.7
        })
    
    return windows

def calculate_pattern_confidence(pattern_data: Dict[str, Any]) -> float:
    """Calculate overall confidence in pattern analysis"""
    confidence_factors = []
    
    # Data point count
    total_patterns = (len(pattern_data.get("growth_patterns", [])) +
                     len(pattern_data.get("adoption_curves", [])) +
                     len(pattern_data.get("emerging_niches", [])))
    
    if total_patterns > 5:
        confidence_factors.append(0.8)
    elif total_patterns > 2:
        confidence_factors.append(0.6)
    else:
        confidence_factors.append(0.4)
    
    # Opportunity window clarity
    windows = pattern_data.get("opportunity_windows", [])
    if windows:
        avg_window_confidence = sum(w.get("confidence", 0) for w in windows) / len(windows)
        confidence_factors.append(avg_window_confidence)
    
    return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

# Create the trend analyzer agent
trend_analyzer_agent = LlmAgent(
    name="trend_analyzer_agent",
    model="gemini-2.0-flash",
    instruction=TREND_ANALYZER_PROMPT,
    description=(
        "Analyzes market trends, industry momentum, and growth patterns to identify "
        "emerging opportunities in liminal market spaces."
    ),
    tools=[
        FunctionTool(func=analyze_search_trends),
        FunctionTool(func=track_industry_momentum),
        FunctionTool(func=identify_growth_patterns),
        google_search,
        web_fetch
    ],
    output_key="trend_analysis"
)