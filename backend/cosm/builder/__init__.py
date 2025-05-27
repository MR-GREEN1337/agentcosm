"""
Builder Agents - Create testable business assets from validated opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

from cosm.prompts import (
    BRAND_CREATOR_PROMPT,
    COPY_WRITER_PROMPT,
    LANDING_BUILDER_PROMPT,
)

client = Client()

# =============================================================================
# BRAND CREATOR AGENT
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.4
            ),
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
# COPY WRITER AGENT
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.4
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error generating core copy: {e}")

    return None


def generate_website_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, str]:
    """Generate website copy sections"""

    brand_name = brand_data.get("brand_name", "Solution")
    value_prop = brand_data.get("value_proposition", "Transform your workflow")

    website_copy = {
        "hero_headline": f"Finally, {value_prop.lower()}",
        "hero_subheadline": f"{brand_name} bridges the gap between your existing tools to eliminate manual work and reduce errors.",
        "problem_section": """
        **The Problem Everyone Faces**

        You're switching between multiple tools, copying data manually, and losing time on tasks that should be automated. Your workflow breaks down at the integration points, forcing you into inefficient workarounds.
        """,
        "solution_section": f"""
        **How {brand_name} Works**

        {brand_name} sits in the gap between your existing tools, automatically handling the connections and data transfers that currently require manual work. No complex setup, no workflow disruption - just intelligent automation where you need it most.
        """,
        "benefits_section": """
        **What You'll Achieve**

        - Eliminate manual data entry between systems
        - Reduce errors from copy-paste workflows
        - Save hours every week on repetitive tasks
        - Keep using the tools you already know
        - Scale your processes without scaling your effort
        """,
        "how_it_works": f"""
        **Simple Integration**

        1. **Connect**: Link {brand_name} to your existing tools (2-minute setup)
        2. **Configure**: Set up the automated workflows you need
        3. **Automate**: Watch as manual processes become seamless automation
        """,
        "cta_primary": "Start Automating Your Workflow",
        "cta_secondary": f"See {brand_name} in Action",
    }

    return website_copy


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
# LANDING BUILDER AGENT
# =============================================================================


def build_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Builds a complete landing page ready for deployment
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
    }

    try:
        # Generate page metadata
        landing_page["metadata"] = generate_page_metadata(brand_data, copy_data)

        # Generate HTML template
        landing_page["html_template"] = generate_html_template()

        # Generate CSS styles
        landing_page["css_styles"] = generate_css_styles(brand_data)

        # Generate JavaScript
        landing_page["javascript"] = generate_javascript_code()

        # Prepare content data
        landing_page["content_data"] = prepare_content_data(
            brand_data, copy_data, opportunity_data
        )

        # Configure deployment
        landing_page["deployment_config"] = generate_deployment_config(brand_data)

        # Configure analytics
        landing_page["analytics_config"] = generate_analytics_config()

        return landing_page

    except Exception as e:
        print(f"Error building landing page: {e}")
        landing_page["error"] = str(e)
        return landing_page


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


def generate_html_template() -> str:
    """Generate responsive HTML template"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <meta name="description" content="{{ description }}">
    <meta name="keywords" content="{{ keywords|join(', ') }}">

    <!-- Open Graph -->
    <meta property="og:title" content="{{ og_title }}">
    <meta property="og:description" content="{{ og_description }}">
    <meta property="og:image" content="{{ og_image }}">
    <meta property="og:type" content="website">

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="nav">
                <div class="logo">{{ brand_name }}</div>
                <button class="cta-button-nav">{{ cta_primary }}</button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-headline">{{ hero_headline }}</h1>
                <p class="hero-subheadline">{{ hero_subheadline }}</p>
                <div class="hero-cta">
                    <button class="cta-button-primary" onclick="scrollToDemo()">{{ cta_primary }}</button>
                    <button class="cta-button-secondary" onclick="trackEvent('secondary_cta_click')">{{ cta_secondary }}</button>
                </div>
            </div>
            <div class="hero-visual">
                <div class="demo-placeholder">
                    <div class="demo-screen">
                        <div class="demo-content">
                            <div class="tool-connection">
                                <div class="tool-box">Tool A</div>
                                <div class="connection-arrow">→</div>
                                <div class="bridge-box">{{ brand_name }}</div>
                                <div class="connection-arrow">→</div>
                                <div class="tool-box">Tool B</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Problem Section -->
    <section class="problem-section">
        <div class="container">
            <h2>The Problem Everyone Faces</h2>
            <div class="problem-grid">
                <div class="problem-item">
                    <div class="problem-icon">⚡</div>
                    <h3>Manual Data Entry</h3>
                    <p>Copy-pasting between tools wastes hours every week</p>
                </div>
                <div class="problem-item">
                    <div class="problem-icon">🔗</div>
                    <h3>Broken Workflows</h3>
                    <p>Your process stops working when tools don't connect</p>
                </div>
                <div class="problem-item">
                    <div class="problem-icon">❌</div>
                    <h3>Error-Prone Processes</h3>
                    <p>Manual handoffs introduce mistakes and inconsistencies</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Solution Section -->
    <section class="solution-section">
        <div class="container">
            <h2>How {{ brand_name }} Works</h2>
            <div class="solution-content">
                <div class="solution-text">
                    <p>{{ brand_name }} sits in the gap between your existing tools, automatically handling the connections and data transfers that currently require manual work.</p>
                    <ul class="benefits-list">
                        {% for benefit in benefits %}
                        <li>{{ benefit }}</li>
                        {% endfor %}
                    </ul>
                </div>
                <div class="solution-visual">
                    <div class="workflow-demo">
                        <div class="step">
                            <div class="step-number">1</div>
                            <div class="step-content">Connect your tools</div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div class="step-content">Configure workflows</div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div class="step-content">Automate everything</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Social Proof Section -->
    <section class="social-proof">
        <div class="container">
            <h2>Join Early Adopters Already Saving Time</h2>
            <div class="testimonials">
                <div class="testimonial">
                    <p>"Finally, a solution that connects our tools without disrupting our workflow."</p>
                    <div class="testimonial-author">- Sarah K., Operations Manager</div>
                </div>
                <div class="testimonial">
                    <p>"We're saving 10+ hours per week on manual data entry."</p>
                    <div class="testimonial-author">- Mike R., Team Lead</div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section" id="demo">
        <div class="container">
            <div class="cta-content">
                <h2>Ready to Eliminate Manual Work?</h2>
                <p>Join hundreds of teams already automating their workflows with {{ brand_name }}</p>

                <div class="signup-form">
                    <form id="early-access-form" onsubmit="handleFormSubmit(event)">
                        <div class="form-group">
                            <input type="email" id="email" placeholder="Enter your work email" required>
                            <input type="text" id="company" placeholder="Company name" required>
                        </div>
                        <button type="submit" class="cta-button-large">Get Early Access</button>
                    </form>
                    <p class="form-note">No spam. Unsubscribe anytime. Get notified when we launch.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section class="faq-section">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <h3>How quickly can I get started?</h3>
                    <p>Most teams are up and running within 15 minutes. Our setup is designed to be simple and non-disruptive.</p>
                </div>
                <div class="faq-item">
                    <h3>Will this replace my existing tools?</h3>
                    <p>No. {{ brand_name }} works with your existing tools to automate the connections between them.</p>
                </div>
                <div class="faq-item">
                    <h3>Is my data secure?</h3>
                    <p>Yes. We use enterprise-grade security and never store your sensitive data permanently.</p>
                </div>
                <div class="faq-item">
                    <h3>What tools do you integrate with?</h3>
                    <p>We support the most popular business tools and are constantly adding new integrations based on user requests.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-logo">{{ brand_name }}</div>
                <div class="footer-links">
                    <a href="#privacy">Privacy</a>
                    <a href="#terms">Terms</a>
                    <a href="#contact">Contact</a>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
