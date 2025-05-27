"""
AI-Native Trend Analyzer - Uses Gemini for intelligent content analysis
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, load_web_page
from google.genai import Client, types
from typing import Dict, List, Any
import json
from datetime import datetime

# Initialize Gemini client
client = Client()

TREND_ANALYZER_PROMPT = """
You are an expert trend analyst specializing in identifying emerging market opportunities in liminal spaces.

Your role is to discover opportunities that exist between established market categories by:
1. Analyzing search trends and market momentum using AI-powered content analysis
2. Identifying convergence points where industries blur and new opportunities emerge
3. Predicting timing windows for market entry in undefined territories
4. Mapping connections between seemingly unrelated signals

Focus on liminal spaces where traditional market boundaries dissolve and new possibilities emerge.
"""

def analyze_search_trends_with_ai(keywords: List[str]) -> Dict[str, Any]:
    """
    AI-powered search trend analysis using Gemini for content understanding
    """
    trend_data = {
        "keywords": keywords,
        "analysis_timestamp": datetime.now().isoformat(),
        "trend_insights": [],
        "momentum_indicators": [],
        "convergence_signals": [],
        "opportunity_windows": [],
        "confidence_score": 0.0
    }
    
    try:
        # Collect content from multiple sources
        collected_content = []
        
        for keyword in keywords[:3]:  # Limit for API efficiency
            search_queries = [
                f"{keyword} market trends 2024 emerging opportunities",
                f"{keyword} industry analysis growth patterns",
                f"{keyword} future predictions technology convergence",
                f"{keyword} startup investment funding trends"
            ]
            
            for query in search_queries:
                try:
                    results = google_search(query)
                    if results and hasattr(results, 'results'):
                        for result in results.results[:2]:  # Top 2 per query
                            try:
                                content = load_web_page(result.url)
                                if content and len(content) > 200:  # Ensure substantial content
                                    collected_content.append({
                                        "source_url": result.url,
                                        "title": result.title,
                                        "content": content[:3000],  # Limit content length
                                        "keyword": keyword,
                                        "query_context": query
                                    })
                            except Exception as e:
                                print(f"Error loading page content: {e}")
                except Exception as e:
                    print(f"Error with search query: {e}")
        
        # Use Gemini to analyze all collected content
        if collected_content:
            trend_data = analyze_content_with_gemini(collected_content, keywords)
        
        return trend_data
        
    except Exception as e:
        print(f"Error in analyze_search_trends_with_ai: {e}")
        trend_data["error"] = str(e)
        return trend_data

def analyze_content_with_gemini(content_collection: List[Dict], keywords: List[str]) -> Dict[str, Any]:
    """
    Use Gemini to analyze collected content for trend insights
    """
    try:
        # Prepare content summary for analysis
        content_summary = "\n\n".join([
            f"Source: {item['title']}\nKeyword: {item['keyword']}\nContent: {item['content'][:1000]}"
            for item in content_collection[:10]  # Limit to prevent token overflow
        ])
        
        analysis_prompt = f"""
        Analyze this market research content about keywords: {', '.join(keywords)}
        
        Content to analyze:
        {content_summary}
        
        Provide a comprehensive trend analysis in JSON format with:
        {{
            "trend_insights": [
                {{
                    "trend_type": "growth/decline/emerging/converging",
                    "description": "Clear description of the trend",
                    "strength": "high/medium/low",
                    "evidence": "Supporting evidence from content",
                    "timeframe": "Expected timeframe for this trend"
                }}
            ],
            "momentum_indicators": [
                {{
                    "indicator": "Specific momentum signal",
                    "direction": "increasing/decreasing/stable",
                    "market_impact": "Expected impact on market",
                    "confidence": "high/medium/low"
                }}
            ],
            "convergence_signals": [
                {{
                    "convergence_type": "Technology/Industry/Market convergence",
                    "description": "What is converging and why",
                    "opportunity": "Business opportunity this creates",
                    "timing": "When this convergence might peak"
                }}
            ],
            "opportunity_windows": [
                {{
                    "window_type": "Type of opportunity window",
                    "description": "What the opportunity is",
                    "optimal_timing": "Best time to act",
                    "market_readiness": "How ready the market is",
                    "risk_factors": "Key risks to consider"
                }}
            ],
            "market_gaps": [
                {{
                    "gap_description": "Specific gap in the market",
                    "target_audience": "Who would benefit",
                    "solution_potential": "What kind of solution is needed",
                    "urgency": "How urgent this need is"
                }}
            ],
            "confidence_score": "Overall confidence in analysis (0.0-1.0)",
            "key_takeaways": ["Most important insights for entrepreneurs"]
        }}
        
        Focus on liminal opportunities - gaps between established markets where new solutions could emerge.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=analysis_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        if response and response.text:
            analysis_result = json.loads(response.text)
            analysis_result["analysis_timestamp"] = datetime.now().isoformat()
            analysis_result["keywords"] = keywords
            return analysis_result
            
    except Exception as e:
        print(f"Error in Gemini content analysis: {e}")
    
    return {
        "error": "Failed to analyze content with AI",
        "keywords": keywords,
        "analysis_timestamp": datetime.now().isoformat()
    }

