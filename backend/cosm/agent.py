from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import FunctionTool
from typing import Dict, List, Any, Optional
import asyncio
from google.adk.agents.invocation_context import InvocationContext

# ----- EXPLORER AGENTS -----

def search_social_media(topic: str, platforms: List[str] = ["reddit", "twitter"]) -> Dict:
    """
    Searches social media platforms for conversations about the given topic.
    
    Args:
        topic: The market area or topic to research
        platforms: List of social media platforms to search
        
    Returns:
        Dictionary with search results and sentiment analysis
    """
    # In a real implementation, this would use APIs to search platforms
    # For demo purposes, we return simulated data
    return {
        "status": "success",
        "data": {
            "conversations_found": 120,
            "platforms_searched": platforms,
            "top_themes": [
                {"theme": "pricing frustrations", "sentiment": "negative", "frequency": 32},
                {"theme": "missing features", "sentiment": "negative", "frequency": 28},
                {"theme": "integration difficulties", "sentiment": "negative", "frequency": 25},
                {"theme": "alternative solutions", "sentiment": "neutral", "frequency": 18}
            ],
            "sample_quotes": [
                "I wish there was something between the basic and enterprise tier",
                "Nobody offers a good solution for small businesses in this space",
                "The existing tools are either too complex or too simplified"
            ]
        }
    }

def analyze_reviews(product_category: str, min_reviews: int = 100) -> Dict:
    """
    Analyzes product reviews to identify common complaints and unmet needs.
    
    Args:
        product_category: The category of products to analyze
        min_reviews: Minimum number of reviews to analyze
        
    Returns:
        Dictionary with analysis of common pain points
    """
    # In a real implementation, this would scrape reviews from sites like Amazon, G2, etc.
    return {
        "status": "success",
        "data": {
            "reviews_analyzed": 250,
            "average_rating": 3.6,
            "common_complaints": [
                {"issue": "expensive for limited features", "frequency": 42},
                {"issue": "poor integration options", "frequency": 38},
                {"issue": "steep learning curve", "frequency": 29}
            ],
            "feature_requests": [
                {"feature": "simplified interface", "frequency": 34},
                {"feature": "mid-tier pricing option", "frequency": 27},
                {"feature": "better mobile experience", "frequency": 21}
            ]
        }
    }

def search_forums(keywords: List[str]) -> Dict:
    """
    Searches forums and communities for discussions related to the keywords.
    
    Args:
        keywords: List of keywords to search for
        
    Returns:
        Dictionary with forum search results
    """
    # In a real implementation, this would search forums like Reddit, Quora, industry forums
    return {
        "status": "success",
        "data": {
            "discussions_found": 85,
            "forums_searched": ["Reddit", "Quora", "HackerNews", "Industry Forums"],
            "recurring_questions": [
                {"question": "Alternatives to [product] for small teams?", "frequency": 18},
                {"question": "How to do [task] without enterprise software?", "frequency": 15},
                {"question": "Budget-friendly options for [task]?", "frequency": 12}
            ],
            "community_sentiment": {
                "frustration_level": "high",
                "price_sensitivity": "high",
                "willingness_to_try_alternatives": "very high"
            }
        }
    }

def analyze_search_trends(topic: str, time_period: str = "6 months") -> Dict:
    """
    Analyzes search trends related to the topic.
    
    Args:
        topic: The topic or market area to research
        time_period: The time period to analyze
        
    Returns:
        Dictionary with search trend analysis
    """
    # In a real implementation, this would use Google Trends API or similar
    return {
        "status": "success",
        "data": {
            "search_volume_change": "+18%",
            "related_rising_searches": [
                {"term": f"alternatives to {topic}", "growth": "+32%"},
                {"term": f"cheaper {topic} options", "growth": "+24%"},
                {"term": f"{topic} for small business", "growth": "+21%"}
            ],
            "geographic_hotspots": ["San Francisco", "New York", "London", "Berlin"],
            "seasonal_patterns": "Increasing interest in Q1 and Q3"
        }
    }

# Create explorer agent tools
social_media_tool = FunctionTool(func=search_social_media)
reviews_tool = FunctionTool(func=analyze_reviews)
forums_tool = FunctionTool(func=search_forums)
trends_tool = FunctionTool(func=analyze_search_trends)