"""


def generate_css_styles(brand_data: Dict[str, Any]) -> str:
    """Generate CSS styles based on brand identity"""

    visual_identity = brand_data.get("visual_identity", {})
    colors = visual_identity.get("color_palette", ["#2563eb", "#1e40af", "#3b82f6"])

    primary_color = colors[0] if colors else "#2563eb"
    secondary_color = colors[1] if len(colors) > 1 else "#1e40af"

    return f"""
/* Reset and Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: #1f2937;
    background-color: #ffffff;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.header {{
    background: white;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {primary_color};
}}

/* Buttons */
.cta-button-nav {{
    background: {primary_color};
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}}

.cta-button-primary {{
    background: {primary_color};
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.3);
}}

.cta-button-primary:hover {{
    background: {secondary_color};
    transform: translateY(-2px);
    box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4);
}}

.cta-button-secondary {{
    background: transparent;
    color: {primary_color};
    border: 2px solid {primary_color};
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    margin-left: 1rem;
}}

.cta-button-secondary:hover {{
    background: {primary_color};
    color: white;
}}

.cta-button-large {{
    background: {primary_color};
    color: white;
    border: none;
    padding: 1.2rem 2.5rem;
    border-radius: 8px;
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    max-width: 300px;
}}

/* Hero Section */
.hero {{
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 4rem 0;
    min-height: 70vh;
    display: flex;
    align-items: center;
}}

