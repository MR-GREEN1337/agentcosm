"""
Builder Agents - Create testable business assets from validated opportunities
Updated with dynamic code generation for renderer service compatibility
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime
from cosm.config import MODEL_CONFIG
from cosm.prompts import (
    BRAND_CREATOR_PROMPT,
    COPY_WRITER_PROMPT,
)
from litellm import completion
from cosm.settings import settings

client = Client()

# =============================================================================
# BRAND CREATOR AGENT (unchanged)
# =============================================================================


def create_brand_identity(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates comprehensive brand identity for a market opportunity
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

        if response and response.text:
            return json.loads(response.text)

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
# COPY WRITER AGENT (unchanged)
# =============================================================================


def generate_marketing_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates comprehensive marketing copy for the opportunity
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

        if response and response.text:
            return json.loads(response.text)

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

        if response and response.text:
            return json.loads(response.text)

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
# LANDING BUILDER AGENT (UPDATED FOR DYNAMIC GENERATION)
# =============================================================================


def build_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Builds a complete landing page ready for deployment to the renderer service
    """
    landing_page = {
        "metadata": {
            "title": "",
            "description": "",
            "keywords": [],
            "created_at": datetime.now().isoformat(),
        },
        "html_template": "",
        "css_styles": "",
        "javascript": "",
        "content_data": {},
        "deployment_config": {},
        "analytics_config": {},
        "conversion_tracking": {},
        "deployment_payload": {},  # Added for renderer service
    }

    try:
        # Generate design requirements first
        design_requirements = generate_design_requirements(brand_data, opportunity_data)

        # Generate page metadata
        landing_page["metadata"] = generate_page_metadata(brand_data, copy_data)

        # Generate dynamic HTML template (Jinja2 compatible)
        landing_page["html_template"] = generate_html_template(
            brand_data, copy_data, design_requirements
        )

        # Generate dynamic CSS styles
        landing_page["css_styles"] = generate_css_styles(
            brand_data, design_requirements
        )

        # Generate dynamic JavaScript
        landing_page["javascript"] = generate_javascript_code(
            brand_data, design_requirements
        )

        # Prepare content data for renderer service
        landing_page["content_data"] = prepare_content_data(
            brand_data, copy_data, opportunity_data
        )

        # Configure deployment
        landing_page["deployment_config"] = generate_deployment_config(brand_data)

        # Configure analytics
        landing_page["analytics_config"] = generate_analytics_config()

        # Prepare complete deployment payload for renderer service
        landing_page["deployment_payload"] = prepare_deployment_payload(
            brand_data, copy_data, opportunity_data, landing_page
        )

        return landing_page

    except Exception as e:
        print(f"Error building landing page: {e}")
        landing_page["error"] = str(e)
        return landing_page


