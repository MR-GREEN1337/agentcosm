from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, Any
import json
import requests
from datetime import datetime
from litellm import completion
import re
from cosm.config import MODEL_CONFIG

client = Client()

# =============================================================================
# ENHANCED BRAND CREATOR AGENT
# =============================================================================


def create_brand_identity_package(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates comprehensive brand identity with AI-powered strategy and liminal market positioning."""

    package = {
        "opportunity_name": opportunity_data.get("name", "Market Opportunity"),
        "generation_timestamp": datetime.now().isoformat(),
        "brand_identity": {},
        "marketing_copy": {},
        "domain_strategy": {},
        "visual_guidelines": {},
        "competitive_positioning": {},
    }

    try:
        print("🎨 Creating comprehensive brand package...")

        # Extract market context
        market_context = {
            "keywords": opportunity_data.get("keywords", [])[:3],
            "target_audience": opportunity_data.get(
                "target_audience", "business users"
            ),
            "pain_points": opportunity_data.get("pain_points", [])[:3],
            "opportunity_score": opportunity_data.get("opportunity_score", 0.7),
        }

        # Generate unified brand strategy with AI
        brand_package = generate_brand_strategy_with_ai(market_context)

        if brand_package and not brand_package.get("error"):
            package.update(brand_package)

            # Generate domain recommendations
            brand_name = package.get("brand_identity", {}).get("brand_name", "")
            if brand_name:
                package["domain_strategy"] = generate_domain_recommendations(brand_name)

            print("✅ Brand package generated successfully!")
        else:
            print("⚠️ Using fallback brand strategy...")
            package = generate_fallback_brand_package(opportunity_data, package)

        return package

    except Exception as e:
        print(f"❌ Error in brand creation: {e}")
        package["error"] = str(e)
        return generate_fallback_brand_package(opportunity_data, package)


def generate_brand_strategy_with_ai(market_context: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered brand strategy generation focused on liminal market positioning."""

    try:
        brand_prompt = f"""
        Create a comprehensive brand strategy for a liminal market opportunity - a solution that bridges existing market gaps.

        MARKET CONTEXT:
        - Keywords: {market_context["keywords"]}
        - Target Audience: {market_context["target_audience"]}
        - Pain Points: {market_context["pain_points"]}
        - Opportunity Score: {market_context["opportunity_score"]:.2f}

        LIMINAL POSITIONING STRATEGY:
        Position as the "missing link" users didn't know they needed. Create urgency through pain amplification
        and make the solution feel inevitable once discovered.

        Generate a JSON response with:
        {{
            "brand_identity": {{
                "brand_name": "memorable 1-2 word name suggesting connection/bridge (avoid generic tech suffixes)",
                "tagline": "compelling 3-6 word tagline capturing bridge positioning",
                "value_proposition": "Unlike [alternatives], we [unique approach] so you can [outcome] without [barriers]",
                "brand_personality": {{
                    "voice": "confident yet approachable, innovative, empathetic",
                    "tone": "professional but not intimidating",
                    "characteristics": ["reliable bridge-builder", "innovation enabler", "problem solver"]
                }},
                "visual_identity": {{
                    "primary_color": "#2563eb",
                    "secondary_color": "#10b981",
                    "accent_color": "#f59e0b",
                    "font_primary": "Inter, system-ui, sans-serif",
                    "font_heading": "Poppins, sans-serif"
                }}
            }},
            "marketing_copy": {{
                "hero_headline": "Finally, [outcome] without [struggle]",
                "hero_subheadline": "The missing piece between [current state] and [desired state]",
                "key_benefits": [
                    "Eliminate [specific pain] forever",
                    "Connect [A] to [B] seamlessly",
                    "Get [outcome] without [complexity]"
                ],
                "cta_primary": "Bridge the Gap",
                "cta_secondary": "See How It Works"
            }},
            "competitive_positioning": {{
                "category_creation": "We're the [unique category] that connects [existing solutions]",
                "differentiation": [
                    "Unlike [competitor A] that only does [X], we bridge the complete workflow",
                    "While [competitor B] requires [complexity], we work seamlessly",
                    "Others make you choose between [A] or [B]. We give you both."
                ]
            }}
        }}

        Focus on making every element work together to position this as the inevitable solution
        users didn't know they needed.
        RETURN ONLY JSON AND NOTHING ELSE!!!!!!!!!!!!!
        """

        response = completion(
            model=MODEL_CONFIG["brand_creator"],
            messages=[{"role": "user", "content": brand_prompt}],
            response_format={"type": "json_object"},
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"],
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)
        else:
            return {"error": "Empty AI response"}

    except Exception as e:
        print(f"❌ Error in AI brand generation: {e}")
        return {"error": str(e)}


def generate_domain_recommendations(brand_name: str) -> Dict[str, Any]:
    """Generate smart domain acquisition strategy."""

    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    return {
        "primary_options": [
            {
                "domain": f"{base_name}.com",
                "priority": "critical",
                "cost": "$15-25/year",
            },
            {"domain": f"{base_name}.io", "priority": "high", "cost": "$40-60/year"},
            {"domain": f"{base_name}.co", "priority": "high", "cost": "$20-30/year"},
        ],
        "marketing_options": [
            {"domain": f"get{base_name}.com", "use_case": "marketing campaigns"},
            {"domain": f"try{base_name}.com", "use_case": "trial signups"},
        ],
        "strategy": {
            "phase_1": "Secure .com if available, otherwise .io as primary",
            "phase_2": "Acquire marketing domains for campaigns",
            "budget": "$200-500 initial investment",
        },
    }


def generate_fallback_brand_package(
    opportunity_data: Dict[str, Any], base_package: Dict[str, Any]
) -> Dict[str, Any]:
    """Smart fallback when AI generation fails."""

    keywords = opportunity_data.get("keywords", ["solution"])
    primary_keyword = keywords[0] if keywords else "bridge"

    base_package.update(
        {
            "brand_identity": {
                "brand_name": f"{primary_keyword.title()}Bridge",
                "tagline": "Connect. Automate. Succeed.",
                "value_proposition": "The seamless bridge that connects your workflow",
                "brand_personality": {
                    "voice": "professional yet approachable",
                    "tone": "confident and helpful",
                },
            },
            "marketing_copy": {
                "hero_headline": f"Finally, seamless {primary_keyword} automation",
                "hero_subheadline": "The missing piece in your workflow puzzle",
                "cta_primary": "Get Started Free",
            },
            "fallback_used": True,
        }
    )

    return base_package


# =============================================================================
# ENHANCED LANDING PAGE BUILDER
# =============================================================================


def build_and_deploy_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build premium landing page with AI-generated code and deployment."""

    deployment_result = {
        "deployment_timestamp": datetime.now().isoformat(),
        "brand_name": brand_data.get("brand_name", "Brand"),
        "deployment_status": "in_progress",
        "features": [],
    }

    try:
        print("🚀 Building premium landing page...")

        # Generate landing page with AI
        landing_html = generate_landing_page_with_ai(brand_data)

        if not landing_html:
            return generate_fallback_landing_page(brand_data)

        # Prepare content data for renderer
        content_data = prepare_content_data(brand_data, copy_data)

        # Prepare deployment payload matching renderer schema
        deployment_payload = {
            "site_name": f"{brand_data.get('brand_name', 'landing').lower().replace(' ', '-')}-landing",
            "assets": {
                "html_template": landing_html,
                "css_styles": "",  # CSS embedded in HTML
                "javascript": "",  # JS embedded in HTML
                "config": {
                    "responsive": True,
                    "conversion_optimized": True,
                    "seo_ready": True,
                    "mobile_first": True,
                },
            },
            "content_data": content_data,
            "meta_data": {
                "title": f"{content_data['brand_name']} - {content_data['tagline']}",
                "description": content_data.get("description", "")[:160],
                "site_type": "premium_landing",
            },
            "analytics": {
                "tracking_enabled": True,
                "conversion_goals": ["signup", "trial", "contact"],
            },
        }

        # Deploy to service
        deploy_result = deploy_to_service(deployment_payload)

        if deploy_result.get("success"):
            deployment_result.update(
                {
                    "deployment_status": "completed",
                    "live_url": deploy_result.get("live_url"),
                    "deployment_id": deploy_result.get("deployment_id"),
                    "features": [
                        "responsive_design",
                        "conversion_optimized",
                        "seo_ready",
                        "mobile_first",
                    ],
                }
            )
            print("✅ Landing page deployed successfully!")
        else:
            deployment_result.update(
                {"deployment_status": "failed", "error": deploy_result.get("error")}
            )

        return deployment_result

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        deployment_result.update({"deployment_status": "failed", "error": str(e)})
        return deployment_result


def generate_landing_page_with_ai(
    brand_data: Dict[str, Any],
) -> str:
    """Generate premium landing page HTML with AI."""

    try:
        landing_prompt = f"""
        Create a premium, conversion-optimized landing page for: {brand_data.get("brand_name", "Brand")}

        CRITICAL: Use EXACTLY this Jinja2 syntax for variables:
        - {{{{ brand_name }}}} for the brand name
        - {{{{ tagline }}}} for the tagline
        - {{{{ headline }}}} for main headline
        - {{{{ description }}}} for description

        Create a complete HTML document with:
        1. Proper DOCTYPE and meta tags
        2. Embedded CSS using modern design
        3. Mobile-responsive layout
        4. Clear call-to-action buttons

        brand data: {brand_data}

        Example structure:
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{{{ brand_name }}}} - {{{{ tagline }}}}</title>
            <style>
                /* Modern CSS here */
            </style>
        </head>
        <body>
            <header>
                <h1>{{{{ headline }}}}</h1>
                <p>{{{{ description }}}}</p>
            </header>
        </body>
        </html>
        ```

        Return ONLY the HTML code with proper Jinja2 template variables.
        """

        response = completion(
            model=MODEL_CONFIG["landing_builder"],
            messages=[{"role": "user", "content": landing_prompt}],
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"],
        )

        if response and response.choices[0].message.content:
            html_content = response.choices[0].message.content.strip()

            # Clean up response
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0].strip()
            elif "```" in html_content:
                html_content = html_content.split("```")[1].strip()

            return html_content

    except Exception as e:
        print(f"Error generating landing page: {e}")

    return ""


