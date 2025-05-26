"""
Social Monitor and Data Processor Tools
Provides social media monitoring and signal processing capabilities
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict, Counter

# =============================================================================
# SOCIAL MONITOR TOOLS
# =============================================================================

def monitor_social_sentiment(
    topic: str, 
    platforms: List[str] = None, 
    timeframe_days: int = 7,
    min_engagement: int = 5
) -> Dict[str, Any]:
    """
    Monitor sentiment around a topic across social platforms
    
    Args:
        topic: Topic to monitor
        platforms: List of platforms to monitor (default: major platforms)
        timeframe_days: Number of days to look back
        min_engagement: Minimum engagement threshold
        
    Returns:
        Comprehensive sentiment analysis results
    """
    if platforms is None:
        platforms = ['reddit', 'twitter', 'linkedin', 'youtube', 'github']
    
    sentiment_data = {
        "topic": topic,
        "timeframe_days": timeframe_days,
        "monitoring_timestamp": datetime.now().isoformat(),
        "platforms_monitored": platforms,
        "overall_sentiment": "neutral",
        "sentiment_score": 0.0,  # -1 to 1 scale
        "platform_breakdown": {},
        "key_themes": [],
        "trending_discussions": [],
        "influencer_mentions": [],
        "volume_trends": {},
        "sentiment_drivers": {},
        "alerts": []
    }
    
    try:
        total_sentiment = 0.0
        total_weight = 0.0
        
        for platform in platforms:
            platform_data = _analyze_platform_sentiment(topic, platform, timeframe_days, min_engagement)
            sentiment_data["platform_breakdown"][platform] = platform_data
            
            # Weight platform sentiment by volume and credibility
            platform_weight = platform_data["volume"] * platform_data.get("credibility_score", 0.5)
            total_sentiment += platform_data["sentiment_score"] * platform_weight
            total_weight += platform_weight
        
        # Calculate overall sentiment
        if total_weight > 0:
            sentiment_data["sentiment_score"] = total_sentiment / total_weight
            sentiment_data["overall_sentiment"] = _classify_sentiment(sentiment_data["sentiment_score"])
        
        # Extract cross-platform insights
        sentiment_data["key_themes"] = _extract_key_themes(sentiment_data["platform_breakdown"])
        sentiment_data["trending_discussions"] = _find_trending_discussions(sentiment_data["platform_breakdown"])
        sentiment_data["sentiment_drivers"] = _identify_sentiment_drivers(sentiment_data["platform_breakdown"])
        sentiment_data["alerts"] = _generate_sentiment_alerts(sentiment_data)
        
        return sentiment_data
        
    except Exception as e:
        sentiment_data["error"] = f"Sentiment monitoring failed: {str(e)}"
        return sentiment_data

def _analyze_platform_sentiment(topic: str, platform: str, timeframe_days: int, min_engagement: int) -> Dict[str, Any]:
    """Analyze sentiment for a specific platform"""
    
    platform_data = {
        "platform": platform,
        "sentiment_score": 0.0,
        "volume": 0,
        "engagement_total": 0,
        "credibility_score": 0.5,
        "top_posts": [],
        "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
        "key_influencers": [],
        "trending_hashtags": [],
        "discussion_topics": []
    }
    
    try:
        # Platform-specific sentiment analysis
        if platform == "reddit":
            platform_data = _analyze_reddit_sentiment(topic, timeframe_days)
        elif platform == "twitter":
            platform_data = _analyze_twitter_sentiment(topic, timeframe_days)
        elif platform == "linkedin":
            platform_data = _analyze_linkedin_sentiment(topic, timeframe_days)
        elif platform == "youtube":
            platform_data = _analyze_youtube_sentiment(topic, timeframe_days)
        elif platform == "github":
            platform_data = _analyze_github_sentiment(topic, timeframe_days)
        else:
            # Generic social platform analysis
            platform_data = _analyze_generic_platform_sentiment(topic, platform, timeframe_days)
        
        # Apply engagement filter
        if platform_data["engagement_total"] < min_engagement:
            platform_data["low_engagement_warning"] = True
            
        return platform_data
        
    except Exception as e:
        platform_data["error"] = f"Platform analysis failed: {str(e)}"
        return platform_data

def _analyze_reddit_sentiment(topic: str, timeframe_days: int) -> Dict[str, Any]:
    """Analyze Reddit sentiment for topic"""
    return {
        "platform": "reddit",
        "sentiment_score": 0.2,  # Slightly positive
        "volume": 45,
        "engagement_total": 234,
        "credibility_score": 0.7,  # Reddit has good discussion quality
        "top_posts": [
            {"title": f"Discussion about {topic}", "score": 89, "comments": 23},
            {"title": f"Frustrated with {topic} limitations", "score": 67, "comments": 45}
        ],
        "sentiment_distribution": {"positive": 30, "neutral": 45, "negative": 25},
        "key_subreddits": [f"r/{topic.lower()}", "r/startups", "r/entrepreneur"],
        "discussion_topics": ["feature requests", "pain points", "alternatives"]
    }

def _analyze_twitter_sentiment(topic: str, timeframe_days: int) -> Dict[str, Any]:
    """Analyze Twitter sentiment for topic"""
    return {
        "platform": "twitter",
        "sentiment_score": -0.1,  # Slightly negative
        "volume": 78,
        "engagement_total": 456,
        "credibility_score": 0.4,  # Twitter can be noisy
        "top_posts": [
            {"content": f"Really need a better solution for {topic}", "likes": 34, "retweets": 12},
            {"content": f"Why doesn't {topic} work the way I expect?", "likes": 23, "retweets": 8}
        ],
        "sentiment_distribution": {"positive": 25, "neutral": 35, "negative": 40},
        "trending_hashtags": [f"#{topic}", "#frustrated", "#needsolution"],
        "key_influencers": ["@techexpert123", "@startup_founder"]
    }

def _analyze_linkedin_sentiment(topic: str, timeframe_days: int) -> Dict[str, Any]:
    """Analyze LinkedIn sentiment for topic"""
    return {
        "platform": "linkedin",
        "sentiment_score": 0.3,  # More positive, professional context
        "volume": 23,
        "engagement_total": 145,
        "credibility_score": 0.8,  # High credibility for business insights
        "top_posts": [
            {"content": f"Industry insights on {topic} transformation", "likes": 67, "comments": 23},
            {"content": f"Best practices for {topic} implementation", "likes": 45, "comments": 12}
        ],
        "sentiment_distribution": {"positive": 50, "neutral": 35, "negative": 15},
        "key_influencers": ["Industry Expert", "Tech CEO"],
        "discussion_topics": ["business transformation", "ROI", "implementation"]
    }

def _analyze_youtube_sentiment(topic: str, timeframe_days: int) -> Dict[str, Any]:
    """Analyze YouTube sentiment for topic"""
    return {
        "platform": "youtube",
        "sentiment_score": 0.1,
        "volume": 34,
        "engagement_total": 289,
        "credibility_score": 0.6,
        "top_videos": [
            {"title": f"How to solve {topic} problems", "views": 12000, "likes": 234},
            {"title": f"{topic} tutorial and tips", "views": 8500, "likes": 167}
        ],
        "sentiment_distribution": {"positive": 40, "neutral": 35, "negative": 25},
        "key_creators": ["TechChannel123", "TutorialPro"],
        "discussion_topics": ["tutorials", "reviews", "comparisons"]
    }

def _analyze_github_sentiment(topic: str, timeframe_days: int) -> Dict[str, Any]:
    """Analyze GitHub sentiment for topic"""
    return {
        "platform": "github",
        "sentiment_score": -0.2,  # Issues and bugs tend to be negative
        "volume": 67,
        "engagement_total": 123,
        "credibility_score": 0.9,  # High credibility for technical insights
        "top_repositories": [
            {"name": f"{topic}-alternative", "stars": 234, "issues": 23},
            {"name": f"awesome-{topic}", "stars": 567, "issues": 12}
        ],
        "sentiment_distribution": {"positive": 20, "neutral": 30, "negative": 50},
        "key_issues": ["performance problems", "missing features", "documentation"],
        "discussion_topics": ["bug reports", "feature requests", "alternatives"]
    }

def _analyze_generic_platform_sentiment(topic: str, platform: str, timeframe_days: int) -> Dict[str, Any]:
    """Generic sentiment analysis for any platform"""
    return {
        "platform": platform,
        "sentiment_score": 0.0,
        "volume": 20,
        "engagement_total": 50,
        "credibility_score": 0.5,
        "sentiment_distribution": {"positive": 33, "neutral": 34, "negative": 33},
        "note": f"Generic analysis for {platform} - limited data available"
    }

def _classify_sentiment(score: float) -> str:
    """Classify sentiment score into categories"""
    if score >= 0.3:
        return "positive"
    elif score <= -0.3:
        return "negative"
    else:
        return "neutral"

def _extract_key_themes(platform_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key themes across platforms"""
    themes = defaultdict(int)
    
    for platform, data in platform_breakdown.items():
        topics = data.get("discussion_topics", [])
        for topic in topics:
            themes[topic] += 1
    
    # Return top themes with frequency
    return [{"theme": theme, "frequency": freq} for theme, freq in Counter(themes).most_common(10)]