.hero .container {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
}}

.hero-headline {{
    font-size: 3rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
    color: #1f2937;
}}

.hero-subheadline {{
    font-size: 1.25rem;
    color: #6b7280;
    margin-bottom: 2rem;
    line-height: 1.6;
}}

.hero-cta {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}}

/* Demo Visual */
.demo-placeholder {{
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}}

.demo-screen {{
    background: #f8fafc;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
}}

.tool-connection {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}}

.tool-box {{
    background: #e5e7eb;
    padding: 1rem;
    border-radius: 6px;
    font-weight: 500;
    text-align: center;
    flex: 1;
}}

.bridge-box {{
    background: {primary_color};
    color: white;
    padding: 1rem;
    border-radius: 6px;
    font-weight: 600;
    text-align: center;
    flex: 1;
}}

.connection-arrow {{
    font-size: 1.5rem;
    color: {primary_color};
    font-weight: bold;
}}

/* Problem Section */
.problem-section {{
    padding: 4rem 0;
    background: white;
}}

.problem-section h2 {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 3rem;
    color: #1f2937;
}}

.problem-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}}

.problem-item {{
    text-align: center;
    padding: 2rem;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
}}

.problem-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.problem-item h3 {{
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1f2937;
}}

/* Solution Section */
.solution-section {{
    padding: 4rem 0;
    background: #f8fafc;
}}

.solution-section h2 {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 3rem;
    color: #1f2937;
}}

.solution-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
}}

.benefits-list {{
    list-style: none;
    margin-top: 1.5rem;
}}

.benefits-list li {{
    padding: 0.5rem 0;
    position: relative;
    padding-left: 1.5rem;
}}

.benefits-list li:before {{
    content: "✓";
    position: absolute;
    left: 0;
    color: {primary_color};
    font-weight: bold;
}}

.workflow-demo {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
}}

.step {{
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
}}

.step-number {{
    background: {primary_color};
    color: white;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-right: 1rem;
}}

/* Social Proof */
.social-proof {{
    padding: 4rem 0;
    background: white;
}}

.social-proof h2 {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 3rem;
    color: #1f2937;
}}

.testimonials {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}}

.testimonial {{
    background: #f8fafc;
    padding: 2rem;
    border-radius: 12px;
    border-left: 4px solid {primary_color};
}}

.testimonial p {{
    font-size: 1.1rem;
    font-style: italic;
    margin-bottom: 1rem;
}}

.testimonial-author {{
    font-weight: 600;
    color: #6b7280;
}}

/* CTA Section */
.cta-section {{
    padding: 4rem 0;
    background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
    color: white;
    text-align: center;
}}

.cta-content h2 {{
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
}}

.cta-content p {{
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

.signup-form {{
    max-width: 500px;
    margin: 0 auto;
}}

.form-group {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}}

.form-group input {{
    padding: 1rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
}}

.form-note {{
    font-size: 0.9rem;
    opacity: 0.8;
    margin-top: 1rem;
}}

/* FAQ Section */
.faq-section {{
    padding: 4rem 0;
    background: #f8fafc;
}}

.faq-section h2 {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 3rem;
    color: #1f2937;
}}

.faq-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}}