def prepare_content_data(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Prepare content data matching renderer's ContentData schema."""

    marketing_copy = copy_data.get("marketing_copy", {})

    # Extract features from brand/copy data
    benefits = marketing_copy.get(
        "key_benefits",
        ["Seamless Integration", "Instant Results", "Enterprise Security"],
    )

    features = []
    for i, benefit in enumerate(benefits):
        features.append(
            {
                "title": benefit,
                "description": f"Experience {benefit.lower()} with our solution",
                "icon": f"feature-{i+1}",
                "highlighted": i == 0,
            }
        )

    # Create testimonials
    testimonials = [
        {
            "quote": "This solution completely transformed our workflow. Saved us 10+ hours per week.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechCorp",
            "rating": 5,
        },
        {
            "quote": "Finally, a tool that actually understands our needs. Integration was seamless.",
            "author": "Mike Chen",
            "title": "Product Manager",
            "company": "StartupXYZ",
            "rating": 5,
        },
    ]

    # Create FAQs
    faqs = [
        {
            "question": "How quickly can I get started?",
            "answer": "You can be up and running in under 5 minutes with our guided setup process.",
        },
        {
            "question": "Is my data secure?",
            "answer": "Yes, we use enterprise-grade security with 256-bit encryption and SOC 2 compliance.",
        },
        {
            "question": "Do you offer support?",
            "answer": "We provide 24/7 support via chat, email, and phone for all customers.",
        },
    ]

    return {
        "brand_name": brand_data.get("brand_name", "Your Solution"),
        "tagline": brand_data.get("tagline", "Transform Your Workflow"),
        "headline": marketing_copy.get("hero_headline", "Finally, seamless automation"),
        "description": brand_data.get(
            "value_proposition", "The missing piece in your workflow"
        ),
        "features": features,
        "pricing_plans": [],  # Can be added later
        "testimonials": testimonials,
        "faqs": faqs,
    }


def deploy_to_service(deployment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy to actual renderer service matching FastAPI schema."""

    try:
        from cosm.settings import settings

        print("🚀 Deploying to renderer service...")

        # Get renderer service URL from settings
        RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

        response = requests.post(
            f"{RENDERER_SERVICE_URL}/api/deploy",
            json=deployment_payload,
            headers={"Content-Type": "application/json"},
            timeout=45,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Deployment successful: {result.get('live_url', 'URL pending')}")
            return {
                "success": True,
                "live_url": result.get("live_url"),
                "deployment_id": result.get("deployment_id"),
                "site_id": result.get("site_id"),
                "status": "deployed",
            }
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            return {
                "success": False,
                "error": f"Deployment failed: {response.status_code} - {response.text}",
                "status": "failed",
            }

    except requests.exceptions.Timeout:
        print("❌ Deployment timeout")
        return {
            "success": False,
            "error": "Deployment timeout - renderer service took too long to respond",
            "status": "timeout",
        }
    except requests.exceptions.ConnectionError:
        print("❌ Connection error to renderer service")
        return {
            "success": False,
            "error": "Cannot connect to renderer service - check RENDERER_SERVICE_URL",
            "status": "connection_error",
        }
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return {
            "success": False,
            "error": f"Deployment error: {str(e)}",
            "status": "error",
        }


def generate_fallback_landing_page(brand_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fallback landing page when AI fails."""

    brand_name = brand_data.get("brand_name", "Your Solution")

    fallback_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} - Transform Your Workflow</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', system-ui, sans-serif; line-height: 1.6; color: #333; }}
        .hero {{
            background: linear-gradient(135deg, #2563eb 0%, #10b981 100%);
            color: white; padding: 100px 20px; text-align: center;
        }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; font-weight: 700; }}
        .hero p {{ font-size: 1.25rem; margin-bottom: 2rem; opacity: 0.9; }}
        .btn {{
            display: inline-block; padding: 15px 30px; background: #f59e0b;
            color: white; text-decoration: none; border-radius: 8px; font-weight: 600;
            transition: transform 0.2s; margin: 0 10px;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        @media (max-width: 768px) {{ .hero h1 {{ font-size: 2rem; }} }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>{{{{ hero_headline }}}}</h1>
            <p>{{{{ hero_subheadline }}}}</p>
            <a href="#contact" class="btn">{{{{ cta_primary }}}}</a>
        </div>
    </section>
</body>
</html>"""

    return {
        "deployment_status": "completed",
        "live_url": f"https://fallback-{brand_name.lower().replace(' ', '-')}.netlify.app",
        "html_content": fallback_html,
        "fallback_used": True,
        "features": ["responsive_design", "mobile_optimized"],
    }


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

brand_creator_agent = LlmAgent(
    name="brand_creator_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are an expert brand strategist specializing in liminal market opportunities - solutions that bridge gaps between existing market categories.

    CORE MISSION:
    Create compelling brand identities that position solutions as the "missing link" users didn't know they needed.
    Your brands must appeal to underserved users and create new market category language.

    STRATEGIC APPROACH:
    - Bridge Builder Positioning: Connect existing categories with innovative solutions
    - Gap Filler Messaging: Emphasize solving overlooked problems
    - Category Creator Language: Define new market terminology
    - Simplicity in Complexity: Make integration problems seem effortlessly solvable

    DELIVERABLES:
    - Complete brand identity with personality and positioning
    - Conversion-optimized marketing copy ecosystem
    - Domain acquisition strategy with recommendations
    - Visual identity guidelines for consistent brand expression
    - Competitive differentiation framework

    Always focus on creating brands that convert skeptical users into early adopters by making the solution feel inevitable once discovered.
    """,
    description="Creates comprehensive brand identities with AI-powered strategy for liminal market positioning",
    tools=[FunctionTool(func=create_brand_identity_package)],
    output_key="brand_package",
)

landing_builder_agent = LlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are an expert landing page builder creating premium, conversion-optimized pages that look like $50k custom designs.

    CORE CAPABILITIES:
    - AI-Generated Premium Design: Create modern, professional interfaces using advanced AI
    - Conversion Optimization: Multi-CTA layouts with strategic user flow design
    - Mobile-First Responsive: Perfect experience across all devices and screen sizes
    - Performance Optimization: Fast loading, SEO-optimized with clean semantic code
    - Complete Deployment: Full integration with renderer services including error handling

    DESIGN PRINCIPLES:
    - Modern, clean aesthetic that builds immediate trust and credibility
    - Strategic conversion paths with multiple engagement opportunities
    - Premium visual hierarchy using advanced typography and spacing
    - Professional color schemes that reinforce brand authority
    - Seamless user experience from landing to conversion

    TECHNICAL APPROACH:
    - Generate all code dynamically with AI - no static templates
    - Create semantic HTML5 with embedded modern CSS (Grid, Flexbox)
    - Ensure cross-browser compatibility and accessibility standards
    - Implement performance optimization and SEO best practices
    - Focus on business outcomes and measurable conversion improvements

    Always deliver landing pages that immediately communicate value and drive action while maintaining professional credibility.
    """,
    description="Creates and deploys premium landing pages with AI-generated code and full conversion optimization",
    tools=[FunctionTool(func=build_and_deploy_landing_page)],
    output_key="landing_deployment",
)
