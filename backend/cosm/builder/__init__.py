"""
Builder Agents - Create and deploy testable business assets from validated opportunities
Updated to deploy directly to renderer service instead of returning code
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any, Optional
import json
import re
import requests
from cosm.config import MODEL_CONFIG
from cosm.prompts import (
    BRAND_CREATOR_PROMPT,
    COPY_WRITER_PROMPT,
)
from litellm import completion
from cosm.settings import settings

client = Client()

# Renderer service configuration
RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

# =============================================================================
# DEPLOYMENT SERVICE INTEGRATION
# =============================================================================


def deploy_to_renderer_service(deployment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy landing page to the renderer service and return live URLs"""
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


def get_deployment_status(site_id: str) -> Dict[str, Any]:
    """Check deployment status and get site information"""
    try:
        response = requests.get(
            f"{RENDERER_SERVICE_URL}/api/sites/{site_id}/data", timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Site not found or service unavailable"}
    except Exception as e:
        return {"error": f"Failed to check deployment status: {str(e)}"}


# =============================================================================
# BRAND CREATOR AGENT (unchanged)
# =============================================================================


def create_brand_identity(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates comprehensive brand identity for a market opportunity"""
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
    }

    try:
        # Generate brand identity using AI
        brand_response = generate_brand_with_ai(opportunity_data)
        if brand_response:
            brand_identity.update(brand_response)

        # Generate domain suggestions
        brand_identity["domain_suggestions"] = generate_domain_suggestions(
            brand_identity.get("brand_name", "")
        )

        # Add trademark considerations
        brand_identity["trademark_considerations"] = assess_trademark_risks(
            brand_identity.get("brand_name", "")
        )

        return brand_identity

    except Exception as e:
        print(f"Error creating brand identity: {e}")
        brand_identity["error"] = str(e)
        return brand_identity


def generate_brand_with_ai(
    opportunity_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Use AI to generate comprehensive brand identity"""
    try:
        prompt = f"""
        Create a comprehensive brand identity for this market opportunity:

        Opportunity: {json.dumps(opportunity_data, indent=2)}

        Generate a JSON response with:
        {{
            "brand_name": "Memorable, unique brand name",
            "tagline": "Compelling 3-7 word tagline",
            "positioning_statement": "One sentence positioning vs competitors",
            "value_proposition": "Clear value statement for target users",
            "target_audience": "Specific target customer description",
            "brand_personality": {{
                "voice": "brand voice (professional/friendly/innovative/etc)",
                "tone": "communication tone",
                "personality_traits": ["trait1", "trait2", "trait3"]
            }},
            "visual_identity": {{
                "color_palette": ["primary_color", "secondary_color", "accent_color"],
                "typography": "font style recommendation",
                "imagery_style": "visual style description"
            }},
            "messaging_framework": {{
                "primary_message": "main message to communicate",
                "supporting_messages": ["message1", "message2", "message3"],
                "differentiation_points": ["differentiator1", "differentiator2"]
            }}
        }}

        Focus on liminal market positioning - how this sits between existing categories.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating brand with AI: {e}")

    return None


def generate_domain_suggestions(brand_name: str) -> List[Dict[str, Any]]:
    """Generate domain name suggestions"""
    if not brand_name:
        return []

    suggestions = []
    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    # Primary domain options
    primary_options = [f"{base_name}.com", f"{base_name}.io", f"{base_name}.co"]

    # Alternative options
    alternative_options = [
        f"get{base_name}.com",
        f"{base_name}app.com",
        f"{base_name}hq.com",
        f"{base_name}pro.com",
        f"try{base_name}.com",
    ]

    # Add suggestions with priority
    for domain in primary_options:
        suggestions.append(
            {
                "domain": domain,
                "priority": "high",
                "availability": "check_required",
                "recommendation": "primary_option",
            }
        )

    for domain in alternative_options:
        suggestions.append(
            {
                "domain": domain,
                "priority": "medium",
                "availability": "check_required",
                "recommendation": "alternative_option",
            }
        )

    return suggestions


def assess_trademark_risks(brand_name: str) -> List[str]:
    """Assess potential trademark risks"""
    considerations = []

    if not brand_name:
        return ["No brand name provided for assessment"]

    # Basic trademark considerations
    considerations.extend(
        [
            "Conduct comprehensive trademark search before final selection",
            "Check for existing trademarks in relevant business categories",
            "Consider international trademark implications",
            "Verify domain availability for primary brand name",
            "Search for existing companies with similar names",
        ]
    )

    # Name-specific considerations
    if len(brand_name.split()) > 2:
        considerations.append("Multi-word names may be harder to trademark")

    if any(char.isdigit() for char in brand_name):
        considerations.append("Names with numbers may face trademark challenges")

    return considerations


# =============================================================================
# COPY WRITER AGENT (unchanged from original)
# =============================================================================


def generate_marketing_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates comprehensive marketing copy for the opportunity"""
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
    }

    try:
        # Generate core copy elements
        core_copy = generate_core_copy_with_ai(brand_data, opportunity_data)
        if core_copy:
            copy_package.update(core_copy)

        # Generate website copy
        copy_package["website_copy"] = generate_website_copy(
            brand_data, opportunity_data
        )

        # Generate email sequences
        copy_package["email_sequences"] = generate_email_sequences(
            brand_data, opportunity_data
        )

        # Generate social media copy
        copy_package["social_media_copy"] = generate_social_copy(
            brand_data, opportunity_data
        )

        return copy_package

    except Exception as e:
        print(f"Error generating marketing copy: {e}")
        copy_package["error"] = str(e)
        return copy_package


def generate_core_copy_with_ai(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Generate core copy elements using AI"""
    try:
        prompt = f"""
        Create marketing copy for this brand and opportunity:

        Brand Data: {json.dumps(brand_data, indent=2)}
        Opportunity Data: {json.dumps(opportunity_data, indent=2)}

        Generate JSON with:
        {{
            "headlines": [
                "Primary headline for landing page",
                "Alternative headline option",
                "Email subject line headline"
            ],
            "taglines": [
                "3-word tagline",
                "5-word tagline",
                "7-word tagline"
            ],
            "value_propositions": [
                "Outcome-focused value prop",
                "Process-focused value prop",
                "Competitive differentiation value prop"
            ],
            "ad_copy": {{
                "google_ads": [
                    "30-character headline",
                    "90-character description"
                ],
                "facebook_ads": [
                    "Primary text (125 chars)",
                    "Headline (40 chars)"
                ]
            }}
        }}

        Focus on liminal market positioning and immediate user benefits.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating core copy: {e}")

    return None


def generate_website_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, str]:
    """Generate website copy sections dynamically based on brand and opportunity"""

    brand_name = brand_data.get("brand_name", "Solution")
    value_prop = brand_data.get("value_proposition", "Transform your workflow")
    target_audience = brand_data.get("target_audience", "teams")

    # Extract opportunity-specific context
    opportunity_type = opportunity_data.get("type", "general")
    pain_points = opportunity_data.get("pain_points", [])
    benefits = opportunity_data.get("benefits", [])

    # Generate dynamic copy based on context
    try:
        prompt = f"""
        Generate website copy sections for this specific brand and opportunity:

        Brand: {brand_name}
        Value Proposition: {value_prop}
        Target Audience: {target_audience}
        Opportunity Type: {opportunity_type}
        Pain Points: {pain_points}
        Benefits: {benefits}

        Create dynamic, brand-specific copy that avoids generic templates.
        Generate JSON with these sections:
        {{
            "hero_headline": "Compelling headline that reflects the brand personality",
            "hero_subheadline": "Supporting text that explains the value proposition",
            "problem_section": "Section explaining the specific problems this audience faces",
            "solution_section": "How this brand solves those problems uniquely",
            "benefits_section": "Specific benefits formatted as bullet points",
            "how_it_works": "Step-by-step process specific to this solution",
            "cta_primary": "Primary call-to-action button text",
            "cta_secondary": "Secondary CTA text"
        }}

        Make it specific to {brand_name} and avoid generic "workflow automation" language.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating dynamic website copy: {e}")

    # Fallback to basic copy if AI generation fails
    return {
        "hero_headline": f"Finally, {value_prop.lower()}",
        "hero_subheadline": f"{brand_name} bridges the gap between your existing tools to eliminate manual work and reduce errors.",
        "problem_section": f"**The Problem {target_audience.title()} Face**\n\nYou're switching between multiple tools, copying data manually, and losing time on tasks that should be automated.",
        "solution_section": f"**How {brand_name} Works**\n\n{brand_name} sits in the gap between your existing tools, automatically handling the connections and data transfers that currently require manual work.",
        "benefits_section": "**What You'll Achieve**\n\n- Eliminate manual data entry between systems\n- Reduce errors from copy-paste workflows\n- Save hours every week on repetitive tasks",
        "how_it_works": f"**Simple Integration**\n\n1. **Connect**: Link {brand_name} to your existing tools\n2. **Configure**: Set up the automated workflows you need\n3. **Automate**: Watch as manual processes become seamless automation",
        "cta_primary": "Start Automating Your Workflow",
        "cta_secondary": f"See {brand_name} in Action",
    }


def generate_email_sequences(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, List[Dict[str, str]]]:
    """Generate email marketing sequences"""

    brand_name = brand_data.get("brand_name", "Solution")

    sequences = {
        "welcome_sequence": [
            {
                "subject": f"Welcome to {brand_name} - Your workflow just got easier",
                "preview": "Here's what happens next...",
                "body": f"Thanks for joining {brand_name}! You're about to eliminate the manual work that's been slowing down your workflow. Here's what to expect...",
            },
            {
                "subject": "The #1 workflow killer (and how to fix it)",
                "preview": "It's not what you think...",
                "body": "The biggest productivity killer isn't big problems - it's the small friction points between your tools that add up to hours of wasted time every week.",
            },
            {
                "subject": f"See {brand_name} in action (2-minute demo)",
                "preview": "Watch this quick demo...",
                "body": f"Here's a quick demo showing exactly how {brand_name} eliminates the manual work between your existing tools.",
            },
        ],
        "nurture_sequence": [
            {
                "subject": "Case study: How TeamX saved 15 hours/week",
                "preview": "Real results from real users",
                "body": f"See how one team used {brand_name} to eliminate manual data entry and save 15 hours per week.",
            },
            {
                "subject": "The hidden cost of manual workflows",
                "preview": "It's more than just time...",
                "body": "Manual workflows don't just waste time - they introduce errors, create bottlenecks, and prevent scaling.",
            },
        ],
    }

    return sequences


def generate_social_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, List[str]]:
    """Generate social media copy"""

    brand_name = brand_data.get("brand_name", "Solution")
    value_prop = brand_data.get("value_proposition", "workflow automation")

    social_copy = {
        "twitter_posts": [
            f"Stop copying data between tools manually. {brand_name} automates the connections your workflow needs. 🚀",
            f"The gap between your tools is where productivity goes to die. {brand_name} bridges those gaps automatically.",
            f"Manual workflows don't scale. {value_prop} does. See how: [link]",
        ],
        "linkedin_posts": [
            f"Productivity insight: The biggest workflow bottlenecks aren't in your tools - they're between your tools. {brand_name} solves this by automating the manual handoffs that slow teams down.",
            f"Team efficiency tip: Audit your manual processes this week. Any task you do more than once between different tools is a candidate for automation with {brand_name}.",
        ],
        "facebook_posts": [
            f"Tired of switching between multiple tools and copying data manually? {brand_name} connects your existing tools so you can focus on work that matters.",
            f"Save hours every week by automating the busy work between your favorite tools. See how {brand_name} works: [link]",
        ],
    }

    return social_copy


# =============================================================================
# LANDING BUILDER AGENT (UPDATED FOR DEPLOYMENT)
# =============================================================================


def build_and_deploy_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build and deploy a complete landing page to the renderer service
    Returns deployment information and live URLs instead of code
    """

    try:
        # Generate all the assets first
        design_requirements = generate_design_requirements(brand_data, opportunity_data)
        html_template = generate_html_template(
            brand_data, copy_data, design_requirements
        )

        # Validate the HTML template before proceeding
        template_validation = validate_jinja_template(html_template)
        if not template_validation["valid"]:
            return {
                "deployment_status": "failed",
                "error": f"Template validation failed: {template_validation['error']}",
                "suggestion": template_validation.get(
                    "suggestion", "Check template syntax"
                ),
            }

        css_styles = generate_css_styles(brand_data, design_requirements)
        javascript = generate_javascript_code(brand_data, design_requirements)
        content_data = prepare_content_data(brand_data, copy_data, opportunity_data)

        # Prepare deployment payload for renderer service
        deployment_payload = {
            "site_name": brand_data.get("brand_name", "landing-page")
            .lower()
            .replace(" ", "-"),
            "assets": {
                "html_template": html_template,
                "css_styles": css_styles,
                "javascript": javascript,
                "config": {
                    "responsive": True,
                    "analytics_enabled": True,
                    "conversion_tracking": True,
                },
            },
            "content_data": content_data,
            "meta_data": {
                "title": f"{content_data.get('brand_name', '')} - {content_data.get('tagline', '')}",
                "description": content_data.get("description", "")[:160],
                "keywords": [
                    content_data.get("brand_name", "").lower(),
                    "workflow automation",
                    "productivity tools",
                    "business integration",
                ],
                "brand_style": brand_data.get("visual_identity", {}),
                "opportunity_type": opportunity_data.get("type", "standard"),
            },
            "analytics": {
                "conversion_events": ["cta-primary", "cta-secondary", "form-submit"],
                "engagement_tracking": True,
                "scroll_tracking": True,
                "exit_intent": True,
            },
        }

        # Deploy to renderer service
        deployment_result = deploy_to_renderer_service(deployment_payload)

        if deployment_result.get("success"):
            # Return deployment information with live URLs and functionality description
            return {
                "deployment_status": "success",
                "brand_name": brand_data.get("brand_name", "Your Brand"),
                "live_url": deployment_result.get("live_url"),
                "admin_url": deployment_result.get("admin_url"),
                "analytics_url": deployment_result.get("analytics_url"),
                "site_id": deployment_result.get("site_id"),
                "functionality_description": generate_functionality_description(
                    brand_data, content_data
                ),
                "testing_instructions": generate_testing_instructions(
                    brand_data, content_data
                ),
                "deployment_details": deployment_result.get("deployment_details", {}),
                "success_message": f"🚀 {brand_data.get('brand_name', 'Your landing page')} is now live and ready for validation!",
            }
        else:
            return {
                "deployment_status": "failed",
                "error": deployment_result.get("error", "Unknown deployment error"),
                "fallback_assets": {
                    "html_template": html_template,
                    "css_styles": css_styles,
                    "javascript": javascript,
                    "content_data": content_data,
                },
            }

    except Exception as e:
        print(f"Error building and deploying landing page: {e}")
        return {
            "deployment_status": "failed",
            "error": f"Build and deployment failed: {str(e)}",
        }


def generate_functionality_description(
    brand_data: Dict[str, Any], content_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate description of the deployed landing page functionality"""

    brand_name = brand_data.get("brand_name", "Your Brand")
    features_count = len(content_data.get("features", []))
    testimonials_count = len(content_data.get("testimonials", []))

    return {
        "overview": f"Live landing page for {brand_name} with complete functionality for market validation",
        "key_features": [
            "📱 Fully responsive design optimized for mobile and desktop",
            "⚡ Fast-loading single-page experience",
            f"🎯 {features_count} product features showcased with engaging visuals",
            f"💬 {testimonials_count} customer testimonials for social proof",
            "📝 Lead capture form with email validation",
            "📊 Built-in analytics tracking for all user interactions",
            "🔥 Conversion-optimized CTA buttons throughout the page",
        ],
        "sections_included": [
            "Hero section with compelling headline and primary CTA",
            "Problem/solution presentation",
            "Feature highlights with icons and descriptions",
            "Customer testimonials and social proof",
            "Pricing information (if applicable)",
            "FAQ section addressing common concerns",
            "Footer with contact information",
        ],
        "analytics_capabilities": [
            "Page view tracking",
            "Button click tracking for all CTAs",
            "Form submission tracking with validation",
            "Scroll depth analysis",
            "User engagement metrics",
            "Exit intent detection",
        ],
        "conversion_elements": [
            "Multiple strategically placed CTA buttons",
            "Email capture form with instant feedback",
            "Social proof elements to build trust",
            "FAQ section to address objections",
            "Mobile-optimized design for on-the-go users",
        ],
    }


def generate_testing_instructions(
    brand_data: Dict[str, Any], content_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate testing instructions for the deployed landing page"""

    brand_name = brand_data.get("brand_name", "Your Brand")

    return {
        "validation_checklist": [
            "✅ Test the main CTA button and form submission",
            "✅ Verify mobile responsiveness on different devices",
            "✅ Check loading speed and visual elements",
            "✅ Test email capture form validation",
            "✅ Review all copy and messaging for clarity",
            "✅ Ensure all features are accurately represented",
        ],
        "conversion_testing": [
            "Track form submission rates",
            "Monitor button click-through rates",
            "Analyze scroll depth and engagement",
            "Test different traffic sources",
            "A/B test headline variations if needed",
        ],
        "feedback_collection": [
            "Share with target customers for feedback",
            "Test with colleagues outside your industry",
            "Get input on value proposition clarity",
            "Validate pricing positioning",
            "Assess overall trust and credibility",
        ],
        "next_steps": [
            "Share the live URL to start collecting early interest",
            "Use the admin panel to monitor real-time analytics",
            "Iterate based on user behavior and feedback",
            "Consider traffic campaigns once conversion rate is optimized",
            f"Prepare follow-up sequences for {brand_name} leads",
        ],
    }


# [Include all other helper functions from original code - generate_design_requirements, etc.]
# For brevity, I'm including key functions. The full implementation would include all helper functions.


def generate_design_requirements(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate specific design requirements based on brand and opportunity"""

    visual_identity = brand_data.get("visual_identity", {})
    brand_personality = brand_data.get("brand_personality", {})

    # Map personality to design constraints
    personality_traits = brand_personality.get("personality_traits", [])
    voice = brand_personality.get("voice", "professional")

    design_style = "modern-minimal"
    if "innovative" in personality_traits or "cutting-edge" in voice.lower():
        design_style = "futuristic-bold"
    elif "friendly" in personality_traits or "approachable" in voice.lower():
        design_style = "warm-friendly"
    elif "premium" in personality_traits or "luxury" in voice.lower():
        design_style = "premium-elegant"

    return {
        "design_style": design_style,
        "layout_complexity": "medium",
        "color_palette": visual_identity.get(
            "color_palette", ["#2563eb", "#1e40af", "#3b82f6"]
        ),
        "typography_style": visual_identity.get("typography", "modern-sans"),
        "brand_voice": voice,
        "personality_traits": personality_traits,
        "conversion_focus": "early_signup",
        "mobile_priority": True,
        "accessibility_level": "wcag_aa",
        "animation_level": "subtle",
    }


def validate_jinja_template(template_str: str) -> Dict[str, Any]:
    """Validate Jinja2 template syntax before deployment"""
    try:
        from jinja2 import Environment, BaseLoader, TemplateSyntaxError

        env = Environment(loader=BaseLoader())
        template = env.from_string(template_str)

        # Try to render with dummy data to catch runtime errors
        dummy_data = {
            "brand_name": "Test Brand",
            "headline": "Test Headline",
            "description": "Test Description",
            "tagline": "Test Tagline",
            "features": [{"title": "Test Feature", "description": "Test Description"}],
            "testimonials": [
                {"quote": "Test Quote", "author": "Test Author", "title": "Test Title"}
            ],
            "faqs": [{"question": "Test Question?", "answer": "Test Answer"}],
            "pricing_plans": [],
            "current_year": 2025,
        }

        rendered = template.render(**dummy_data)

        return {
            "valid": True,
            "template": template_str,
            "test_render": rendered[:200] + "..." if len(rendered) > 200 else rendered,
        }

    except TemplateSyntaxError as e:
        return {
            "valid": False,
            "error": f"Template syntax error: {str(e)}",
            "line": getattr(e, "lineno", None),
            "suggestion": "Check for missing {% endfor %}, {% endif %}, or {% endblock %} tags",
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Template validation error: {str(e)}",
            "suggestion": "Check template syntax and variable names",
        }


def generate_html_template(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    design_requirements: Dict[str, Any],
) -> str:
    """Generate dynamic HTML template with Jinja2 syntax for renderer service"""

    try:
        prompt = f"""
        Create a complete HTML template for the In-Memory Webpage Renderer service:

        BRAND DATA: {json.dumps(brand_data, indent=2)}
        COPY DATA: {json.dumps(copy_data, indent=2)}
        DESIGN REQUIREMENTS: {json.dumps(design_requirements, indent=2)}

        CRITICAL REQUIREMENTS:
        1. Use {{{{ variable_name }}}} for all dynamic content
        2. Available variables: brand_name, tagline, headline, description, features, pricing_plans, testimonials, faqs
        3. Use {{% for feature in features %}} loops for dynamic lists
        4. NO embedded CSS or JavaScript - renderer service injects separately
        5. Add data-track attributes for analytics
        6. Design style: {design_requirements.get('design_style', 'modern-minimal')}

        Generate complete HTML with proper Jinja2 templating syntax.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            generated_template = response.choices[0].message.content.strip()

            # Validate the generated template
            validation = validate_jinja_template(generated_template)
            if validation["valid"]:
                return generated_template
            else:
                print(f"Generated template validation failed: {validation['error']}")
                print("Falling back to default template...")
                # Fall through to use fallback template

    except Exception as e:
        print(f"Error generating HTML template: {e}")

    # Fallback template with proper Jinja2 syntax
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ headline }} | {{ brand_name }}</title>
    <meta name="description" content="{{ description }}">
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="logo">{{ brand_name }}</div>
            <button class="cta-nav" data-track="nav-cta">Get Started</button>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>{{ headline }}</h1>
            <p>{{ description }}</p>
            <button class="cta-primary" data-track="cta-primary">Get Started</button>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2>Why Choose {{ brand_name }}?</h2>
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card" data-track="feature-click">
                    <h3>{{ feature.title }}</h3>
                    <p>{{ feature.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="testimonials">
        <div class="container">
            <h2>What Our Customers Say</h2>
            <div class="testimonials-grid">
                {% for testimonial in testimonials %}
                <div class="testimonial-card">
                    <p>"{{ testimonial.quote }}"</p>
                    <div class="author">- {{ testimonial.author }}, {{ testimonial.title }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="faq">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-list">
                {% for faq in faqs %}
                <div class="faq-item">
                    <h3>{{ faq.question }}</h3>
                    <p>{{ faq.answer }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="cta-section">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <form class="signup-form" data-track="form-submit">
                <input type="email" placeholder="Enter your email" required>
                <button type="submit">Start Free Trial</button>
            </form>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; {{ current_year }} {{ brand_name }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""


def generate_css_styles(
    brand_data: Dict[str, Any], design_requirements: Dict[str, Any]
) -> str:
    """Generate dynamic CSS styles based on brand identity"""

    visual_identity = brand_data.get("visual_identity", {})
    colors = visual_identity.get("color_palette", ["#2563eb", "#1e40af", "#3b82f6"])
    primary_color = colors[0] if colors else "#2563eb"

    return f"""
/* Dynamic CSS for {brand_data.get('brand_name', 'Brand')} */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

.header {{ background: white; padding: 1rem 0; border-bottom: 1px solid #e5e7eb; }}
.header .container {{ display: flex; justify-content: space-between; align-items: center; }}
.logo {{ font-size: 1.5rem; font-weight: 700; color: {primary_color}; }}

.cta-primary, .cta-nav {{
    background: {primary_color};
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}}

.hero {{ padding: 4rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }}
.hero h1 {{ font-size: 3rem; margin-bottom: 1rem; color: #1f2937; }}
.hero p {{ font-size: 1.25rem; color: #6b7280; margin-bottom: 2rem; }}

.features {{ padding: 4rem 0; }}
.features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
.feature-card {{
    padding: 2rem;
    border-radius: 8px;
    background: #f8fafc;
    transition: all 0.3s ease;
}}

.cta-section {{
    padding: 4rem 0;
    background: {primary_color};
    color: white;
    text-align: center;
}}

@media (max-width: 768px) {{
    .hero h1 {{ font-size: 2rem; }}
    .features-grid {{ grid-template-columns: 1fr; }}
}}
"""


def generate_javascript_code(
    brand_data: Dict[str, Any], design_requirements: Dict[str, Any]
) -> str:
    """Generate dynamic JavaScript compatible with renderer service analytics"""

    return """
// Auto-track data-track elements
document.addEventListener('click', function(e) {
    const trackElement = e.target.closest('[data-track]');
    if (trackElement) {
        const trackType = trackElement.getAttribute('data-track');
        trackEvent(trackType + '_click', {
            element: trackType,
            text: trackElement.textContent.trim().substring(0, 50),
            timestamp: new Date().toISOString()
        });
    }
});

// Form handling with validation
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.matches('[data-track="form-submit"]')) {
        e.preventDefault();

        const formData = new FormData(form);
        const email = formData.get('email');

        if (!email || !email.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }

        trackEvent('form_submit', {
            form_type: 'signup',
            has_email: !!email,
            timestamp: new Date().toISOString()
        });

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Thank you!';
        submitBtn.disabled = true;

        setTimeout(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            form.reset();
        }, 2000);
    }
});

// Scroll depth tracking
let scrollThresholds = [25, 50, 75, 100];
let trackedThresholds = new Set();

window.addEventListener('scroll', function() {
    const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;

    scrollThresholds.forEach(threshold => {
        if (scrollPercent >= threshold && !trackedThresholds.has(threshold)) {
            trackedThresholds.add(threshold);
            trackEvent('scroll_depth', {
                percentage: threshold,
                timestamp: new Date().toISOString()
            });
        }
    });
});
"""


def prepare_content_data(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare content data for renderer service ContentData model"""

    website_copy = copy_data.get("website_copy", {})

    # Prepare features from opportunity data
    features = []
    opportunity_benefits = opportunity_data.get("benefits", [])
    for i, benefit in enumerate(opportunity_benefits[:6]):
        if isinstance(benefit, dict):
            features.append(
                {
                    "title": benefit.get("title", f"Feature {i+1}"),
                    "description": benefit.get("description", "Benefit description"),
                    "icon": benefit.get("icon", "⚡"),
                }
            )
        else:
            features.append(
                {
                    "title": f"Feature {i+1}",
                    "description": str(benefit),
                    "icon": "⚡",
                }
            )

    # Default features if none exist
    if not features:
        features = [
            {
                "title": "Easy Integration",
                "description": "Connect with your existing tools in minutes",
                "icon": "🔗",
            },
            {
                "title": "Save Time",
                "description": "Automate repetitive tasks and focus on what matters",
                "icon": "⏰",
            },
            {
                "title": "Secure & Reliable",
                "description": "Enterprise-grade security and 99.9% uptime",
                "icon": "🔒",
            },
        ]

    # Prepare testimonials
    testimonials = [
        {
            "quote": "This solution transformed our workflow completely.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechCorp",
        },
        {
            "quote": "We're saving 10+ hours per week on manual tasks.",
            "author": "Mike Chen",
            "title": "Team Lead",
            "company": "StartupXYZ",
        },
    ]

    # Prepare FAQs
    faqs = [
        {
            "question": "How quickly can I get started?",
            "answer": "Most teams are up and running within 15 minutes. Our setup is designed to be simple and non-disruptive.",
        },
        {
            "question": "Do you integrate with my existing tools?",
            "answer": "Yes, we support the most popular business tools and are constantly adding new integrations.",
        },
        {
            "question": "Is my data secure?",
            "answer": "Absolutely. We use enterprise-grade security and never store your sensitive data permanently.",
        },
    ]

    return {
        "brand_name": brand_data.get("brand_name", "Demo Site"),
        "tagline": brand_data.get("tagline", ""),
        "headline": website_copy.get(
            "hero_headline", copy_data.get("headlines", ["Transform Your Workflow"])[0]
        ),
        "description": brand_data.get(
            "value_proposition", "The best solution for your needs"
        ),
        "features": features,
        "pricing_plans": [],
        "testimonials": testimonials,
        "faqs": faqs,
    }


# =============================================================================
# UPDATED AGENT DEFINITIONS
# =============================================================================

# Create the builder agents with updated landing builder
brand_creator_agent = LlmAgent(
    name="brand_creator_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=BRAND_CREATOR_PROMPT,
    description="Creates compelling brand identities for liminal market opportunities",
    tools=[
        FunctionTool(func=create_brand_identity),
        FunctionTool(func=generate_domain_suggestions),
        FunctionTool(func=assess_trademark_risks),
    ],
    output_key="brand_identity",
)

copy_writer_agent = LlmAgent(
    name="copy_writer_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=COPY_WRITER_PROMPT,
    description="Generates high-converting copy for early-stage market validation",
    tools=[
        FunctionTool(func=generate_marketing_copy),
        FunctionTool(func=generate_website_copy),
        FunctionTool(func=generate_email_sequences),
        FunctionTool(func=generate_social_copy),
    ],
    output_key="marketing_copy",
)

# UPDATED: Landing builder now deploys instead of returning code
landing_builder_agent = LlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=f"""
    You are a Landing Builder Agent that creates and DEPLOYS custom, high-converting landing pages to the In-Memory Webpage Renderer service at {RENDERER_SERVICE_URL}.

    CRITICAL: Your role is to BUILD and DEPLOY, not return code.

    Your process:
    1. Analyze brand identity and opportunity data
    2. Generate all required assets (HTML, CSS, JS, content)
    3. Deploy directly to the renderer service
    4. Return live URLs and functionality description

    SUCCESS CRITERIA:
    - Return live_url, admin_url, analytics_url - NOT code
    - Provide comprehensive functionality description
    - Include testing instructions for market validation
    - Explain all available features and analytics capabilities

    RESPONSE FORMAT:
    {{
        "deployment_status": "success",
        "brand_name": "Brand Name",
        "live_url": "{settings.RENDERER_SERVICE_URL}/site/abc123",
        "admin_url": "{settings.RENDERER_SERVICE_URL}/admin/abc123",
        "analytics_url": "{settings.RENDERER_SERVICE_URL}/analytics/abc123",
        "functionality_description": {{"overview": "...", "key_features": [...]}},
        "testing_instructions": {{"validation_checklist": [...]}},
        "success_message": "🚀 Brand Name is now live and ready for validation!"
    }}

    Focus on deployment success and providing actionable next steps for market validation.
    """,
    description="Builds and deploys renderer-service compatible landing pages with live URLs",
    tools=[
        FunctionTool(func=build_and_deploy_landing_page),
        FunctionTool(func=get_deployment_status),
        FunctionTool(func=generate_functionality_description),
        FunctionTool(func=generate_testing_instructions),
    ],
    output_key="deployment_result",
)