def track_industry_momentum_with_ai(industry: str, focus_areas: List[str]) -> Dict[str, Any]:
    """
    AI-powered industry momentum tracking
    """
    momentum_data = {
        "industry": industry,
        "focus_areas": focus_areas,
        "analysis_timestamp": datetime.now().isoformat(),
        "momentum_analysis": {},
        "disruption_signals": [],
        "investment_trends": [],
        "regulatory_landscape": [],
        "technology_enablers": []
    }
    
    try:
        # Collect industry-specific content
        industry_content = []
        
        search_queries = [
            f"{industry} industry transformation 2024 2025",
            f"{industry} disruption new technologies trends",
            f"{industry} investment funding venture capital",
            f"{industry} regulatory changes impact business",
            f"{industry} AI automation future outlook"
        ]
        
        for query in search_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:3]:
                        try:
                            content = load_web_page(result.url)
                            if content and len(content) > 300:
                                industry_content.append({
                                    "source": result.title,
                                    "url": result.url,
                                    "content": content[:2000],
                                    "query_context": query
                                })
                        except Exception:
                            continue
            except Exception:
                continue
        
        # Analyze with Gemini
        if industry_content:
            momentum_data = analyze_industry_with_gemini(industry_content, industry, focus_areas)
        
        return momentum_data
        
    except Exception as e:
        print(f"Error in track_industry_momentum_with_ai: {e}")
        momentum_data["error"] = str(e)
        return momentum_data