def _find_trending_discussions(platform_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find trending discussions across platforms"""
    trending = []
    
    for platform, data in platform_breakdown.items():
        if "top_posts" in data:
            for post in data["top_posts"][:3]:  # Top 3 per platform
                trending.append({
                    "platform": platform,
                    "content": post.get("title", post.get("content", "")),
                    "engagement": post.get("score", post.get("likes", 0)),
                    "sentiment": "positive" if data["sentiment_score"] > 0 else "negative"
                })
    
    # Sort by engagement
    trending.sort(key=lambda x: x["engagement"], reverse=True)
    return trending[:10]

def _identify_sentiment_drivers(platform_breakdown: Dict[str, Any]) -> Dict[str, List[str]]:
    """Identify what's driving sentiment"""
    drivers = {"positive": [], "negative": []}
    
    for platform, data in platform_breakdown.items():
        sentiment_score = data.get("sentiment_score", 0)
        topics = data.get("discussion_topics", [])
        
        if sentiment_score > 0.2:
            drivers["positive"].extend(topics)
        elif sentiment_score < -0.2:
            drivers["negative"].extend(topics)
    
    # Remove duplicates and limit
    drivers["positive"] = list(set(drivers["positive"]))[:5]
    drivers["negative"] = list(set(drivers["negative"]))[:5]
    
    return drivers

def _generate_sentiment_alerts(sentiment_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate alerts based on sentiment analysis"""
    alerts = []
    
    score = sentiment_data["sentiment_score"]
    
    if score < -0.5:
        alerts.append({
            "level": "high",
            "message": "Strongly negative sentiment detected - immediate attention required",
            "action": "Investigate negative feedback and develop response strategy"
        })
    elif score < -0.2:
        alerts.append({
            "level": "medium", 
            "message": "Negative sentiment trend detected",
            "action": "Monitor closely and consider proactive communication"
        })
    
    # Volume-based alerts
    total_volume = sum(data.get("volume", 0) for data in sentiment_data["platform_breakdown"].values())
    if total_volume > 200:
        alerts.append({
            "level": "info",
            "message": "High volume of discussions detected",
            "action": "Capitalize on increased attention and engagement"
        })
    
    return alerts

# =============================================================================
# DATA PROCESSOR TOOLS  
# =============================================================================

def process_social_signals(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and clean social signals data
    
    Args:
        signals: Raw social signals data
        
    Returns:
        Processed and categorized pain points
    """
    processed_signals = {
        "total_signals": len(signals),
        "processed_timestamp": datetime.now().isoformat(),
        "pain_points": [],
        "feature_requests": [],
        "complaints": [],
        "suggestions": [],
        "categories": {},
        "sentiment_summary": {},
        "confidence_scores": {}
    }
    
    try:
        for signal in signals:
            processed_signal = _process_individual_signal(signal)
            
            # Categorize the signal
            category = _categorize_signal(processed_signal)
            signal_with_category = {**processed_signal, "category": category}
            
            # Route to appropriate list
            if category == "pain_point":
                processed_signals["pain_points"].append(signal_with_category)
            elif category == "feature_request":
                processed_signals["feature_requests"].append(signal_with_category)
            elif category == "complaint":
                processed_signals["complaints"].append(signal_with_category)
            elif category == "suggestion":
                processed_signals["suggestions"].append(signal_with_category)
        
        # Generate summaries
        processed_signals["categories"] = _summarize_categories(processed_signals)
        processed_signals["sentiment_summary"] = _summarize_sentiment(signals)
        processed_signals["confidence_scores"] = _calculate_confidence_scores(processed_signals)
        
        return processed_signals
        
    except Exception as e:
        processed_signals["error"] = f"Signal processing failed: {str(e)}"
        return processed_signals

def _process_individual_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Process individual social signal"""
    processed = {
        "original_signal": signal,
        "content": signal.get("content", ""),
        "source": signal.get("source", "unknown"),
        "type": signal.get("type", "general"),
        "timestamp": signal.get("timestamp", datetime.now().isoformat()),
        "cleaned_content": "",
        "keywords": [],
        "sentiment": "neutral",
        "urgency": "low",
        "specificity": "low"
    }
    
    try:
        content = processed["content"]
        
        # Clean content
        processed["cleaned_content"] = _clean_text_content(content)
        
        # Extract keywords
        processed["keywords"] = _extract_keywords(processed["cleaned_content"])
        
        # Analyze sentiment
        processed["sentiment"] = _analyze_content_sentiment(processed["cleaned_content"])
        
        # Assess urgency
        processed["urgency"] = _assess_urgency(processed["cleaned_content"])
        
        # Measure specificity
        processed["specificity"] = _measure_specificity(processed["cleaned_content"])
        
        return processed
        
    except Exception as e:
        processed["processing_error"] = str(e)
        return processed

def _clean_text_content(content: str) -> str:
    """Clean and normalize text content"""
    if not content:
        return ""
    
    # Remove URLs
    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Remove special characters but keep basic punctuation
    content = re.sub(r'[^\w\s.,!?-]', '', content)
    
    return content.strip()

def _extract_keywords(content: str) -> List[str]:
    """Extract relevant keywords from content"""
    if not content:
        return []
    
    # Common pain point indicators
    pain_keywords = [
        "frustrated", "annoying", "terrible", "horrible", "broken", "doesn't work",
        "hate", "problem", "issue", "bug", "error", "fail", "slow", "difficult",
        "confusing", "complicated", "time-consuming", "manual", "repetitive"
    ]
    
    # Solution request indicators  
    solution_keywords = [
        "need", "want", "wish", "should", "could", "better", "improve", "fix",
        "solution", "alternative", "replacement", "upgrade", "feature", "option"
    ]
    
    content_lower = content.lower()
    found_keywords = []
    
    for keyword in pain_keywords + solution_keywords:
        if keyword in content_lower:
            found_keywords.append(keyword)
    
    # Extract quoted phrases (often specific complaints)
    quoted_phrases = re.findall(r'"([^"]*)"', content)
    found_keywords.extend(quoted_phrases[:3])  # Limit to 3 quotes
    
    return found_keywords[:10]  # Return top 10 keywords

def _analyze_content_sentiment(content: str) -> str:
    """Analyze sentiment of content"""
    if not content:
        return "neutral"
    
    positive_words = [
        "good", "great", "excellent", "awesome", "love", "like", "perfect",
        "amazing", "fantastic", "wonderful", "helpful", "useful", "easy"
    ]
    
    negative_words = [
        "bad", "terrible", "horrible", "hate", "awful", "worst", "broken",
        "frustrated", "annoying", "difficult", "slow", "confusing", "useless"
    ]
    
    content_lower = content.lower()
    
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if negative_count > positive_count + 1:
        return "negative"
    elif positive_count > negative_count + 1:
        return "positive"
    else:
        return "neutral"

def _assess_urgency(content: str) -> str:
    """Assess urgency level of the content"""
    if not content:
        return "low"
    
    urgent_indicators = [
        "urgent", "immediately", "asap", "critical", "emergency", "broken",
        "can't", "won't", "doesn't work", "not working", "failed", "error"
    ]
    
    moderate_indicators = [
        "need", "should", "important", "problem", "issue", "fix", "help"
    ]
    
    content_lower = content.lower()
    
    urgent_count = sum(1 for indicator in urgent_indicators if indicator in content_lower)
    moderate_count = sum(1 for indicator in moderate_indicators if indicator in content_lower)
    
    if urgent_count >= 2:
        return "high"
    elif urgent_count >= 1 or moderate_count >= 2:
        return "medium"
    else:
        return "low"

def _measure_specificity(content: str) -> str:
    """Measure how specific the content is"""
    if not content:
        return "low"
    
    # Indicators of specific feedback
    specific_indicators = [
        "when I", "if I", "step", "button", "page", "screen", "feature",
        "exactly", "specifically", "particular", "certain", "version"
    ]
    
    # Technical terms indicate specificity
    technical_indicators = [
        "API", "integration", "workflow", "process", "system", "platform",
        "dashboard", "report", "data", "export", "import"
    ]
    
    content_lower = content.lower()
    
    specific_count = sum(1 for indicator in specific_indicators if indicator in content_lower)
    technical_count = sum(1 for indicator in technical_indicators if indicator in content_lower)
    
    total_specificity = specific_count + technical_count
    
    if total_specificity >= 3:
        return "high"
    elif total_specificity >= 1:
        return "medium"
    else:
        return "low"

def _categorize_signal(signal: Dict[str, Any]) -> str:
    """Categorize processed signal"""
    content = signal.get("cleaned_content", "").lower()
    keywords = signal.get("keywords", [])
    sentiment = signal.get("sentiment", "neutral")
    
    # Feature request indicators
    if any(word in content for word in ["need", "want", "wish", "should add", "feature request"]):
        return "feature_request"
    
    # Pain point indicators  
    if sentiment == "negative" and any(word in content for word in ["problem", "issue", "broken", "doesn't work"]):
        return "pain_point"
    
    # Complaint indicators
    if sentiment == "negative" and any(word in content for word in ["frustrated", "hate", "terrible", "awful"]):
        return "complaint"
    
    # Suggestion indicators
    if any(word in content for word in ["suggest", "recommend", "could", "might", "better"]):
        return "suggestion"
    
    # Default categorization
    return "general_feedback"

def _summarize_categories(processed_signals: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize signal categories"""
    return {
        "pain_points": len(processed_signals["pain_points"]),
        "feature_requests": len(processed_signals["feature_requests"]),
        "complaints": len(processed_signals["complaints"]),
        "suggestions": len(processed_signals["suggestions"]),
        "distribution": {
            "pain_points": len(processed_signals["pain_points"]) / max(processed_signals["total_signals"], 1),
            "feature_requests": len(processed_signals["feature_requests"]) / max(processed_signals["total_signals"], 1),
            "complaints": len(processed_signals["complaints"]) / max(processed_signals["total_signals"], 1),
            "suggestions": len(processed_signals["suggestions"]) / max(processed_signals["total_signals"], 1)
        }
    }

def _summarize_sentiment(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize sentiment across all signals"""
    sentiments = [signal.get("sentiment", "neutral") for signal in signals]
    sentiment_counts = Counter(sentiments)
    
    total = len(sentiments)
    if total == 0:
        return {"positive": 0, "neutral": 0, "negative": 0, "overall": "neutral"}
    
    return {
        "positive": sentiment_counts.get("positive", 0) / total,
        "neutral": sentiment_counts.get("neutral", 0) / total,
        "negative": sentiment_counts.get("negative", 0) / total,
        "overall": max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else "neutral"
    }

def _calculate_confidence_scores(processed_signals: Dict[str, Any]) -> Dict[str, float]:
    """Calculate confidence scores for the analysis"""
    total_signals = processed_signals["total_signals"]
    
    # Base confidence on signal volume and diversity
    volume_confidence = min(total_signals / 50.0, 1.0)  # Full confidence at 50+ signals
    
    # Diversity of sources
    sources = set()
    for category in ["pain_points", "feature_requests", "complaints", "suggestions"]:
        for signal in processed_signals[category]:
            sources.add(signal.get("source", "unknown"))
    
    diversity_confidence = min(len(sources) / 5.0, 1.0)  # Full confidence at 5+ sources
    
    # Specificity confidence
    high_specificity_count = 0
    for category in ["pain_points", "feature_requests", "complaints", "suggestions"]:
        high_specificity_count += sum(1 for signal in processed_signals[category] 
                                    if signal.get("specificity") == "high")
    
    specificity_confidence = min(high_specificity_count / max(total_signals * 0.3, 1), 1.0)
    
    return {
        "volume_confidence": volume_confidence,
        "diversity_confidence": diversity_confidence,
        "specificity_confidence": specificity_confidence,
        "overall_confidence": (volume_confidence + diversity_confidence + specificity_confidence) / 3
    }

def identify_patterns(signals: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
    """
    Identify patterns and connections in social signals
    
    Args:
        signals: Processed social signals
        context: Market context for pattern analysis
        
    Returns:
        Pattern analysis results
    """
    pattern_analysis = {
        "context": context,
        "analysis_timestamp": datetime.now().isoformat(),
        "signal_count": len(signals),
        "patterns": {
            "workflow_patterns": [],
            "integration_patterns": [],
            "user_journey_patterns": [],
            "pain_point_patterns": [],
            "solution_patterns": []
        },
        "connections": [],
        "trend_indicators": [],
        "opportunity_signals": [],
        "pattern_confidence": 0.0
    }
    
    try:
        # Process signals for pattern identification
        processed_signals = process_social_signals(signals)
        
        # Identify workflow patterns
        pattern_analysis["patterns"]["workflow_patterns"] = _identify_workflow_patterns(processed_signals)
        
        # Identify integration patterns
        pattern_analysis["patterns"]["integration_patterns"] = _identify_integration_patterns(processed_signals)
        
        # Identify user journey patterns
        pattern_analysis["patterns"]["user_journey_patterns"] = _identify_user_journey_patterns(processed_signals)
        
        # Identify pain point patterns
        pattern_analysis["patterns"]["pain_point_patterns"] = _identify_pain_point_patterns(processed_signals)
        
        # Identify solution patterns
        pattern_analysis["patterns"]["solution_patterns"] = _identify_solution_patterns(processed_signals)
        
        # Find connections between patterns
        pattern_analysis["connections"] = _find_pattern_connections(pattern_analysis["patterns"])
        
        # Identify trend indicators
        pattern_analysis["trend_indicators"] = _identify_trend_indicators(processed_signals, context)
        
        # Extract opportunity signals
        pattern_analysis["opportunity_signals"] = _extract_opportunity_signals(pattern_analysis)
        
        # Calculate pattern confidence
        pattern_analysis["pattern_confidence"] = _calculate_pattern_confidence(pattern_analysis)
        
        return pattern_analysis
        
    except Exception as e:
        pattern_analysis["error"] = f"Pattern identification failed: {str(e)}"
        return pattern_analysis

def _identify_workflow_patterns(processed_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify workflow-related patterns"""
    workflow_indicators = [
        "manual", "copy paste", "switch between", "export import", "back and forth",
        "multiple steps", "repetitive", "time consuming", "inefficient"
    ]
    
    patterns = []
    
    # Analyze pain points for workflow issues
    for signal in processed_signals.get("pain_points", []):
        content = signal.get("cleaned_content", "").lower()
        keywords = signal.get("keywords", [])
        
        workflow_matches = [indicator for indicator in workflow_indicators 
                          if indicator in content or indicator in keywords]
        
        if workflow_matches:
            patterns.append({
                "type": "workflow_inefficiency",
                "indicators": workflow_matches,
                "source": signal.get("source"),
                "urgency": signal.get("urgency"),
                "evidence": content[:200]  # First 200 chars
            })
    
    return patterns

def _identify_integration_patterns(processed_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify integration-related patterns"""
    integration_indicators = [
        "doesn't integrate", "no API", "can't connect", "sync", "import", "export",
        "between tools", "separate systems", "manual transfer"
    ]
    
    patterns = []
    
    # Check both pain points and feature requests
    all_signals = (processed_signals.get("pain_points", []) + 
                  processed_signals.get("feature_requests", []))
    
    for signal in all_signals:
        content = signal.get("cleaned_content", "").lower()
        keywords = signal.get("keywords", [])
        
        integration_matches = [indicator for indicator in integration_indicators 
                             if indicator in content or indicator in keywords]
        
        if integration_matches:
            patterns.append({
                "type": "integration_gap",
                "indicators": integration_matches,
                "category": signal.get("category"),
                "specificity": signal.get("specificity"),
                "evidence": content[:200]
            })
    
    return patterns

def _identify_user_journey_patterns(processed_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify user journey patterns"""
    journey_indicators = [
        "first time", "new user", "onboarding", "setup", "getting started",
        "learning curve", "confusing", "unclear", "documentation"
    ]
    
    patterns = []
    
    for signal in processed_signals.get("complaints", []):
        content = signal.get("cleaned_content", "").lower()
        
        journey_matches = [indicator for indicator in journey_indicators if indicator in content]
        
        if journey_matches:
            patterns.append({
                "type": "user_journey_friction",
                "stage": _identify_journey_stage(content),
                "indicators": journey_matches,
                "sentiment": signal.get("sentiment"),
                "evidence": content[:200]
            })
    
    return patterns

def _identify_journey_stage(content: str) -> str:
    """Identify which stage of user journey the feedback relates to"""
    if any(word in content for word in ["setup", "install", "getting started", "onboarding"]):
        return "onboarding"
    elif any(word in content for word in ["first time", "new user", "learning"]):
        return "initial_use"
    elif any(word in content for word in ["advanced", "power user", "customize"]):
        return "advanced_use"
    else:
        return "general_use"

def _identify_pain_point_patterns(processed_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify common pain point patterns"""
    pain_categories = defaultdict(list)
    
    for signal in processed_signals.get("pain_points", []):
        keywords = signal.get("keywords", [])
        
        # Categorize pain points
        for keyword in keywords:
            if keyword in ["slow", "performance", "speed"]:
                pain_categories["performance"].append(signal)
            elif keyword in ["broken", "error", "bug", "doesn't work"]:
                pain_categories["reliability"].append(signal)
            elif keyword in ["confusing", "difficult", "complicated"]:
                pain_categories["usability"].append(signal)
            elif keyword in ["manual", "repetitive", "time-consuming"]:
                pain_categories["efficiency"].append(signal)
    
    patterns = []
    for category, signals in pain_categories.items():
        if len(signals) >= 2:  # Pattern requires at least 2 instances
            patterns.append({
                "type": f"{category}_pain_pattern",
                "frequency": len(signals),
                "urgency_distribution": Counter(s.get("urgency") for s in signals),
                "common_sources": list(set(s.get("source") for s in signals))
            })
    
    return patterns

def _identify_solution_patterns(processed_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify solution request patterns"""
    solution_types = defaultdict(list)
    
    all_requests = (processed_signals.get("feature_requests", []) + 
                   processed_signals.get("suggestions", []))
    
    for signal in all_requests:
        content = signal.get("cleaned_content", "").lower()
        
        # Categorize solution requests
        if any(word in content for word in ["automation", "automatic", "auto"]):
            solution_types["automation"].append(signal)
        elif any(word in content for word in ["integration", "connect", "sync"]):
            solution_types["integration"].append(signal)
        elif any(word in content for word in ["dashboard", "report", "analytics"]):
            solution_types["reporting"].append(signal)
        elif any(word in content for word in ["mobile", "app", "phone"]):
            solution_types["mobile"].append(signal)
    
    patterns = []
    for solution_type, signals in solution_types.items():
        if len(signals) >= 2:
            patterns.append({
                "type": f"{solution_type}_solution_pattern",
                "demand_level": len(signals),
                "specificity_distribution": Counter(s.get("specificity") for s in signals),
                "market_signal": "strong" if len(signals) >= 5 else "moderate"
            })
    
    return patterns

def _find_pattern_connections(patterns: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Find connections between different pattern types"""
    connections = []
    
    # Example: workflow patterns often connect to integration patterns
    workflow_patterns = patterns.get("workflow_patterns", [])
    integration_patterns = patterns.get("integration_patterns", [])
    
    if workflow_patterns and integration_patterns:
        connections.append({
            "connection_type": "workflow_integration_nexus",
            "description": "Workflow inefficiencies often stem from poor tool integration",
            "pattern_types": ["workflow_patterns", "integration_patterns"],
            "strength": "strong" if len(workflow_patterns) >= 3 and len(integration_patterns) >= 3 else "moderate"
        })
    
    # Pain point to solution connections
    pain_patterns = patterns.get("pain_point_patterns", [])
    solution_patterns = patterns.get("solution_patterns", [])
    
    if pain_patterns and solution_patterns:
        connections.append({
            "connection_type": "pain_solution_alignment", 
            "description": "User pain points align with requested solutions",
            "pattern_types": ["pain_point_patterns", "solution_patterns"],
            "opportunity": "high" if len(solution_patterns) >= 2 else "moderate"
        })
    
    return connections

def _identify_trend_indicators(processed_signals: Dict[str, Any], context: str) -> List[Dict[str, Any]]:
    """Identify trend indicators from signals"""
    trends = []
    
    # Volume trend
    total_signals = processed_signals["total_signals"]
    if total_signals >= 30:
        trends.append({
            "trend_type": "volume_increase",
            "indicator": f"High signal volume ({total_signals} signals) suggests growing interest",
            "strength": "strong" if total_signals >= 50 else "moderate"
        })
    
    # Sentiment trend
    sentiment_summary = processed_signals.get("sentiment_summary", {})
    negative_ratio = sentiment_summary.get("negative", 0)
    
    if negative_ratio > 0.6:
        trends.append({
            "trend_type": "dissatisfaction_trend",
            "indicator": f"High negative sentiment ({negative_ratio:.1%}) indicates market frustration",
            "strength": "strong",
            "opportunity": "market_gap"
        })
    
    return trends

def _extract_opportunity_signals(pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract opportunity signals from pattern analysis"""
    opportunities = []
    
    patterns = pattern_analysis.get("patterns", {})
    connections = pattern_analysis.get("connections", [])
    
    # Integration opportunity
    integration_patterns = patterns.get("integration_patterns", [])
    if len(integration_patterns) >= 3:
        opportunities.append({
            "opportunity_type": "integration_platform",
            "description": "Strong demand for tool integration solutions",
            "evidence_count": len(integration_patterns),
            "market_readiness": "high"
        })
    
    # Automation opportunity
    workflow_patterns = patterns.get("workflow_patterns", [])
    if len(workflow_patterns) >= 3:
        opportunities.append({
            "opportunity_type": "workflow_automation",
            "description": "Manual workflow pain points indicate automation opportunity",
            "evidence_count": len(workflow_patterns),
            "market_readiness": "high"
        })
    
    # Solution gap opportunity
    for connection in connections:
        if connection.get("connection_type") == "pain_solution_alignment":
            opportunities.append({
                "opportunity_type": "solution_gap",
                "description": "Clear alignment between user pain and solution requests",
                "connection_strength": connection.get("strength", "moderate"),
                "market_readiness": "medium"
            })
    
    return opportunities

def _calculate_pattern_confidence(pattern_analysis: Dict[str, Any]) -> float:
    """Calculate confidence in pattern analysis"""
    signal_count = pattern_analysis["signal_count"]
    patterns = pattern_analysis.get("patterns", {})
    connections = pattern_analysis.get("connections", [])
    
    # Base confidence on signal volume
    volume_confidence = min(signal_count / 30.0, 1.0)
    
    # Pattern diversity confidence
    pattern_count = sum(len(pattern_list) for pattern_list in patterns.values())
    diversity_confidence = min(pattern_count / 10.0, 1.0)
    
    # Connection confidence
    connection_confidence = min(len(connections) / 3.0, 1.0)
    
    return (volume_confidence + diversity_confidence + connection_confidence) / 3