# Create Explorer Agents
social_media_explorer = LlmAgent(
    name="SocialMediaExplorer",
    model="gemini-2.0-flash",
    description="Analyzes social media conversations to find patterns of user frustration and unmet needs",
    instruction=(
        "You explore social media platforms to identify patterns of frustration and unmet needs in specific market categories. "
        "Use the search_social_media tool to gather data, then analyze the results to identify recurring themes of user frustration, "
        "gaps in existing solutions, and potential opportunities in the spaces between established categories. "
        "Focus on finding signals of liminal market opportunities - places where users are frustrated because existing solutions "
        "fall into categories that don't quite meet their needs."
    ),
    tools=[social_media_tool],
    output_key="social_media_insights"
)

reviews_explorer = LlmAgent(
    name="ReviewsExplorer",
    model="gemini-2.0-flash",
    description="Analyzes product reviews to find common complaints and feature requests",
    instruction=(
        "You analyze product reviews to identify patterns of user frustration and feature requests. "
        "Use the analyze_reviews tool to gather data, then analyze the results to identify recurring complaints, "
        "missing features, and potential opportunities to create solutions that address unmet needs. "
        "Focus particularly on identifying opportunities that exist between established product categories, "
        "where users are expressing frustration because existing solutions don't quite fit their needs."
    ),
    tools=[reviews_tool],
    output_key="review_insights"
)

forums_explorer = LlmAgent(
    name="ForumsExplorer",
    model="gemini-2.0-flash",
    description="Searches forums and communities for discussions about problems and solutions",
    instruction=(
        "You explore forums and online communities to find discussions about problems and potential solutions. "
        "Use the search_forums tool to gather data, then analyze the results to identify recurring questions, "
        "common frustrations, and potential opportunities to create solutions that address unmet needs. "
        "Look specifically for signals indicating gaps between established categories where users are struggling to find solutions."
    ),
    tools=[forums_tool],
    output_key="forum_insights"
)

trends_explorer = LlmAgent(
    name="TrendsExplorer",
    model="gemini-2.0-flash",
    description="Analyzes search trends to identify growing interest in specific topics",
    instruction=(
        "You analyze search trends to identify growing interest in specific topics and related searches. "
        "Use the analyze_search_trends tool to gather data, then interpret the results to identify "
        "emerging patterns, growing interest areas, and potential opportunities for new solutions. "
        "Focus on finding signals that indicate growing dissatisfaction with existing categories and "
        "interest in alternatives or solutions that might exist between established categories."
    ),
    tools=[trends_tool],
    output_key="trends_insights"
)

# ----- CARTOGRAPHER AGENTS -----

def map_opportunity_space(exploration_data: Dict) -> Dict:
    """
    Maps the opportunity space based on exploration data.
    
    Args:
        exploration_data: Data collected from explorers
        
    Returns:
        Dictionary with mapped opportunity space
    """
    # In a real implementation, this would use ML to analyze patterns
    return {
        "status": "success",
        "data": {
            "identified_gaps": [
                {
                    "gap_name": "Mid-market solution gap",
                    "description": "Gap between enterprise and consumer solutions",
                    "pain_points": ["pricing", "feature complexity", "implementation time"],
                    "potential_opportunity_score": 8.2
                },
                {
                    "gap_name": "Integration solution gap",
                    "description": "Gap between all-in-one platforms and single-purpose tools",
                    "pain_points": ["data silos", "workflow friction", "learning multiple systems"],
                    "potential_opportunity_score": 7.5
                }
            ],
            "market_quadrants": {
                "overcrowded": ["enterprise all-in-one", "basic free tools"],
                "underserved": ["mid-market specialized", "prosumer integrations"]
            }
        }
    }

def validate_opportunity(opportunity: Dict, market_size: str) -> Dict:
    """
    Validates an identified market opportunity.
    
    Args:
        opportunity: The opportunity to validate
        market_size: Estimated size of the market
        
    Returns:
        Dictionary with validation results
    """
    # In a real implementation, this would use market data and predictive models
    return {
        "status": "success",
        "data": {
            "validation_score": 76,
            "estimated_market_size": market_size,
            "competitive_landscape": {
                "direct_competitors": 3,
                "adjacent_solutions": 8,
                "barriers_to_entry": "moderate"
            },
            "recommended_positioning": "Simplified mid-market solution with key enterprise features",
            "potential_revenue_models": [
                "subscription with tiered pricing",
                "usage-based pricing",
                "freemium with paid integrations"
            ]
        }
    }

# Create cartographer agent tools
map_opportunity_tool = FunctionTool(func=map_opportunity_space)
validate_opportunity_tool = FunctionTool(func=validate_opportunity)

