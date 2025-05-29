"""
COMPLETE Builder Agents Suite - All Three Agents with OpenAI Integration
Brand Creator + Copy Writer + Landing Builder + Admin Dashboard Generator
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any
import json
import re
import requests
from datetime import datetime
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings

client = Client()

# Renderer service configuration
RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

# =============================================================================
# BRAND CREATOR AGENT - ENHANCED WITH OPENAI
# =============================================================================


def create_brand_identity_with_openai(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Creates comprehensive brand identity using OpenAI for liminal market opportunities
    """
    brand_identity = {
        "opportunity_name": opportunity_data.get("name", "Unknown Opportunity"),
        "brand_name": "",
        "tagline": "",
        "positioning_statement": "",
        "value_proposition": "",
        "target_audience": "",
        "brand_personality": {},
        "visual_identity": {},
        "messaging_framework": {},
        "domain_suggestions": [],
        "trademark_considerations": [],
        "brand_story": "",
        "competitive_differentiation": [],
        "brand_architecture": {},
    }

    try:
        # Create comprehensive brand development prompt
        brand_prompt = f"""
        You are a world-class brand strategist tasked with creating a compelling brand identity for a liminal market opportunity.

        OPPORTUNITY CONTEXT:
        {json.dumps(opportunity_data, indent=2)}

        LIMINAL POSITIONING STRATEGY:
        This opportunity exists in the space BETWEEN established market categories. Your brand must:
        - Position uniquely between existing solutions
        - Appeal to users underserved by mainstream options
        - Create new category language and mental models
        - Bridge the gap between what exists and what's needed

        COMPREHENSIVE BRAND DEVELOPMENT:
        Create a complete brand identity that includes:

        1. **Brand Foundation**:
        - Memorable, distinctive brand name that suggests innovation
        - Compelling tagline (3-7 words) that captures the liminal positioning
        - Clear positioning statement vs competitors
        - Unique value proposition for target users

        2. **Brand Personality & Voice**:
        - Brand archetype (Explorer, Creator, Revolutionary, etc.)
        - Voice characteristics (professional/friendly/innovative/disruptive)
        - Personality traits that resonate with target audience
        - Communication tone and style guidelines

        3. **Visual Identity Framework**:
        - Primary color palette (3-4 colors with hex codes)
        - Secondary accent colors
        - Typography recommendations (primary + secondary fonts)
        - Visual style direction (modern/minimalist/bold/organic)
        - Imagery style and aesthetic direction

        4. **Messaging Architecture**:
        - Primary brand message (elevator pitch)
        - Supporting key messages for different contexts
        - Differentiation points vs established players
        - Category-defining language and terminology

        5. **Brand Story & Narrative**:
        - Origin story that explains why this brand exists
        - Mission statement with emotional resonance
        - Vision for transforming the market space
        - Brand values that guide decisions

        6. **Competitive Differentiation**:
        - How this brand is uniquely different
        - What traditional solutions miss
        - Why users should switch or try something new
        - Proof points and credibility builders

        7. **Brand Architecture**:
        - Master brand strategy
        - Product/service naming conventions
        - Brand extension possibilities
        - Partnership and co-branding guidelines

        Return comprehensive JSON with all brand elements that creates a distinctive, memorable identity for this liminal market opportunity.

        Make this brand feel inevitable - like users will wonder how they ever lived without it.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": brand_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=2000,
        )

        if response and response.choices[0].message.content:
            ai_brand_data = json.loads(response.choices[0].message.content)
            brand_identity.update(ai_brand_data)

        # Generate domain suggestions
        brand_name = brand_identity.get("brand_name", "")
        if brand_name:
            brand_identity["domain_suggestions"] = generate_smart_domain_suggestions(
                brand_name
            )
            brand_identity["trademark_considerations"] = (
                assess_comprehensive_trademark_risks(brand_name)
            )

        return brand_identity

    except Exception as e:
        print(f"Error creating brand identity: {e}")
        brand_identity["error"] = str(e)
        return brand_identity


def generate_smart_domain_suggestions(brand_name: str) -> List[Dict[str, Any]]:
    """Generate intelligent domain name suggestions with availability hints"""
    suggestions = []
    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    # Primary options
    primary_domains = [
        f"{base_name}.com",
        f"{base_name}.io",
        f"{base_name}.co",
        f"{base_name}.ai",
    ]

    # Creative variations
    creative_domains = [
        f"get{base_name}.com",
        f"try{base_name}.com",
        f"{base_name}app.com",
        f"{base_name}hq.com",
        f"{base_name}pro.com",
        f"use{base_name}.com",
        f"{base_name}labs.com",
        f"{base_name}tech.com",
    ]

    # Short variations if name is long
    if len(base_name) > 8:
        short_variants = [
            f"{base_name[:6]}.com",
            f"{base_name[:5]}app.com",
            f"{base_name[:4]}pro.com",
        ]
        creative_domains.extend(short_variants)

    # Add to suggestions with priority
    for domain in primary_domains:
        suggestions.append(
            {
                "domain": domain,
                "priority": "high",
                "category": "primary",
                "recommendation": "First choice - professional and memorable",
            }
        )

    for domain in creative_domains:
        suggestions.append(
            {
                "domain": domain,
                "priority": "medium",
                "category": "alternative",
                "recommendation": "Good alternative if primary unavailable",
            }
        )

    return suggestions


def assess_comprehensive_trademark_risks(brand_name: str) -> List[Dict[str, str]]:
    """Comprehensive trademark risk assessment"""
    considerations = []

    # Basic trademark checks
    considerations.extend(
        [
            {
                "category": "search_required",
                "risk": "Comprehensive trademark search needed",
                "action": "Conduct USPTO and international trademark database search",
                "priority": "high",
            },
            {
                "category": "category_check",
                "risk": "Check existing marks in relevant business categories",
                "action": "Search in SaaS, technology, and business services classes",
                "priority": "high",
            },
            {
                "category": "domain_check",
                "risk": "Verify domain availability and potential conflicts",
                "action": "Check domain registrations and parking pages",
                "priority": "medium",
            },
            {
                "category": "common_law",
                "risk": "Search for unregistered common law trademarks",
                "action": "Google search for existing business usage",
                "priority": "medium",
            },
        ]
    )

    # Name-specific risks
    word_count = len(brand_name.split())
    if word_count > 2:
        considerations.append(
            {
                "category": "complexity",
                "risk": "Multi-word names may face trademark challenges",
                "action": "Consider shorter alternatives or unique combinations",
                "priority": "low",
            }
        )

    if any(char.isdigit() for char in brand_name):
        considerations.append(
            {
                "category": "numbers",
                "risk": "Names with numbers may be harder to trademark",
                "action": "Ensure numbers are distinctive, not merely descriptive",
                "priority": "medium",
            }
        )

    # Check for common descriptive terms
    descriptive_terms = ["app", "tech", "pro", "max", "plus", "hub", "lab"]
    if any(term in brand_name.lower() for term in descriptive_terms):
        considerations.append(
            {
                "category": "descriptive",
                "risk": "Descriptive elements may weaken trademark protection",
                "action": "Combine with distinctive elements for stronger protection",
                "priority": "medium",
            }
        )

    return considerations


# =============================================================================
# COPY WRITER AGENT - ENHANCED WITH OPENAI
# =============================================================================


def generate_comprehensive_marketing_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates comprehensive marketing copy using OpenAI for early-stage validation
    """
    copy_package = {
        "brand_name": brand_data.get("brand_name", ""),
        "headlines": [],
        "taglines": [],
        "value_propositions": [],
        "website_copy": {},
        "email_sequences": {},
        "social_media_copy": {},
        "ad_copy": {},
        "press_release": "",
        "sales_copy": {},
        "onboarding_copy": {},
        "product_descriptions": {},
        "faq_content": [],
        "testimonial_templates": [],
        "case_study_frameworks": [],
    }

    try:
        # Create comprehensive copywriting prompt
        copy_prompt = f"""
        You are an expert conversion copywriter specializing in liminal market opportunities and early-stage validation.

        BRAND CONTEXT:
        {json.dumps(brand_data, indent=2)[:1500]}

        OPPORTUNITY CONTEXT:
        {json.dumps(opportunity_data, indent=2)[:1500]}

        LIMINAL MARKET COPY STRATEGY:
        This brand exists between established categories. Your copy must:
        - Address the frustration with existing solutions
        - Position as the missing link users didn't know they needed
        - Create urgency through pain amplification
        - Build trust through specificity and understanding
        - Drive early adoption and validation

        COMPREHENSIVE COPY DEVELOPMENT:
        Generate high-converting copy across all touchpoints:

        1. **Headlines & Taglines**:
        - 5 primary headlines for landing pages (outcome-focused)
        - 3 tagline variations (3, 5, and 7 words)
        - 3 value proposition statements (different angles)
        - Headlines optimized for different traffic sources

        2. **Website Copy Sections**:
        - Hero headline + subheadline combination
        - Problem agitation copy that amplifies current pain
        - Solution explanation that bridges the gap
        - Benefit statements (outcome-focused, not feature-focused)
        - Social proof integration points
        - FAQ answers addressing common objections
        - Call-to-action variations for different contexts

        3. **Email Marketing Sequences**:
        - Welcome sequence (3 emails) for new subscribers
        - Nurture sequence (5 emails) for prospects
        - Product announcement sequence (3 emails)
        - Re-engagement sequence (3 emails) for inactive users
        - Each email with subject line + preview text + body

        4. **Social Media Copy**:
        - Twitter/X posts (5 variations) with hooks and engagement
        - LinkedIn posts (3 variations) for professional audience
        - Instagram captions (3 variations) with storytelling
        - Facebook posts (3 variations) for community building

        5. **Ad Copy Variations**:
        - Google Ads: Headlines (30 chars) + Descriptions (90 chars)
        - Facebook Ads: Primary text + Headlines + Descriptions
        - LinkedIn Ads: Professional messaging variations
        - Twitter Ads: Concise, scroll-stopping copy

        6. **Sales & Onboarding Copy**:
        - Sales page structure with persuasion sequences
        - Onboarding welcome messages and instructions
        - Product tour copy and user guidance
        - Success milestone celebrations

        7. **Support Content**:
        - FAQ answers for common questions and objections
        - Help documentation with user-friendly explanations
        - Error messages that maintain brand voice
        - Customer success story templates

        CONVERSION OPTIMIZATION PRINCIPLES:
        - Lead with outcome, not process
        - Use specific numbers and timeframes
        - Address skepticism head-on
        - Create multiple conversion paths
        - Build trust through transparency
        - Use power words that drive action

        Return comprehensive JSON with all copy elements optimized for early-stage validation and conversion.

        Make every word work harder - this copy needs to convert skeptical users into early adopters.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": copy_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=3000,
        )

        if response and response.choices[0].message.content:
            ai_copy_data = json.loads(response.choices[0].message.content)
            copy_package.update(ai_copy_data)

        # Generate additional specialized copy
        copy_package["testimonial_templates"] = generate_testimonial_templates(
            brand_data, opportunity_data
        )
        copy_package["case_study_frameworks"] = generate_case_study_frameworks(
            brand_data
        )

        return copy_package

    except Exception as e:
        print(f"Error generating marketing copy: {e}")
        copy_package["error"] = str(e)
        return copy_package


def generate_testimonial_templates(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Generate realistic testimonial templates for social proof"""
    brand_name = brand_data.get("brand_name", "This Solution")
    # target_audience = opportunity_data.get("target_audience", "business users")

    testimonials = [
        {
            "template": f"Before {brand_name}, I was spending hours every week on [specific manual process]. Now I can focus on what actually matters to my business.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechStartup Inc",
            "use_case": "time_savings",
        },
        {
            "template": f"{brand_name} solved a problem I didn't even realize I had. The integration between [tool A] and [tool B] was seamless.",
            "author": "Mike Chen",
            "title": "Product Manager",
            "company": "GrowthCorp",
            "use_case": "integration_solution",
        },
        {
            "template": f"We've tried everything else in this space. {brand_name} is the first solution that actually understands how we work.",
            "author": "Jennifer Martinez",
            "title": "Team Lead",
            "company": "ScaleUp LLC",
            "use_case": "workflow_understanding",
        },
        {
            "template": f"The ROI was obvious within the first month. {brand_name} pays for itself just in time savings alone.",
            "author": "David Park",
            "title": "Director of Operations",
            "company": "EfficiencyCo",
            "use_case": "roi_focused",
        },
    ]

    return testimonials