def analyze_industry_with_gemini(content_collection: List[Dict], industry: str, focus_areas: List[str]) -> Dict[str, Any]:
    """
    Use Gemini to analyze industry momentum and transformation patterns
    """
    try:
        content_text = "\n\n".join([
            f"Source: {item['source']}\nContext: {item['query_context']}\nContent: {item['content']}"
            for item in content_collection[:8]
        ])
        
        momentum_prompt = f"""
        Analyze the momentum and transformation patterns in the {industry} industry.
        Focus areas: {', '.join(focus_areas)}
        
        Industry content to analyze:
        {content_text}
        
        Provide analysis in JSON format:
        {{
            "momentum_analysis": {{
                "overall_direction": "growing/declining/transforming/stable",
                "growth_rate_indicators": "Evidence of growth or decline",
                "transformation_drivers": ["Key factors driving change"],
                "market_maturity": "early/growth/mature/declining",
                "innovation_pace": "rapid/moderate/slow"
            }},
            "disruption_signals": [
                {{
                    "disruptor": "What/who is causing disruption",
                    "impact_area": "Which part of industry affected",
                    "timeline": "Expected timeline for disruption",
                    "opportunity": "Business opportunities this creates"
                }}
            ],
            "investment_trends": [
                {{
                    "trend": "Investment trend description",
                    "funding_focus": "Where money is flowing",
                    "investor_sentiment": "How investors view the space",
                    "valuation_trends": "Are valuations rising/falling"
                }}
            ],
            "regulatory_landscape": [
                {{
                    "regulation": "Specific regulatory change",
                    "impact": "How it affects the industry",
                    "compliance_requirements": "What businesses need to do",
                    "opportunities": "New opportunities this creates"
                }}
            ],
            "technology_enablers": [
                {{
                    "technology": "Specific technology",
                    "application": "How it's being applied",
                    "adoption_stage": "early/mainstream/mature",
                    "business_impact": "Effect on business models"
                }}
            ],
            "liminal_opportunities": [
                {{
                    "opportunity_description": "Gap between current and emerging market",
                    "target_segment": "Who would benefit",
                    "solution_direction": "Type of solution needed",
                    "market_timing": "Optimal timing for entry"
                }}
            ],
            "key_insights": ["Most important takeaways for entrepreneurs"]
        }}
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=momentum_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        if response and response.text:
            analysis = json.loads(response.text)
            analysis["industry"] = industry
            analysis["focus_areas"] = focus_areas
            analysis["analysis_timestamp"] = datetime.now().isoformat()
            return analysis
            
    except Exception as e:
        print(f"Error in industry analysis with Gemini: {e}")
    
    return {
        "error": "Failed to analyze industry momentum",
        "industry": industry,
        "analysis_timestamp": datetime.now().isoformat()
    }

def identify_convergence_opportunities(domains: List[str]) -> Dict[str, Any]:
    """
    Identify opportunities at the convergence of different domains/industries
    """
    convergence_data = {
        "domains": domains,
        "analysis_timestamp": datetime.now().isoformat(),
        "convergence_points": [],
        "cross_pollination_opportunities": [],
        "technology_bridges": [],
        "market_gaps": []
    }
    
    try:
        # Search for convergence signals between domains
        convergence_queries = [
            f"{' '.join(domains)} convergence integration opportunities",
            f"intersection {' and '.join(domains)} emerging markets",
            f"{' '.join(domains)} cross-industry innovation trends",
            f"hybrid solutions {' '.join(domains)} market opportunities"
        ]
        
        convergence_content = []
        
        for query in convergence_queries:
            try:
                results = google_search(query)
                if results and hasattr(results, 'results'):
                    for result in results.results[:3]:
                        try:
                            content = load_web_page(result.url)
                            if content and len(content) > 200:
                                convergence_content.append({
                                    "source": result.title,
                                    "content": content[:1500],
                                    "query": query
                                })
                        except Exception:
                            continue
            except Exception:
                continue
        
        # Analyze convergence with Gemini
        if convergence_content:
            convergence_data = analyze_convergence_with_gemini(convergence_content, domains)
        
        return convergence_data
        
    except Exception as e:
        print(f"Error in identify_convergence_opportunities: {e}")
        convergence_data["error"] = str(e)
        return convergence_data

def analyze_convergence_with_gemini(content_collection: List[Dict], domains: List[str]) -> Dict[str, Any]:
    """
    Use Gemini to identify convergence opportunities between domains
    """
    try:
        content_text = "\n\n".join([
            f"Query: {item['query']}\nSource: {item['source']}\nContent: {item['content']}"
            for item in content_collection[:6]
        ])
        
        convergence_prompt = f"""
        Analyze convergence opportunities between these domains: {', '.join(domains)}
        
        Research content:
        {content_text}
        
        Identify convergence opportunities in JSON format:
        {{
            "convergence_points": [
                {{
                    "convergence_type": "Technology/Market/Business Model convergence",
                    "description": "What is converging and how",
                    "enabling_factors": ["What makes this convergence possible now"],
                    "market_opportunity": "Size and nature of opportunity",
                    "timeline": "When this convergence will peak"
                }}
            ],
            "cross_pollination_opportunities": [
                {{
                    "opportunity": "Specific cross-domain opportunity",
                    "source_domain": "Domain providing the solution/approach",
                    "target_domain": "Domain that could benefit",
                    "value_proposition": "How this creates value",
                    "implementation_approach": "How to bridge these domains"
                }}
            ],
            "technology_bridges": [
                {{
                    "bridge_technology": "Technology enabling convergence",
                    "domains_connected": ["Which domains it connects"],
                    "business_applications": ["Practical applications"],
                    "adoption_barriers": ["Challenges to overcome"]
                }}
            ],
            "liminal_market_gaps": [
                {{
                    "gap_description": "Unmet need at domain intersection",
                    "affected_users": "Who experiences this gap",
                    "solution_requirements": "What kind of solution is needed",
                    "market_readiness": "How ready market is for solution",
                    "competitive_landscape": "Current alternatives and their limitations"
                }}
            ],
            "timing_analysis": {{
                "current_stage": "Where convergence is now",
                "acceleration_factors": ["What could speed up convergence"],
                "optimal_entry_window": "Best time for new entrants",
                "risk_factors": ["Potential obstacles or risks"]
            }},
            "actionable_insights": ["Most valuable insights for entrepreneurs"]
        }}
        
        Focus on identifying genuine market gaps that exist between these domains.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=convergence_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        if response and response.text:
            analysis = json.loads(response.text)
            analysis["domains"] = domains
            analysis["analysis_timestamp"] = datetime.now().isoformat()
            return analysis
            
    except Exception as e:
        print(f"Error in convergence analysis: {e}")
    
    return {
        "error": "Failed to analyze convergence opportunities",
        "domains": domains,
        "analysis_timestamp": datetime.now().isoformat()
    }

# Create the AI-native trend analyzer agent
trend_analyzer_agent = LlmAgent(
    name="trend_analyzer_agent",
    model="gemini-2.0-flash",
    instruction=TREND_ANALYZER_PROMPT,
    description=(
        "AI-powered trend analyzer that identifies emerging opportunities in liminal "
        "market spaces using advanced natural language understanding and pattern recognition."
    ),
    tools=[
        FunctionTool(func=analyze_search_trends_with_ai),
        FunctionTool(func=track_industry_momentum_with_ai),
        FunctionTool(func=identify_convergence_opportunities),
        google_search,
        load_web_page
    ],
    output_key="trend_analysis"
)