def generate_design_requirements(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate specific design requirements based on brand and opportunity"""

    visual_identity = brand_data.get("visual_identity", {})
    brand_personality = brand_data.get("brand_personality", {})
    target_audience = brand_data.get("target_audience", "")

    # Determine design style based on brand personality
    personality_traits = brand_personality.get("personality_traits", [])
    voice = brand_personality.get("voice", "professional")

    # Map personality to design constraints
    design_style = "modern-minimal"
    if "innovative" in personality_traits or "cutting-edge" in voice.lower():
        design_style = "futuristic-bold"
    elif "friendly" in personality_traits or "approachable" in voice.lower():
        design_style = "warm-friendly"
    elif "premium" in personality_traits or "luxury" in voice.lower():
        design_style = "premium-elegant"

    # Determine layout complexity based on opportunity type
    opportunity_type = opportunity_data.get("type", "standard")
    complexity = "medium"
    if opportunity_type in ["enterprise", "b2b"]:
        complexity = "high"
    elif opportunity_type in ["consumer", "simple"]:
        complexity = "low"

    return {
        "design_style": design_style,
        "layout_complexity": complexity,
        "color_palette": visual_identity.get(
            "color_palette", ["#2563eb", "#1e40af", "#3b82f6"]
        ),
        "typography_style": visual_identity.get("typography", "modern-sans"),
        "brand_voice": voice,
        "personality_traits": personality_traits,
        "target_audience": target_audience,
        "conversion_focus": "early_signup",
        "mobile_priority": True,
        "accessibility_level": "wcag_aa",
        "animation_level": "subtle",
        "sections_required": [
            "hero",
            "problem",
            "solution",
            "social_proof",
            "cta",
            "faq",
        ],
    }


def generate_html_template(
    brand_data: Dict[str, Any] = None,
    copy_data: Dict[str, Any] = None,
    design_requirements: Dict[str, Any] = None,
) -> str:
    """Generate dynamic HTML template with Jinja2 syntax for renderer service"""

    if brand_data is None:
        brand_data = {}
    if copy_data is None:
        copy_data = {}
    if design_requirements is None:
        design_requirements = generate_design_requirements(brand_data, {})

    try:
        prompt = f"""
        Create a complete HTML template for the In-Memory Webpage Renderer service:

        BRAND DATA:
        {json.dumps(brand_data, indent=2)}

        COPY DATA:
        {json.dumps(copy_data, indent=2)}

        DESIGN REQUIREMENTS:
        {json.dumps(design_requirements, indent=2)}

        CRITICAL REQUIREMENTS:

        1. JINJA2 TEMPLATE FORMAT:
        - Use {{{{ variable_name }}}} for all dynamic content
        - Available variables: brand_name, tagline, headline, description, features, pricing_plans, testimonials, faqs, current_year, site_url
        - Use {{% for feature in features %}} loops for dynamic lists

        2. NO EMBEDDED CSS OR JAVASCRIPT:
        - Do NOT include <style> or <script> tags
        - Renderer service will inject CSS and JS separately

        3. ANALYTICS READY:
        - Add data-track attributes: data-track="cta-primary", data-track="feature-click", etc.
        - Include onclick="trackEvent('event_name')" for key interactions

        4. RESPONSIVE STRUCTURE:
        - Semantic HTML5 elements
        - Mobile-first structure
        - Proper accessibility attributes

        5. DESIGN STYLE: {design_requirements.get('design_style', 'modern-minimal')}
        - Reflect this style in the HTML structure and class names

        6. REQUIRED SECTIONS:
        - Header with navigation
        - Hero section with main CTA
        - Features section using {{{{ features }}}} loop
        - Testimonials using {{{{ testimonials }}}} loop
        - Pricing using {{{{ pricing_plans }}}} loop (if applicable)
        - FAQ using {{{{ faqs }}}} loop
        - CTA section with form
        - Footer

        Generate complete HTML with proper Jinja2 templating syntax.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.text:
            # Clean up any accidental CSS/JS inclusions
            html = response.text.strip()
            html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
            html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
            return html

    except Exception as e:
        print(f"Error generating dynamic HTML: {e}")

    # Fallback template with Jinja2 syntax
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ headline }} | {{ brand_name }}</title>
    <meta name="description" content="{{ description }}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
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
            <button class="cta-primary" data-track="cta-primary" onclick="trackEvent('hero_cta_click')">Get Started</button>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2>Why Choose {{ brand_name }}?</h2>
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card" data-track="feature-click">
                    <div class="feature-icon">{{ feature.icon }}</div>
                    <h3>{{ feature.title }}</h3>
                    <p>{{ feature.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="testimonials">
        <div class="container">
            <h2>What Our Users Say</h2>
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
    brand_data: Dict[str, Any], design_requirements: Dict[str, Any] = None
) -> str:
    """Generate dynamic CSS styles based on brand identity and design requirements"""

    if design_requirements is None:
        design_requirements = generate_design_requirements(brand_data, {})

    visual_identity = brand_data.get("visual_identity", {})
    colors = visual_identity.get("color_palette", ["#2563eb", "#1e40af", "#3b82f6"])
    design_style = design_requirements.get("design_style", "modern-minimal")

    try:
        prompt = f"""
        Create CSS styles for the In-Memory Webpage Renderer service:

        BRAND DATA:
        {json.dumps(brand_data, indent=2)}

        DESIGN REQUIREMENTS:
        {json.dumps(design_requirements, indent=2)}

        CRITICAL REQUIREMENTS:

        1. STANDALONE CSS (no <style> tags):
        - Will be injected by renderer service
        - Must work independently

        2. BRAND-SPECIFIC STYLING:
        - Primary color: {colors[0] if colors else '#2563eb'}
        - Secondary colors: {colors[1:] if len(colors) > 1 else ['#1e40af']}
        - Design style: {design_style}

        3. DESIGN STYLE INTERPRETATION:
        - "futuristic-bold": Gradients, geometric shapes, neon accents, bold shadows
        - "warm-friendly": Rounded corners, soft shadows, warm colors, approachable fonts
        - "premium-elegant": Minimalist, luxury typography, sophisticated colors, subtle effects
        - "modern-minimal": Clean lines, ample whitespace, simple typography, restrained colors

        4. ANALYTICS INTEGRATION:
        - Style [data-track] elements with hover effects
        - Prominent CTA button styling
        - Form styling that encourages completion

        5. RESPONSIVE DESIGN:
        - Mobile-first approach
        - Breakpoints: 768px, 1024px, 1440px
        - CSS Grid and Flexbox

        Generate complete CSS that reflects the brand personality and creates a unique visual identity.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.text:
            return response.text.strip()

    except Exception as e:
        print(f"Error generating dynamic CSS: {e}")

    # Fallback CSS
    primary_color = colors[0] if colors else "#2563eb"
    secondary_color = colors[1] if len(colors) > 1 else "#1e40af"

    return f"""
/* Dynamic CSS for {brand_data.get('brand_name', 'Brand')} */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

/* Analytics-ready elements */
[data-track] {{ cursor: pointer; transition: all 0.3s ease; }}
[data-track]:hover {{ transform: translateY(-2px); }}

/* Header */
.header {{ background: white; padding: 1rem 0; border-bottom: 1px solid #e5e7eb; }}
.header .container {{ display: flex; justify-content: space-between; align-items: center; }}
.logo {{ font-size: 1.5rem; font-weight: 700; color: {primary_color}; }}

/* CTA Buttons */
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
.cta-primary:hover, .cta-nav:hover {{
    background: {secondary_color};
    transform: translateY(-2px);
}}

/* Hero */
.hero {{ padding: 4rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }}
.hero h1 {{ font-size: 3rem; margin-bottom: 1rem; color: #1f2937; }}
.hero p {{ font-size: 1.25rem; color: #6b7280; margin-bottom: 2rem; }}

/* Features */
.features {{ padding: 4rem 0; }}
.features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
.feature-card {{
    padding: 2rem;
    border-radius: 8px;
    background: #f8fafc;
    transition: all 0.3s ease;
    border: 1px solid #e5e7eb;
}}
.feature-card:hover {{ transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}

/* Testimonials */
.testimonials {{ padding: 4rem 0; background: #f8fafc; }}
.testimonials-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; }}
.testimonial-card {{
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid {primary_color};
}}

/* CTA Section */
.cta-section {{
    padding: 4rem 0;
    background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
    color: white;
    text-align: center;
}}
.signup-form {{ max-width: 400px; margin: 0 auto; }}
.signup-form input {{
    width: 100%;
    padding: 1rem;
    margin-bottom: 1rem;
    border: none;
    border-radius: 6px;
}}

/* Footer */
.footer {{ background: #1f2937; color: white; padding: 2rem 0; text-align: center; }}

/* Responsive */
@media (max-width: 768px) {{
    .hero h1 {{ font-size: 2rem; }}
    .features-grid {{ grid-template-columns: 1fr; }}
    .testimonials-grid {{ grid-template-columns: 1fr; }}
}}
"""


def generate_javascript_code(
    brand_data: Dict[str, Any], design_requirements: Dict[str, Any] = None
) -> str:
    """Generate dynamic JavaScript compatible with renderer service analytics"""

    if design_requirements is None:
        design_requirements = generate_design_requirements(brand_data, {})

    try:
        prompt = f"""
        Create JavaScript for the In-Memory Webpage Renderer service:

        BRAND DATA:
        {json.dumps(brand_data, indent=2)}

        DESIGN REQUIREMENTS:
        {json.dumps(design_requirements, indent=2)}

        CRITICAL REQUIREMENTS:

        1. RENDERER SERVICE INTEGRATION:
        - window.SITE_ID is provided by the service
        - trackEvent(eventType, eventData) function is provided
        - Do NOT redefine these functions
        - Code will be injected before </body>

        2. REQUIRED ANALYTICS:
        - Auto-track all [data-track] element clicks
        - Track form submissions with validation
        - Track scroll depth (25%, 50%, 75%, 100%)
        - Track engagement metrics

        3. BRAND-SPECIFIC INTERACTIONS:
        - Animation level: {design_requirements.get('animation_level', 'subtle')}
        - Conversion focus: {design_requirements.get('conversion_focus', 'signup')}
        - Design style: {design_requirements.get('design_style', 'modern-minimal')}

        4. FORM HANDLING:
        - Validate email addresses
        - Provide user feedback
        - Track conversion funnel

        5. UX ENHANCEMENTS:
        - Smooth scrolling
        - Progressive enhancement
        - Mobile-friendly interactions

        Generate JavaScript that enhances the user experience and provides comprehensive analytics.
        Do NOT include <script> tags.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.text:
            js = response.text.strip()
            # Clean up any script tags
            js = re.sub(r"<script[^>]*>", "", js)
            js = re.sub(r"</script>", "", js)
            return js

    except Exception as e:
        print(f"Error generating dynamic JavaScript: {e}")

    # Fallback JavaScript
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

        // Basic email validation
        if (!email || !email.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }

        const data = Object.fromEntries(formData.entries());

        trackEvent('form_submit', {
            form_type: 'signup',
            has_email: !!email,
            timestamp: new Date().toISOString()
        });

        // Form submission feedback
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;

        setTimeout(() => {
            submitBtn.textContent = 'Thank you!';
            form.reset();
            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        }, 1000);
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

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Enhanced hover effects for tracked elements
document.querySelectorAll('[data-track]').forEach(el => {
    el.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });

    el.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
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
                    "category": benefit.get("category", "benefit"),
                }
            )
        else:
            features.append(
                {
                    "title": f"Feature {i+1}",
                    "description": str(benefit),
                    "icon": "⚡",
                    "category": "benefit",
                }
            )

    # Default features if none exist
    if not features:
        features = [
            {
                "title": "Easy Integration",
                "description": "Connect with your existing tools in minutes",
                "icon": "🔗",
                "category": "integration",
            },
            {
                "title": "Save Time",
                "description": "Automate repetitive tasks and focus on what matters",
                "icon": "⏰",
                "category": "productivity",
            },
            {
                "title": "Secure & Reliable",
                "description": "Enterprise-grade security and 99.9% uptime",
                "icon": "🔒",
                "category": "security",
            },
        ]

    # Prepare testimonials
    testimonials = [
        {
            "quote": "This solution transformed our workflow completely.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechCorp",
            "rating": 5,
        },
        {
            "quote": "We're saving 10+ hours per week on manual tasks.",
            "author": "Mike Chen",
            "title": "Team Lead",
            "company": "StartupXYZ",
            "rating": 5,
        },
    ]

    # Prepare pricing plans
    pricing_plans = opportunity_data.get("pricing", [])
    if not pricing_plans:
        pricing_plans = [
            {
                "name": "Starter",
                "price": "Free",
                "period": "",
                "features": ["Basic automation", "2 integrations", "Email support"],
                "cta": "Get Started",
                "highlighted": False,
            },
            {
                "name": "Professional",
                "price": "$29",
                "period": "/month",
                "features": [
                    "Advanced automation",
                    "Unlimited integrations",
                    "Priority support",
                ],
                "cta": "Start Free Trial",
                "highlighted": True,
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
        "pricing_plans": pricing_plans,
        "testimonials": testimonials,
        "faqs": faqs,
    }


def prepare_deployment_payload(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    landing_page: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare complete deployment payload for renderer service"""

    content_data = landing_page.get("content_data", {})

    # Prepare website assets
    assets = {
        "html_template": landing_page.get("html_template", ""),
        "css_styles": landing_page.get("css_styles", ""),
        "javascript": landing_page.get("javascript", ""),
        "config": {
            "responsive": True,
            "analytics_enabled": True,
            "conversion_tracking": True,
        },
    }

    # Prepare meta data
    meta_data = {
        "title": f"{content_data.get('brand_name', '')} - {content_data.get('tagline', '')}",
        "description": content_data.get("description", "")[:160],
        "keywords": [
            content_data.get("brand_name", "").lower(),
            "workflow automation",
            "productivity tools",
            "business integration",
        ],
        "og_title": content_data.get("headline", ""),
        "og_description": content_data.get("description", ""),
        "brand_style": brand_data.get("visual_identity", {}),
        "opportunity_type": opportunity_data.get("type", "standard"),
    }

    # Prepare analytics config
    analytics = {
        "conversion_events": ["cta-primary", "cta-secondary", "form-submit"],
        "engagement_tracking": True,
        "scroll_tracking": True,
        "exit_intent": True,
    }

    return {
        "site_name": brand_data.get("brand_name", "Landing Page")
        .lower()
        .replace(" ", "-"),
        "assets": assets,
        "content_data": content_data,
        "meta_data": meta_data,
        "analytics": analytics,
    }


def generate_page_metadata(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate SEO and meta data for the page"""

    brand_name = brand_data.get("brand_name", "Solution")
    headlines = copy_data.get("headlines", [])
    primary_headline = (
        headlines[0] if headlines else f"{brand_name} - Workflow Automation"
    )

    return {
        "title": f"{primary_headline} | {brand_name}",
        "description": brand_data.get(
            "value_proposition", "Automate your workflow and eliminate manual processes"
        )[:160],
        "keywords": [
            brand_name.lower(),
            "workflow automation",
            "productivity tools",
            "integration platform",
            "business automation",
        ],
        "og_title": primary_headline,
        "og_description": brand_data.get("value_proposition", ""),
        "og_image": "/images/og-image.jpg",
    }


def generate_deployment_config(brand_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate deployment configuration"""
    brand_name = brand_data.get("brand_name", "solution").lower()
    clean_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name)

    return {
        "site_name": f"{clean_name}-landing",
        "suggested_domains": [
            f"{clean_name}.com",
            f"get{clean_name}.com",
            f"{clean_name}app.com",
        ],
        "environment": "staging",
        "ssl_required": True,
        "custom_domain_ready": True,
    }


def generate_analytics_config() -> Dict[str, Any]:
    """Generate analytics configuration"""
    return {
        "google_analytics": {"enabled": True, "property_id": "GA_MEASUREMENT_ID"},
        "conversion_tracking": {
            "form_submissions": True,
            "button_clicks": True,
            "scroll_depth": True,
            "exit_intent": True,
        },
        "heatmap_tracking": {"enabled": True, "provider": "hotjar"},
        "a_b_testing": {
            "enabled": True,
            "tests": ["headline_variants", "cta_button_colors", "form_length"],
        },
    }


# Create the builder agents (updated landing builder agent)
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

landing_builder_agent = LlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG.get("openai_model"),
    instruction="""
    You are a Landing Builder Agent that creates custom, high-converting landing pages for the In-Memory Webpage Renderer service.

    CRITICAL SERVICE COMPATIBILITY:
    - Generate Jinja2 HTML templates with {{variable}} syntax
    - Create standalone CSS (no <style> tags - injected by service)
    - Create standalone JavaScript (no <script> tags - injected by service)
    - Use ContentData model variables: brand_name, tagline, headline, description, features, pricing_plans, testimonials, faqs
    - Include data-track attributes for analytics integration
    - Prepare complete deployment payload for the renderer API

    Your role:
    1. Analyze brand identity and opportunity data
    2. Generate design requirements matching brand personality
    3. Create Jinja2 HTML templates with proper variable usage
    4. Generate CSS that works with the renderer's injection system
    5. Create JavaScript that integrates with the service's analytics
    6. Prepare deployment payload in the exact format expected by the API

    Key principles:
    - Every landing page reflects the specific brand personality and colors
    - Design matches target audience expectations and market positioning
    - Code is renderer-service compatible and conversion-optimized
    - Mobile-first responsive design is mandatory
    - Analytics integration uses the service's trackEvent function
    - All content uses Jinja2 template variables for dynamic rendering

    Focus on creating unique, premium designs that convert while being fully compatible with the renderer service architecture.
    """,
    description="Builds renderer-service compatible landing pages with dynamic code generation",
    tools=[
        FunctionTool(func=build_landing_page),
        FunctionTool(func=generate_design_requirements),
        FunctionTool(func=generate_html_template),
        FunctionTool(func=generate_css_styles),
        FunctionTool(func=generate_javascript_code),
        FunctionTool(func=prepare_content_data),
        FunctionTool(func=prepare_deployment_payload),
    ],
    output_key="landing_page",
)