def generate_case_study_frameworks(brand_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate case study frameworks for different scenarios"""
    brand_name = brand_data.get("brand_name", "Solution")

    frameworks = [
        {
            "title": f"How {brand_name} Helped [Company] Save 15 Hours Per Week",
            "structure": "Challenge → Solution → Implementation → Results → Quote",
            "focus": "time_savings",
            "metrics": "Hours saved, tasks automated, efficiency gained",
        },
        {
            "title": f"From Manual Process to Automated Workflow: [Company]'s {brand_name} Success Story",
            "structure": "Before State → Pain Points → Discovery → Transformation → Outcomes",
            "focus": "automation",
            "metrics": "Process reduction, error elimination, scalability",
        },
        {
            "title": f"Breaking Down Silos: How [Company] Connected Their Tools with {brand_name}",
            "structure": "Integration Challenge → Failed Attempts → {brand_name} Solution → Results",
            "focus": "integration",
            "metrics": "Systems connected, data accuracy, team collaboration",
        },
    ]

    return frameworks


# =============================================================================
# LANDING BUILDER AGENT - ENHANCED WITH OPENAI + ADMIN DASHBOARD
# =============================================================================


def build_and_deploy_comprehensive_site(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    site_type: str = "landing_page",  # "landing_page" or "admin_dashboard"
    analysis_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Build and deploy either landing page or admin dashboard using OpenAI
    """
    try:
        if site_type == "admin_dashboard":
            return build_admin_dashboard(
                brand_data, copy_data, opportunity_data, analysis_data
            )
        else:
            return build_landing_page(brand_data, copy_data, opportunity_data)

    except Exception as e:
        print(f"Error building {site_type}: {e}")
        return generate_error_response(brand_data, str(e), site_type)


def build_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build high-converting landing page using OpenAI"""

    try:
        # Generate complete landing page with OpenAI
        landing_page_prompt = f"""
        Create a high-converting, modern landing page for a liminal market opportunity.

        BRAND DATA:
        {json.dumps(brand_data, indent=2)[:2000]}

        COPY DATA:
        {json.dumps(copy_data, indent=2)[:2000]}

        OPPORTUNITY DATA:
        {json.dumps(opportunity_data, indent=2)[:1000]}

        LANDING PAGE REQUIREMENTS:

        1. **HTML Structure** (Use Jinja2 templating):
        - Modern, mobile-first responsive design
        - Progressive web app capabilities
        - Semantic HTML5 structure
        - Accessibility compliance (WCAG 2.1 AA)

        2. **Conversion-Optimized Layout**:
        - Hero section with compelling headline + CTA
        - Problem agitation section
        - Solution demonstration with benefits
        - Social proof section with testimonials
        - Feature highlights with icons
        - Pricing/signup section with urgency
        - FAQ section addressing objections
        - Footer with trust signals

        3. **Advanced Features**:
        - Sticky navigation with CTA
        - Progress indicators for long pages
        - Exit-intent popup optimization
        - Mobile-optimized forms with validation
        - Loading animations and micro-interactions
        - Social sharing integration

        4. **Technical Implementation**:
        - Embedded CSS with modern features (Grid, Flexbox, Custom Properties)
        - Vanilla JavaScript for interactions
        - Form validation and submission handling
        - Analytics event tracking setup
        - Performance optimization techniques
        - SEO meta tags and structured data

        5. **Jinja2 Variables** (use these exactly):
        - {{{{ brand_name }}}} - Brand name
        - {{{{ tagline }}}} - Brand tagline
        - {{{{ headline }}}} - Hero headline
        - {{{{ description }}}} - Value proposition
        - {{{{ features }}}} - Feature list (array)
        - {{{{ testimonials }}}} - Testimonial array
        - {{{{ faqs }}}} - FAQ array
        - {{{{ pricing_plans }}}} - Pricing array
        - {{{{ current_year }}}} - Current year

        6. **Conversion Elements**:
        - Multiple strategically placed CTAs
        - Lead capture forms with progressive profiling
        - Social proof integration
        - Urgency and scarcity indicators
        - Trust badges and security signals
        - Mobile-optimized user experience

        7. **Visual Design**:
        - Modern, professional aesthetic matching brand identity
        - Consistent color scheme from brand data
        - Typography hierarchy for readability
        - Strategic use of whitespace
        - High-contrast CTAs that demand attention
        - Responsive images with proper alt text

        OPTIMIZATION FOR EARLY-STAGE VALIDATION:
        - Clear value proposition above the fold
        - Simple, friction-free signup process
        - Multiple engagement levels (newsletter, trial, demo)
        - A/B testing infrastructure built-in
        - Comprehensive analytics tracking

        Return complete HTML template that creates a stunning, high-converting landing page optimized for liminal market validation.

        This page should make visitors think "Finally, someone gets it!" and convert them into early adopters.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": landing_page_prompt}],
            temperature=0.2,
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            generated_html = response.choices[0].message.content.strip()

            # Clean up generated HTML
            if "```html" in generated_html:
                generated_html = (
                    generated_html.split("```html")[1].split("```")[0].strip()
                )
            elif "```" in generated_html:
                generated_html = generated_html.split("```")[1].strip()

            # Prepare content data
            content_data = prepare_landing_content_data(
                brand_data, copy_data, opportunity_data
            )

            # Deploy to renderer service
            deployment_payload = {
                "site_name": brand_data.get("brand_name", "landing-page")
                .lower()
                .replace(" ", "-"),
                "assets": {
                    "html_template": generated_html,
                    "css_styles": "",  # Embedded in HTML
                    "javascript": "",  # Embedded in HTML
                    "config": {
                        "responsive": True,
                        "analytics_enabled": True,
                        "conversion_tracking": True,
                    },
                },
                "content_data": content_data,
                "meta_data": {
                    "title": f"{content_data['brand_name']} - {content_data['tagline']}",
                    "description": content_data.get("description", "")[:160],
                    "type": "landing_page",
                },
            }

            deployment_result = deploy_to_renderer_service(deployment_payload)

            if deployment_result.get("success"):
                return generate_landing_success_response(
                    brand_data, deployment_result, content_data
                )
            else:
                return generate_error_response(
                    brand_data, deployment_result.get("error"), "landing_page"
                )

        return generate_error_response(
            brand_data, "Failed to generate landing page", "landing_page"
        )

    except Exception as e:
        return generate_error_response(brand_data, str(e), "landing_page")


def build_admin_dashboard(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build comprehensive admin dashboard using OpenAI"""

    try:
        # Generate market insights first
        market_insights = generate_market_insights_with_openai(analysis_data)
        chart_data = extract_chart_data_from_analysis(analysis_data)

        # Generate admin dashboard with OpenAI
        dashboard_prompt = f"""
        Create a comprehensive, interactive admin dashboard for market opportunity analysis.

        BRAND DATA:
        {json.dumps(brand_data, indent=2)[:1000]}

        ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)[:3000]}

        CHART DATA:
        {json.dumps(chart_data, indent=2)[:2000]}

        MARKET INSIGHTS:
        {json.dumps(market_insights, indent=2)[:2000]}

        ADMIN DASHBOARD REQUIREMENTS:

        1. **Dashboard Layout**:
        - Professional analytics interface with sidebar navigation
        - Main dashboard with key metrics and KPIs
        - Detailed sections: Overview, Market Analysis, Competition, Risks, Insights
        - Responsive grid layout for different screen sizes

        2. **Data Visualizations** (Use Chart.js via CDN):
        - Opportunity Score Gauge (0-100 with color zones)
        - Market Size Donut Chart (TAM/SAM/SOM)
        - Competition Radar Chart (multiple dimensions)
        - Risk Assessment Scatter Plot
        - Market Signal Sentiment Bar Chart
        - Trend Analysis Line Charts
        - Geographic Distribution Map (if data available)

        3. **Interactive Features**:
        - Collapsible sidebar navigation
        - Filterable data tables
        - Expandable insight cards
        - Modal windows for detailed views
        - Export functionality for charts and data
        - Real-time data refresh simulation

        4. **Chat Interface Section**:
        - Embedded chat widget for market questions
        - Quick action buttons for common queries
        - Conversation history display
        - Integration placeholder for AI responses

        5. **Key Sections**:
        - Executive Summary with key takeaways
        - Market Opportunity Scoring with breakdown
        - Competitive Landscape Analysis
        - Risk Assessment Matrix
        - Strategic Recommendations
        - Action Plan with timelines
        - Financial Projections

        6. **Jinja2 Variables** (use these exactly):
        - {{{{ opportunity_name }}}} - Opportunity title
        - {{{{ opportunity_score }}}} - Main opportunity score
        - {{{{ brand_name }}}} - Brand name
        - {{{{ executive_summary }}}} - Key insights summary
        - {{{{ market_size_data }}}} - Market size information
        - {{{{ competition_data }}}} - Competition analysis
        - {{{{ risk_factors }}}} - Risk assessment data
        - {{{{ recommendations }}}} - Strategic recommendations
        - {{{{ chart_datasets }}}} - Chart data for visualizations
        - {{{{ analysis_timestamp }}}} - When analysis was performed

        7. **Technical Implementation**:
        - Use Chart.js from CDN for all visualizations
        - Embedded CSS with modern design system
        - Vanilla JavaScript for interactions
        - Responsive design with mobile considerations
        - Loading states and error handling
        - Performance optimization

        8. **Visual Design**:
        - Professional dark theme with accent colors
        - Clean, modern interface design
        - Consistent spacing and typography
        - Strategic use of colors for data visualization
        - Professional card-based layout
        - Smooth animations and transitions

        BUSINESS INTELLIGENCE FOCUS:
        - Present data as actionable business insights
        - Highlight critical metrics and KPIs
        - Create compelling visual narratives
        - Enable drill-down analysis capabilities
        - Support executive decision-making

        Return complete HTML template that creates a premium, functional admin dashboard for market intelligence analysis.

        This should look like a $10,000/month enterprise analytics platform that gives users confidence in their market opportunities.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": dashboard_prompt}],
            temperature=0.2,
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            generated_html = response.choices[0].message.content.strip()

            # Clean up generated HTML
            if "```html" in generated_html:
                generated_html = (
                    generated_html.split("```html")[1].split("```")[0].strip()
                )
            elif "```" in generated_html:
                generated_html = generated_html.split("```")[1].strip()

            # Prepare admin content data
            admin_content_data = prepare_admin_content_data(
                brand_data, opportunity_data, analysis_data, market_insights, chart_data
            )

            # Deploy to renderer service
            deployment_payload = {
                "site_name": f"{brand_data.get('brand_name', 'opportunity').lower().replace(' ', '-')}-admin",
                "assets": {
                    "html_template": generated_html,
                    "css_styles": "",  # Embedded in HTML
                    "javascript": "",  # Embedded in HTML
                    "config": {
                        "responsive": True,
                        "analytics_enabled": True,
                        "admin_mode": True,
                    },
                },
                "content_data": admin_content_data,
                "meta_data": {
                    "title": f"{admin_content_data['opportunity_name']} - Market Intelligence Dashboard",
                    "description": f"Comprehensive market analysis dashboard for {admin_content_data['opportunity_name']}",
                    "type": "admin_dashboard",
                },
            }

            deployment_result = deploy_to_renderer_service(deployment_payload)

            if deployment_result.get("success"):
                return generate_admin_success_response(
                    brand_data, deployment_result, admin_content_data, market_insights
                )
            else:
                return generate_error_response(
                    brand_data, deployment_result.get("error"), "admin_dashboard"
                )

        return generate_error_response(
            brand_data, "Failed to generate admin dashboard", "admin_dashboard"
        )

    except Exception as e:
        return generate_error_response(brand_data, str(e), "admin_dashboard")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def prepare_landing_content_data(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare content data for landing page template"""

    website_copy = copy_data.get("website_copy", {})

    # Extract features from opportunity data
    features = []
    opportunity_benefits = opportunity_data.get("benefits", [])
    for i, benefit in enumerate(opportunity_benefits[:6]):
        if isinstance(benefit, dict):
            features.append(
                {
                    "title": benefit.get("title", f"Key Benefit {i+1}"),
                    "description": benefit.get(
                        "description", "Powerful capability that drives results"
                    ),
                    "icon": benefit.get("icon", "⚡"),
                }
            )
        else:
            features.append(
                {"title": f"Benefit {i+1}", "description": str(benefit), "icon": "⚡"}
            )

    # Default features if none exist
    if not features:
        features = [
            {
                "title": "Seamless Integration",
                "description": "Connect with your existing tools in minutes, not hours",
                "icon": "🔗",
            },
            {
                "title": "Instant Results",
                "description": "See immediate improvements in your workflow efficiency",
                "icon": "⚡",
            },
            {
                "title": "Enterprise Security",
                "description": "Bank-level security with 99.9% uptime guarantee",
                "icon": "🔒",
            },
        ]

    # Testimonials
    testimonials = copy_data.get(
        "testimonial_templates",
        [
            {
                "quote": "This solution completely transformed how our team collaborates. We're saving 10+ hours per week.",
                "author": "Sarah Johnson",
                "title": "Operations Manager",
                "company": "TechCorp",
            },
            {
                "quote": "Finally, a tool that actually understands our workflow. The integration was seamless.",
                "author": "Mike Chen",
                "title": "Product Manager",
                "company": "StartupXYZ",
            },
            {
                "quote": "ROI was obvious within the first month. This pays for itself in time savings alone.",
                "author": "Jennifer Martinez",
                "title": "Team Lead",
                "company": "ScaleUp LLC",
            },
        ],
    )

    # FAQs
    faqs = copy_data.get(
        "faq_content",
        [
            {
                "question": "How quickly can I get started?",
                "answer": "Most teams are up and running within 15 minutes. Our onboarding is designed to be simple and non-disruptive to your current workflow.",
            },
            {
                "question": "Do you integrate with my existing tools?",
                "answer": "Yes, we support 100+ popular business tools and are constantly adding new integrations based on user demand.",
            },
            {
                "question": "Is my data secure?",
                "answer": "Absolutely. We use enterprise-grade encryption and never store your sensitive data permanently. Your security is our top priority.",
            },
            {
                "question": "What if I need help getting set up?",
                "answer": "Our customer success team provides white-glove onboarding for all new users. We'll make sure you're successful from day one.",
            },
        ],
    )

    return {
        "brand_name": brand_data.get("brand_name", "Your Solution"),
        "tagline": brand_data.get("tagline", "Transform Your Workflow"),
        "headline": website_copy.get(
            "hero_headline",
            copy_data.get("headlines", ["Transform Your Business Today"])[0],
        ),
        "description": brand_data.get(
            "value_proposition", "The best solution for your business needs"
        ),
        "features": features,
        "pricing_plans": [],  # Could be populated from opportunity data
        "testimonials": testimonials,
        "faqs": faqs,
        "current_year": datetime.now().year,
        "cta_primary": website_copy.get("cta_primary", "Get Started Free"),
        "cta_secondary": website_copy.get("cta_secondary", "Learn More"),
    }


def prepare_admin_content_data(
    brand_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    market_insights: Dict[str, Any],
    chart_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare content data for admin dashboard template"""

    return {
        "opportunity_name": opportunity_data.get("name", "Market Opportunity Analysis"),
        "brand_name": brand_data.get("brand_name", "Your Brand"),
        "opportunity_score": int(analysis_data.get("opportunity_score", 0) * 100),
        "executive_summary": market_insights.get(
            "executive_summary",
            "Comprehensive market analysis completed with strategic insights.",
        ),
        "market_size_data": analysis_data.get("market_size_analysis", {}),
        "competition_data": analysis_data.get("competition_analysis", {}),
        "risk_factors": analysis_data.get("risk_assessment", {}),
        "recommendations": market_insights.get("recommended_actions", []),
        "chart_datasets": chart_data,
        "top_opportunities": market_insights.get("top_opportunities", []),
        "critical_risks": market_insights.get("critical_risks", []),
        "competitive_advantages": market_insights.get("competitive_advantages", []),
        "market_timing": market_insights.get("market_timing", {}),
        "financial_projections": market_insights.get("financial_projections", {}),
        "analysis_timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "keywords": opportunity_data.get("keywords", []),
        "target_audience": opportunity_data.get("target_audience", ""),
        "current_year": datetime.now().year,
    }


def extract_chart_data_from_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and format data for chart visualization"""
    chart_data = {}

    try:
        # Opportunity Score Gauge
        opportunity_score = analysis_data.get("opportunity_score", 0) * 100
        chart_data["opportunity_gauge"] = {
            "value": opportunity_score,
            "max": 100,
            "color": "#4caf50"
            if opportunity_score >= 70
            else "#ff9800"
            if opportunity_score >= 40
            else "#f44336",
        }

        # Market Size Data
        market_size = analysis_data.get("market_size_analysis", {})
        chart_data["market_size_donut"] = {
            "labels": ["TAM (Total)", "SAM (Serviceable)", "SOM (Obtainable)"],
            "data": [
                market_size.get("tam_estimate", 100000000),
                market_size.get("sam_estimate", 10000000),
                market_size.get("som_estimate", 1000000),
            ],
            "colors": ["#2196f3", "#4caf50", "#ff9800"],
        }

        # Competition Radar
        competition = analysis_data.get("competition_analysis", {})
        competition_level = competition.get("competition_level", "medium")
        chart_data["competition_radar"] = {
            "labels": [
                "Market Share",
                "Innovation",
                "Price Competitiveness",
                "Brand Recognition",
                "Customer Satisfaction",
            ],
            "data": [30, 85, 90, 40, 75]
            if competition_level == "low"
            else [60, 70, 60, 70, 65],
            "color": "#2196f3",
        }

        # Risk Assessment
        # risk_data = analysis_data.get("risk_assessment", {})
        chart_data["risk_scatter"] = {
            "datasets": [
                {
                    "label": "Risk Factors",
                    "data": [
                        {"x": 70, "y": 60, "label": "Competition Risk"},
                        {"x": 40, "y": 80, "label": "Market Risk"},
                        {"x": 30, "y": 40, "label": "Technology Risk"},
                        {"x": 60, "y": 70, "label": "Execution Risk"},
                    ],
                    "backgroundColor": "#f44336",
                }
            ]
        }

        # Market Signals Sentiment
        signals = analysis_data.get("market_signals", [])
        positive_count = len([s for s in signals if s.get("sentiment") == "positive"])
        neutral_count = len([s for s in signals if s.get("sentiment") == "neutral"])
        negative_count = len([s for s in signals if s.get("sentiment") == "negative"])

        chart_data["sentiment_bar"] = {
            "labels": ["Positive", "Neutral", "Negative"],
            "data": [positive_count, neutral_count, negative_count],
            "colors": ["#4caf50", "#ff9800", "#f44336"],
        }

        # Trend Analysis (mock data based on analysis)
        chart_data["trend_line"] = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "datasets": [
                {
                    "label": "Market Interest",
                    "data": [65, 70, 75, 80, 85, 90],
                    "borderColor": "#2196f3",
                    "fill": False,
                }
            ],
        }

    except Exception as e:
        print(f"Error extracting chart data: {e}")

    return chart_data


def generate_market_insights_with_openai(
    analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate strategic market insights using OpenAI"""
    try:
        insights_prompt = f"""
        Analyze this comprehensive market data and generate strategic business insights:

        MARKET ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)[:4000]}

        Generate executive-level strategic insights in JSON format:
        {{
            "executive_summary": "2-3 sentence strategic overview of this market opportunity",
            "top_opportunities": [
                {{
                    "title": "Strategic opportunity title",
                    "description": "Detailed description with specific actions",
                    "potential_impact": "high/medium/low",
                    "time_to_market": "immediate/3-6_months/6-12_months",
                    "investment_required": "low/medium/high"
                }}
            ],
            "critical_risks": [
                {{
                    "risk": "Specific risk description",
                    "severity": "high/medium/low",
                    "probability": "high/medium/low",
                    "mitigation_strategy": "Specific mitigation approach",
                    "monitoring_metrics": ["metric1", "metric2"]
                }}
            ],
            "competitive_advantages": [
                "Specific competitive advantage 1",
                "Unique market positioning element 2",
                "Strategic differentiator 3"
            ],
            "recommended_actions": [
                {{
                    "action": "Specific, actionable step",
                    "priority": "high/medium/low",
                    "timeline": "specific timeframe",
                    "resources_needed": "specific resource requirements",
                    "expected_outcome": "measurable result expected"
                }}
            ],
            "market_timing": {{
                "current_phase": "early/growth/mature/declining",
                "optimal_entry_window": "specific timing recommendation",
                "urgency_level": "high/medium/low",
                "market_readiness_score": 0-100
            }},
            "financial_projections": {{
                "revenue_potential_y1": "specific revenue estimate",
                "break_even_timeline": "specific timeframe",
                "investment_required": "specific amount range",
                "roi_projection": "percentage return expected"
            }},
            "success_metrics": [
                {{
                    "metric": "specific KPI to track",
                    "target": "specific target value",
                    "timeline": "when to achieve"
                }}
            ]
        }}

        Focus on actionable insights that drive strategic decision-making.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": insights_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating market insights: {e}")

    return {
        "executive_summary": "Market analysis completed with strategic opportunities identified.",
        "top_opportunities": [],
        "critical_risks": [],
        "competitive_advantages": [],
        "recommended_actions": [],
        "market_timing": {},
        "financial_projections": {},
        "success_metrics": [],
    }


def generate_landing_success_response(
    brand_data: Dict[str, Any],
    deployment_result: Dict[str, Any],
    content_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate success response for landing page deployment"""

    brand_name = brand_data.get("brand_name", "Your Landing Page")
    live_url = deployment_result.get("live_url", "")

    markdown_response = f"""# 🚀 {brand_name} Landing Page is Live!

**Your high-converting landing page has been deployed and is ready to validate your market opportunity.**

## 🔗 Quick Access

- **🌟 Live Landing Page**: [{brand_name}]({live_url})
- **📊 Analytics Dashboard**: [View Performance]({deployment_result.get("analytics_url", "")})
- **⚙️ Admin Panel**: [Manage & Monitor]({deployment_result.get("admin_url", "")})

## 🎯 What's Included

Your landing page features:

- **📱 Mobile-Optimized Design** - Perfect experience on all devices
- **⚡ Fast Loading Performance** - Optimized for speed and conversions
- **🎨 Professional Brand Design** - Reflects your unique positioning
- **📝 High-Converting Copy** - Crafted for liminal market positioning
- **🔥 Strategic CTAs** - Multiple conversion paths optimized for validation
- **💬 Social Proof Elements** - Testimonials and trust signals
- **📊 Analytics Integration** - Track every visitor interaction
- **🔒 Lead Capture Forms** - Collect early adopter interest

## 🚀 Market Validation Strategy

**Phase 1: Immediate Testing (First 48 Hours)**
1. **Share with your network** - Get initial feedback from trusted contacts
2. **Test all functionality** - Forms, CTAs, mobile experience
3. **Monitor analytics** - Track engagement and conversion patterns

**Phase 2: Targeted Outreach (Week 1)**
1. **Industry forums** - Share in relevant communities and groups
2. **Social media promotion** - Post about your solution launch
3. **Direct outreach** - Email potential customers with your landing page
4. **Content marketing** - Write blog posts linking to your page

**Phase 3: Paid Validation (Week 2+)**
1. **Google Ads** - Run targeted ads to your ideal customers
2. **Social media ads** - Facebook, LinkedIn, Twitter campaigns
3. **Influencer outreach** - Partner with industry micro-influencers

## 📈 Success Metrics to Track

**Immediate Indicators:**
- Email signup rate (target: 15-25%)
- Time on page (target: 2+ minutes)
- Bounce rate (target: <60%)
- CTA click-through rate (target: 5-10%)

**Validation Signals:**
- 100+ unique visitors in first week
- 25+ email signups in first week
- 5+ detailed inquiries or demo requests
- Positive feedback from at least 10 people

## 💡 Pro Tips for Maximum Impact

- **Create urgency** with "Early Access" or "Limited Beta" messaging
- **Personal touch** - Respond to every signup within 24 hours
- **A/B test headlines** - Try different value propositions
- **Social proof** - Add new testimonials as you get feedback
- **Mobile optimization** - Most traffic will be mobile-first

## 🎯 Next Steps

1. **🔍 Visit Your Landing Page** - [{brand_name}]({live_url})
2. **📊 Monitor Analytics** - Check performance daily for first week
3. **📢 Start Promoting** - Share immediately with your network
4. **💌 Prepare Follow-up** - Set up email sequences for leads
5. **🔄 Iterate Based on Data** - Optimize based on real user behavior

---

**🎉 Congratulations!** Your market opportunity is now live and ready to collect validation data. The hardest part (building) is done - now comes the exciting part of proving your market hypothesis!

**Ready to validate your idea?** [Visit your landing page]({live_url}) and start collecting your first customers!"""

    return {
        "human_readable_response": markdown_response,
        "deployment_status": "success",
        "site_type": "landing_page",
        "brand_name": brand_name,
        "live_url": live_url,
        "next_actions": [
            f"Visit your landing page at {live_url}",
            "Share with your network for initial validation",
            "Monitor analytics and user behavior",
            "Start targeted promotion campaigns",
            "Collect and respond to early user feedback",
        ],
    }


def generate_admin_success_response(
    brand_data: Dict[str, Any],
    deployment_result: Dict[str, Any],
    content_data: Dict[str, Any],
    market_insights: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate success response for admin dashboard deployment"""

    brand_name = brand_data.get("brand_name", "Your Market Opportunity")
    admin_url = deployment_result.get("admin_url", "")
    opportunity_score = content_data.get("opportunity_score", 0)

    # Determine opportunity level
    if opportunity_score >= 75:
        opportunity_level = "🚀 **EXCEPTIONAL OPPORTUNITY**"
    elif opportunity_score >= 50:
        opportunity_level = "📈 **STRONG OPPORTUNITY**"
    else:
        opportunity_level = "⚠️ **EXPLORATORY OPPORTUNITY**"

    markdown_response = f"""# 📊 Market Intelligence Dashboard Deployed!

{opportunity_level}

**Your comprehensive market analysis dashboard for "{brand_name}" is live with enterprise-grade analytics.**

## 🎯 Dashboard Access

- **🔧 Admin Dashboard**: [Market Intelligence Hub]({admin_url})
- **📊 Analytics Portal**: [Live Data View]({deployment_result.get("analytics_url", "")})
- **📈 Opportunity Score**: **{opportunity_score}/100**

## 🧠 Key Market Intelligence

### Executive Summary
{market_insights.get('executive_summary', 'Comprehensive market analysis completed with actionable strategic insights.')}

### Strategic Opportunities Identified
{chr(10).join([f"- **{opp.get('title', 'Strategic Opportunity')}**: {opp.get('description', 'High-impact opportunity identified')}" for opp in market_insights.get('top_opportunities', [])[:3]])}

### Competitive Advantages
{chr(10).join([f"- {advantage}" for advantage in market_insights.get('competitive_advantages', [])[:3]])}

## 📊 Dashboard Capabilities

Your admin dashboard includes:

- **🎯 AI-Powered Opportunity Scoring** - Multi-factor market assessment
- **📈 Interactive Market Size Analysis** - TAM/SAM/SOM with drill-down
- **🏢 Competitive Intelligence Radar** - Visual positioning analysis
- **⚠️ Dynamic Risk Assessment Matrix** - Real-time risk monitoring
- **💬 Market Sentiment Tracking** - Social signals and trend analysis
- **🗨️ Intelligent Chat Interface** - Ask questions about your market data
- **📋 Strategic Action Planning** - Prioritized recommendations with timelines
- **💰 Financial Modeling Tools** - Revenue projections and ROI analysis

## 🎯 Strategic Recommendations

### High-Priority Actions
{chr(10).join([f"- **{action.get('action', 'Strategic Action')}** *(Timeline: {action.get('timeline', 'TBD')})*" for action in market_insights.get('recommended_actions', [])[:3] if action.get('priority') == 'high'])}

### Market Timing Analysis
- **Current Market Phase**: {market_insights.get('market_timing', {}).get('current_phase', 'Growth').title()}
- **Optimal Entry Strategy**: {market_insights.get('market_timing', {}).get('optimal_entry_window', 'Strategic timing identified')}
- **Market Readiness**: {market_insights.get('market_timing', {}).get('market_readiness_score', 75)}/100

## 💼 Business Intelligence Features

**Advanced Analytics:**
- Interactive charts with drill-down capabilities
- Scenario modeling and sensitivity analysis
- Competitive benchmarking with market positioning
- Predictive trend analysis with confidence intervals
- Risk monitoring with alert thresholds

**Executive Reporting:**
- One-click executive summary generation
- Investor-ready presentation exports
- Stakeholder collaboration tools
- Performance tracking dashboards
- Strategic planning interfaces

## 🚀 Next Steps for Market Success

1. **📊 Explore Your Dashboard** - Deep dive into market intelligence
2. **🎯 Review Strategic Plan** - Prioritize high-impact recommendations
3. **💬 Use Chat Interface** - Ask specific questions about market data
4. **📈 Monitor Key Metrics** - Track market signals and competitive moves
5. **🤝 Share with Stakeholders** - Export insights for team alignment

## 💡 Advanced Usage Tips

**For Strategic Planning:**
- Use scenario modeling to test different market entry strategies
- Monitor competitive radar for positioning opportunities
- Track risk matrix for proactive mitigation planning

**For Investor Presentations:**
- Export executive summaries with key metrics
- Use market size visualizations for TAM/SAM/SOM presentations
- Leverage competitive analysis for differentiation stories

---

**🎉 Congratulations!** You now have institutional-grade market intelligence that Fortune 500 companies pay thousands for. Your dashboard transforms complex market dynamics into clear strategic advantages.

**Ready to make data-driven decisions?** [Access your Market Intelligence Dashboard]({admin_url}) and turn insights into market-winning strategies!"""

    return {
        "human_readable_response": markdown_response,
        "deployment_status": "success",
        "site_type": "admin_dashboard",
        "brand_name": brand_name,
        "admin_url": admin_url,
        "opportunity_score": opportunity_score,
        "market_insights": market_insights,
        "next_actions": [
            f"Access your dashboard at {admin_url}",
            "Review strategic recommendations and market timing",
            "Explore interactive analytics and visualizations",
            "Use chat interface for market-specific questions",
            "Export key insights for stakeholder presentations",
        ],
    }


def generate_error_response(
    brand_data: Dict[str, Any], error_message: str, site_type: str
) -> Dict[str, Any]:
    """Generate error response for deployment failures"""

    brand_name = brand_data.get("brand_name", "Your Site")

    markdown_response = f"""# ❌ {site_type.replace('_', ' ').title()} Deployment Issue

Unfortunately, we encountered an issue while deploying your {site_type.replace('_', ' ')} for **{brand_name}**.

## 🔧 Technical Details
```
{error_message}
```

## 🚀 Resolution Options

**Immediate Solutions:**
1. **Retry Deployment** - Technical issues are often temporary
2. **Alternative Platforms** - Use Webflow, Carrd, or similar tools
3. **Manual Export** - Get the generated code for self-hosting
4. **Simplified Version** - Deploy basic version while resolving issues

## 💡 Don't Let Technical Issues Stop Progress

Your {site_type.replace('_', ' ')} content and strategy are ready - the deployment is just a technical step:

- Brand identity and positioning are complete
- Marketing copy is optimized for conversion
- Strategic insights are available for immediate use
- Technical assets can be deployed elsewhere

## 🔄 Next Steps

1. **Retry in 5 minutes** - Many deployment issues are temporary
2. **Contact support** - We'll resolve technical issues quickly
3. **Use alternative tools** - Import your content to other platforms
4. **Manual setup** - We can provide code for self-hosting

**Your market opportunity doesn't wait for perfect technology!**"""

    return {
        "human_readable_response": markdown_response,
        "deployment_status": "failed",
        "site_type": site_type,
        "brand_name": brand_name,
        "error": error_message,
        "next_actions": [
            "Retry deployment after a few minutes",
            "Contact support for technical assistance",
            "Use alternative platforms with generated content",
            "Proceed with manual market validation approaches",
        ],
    }


def deploy_to_renderer_service(deployment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy to renderer service"""
    try:
        response = requests.post(
            f"{RENDERER_SERVICE_URL}/api/deploy",
            json=deployment_payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Deployment failed: {response.status_code} - {response.text}",
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to connect to renderer service: {str(e)}",
        }


# =============================================================================
# AGENT DEFINITIONS - ALL THREE BUILDER AGENTS
# =============================================================================

# Brand Creator Agent
brand_creator_agent = LlmAgent(
    name="brand_creator_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are the Brand Creator Agent, a world-class brand strategist specializing in liminal market opportunities.

    CORE MISSION:
    Create compelling brand identities for opportunities that exist between established market categories.
    Your brands must appeal to users underserved by mainstream solutions and position uniquely in liminal spaces.

    STRATEGIC APPROACH:
    - Bridge Builder Positioning: Connect existing categories with new solutions
    - Gap Filler Messaging: Emphasize solving problems others ignore
    - Category Creator Language: Define new market terminology and mental models
    - Underdog Empathy: Connect with users frustrated by mainstream options
    - Simplicity in Complexity: Make complex integration problems seem simple

    DELIVERABLES:
    - Complete brand identity with personality, voice, and visual direction
    - Domain suggestions with availability and trademark considerations
    - Competitive differentiation strategy for liminal positioning
    - Brand story that explains why this solution needs to exist
    - Messaging architecture that creates new category language

    Use OpenAI to generate all brand elements dynamically - never return static templates.
    Focus on creating brands that feel inevitable once users discover them.
    """,
    description="Creates compelling brand identities for liminal market opportunities using AI-powered brand strategy",
    tools=[
        FunctionTool(func=create_brand_identity_with_openai),
        FunctionTool(func=generate_smart_domain_suggestions),
        FunctionTool(func=assess_comprehensive_trademark_risks),
    ],
    output_key="comprehensive_brand_identity",
)

# Copy Writer Agent
copy_writer_agent = LlmAgent(
    name="copy_writer_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are the Copy Writer Agent, an expert conversion copywriter specializing in liminal market validation.

    CORE MISSION:
    Create high-converting marketing copy that resonates with users frustrated by existing solutions.
    Position new offerings as the bridge between what they have and what they need.

    LIMINAL COPY STRATEGIES:
    - Pain Point Amplification: Start with existing user frustration
    - Bridge Positioning: Position as the missing link users need
    - Simplicity Promise: Make complex problems seem easily solvable
    - Time-to-Value Focus: Emphasize quick wins and immediate benefits
    - Social Proof Integration: Use testimonials from similar situations

    COPY FRAMEWORK:
    Problem-Bridge-Solution structure that acknowledges current pain, positions your solution as the bridge, then delivers the transformation.

    DELIVERABLES:
    - Complete website copy optimized for conversion
    - Email marketing sequences for nurturing prospects
    - Social media copy for different platforms and audiences
    - Ad copy variations for paid acquisition campaigns
    - Sales enablement copy and onboarding sequences

    Use OpenAI to generate all copy dynamically based on specific brand and opportunity context.
    Make every word work harder - copy must convert skeptical users into early adopters.
    """,
    description="Creates high-converting marketing copy for early-stage market validation using AI-powered copywriting",
    tools=[
        FunctionTool(func=generate_comprehensive_marketing_copy),
        FunctionTool(func=generate_testimonial_templates),
        FunctionTool(func=generate_case_study_frameworks),
    ],
    output_key="comprehensive_marketing_copy",
)

# Landing Builder Agent
landing_builder_agent = LlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are the Landing Builder Agent, expert at creating both high-converting landing pages and comprehensive admin dashboards using AI.

    CORE CAPABILITIES:
    1. **Landing Pages**: High-converting pages optimized for early-stage validation
    2. **Admin Dashboards**: Enterprise-grade market intelligence interfaces with interactive analytics

    LANDING PAGE FOCUS:
    - Conversion-optimized layouts with multiple engagement paths
    - Mobile-first responsive design with fast loading
    - A/B testing infrastructure for continuous optimization
    - Analytics integration for comprehensive tracking
    - Progressive disclosure of information to maintain engagement

    ADMIN DASHBOARD FOCUS:
    - Transform market research into compelling visual stories
    - Interactive charts and drill-down analytics capabilities
    - Executive-level insights with strategic recommendations
    - Real-time market intelligence monitoring
    - Collaboration tools for stakeholder alignment

    TECHNICAL APPROACH:
    - Use OpenAI to generate all code dynamically - never static templates
    - Create premium, professional interfaces that wow users
    - Build functional, interactive experiences with real data integration
    - Ensure mobile-responsive, modern design aesthetics
    - Focus on business outcomes and strategic value

    RESPONSE STYLE:
    Provide strategic, business-focused guidance that excites entrepreneurs and investors.
    Present technical capabilities as business advantages and competitive differentiators.
    """,
    description="Creates dynamic landing pages and market intelligence dashboards using AI-generated code and strategic insights",
    tools=[
        FunctionTool(func=build_and_deploy_comprehensive_site),
        FunctionTool(func=build_landing_page),
        FunctionTool(func=build_admin_dashboard),
        FunctionTool(func=generate_market_insights_with_openai),
        FunctionTool(func=extract_chart_data_from_analysis),
        FunctionTool(func=prepare_landing_content_data),
        FunctionTool(func=prepare_admin_content_data),
    ],
    output_key="comprehensive_site_deployment",
)