# Create Cartographer Agents
opportunity_mapper = LlmAgent(
    name="OpportunityMapper",
    model="gemini-2.0-flash",
    description="Maps connections between data points to identify viable opportunities in market gaps",
    instruction=(
        "You analyze data collected by explorer agents to map out potential market opportunities. "
        "Your primary job is to identify patterns across different data sources that indicate gaps "
        "between established market categories where valuable opportunities might exist. "
        "Use the map_opportunity_space tool to process exploration data, then analyze the results to "
        "identify the most promising liminal markets - those fertile spaces between established categories. "
        "Draw connections between seemingly disparate data points to reveal hidden opportunities."
    ),
    tools=[map_opportunity_tool],
    output_key="opportunity_map"
)

opportunity_validator = LlmAgent(
    name="OpportunityValidator",
    model="gemini-2.0-flash",
    description="Validates identified opportunities against market criteria",
    instruction=(
        "You evaluate identified market opportunities against key validation criteria. "
        "Your job is to assess the viability, market size, competitive landscape, and potential positioning "
        "for opportunities identified in the gaps between established markets. "
        "Use the validate_opportunity tool to process opportunity data, then analyze the results to provide "
        "a clear assessment of which opportunities are most worth pursuing and why. "
        "Focus on identifying opportunities with the highest potential in liminal market spaces."
    ),
    tools=[validate_opportunity_tool],
    output_key="validated_opportunities"
)

# ----- BUILDER AGENTS -----

def generate_business_canvas(opportunity: Dict) -> Dict:
    """
    Generates a business model canvas for the opportunity.
    
    Args:
        opportunity: The validated opportunity
        
    Returns:
        Dictionary with business model canvas
    """
    # In a real implementation, this would use GPT to generate a custom canvas
    return {
        "status": "success",
        "data": {
            "value_proposition": "Simplified mid-market solution with enterprise-grade capabilities at accessible price points",
            "customer_segments": ["Small to mid-sized businesses", "Teams within larger enterprises", "Prosumer power users"],
            "revenue_streams": ["Tiered subscription model", "Add-on services", "API access fees"],
            "key_resources": ["AI-driven automation", "Integration capabilities", "Simplified interface"],
            "customer_relationships": ["Self-service with support tiers", "Community-driven knowledge base"],
            "channels": ["Direct online", "Partnership integrations", "Limited sales team for larger clients"],
            "key_activities": ["Product development", "Customer success", "Integration partnerships"],
            "key_partners": ["Technology platforms", "Complementary service providers", "Industry influencers"],
            "cost_structure": ["Development team", "Cloud infrastructure", "Marketing", "Customer support"]
        }
    }

def create_brand_identity(business_name: str, industry: str) -> Dict:
    """
    Creates a brand identity for the business.
    
    Args:
        business_name: Name of the business
        industry: Industry sector
        
    Returns:
        Dictionary with brand identity elements
    """
    # In a real implementation, this would use AI to generate brand assets
    return {
        "status": "success",
        "data": {
            "brand_story": f"{business_name} was founded to bridge the gap between overly complex enterprise solutions and simplistic consumer tools.",
            "brand_values": ["Simplicity", "Power", "Accessibility", "Efficiency"],
            "voice_and_tone": "Professional yet approachable, expert but not condescending",
            "visual_identity": {
                "color_palette": ["#3A86FF", "#8338EC", "#FF006E", "#FB5607"],
                "typography": {
                    "headings": "Montserrat",
                    "body": "Open Sans"
                },
                "logo_concept": "A bridge symbol connecting two landmasses, representing the connection between existing market categories"
            }
        }
    }

def generate_landing_page(brand_identity: Dict, business_canvas: Dict) -> Dict:
    """
    Generates a landing page for the business.
    
    Args:
        brand_identity: Brand identity information
        business_canvas: Business model canvas
        
    Returns:
        Dictionary with landing page content
    """
    # In a real implementation, this would use AI to generate actual HTML/CSS
    return {
        "status": "success",
        "data": {
            "headline": "Bridge the Gap Between Enterprise Power and Consumer Simplicity",
            "subheadline": "The solution that fits perfectly in your workflow—not too complex, not too simple",
            "value_propositions": [
                "Enterprise features without enterprise complexity",
                "Pricing that scales with your business",
                "Implementation in days, not months"
            ],
            "call_to_action": "Start Your Free Trial",
            "key_sections": [
                "Problem Statement",
                "Solution Overview",
                "Feature Highlights",
                "Pricing Tiers",
                "Customer Testimonials",
                "Getting Started Guide"
            ],
            "layout_structure": "Hero > Problem > Solution > Features > Pricing > Testimonials > CTA",
            "recommended_assets": [
                "Product screenshots",
                "Comparison table",
                "Implementation timeline",
                "ROI calculator"
            ]
        }
    }