.faq-item {{
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

.faq-item h3 {{
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #1f2937;
}}

/* Footer */
.footer {{
    background: #1f2937;
    color: white;
    padding: 2rem 0;
}}

.footer-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.footer-logo {{
    font-size: 1.25rem;
    font-weight: 600;
}}

.footer-links {{
    display: flex;
    gap: 2rem;
}}

.footer-links a {{
    color: #d1d5db;
    text-decoration: none;
    transition: color 0.2s;
}}

.footer-links a:hover {{
    color: white;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .hero .container {{
        grid-template-columns: 1fr;
        text-align: center;
    }}

    .hero-headline {{
        font-size: 2rem;
    }}

    .solution-content {{
        grid-template-columns: 1fr;
    }}

    .testimonials {{
        grid-template-columns: 1fr;
    }}

    .hero-cta {{
        justify-content: center;
    }}

    .cta-button-secondary {{
        margin-left: 0;
        margin-top: 1rem;
    }}

    .form-group {{
        flex-direction: column;
    }}
}}
"""


def generate_javascript_code() -> str:
    """Generate JavaScript for interactions and analytics"""
    return """
// Smooth scrolling and interactions
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({
        behavior: 'smooth'
    });
    trackEvent('hero_cta_click');
}

// Form handling
function handleFormSubmit(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const company = document.getElementById('company').value;

    // Basic validation
    if (!email || !company) {
        alert('Please fill in all fields');
        return;
    }

    // Track form submission
    trackEvent('form_submit', {
        email: email,
        company: company
    });

    // Simulate API call
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    submitButton.textContent = 'Submitting...';
    submitButton.disabled = true;

    setTimeout(() => {
        submitButton.textContent = 'Thank you! We\\'ll be in touch.';
        document.getElementById('early-access-form').reset();

        // Show success message
        setTimeout(() => {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }, 3000);
    }, 1000);
}

// Analytics and event tracking
function trackEvent(eventName, eventData = {}) {
    // Google Analytics 4
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventData);
    }

    // Custom analytics
    if (window.analytics) {
        window.analytics.track(eventName, eventData);
    }

    // Console log for development
    console.log('Event tracked:', eventName, eventData);
}

// Scroll animations
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    document.querySelectorAll('.problem-item, .testimonial, .faq-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    observeElements();
    trackEvent('page_view');
});

// Track exit intent
document.addEventListener('mouseout', function(e) {
    if (e.toElement === null && e.relatedTarget === null) {
        trackEvent('exit_intent');
    }
});
"""


def prepare_content_data(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare all content data for template rendering"""

    website_copy = copy_data.get("website_copy", {})

    return {
        "brand_name": brand_data.get("brand_name", "Solution"),
        "title": f"{brand_data.get('brand_name', 'Solution')} - {brand_data.get('tagline', 'Workflow Automation')}",
        "description": brand_data.get(
            "value_proposition", "Automate your workflow and eliminate manual processes"
        ),
        "keywords": [
            "workflow automation",
            "productivity",
            "integration",
            "business tools",
        ],
        "og_title": website_copy.get("hero_headline", "Transform Your Workflow"),
        "og_description": brand_data.get("value_proposition", ""),
        "og_image": "/images/og-image.jpg",
        "hero_headline": website_copy.get(
            "hero_headline", "Finally, workflow automation that works"
        ),
        "hero_subheadline": website_copy.get(
            "hero_subheadline", "Connect your tools and eliminate manual work"
        ),
        "cta_primary": website_copy.get("cta_primary", "Get Early Access"),
        "cta_secondary": website_copy.get("cta_secondary", "See Demo"),
        "benefits": [
            "Eliminate manual data entry between systems",
            "Reduce errors from copy-paste workflows",
            "Save hours every week on repetitive tasks",
            "Keep using the tools you already know",
            "Scale your processes without scaling effort",
        ],
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


# Create the builder agents
brand_creator_agent = LlmAgent(
    name="brand_creator_agent",
    model="gemini-2.0-flash",
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
    model="gemini-2.0-flash",
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
    model="gemini-2.0-flash",
    instruction=LANDING_BUILDER_PROMPT,
    description="Builds high-converting landing pages for rapid market validation",
    tools=[
        FunctionTool(func=build_landing_page),
        FunctionTool(func=generate_html_template),
        FunctionTool(func=generate_css_styles),
        FunctionTool(func=generate_javascript_code),
    ],
    output_key="landing_page",
)