# Create builder agent tools
business_canvas_tool = FunctionTool(func=generate_business_canvas)
brand_identity_tool = FunctionTool(func=create_brand_identity)
landing_page_tool = FunctionTool(func=generate_landing_page)

# Create Builder Agents
business_canvas_builder = LlmAgent(
    name="BusinessCanvasBuilder",
    model="gemini-2.0-flash",
    description="Creates a comprehensive business model canvas for identified opportunities",
    instruction=(
        "You create comprehensive business model canvases for validated market opportunities. "
        "Your role is to define the key components of a viable business that can address the opportunity "
        "in the liminal space between established market categories. "
        "Use the generate_business_canvas tool to create a detailed canvas, then analyze the results to "
        "provide strategic recommendations for positioning, pricing, and go-to-market strategy. "
        "Focus on creating business models that effectively bridge the gap between existing categories."
    ),
    tools=[business_canvas_tool],
    output_key="business_canvas"
)

brand_identity_builder = LlmAgent(
    name="BrandIdentityBuilder",
    model="gemini-2.0-flash",
    description="Creates brand identities for new business opportunities",
    instruction=(
        "You create compelling brand identities for businesses targeting opportunities in liminal market spaces. "
        "Your job is to define brand elements that effectively communicate the unique value proposition "
        "of a solution that bridges the gap between established categories. "
        "Use the create_brand_identity tool to generate brand identity components, then analyze the results to "
        "provide strategic recommendations for brand positioning and communication. "
        "Focus on creating brands that clearly communicate the value of inhabiting the space between categories."
    ),
    tools=[brand_identity_tool],
    output_key="brand_identity"
)

landing_page_builder = LlmAgent(
    name="LandingPageBuilder",
    model="gemini-2.0-flash",
    description="Creates landing pages for validating business concepts",
    instruction=(
        "You create effective landing pages for businesses targeting opportunities in liminal market spaces. "
        "Your job is to design landing pages that clearly communicate the unique value proposition "
        "of a solution that bridges the gap between established categories. "
        "Use the generate_landing_page tool to create landing page content, then analyze the results to "
        "provide strategic recommendations for messaging, layout, and conversion optimization. "
        "Focus on creating landing pages that effectively validate demand for solutions in between-category spaces."
    ),
    tools=[landing_page_tool],
    output_key="landing_page"
)

# ----- WORKFLOW ORCHESTRATION -----

# Create Explorer Group as a ParallelAgent
explorers = ParallelAgent(
    name="ExplorerTeam",
    description="Team of explorer agents that gather market signals from different sources",
    sub_agents=[social_media_explorer, reviews_explorer, forums_explorer, trends_explorer]
)

# Create Cartographer Group as a SequentialAgent
cartographers = SequentialAgent(
    name="CartographerTeam",
    description="Team of cartographer agents that map and validate opportunities",
    sub_agents=[opportunity_mapper, opportunity_validator]
)

# Create Builder Group as a SequentialAgent
builders = SequentialAgent(
    name="BuilderTeam",
    description="Team of builder agents that create business assets",
    sub_agents=[business_canvas_builder, brand_identity_builder, landing_page_builder]
)

# Create the main workflow as a SequentialAgent
liminal_market_navigator = SequentialAgent(
    name="LiminalMarketNavigator",
    description="Orchestrates the exploration, mapping, and building of liminal market opportunities",
    sub_agents=[explorers, cartographers, builders]
)

# Create the main agentcosm agent
root_agent = Agent(
    name="agentcosm",
    model="gemini-2.0-flash",
    description="AI-powered navigator of market liminal spaces that helps entrepreneurs discover and validate opportunities",
    instruction=(
        "You are agentcosm, an AI-powered navigator of market liminal spaces. Your purpose is to help entrepreneurs "
        "discover and validate opportunities that exist in the fertile void between established market categories. "
        "\n\n"
        "Your process works in three phases:\n"
        "1. EXPLORE: Deploy explorer agents to collect signals from social media, reviews, forums, and search trends.\n"
        "2. MAP: Use cartographer agents to identify patterns and validate opportunities in liminal spaces.\n"
        "3. BUILD: Use builder agents to create business assets needed to validate the opportunity.\n"
        "\n\n"
        "When working with entrepreneurs:\n"
        "- Help them articulate the market area they want to explore\n"
        "- Guide them through the process of discovering opportunities in liminal spaces\n"
        "- Help them evaluate and prioritize the opportunities discovered\n"
        "- Support them in creating assets to quickly validate the most promising opportunities\n"
        "\n\n"
        "Always focus on finding opportunities in the spaces between established categories - "
        "the liminal zones where transformative business potential exists."
    ),
    sub_agents=[liminal_market_navigator]
)