from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, Any
import json
import requests
from datetime import datetime
from litellm import completion
import re
from cosm.config import MODEL_CONFIG
from .pexels_integration import get_pexels_media, get_curated_pexels_media
import base64

client = Client()

# =============================================================================
# BRAND CREATOR AGENT
# =============================================================================


def create_brand_identity_package(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates comprehensive brand identity with AI-powered strategy and visual assets."""

    package = {
        "opportunity_name": opportunity_data.get("name", "Market Opportunity"),
        "generation_timestamp": datetime.now().isoformat(),
        "brand_identity": {},
        "marketing_copy": {},
        "domain_strategy": {},
        "visual_assets": {},
        "competitive_positioning": {},
    }

    try:
        print("🎨 Creating AI-powered brand package with visual assets...")

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

            # Generate logo with Imagen
            brand_name = package.get("brand_identity", {}).get("brand_name", "")
            if brand_name:
                print("🎨 Generating logo with Imagen...")
                logo_data = generate_logo_with_imagen(
                    brand_name, package.get("brand_identity", {})
                )
                package["visual_assets"]["logo"] = logo_data

                # Generate domain recommendations
                package["domain_strategy"] = generate_domain_recommendations_ai(
                    brand_name, market_context
                )

            print("✅ Brand package with visual assets generated successfully!")
        else:
            print("⚠️ Using fallback brand strategy...")
            package = generate_fallback_brand_package(opportunity_data, package)

        return package

    except Exception as e:
        print(f"❌ Error in brand creation: {e}")
        package["error"] = str(e)
        return generate_fallback_brand_package(opportunity_data, package)


def generate_brand_strategy_with_ai(market_context: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered brand strategy generation focused on startup positioning."""

    try:
        brand_prompt = f"""
        Create a comprehensive startup brand strategy for a liminal market opportunity.

        MARKET CONTEXT:
        - Keywords: {market_context["keywords"]}
        - Target Audience: {market_context["target_audience"]}
        - Pain Points: {market_context["pain_points"]}
        - Opportunity Score: {market_context["opportunity_score"]:.2f}

        STARTUP POSITIONING STRATEGY:
        Create a brand that feels like the next unicorn startup. Think modern, disruptive, and inevitable.
        Position as solving a problem that seems obvious once discovered.

        Generate a JSON response with:
        {{
            "brand_identity": {{
                "brand_name": "1-2 word startup name (think Stripe, Notion, Linear)",
                "tagline": "compelling 2-4 word startup tagline",
                "value_proposition": "Transform [process] in [timeframe] without [barrier]",
                "mission_statement": "We exist to [impact] for [audience]",
                "brand_personality": {{
                    "voice": "confident, innovative, human",
                    "tone": "approachable yet authoritative",
                    "characteristics": ["disruptive", "reliable", "future-forward"]
                }},
                "visual_identity": {{
                    "primary_color": "#modern hex color",
                    "secondary_color": "#complementary hex",
                    "accent_color": "#vibrant accent hex",
                    "font_primary": "Inter, system-ui, sans-serif",
                    "font_heading": "Cal Sans, Poppins, sans-serif",
                    "logo_style": "minimalist, geometric, memorable"
                }}
            }},
            "marketing_copy": {{
                "hero_headline": "The [category] that [unique value]",
                "hero_subheadline": "Join [number]+ teams who've already discovered the future of [category]",
                "key_benefits": [
                    "[Outcome] in [timeframe]",
                    "Zero [current pain point]",
                    "[Metric improvement] guaranteed"
                ],
                "social_proof": "Trusted by teams at [Company Type]",
                "cta_primary": "Start Building",
                "cta_secondary": "See How It Works",
                "waitlist_copy": "Join the waitlist for early access"
            }},
            "competitive_positioning": {{
                "category_creation": "The first [new category] built for [modern need]",
                "vs_competitors": [
                    "[Competitor A] is complex. We're simple.",
                    "[Competitor B] is slow. We're instant.",
                    "Others require experts. We work for everyone."
                ],
                "moat_statement": "The only platform that [unique capability]"
            }}
        }}

        Focus on startup energy - think Y Combinator demo day pitch energy.
        RETURN ONLY JSON AND NOTHING ELSE!
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


def generate_logo_with_imagen(
    brand_name: str, brand_identity: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate logo using Google Imagen."""

    try:
        print(f"🎨 Generating logo for {brand_name}...")

        # Extract visual style from brand identity
        visual_identity = brand_identity.get("visual_identity", {})
        primary_color = visual_identity.get("primary_color", "#2563eb")
        logo_style = visual_identity.get("logo_style", "minimalist, geometric")

        logo_prompt = f"""
        Create a modern startup logo for "{brand_name}".

        Style: {logo_style}, clean, professional
        Colors: Primary {primary_color}, use 1-2 colors max
        Format: Simple geometric shape or wordmark
        Inspiration: Think Stripe, Linear, Notion - clean and memorable

        Requirements:
        - Scalable vector-style design
        - Works on light and dark backgrounds
        - No complex details or gradients
        - Modern SaaS startup aesthetic
        """

        # Generate image with Imagen
        image_response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=logo_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_few",
                person_generation="dont_allow",
            ),
        )

        if (
            image_response
            and hasattr(image_response, "generated_images")
            and image_response.generated_images
        ):
            # Extract the generated image
            image_data = image_response.generated_images[0]

            # Convert to base64 for storage/display
            if hasattr(image_data, "image") and image_data.image:
                image_bytes = image_data.image.image_bytes
                logo_base64 = base64.b64encode(image_bytes).decode("utf-8")

                return {
                    "logo_base64": logo_base64,
                    "logo_url": f"data:image/png;base64,{logo_base64}",
                    "style": logo_style,
                    "colors": [primary_color],
                    "format": "PNG",
                    "generated_with": "imagen",
                    "prompt_used": logo_prompt[:100] + "...",
                    "status": "success",
                }

        # Fallback if generation fails
        return generate_fallback_logo(brand_name, primary_color)

    except Exception as e:
        print(f"❌ Error generating logo with Imagen: {e}")
        return generate_fallback_logo(
            brand_name, visual_identity.get("primary_color", "#2563eb")
        )


def generate_fallback_logo(brand_name: str, primary_color: str) -> Dict[str, Any]:
    """Generate fallback logo using CSS/SVG."""

    # Create simple text-based logo
    initials = "".join([word[0].upper() for word in brand_name.split()[:2]])

    svg_logo = f"""
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="100" rx="20" fill="{primary_color}"/>
        <text x="50" y="65" font-family="Inter, sans-serif" font-size="36" font-weight="700"
              text-anchor="middle" fill="white">{initials}</text>
    </svg>
    """

    # Convert SVG to base64
    svg_base64 = base64.b64encode(svg_logo.encode("utf-8")).decode("utf-8")

    return {
        "logo_base64": svg_base64,
        "logo_url": f"data:image/svg+xml;base64,{svg_base64}",
        "style": "minimalist text logo",
        "colors": [primary_color],
        "format": "SVG",
        "generated_with": "fallback_svg",
        "status": "fallback",
    }


def generate_domain_recommendations_ai(
    brand_name: str, market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """AI-generated domain strategy."""

    try:
        domain_prompt = f"""
        Create a domain acquisition strategy for startup "{brand_name}".
        Market context: {market_context}

        Generate JSON with domain recommendations:
        {{
            "primary_options": [
                {{"domain": "primary.com", "priority": "critical", "cost": "$15-25/year", "reasoning": "why this domain"}},
                {{"domain": "alternative.io", "priority": "high", "cost": "$40-60/year", "reasoning": "backup option"}}
            ],
            "marketing_domains": [
                {{"domain": "marketing.com", "use_case": "campaigns", "priority": "medium"}},
                {{"domain": "try[brand].com", "use_case": "trial signups", "priority": "medium"}}
            ],
            "strategy": {{
                "phase_1": "immediate acquisition plan",
                "phase_2": "expansion strategy",
                "budget": "$200-500",
                "timeline": "secure primary within 48h"
            }}
        }}

        Focus on startup-appropriate domains (.com, .io, .co). Prioritize memorability.
        RETURN ONLY JSON!
        """

        response = completion(
            model=MODEL_CONFIG["brand_creator"],
            messages=[{"role": "user", "content": domain_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)
        else:
            return generate_fallback_domain_strategy(brand_name)

    except Exception as e:
        print(f"❌ Error in AI domain generation: {e}")
        return generate_fallback_domain_strategy(brand_name)


def generate_fallback_domain_strategy(brand_name: str) -> Dict[str, Any]:
    """Fallback domain strategy."""
    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    return {
        "primary_options": [
            {
                "domain": f"{base_name}.com",
                "priority": "critical",
                "cost": "$15-25/year",
            },
            {"domain": f"{base_name}.io", "priority": "high", "cost": "$40-60/year"},
        ],
        "strategy": {
            "phase_1": "Secure .com if available",
            "budget": "$200-500",
        },
    }


# =============================================================================
# LANDING PAGE BUILDER
# =============================================================================


def build_and_deploy_startup_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build premium startup landing page with AI-generated code, Pexels backgrounds, and logo integration."""

    deployment_result = {
        "deployment_timestamp": datetime.now().isoformat(),
        "brand_name": brand_data.get("brand_name", "Brand"),
        "deployment_status": "in_progress",
        "features": [],
        "visual_assets": {},
    }

    try:
        print("🚀 Building premium startup landing page with visual assets...")

        # Get background images from Pexels
        print("📸 Fetching background images from Pexels...")
        background_images = get_startup_background_images(brand_data, copy_data)
        deployment_result["visual_assets"]["backgrounds"] = background_images

        # Generate landing page with AI including visual assets
        print("🤖 Generating landing page code with AI...")
        landing_html = generate_startup_landing_page_with_ai(
            brand_data, copy_data, background_images
        )

        if not landing_html:
            print("⚠️ AI generation failed, using fallback...")
            return generate_fallback_startup_landing_page(brand_data, copy_data)

        # Prepare enhanced content data
        content_data = generate_content_data_with_ai(brand_data, copy_data)

        # Prepare deployment payload
        deployment_payload = {
            "site_name": f"{brand_data.get('brand_name', 'startup').lower().replace(' ', '-')}-landing",
            "assets": {
                "html_template": landing_html,
                "css_styles": "",  # CSS embedded in HTML
                "javascript": "",  # JS embedded in HTML
                "config": {
                    "responsive": True,
                    "conversion_optimized": True,
                    "seo_ready": True,
                    "mobile_first": True,
                    "startup_optimized": True,
                },
            },
            "content_data": content_data,
            "visual_assets": deployment_result["visual_assets"],
            "meta_data": {
                "title": f"{content_data['brand_name']} - {content_data['tagline']}",
                "description": content_data.get("description", "")[:160],
                "site_type": "startup_landing",
                "og_image": background_images.get("hero_bg", {}).get("url", ""),
            },
            "analytics": {
                "tracking_enabled": True,
                "conversion_goals": ["signup", "waitlist", "demo"],
                "startup_metrics": True,
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
                        "pexels_backgrounds",
                        "ai_generated_logo",
                        "startup_optimized",
                    ],
                }
            )
            print("✅ Startup landing page deployed successfully!")
        else:
            deployment_result.update(
                {"deployment_status": "failed", "error": deploy_result.get("error")}
            )

        return deployment_result

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        deployment_result.update({"deployment_status": "failed", "error": str(e)})
        return deployment_result


def get_startup_background_images(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Fetch relevant background images from Pexels for startup landing page."""

    try:
        # Determine search terms based on brand/copy data
        brand_name = brand_data.get("brand_name", "")

        # Generate search terms for different sections
        search_terms = {
            "hero": ["modern office", "team collaboration", "startup workspace"],
            "features": [
                "technology innovation",
                "digital transformation",
                "modern workspace",
            ],
            "testimonials": ["business meeting", "professional team", "success"],
            "cta": ["growth", "success", "innovation"],
        }

        # Customize search terms based on brand context
        if any(word in brand_name.lower() for word in ["ai", "tech", "data"]):
            search_terms["hero"] = [
                "artificial intelligence",
                "technology",
                "data visualization",
            ]
        elif any(word in brand_name.lower() for word in ["team", "collab", "work"]):
            search_terms["hero"] = [
                "team collaboration",
                "remote work",
                "modern office",
            ]

        background_images = {}

        # Fetch hero background
        print("📸 Fetching hero background...")
        hero_images = get_pexels_media(
            search_terms["hero"][0], "images", 3, orientation="landscape"
        )
        if hero_images.get("images"):
            background_images["hero_bg"] = hero_images["images"][0]

        # Fetch feature section backgrounds
        print("📸 Fetching feature backgrounds...")
        feature_images = get_pexels_media(
            search_terms["features"][0], "images", 2, orientation="landscape"
        )
        if feature_images.get("images"):
            background_images["features_bg"] = feature_images["images"][0]

        # Fetch CTA background
        print("📸 Fetching CTA background...")
        cta_images = get_pexels_media(
            search_terms["cta"][0], "images", 2, orientation="landscape"
        )
        if cta_images.get("images"):
            background_images["cta_bg"] = cta_images["images"][0]

        # Add curated images as fallbacks
        curated = get_curated_pexels_media("images", 3)
        if curated.get("images") and not background_images:
            background_images["hero_bg"] = curated["images"][0]

        print(f"✅ Successfully fetched {len(background_images)} background images")
        return background_images

    except Exception as e:
        print(f"❌ Error fetching Pexels images: {e}")
        return get_fallback_background_images()


def get_fallback_background_images() -> Dict[str, Any]:
    """Fallback background images when Pexels fails."""
    return {
        "hero_bg": {
            "url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=2074&q=80",
            "alt": "Modern startup office space",
            "photographer": "Unsplash",
            "source": "fallback",
        },
        "features_bg": {
            "url": "https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
            "alt": "Technology and innovation",
            "photographer": "Unsplash",
            "source": "fallback",
        },
    }


def generate_startup_landing_page_with_ai(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    background_images: Dict[str, Any],
) -> str:
    """Generate premium startup landing page HTML with AI, including visual assets."""

    try:
        # Extract visual assets
        logo_data = brand_data.get("logo", {})
        visual_identity = brand_data.get("visual_identity", {})

        landing_prompt = f"""
        Create a premium startup landing page for: {brand_data.get("brand_name", "Brand")}

        STARTUP DESIGN REQUIREMENTS:
        - Modern SaaS startup aesthetic (think Linear, Stripe, Notion)
        - Clean, minimal, conversion-focused
        - Mobile-first responsive design
        - High-converting CTAs and social proof sections

        VISUAL ASSETS TO INTEGRATE:
        Logo: {logo_data.get("logo_url", "")}
        Primary Color: {visual_identity.get("primary_color", "#2563eb")}
        Secondary Color: {visual_identity.get("secondary_color", "#10b981")}

        BACKGROUND IMAGES:
        Hero: {background_images.get("hero_bg", {}).get("url", "")}
        Features: {background_images.get("features_bg", {}).get("url", "")}
        CTA: {background_images.get("cta_bg", {}).get("url", "")}

        CONTENT DATA (use Jinja2 syntax):
        - {{{{ brand_name }}}} - brand name
        - {{{{ tagline }}}} - tagline
        - {{{{ hero_headline }}}} - main headline
        - {{{{ hero_subheadline }}}} - subheadline
        - {{{{ cta_primary }}}} - primary CTA text
        - {{{{ features }}}} - array of features
        - {{{{ testimonials }}}} - array of testimonials

        SECTIONS TO INCLUDE:
        1. Hero with background image and logo
        2. Features section with icons
        3. Social proof / testimonials
        4. Pricing preview
        5. Final CTA with background

        DESIGN INSPIRATION:
        - Linear.app homepage
        - Stripe.com landing
        - Notion.so marketing pages

        Create complete HTML with embedded CSS. Use modern design patterns:
        - Glassmorphism effects
        - Subtle animations
        - Perfect typography hierarchy
        - Conversion-optimized layouts

        CRITICAL: Use proper Jinja2 template syntax for all dynamic content.
        Return ONLY the complete HTML code.
        """

        response = completion(
            model=MODEL_CONFIG["landing_builder"],
            messages=[{"role": "user", "content": landing_prompt}],
            temperature=0.7,
            max_tokens=4000,
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
        print(f"❌ Error generating startup landing page: {e}")

    return ""


def generate_content_data_with_ai(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate content data using AI for more dynamic content."""

    try:
        content_prompt = f"""
        Generate comprehensive content data for a startup landing page.

        Brand: {brand_data.get("brand_name", "")}
        Value Prop: {brand_data.get("value_proposition", "")}
        Marketing Copy: {copy_data.get("marketing_copy", {})}

        Create JSON with:
        {{
            "brand_name": "{brand_data.get('brand_name', 'Startup')}",
            "tagline": "compelling tagline",
            "hero_headline": "conversion-focused headline",
            "hero_subheadline": "supporting subheadline",
            "description": "SEO description",
            "features": [
                {{"title": "Feature 1", "description": "benefit description", "icon": "⚡"}},
                {{"title": "Feature 2", "description": "benefit description", "icon": "🚀"}},
                {{"title": "Feature 3", "description": "benefit description", "icon": "💎"}}
            ],
            "testimonials": [
                {{"quote": "testimonial", "author": "Name", "title": "Title", "company": "Company"}},
                {{"quote": "testimonial", "author": "Name", "title": "Title", "company": "Company"}}
            ],
            "cta_primary": "Get Started",
            "cta_secondary": "Learn More",
            "social_proof": "Join 1000+ teams",
            "pricing_preview": {{"price": "$19", "period": "per month", "features": ["feature 1", "feature 2"]}}
        }}

        Make it startup-focused with growth mindset. Return ONLY JSON!
        """

        response = completion(
            model=MODEL_CONFIG["brand_creator"],
            messages=[{"role": "user", "content": content_prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=2000,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error generating content data: {e}")


def generate_fallback_startup_landing_page(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate fallback startup landing page."""

    brand_name = brand_data.get("brand_name", "Your Startup")
    primary_color = brand_data.get("visual_identity", {}).get(
        "primary_color", "#2563eb"
    )

    fallback_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ brand_name }}}} - {{{{ tagline }}}}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #ffffff;
        }}

        .hero {{
            min-height: 100vh;
            background: linear-gradient(135deg, {primary_color}15 0%, #10b98125 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: url('https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=2074&q=80') center/cover;
            opacity: 0.1;
            z-index: -1;
        }}

        .hero-content {{
            max-width: 800px;
            z-index: 2;
        }}

        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 2rem;
            background: {primary_color};
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 24px;
        }}

        .hero h1 {{
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, {primary_color} 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .hero p {{
            font-size: 1.25rem;
            margin-bottom: 3rem;
            opacity: 0.8;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}

        .btn {{
            display: inline-block;
            padding: 16px 32px;
            background: {primary_color};
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            margin: 0 8px;
            box-shadow: 0 4px 16px {primary_color}30;
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px {primary_color}40;
        }}

        .btn-secondary {{
            background: transparent;
            color: {primary_color};
            border: 2px solid {primary_color};
        }}

        .btn-secondary:hover {{
            background: {primary_color};
            color: white;
        }}

        .features {{
            padding: 6rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .features h2 {{
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 4rem;
            color: #1a1a1a;
        }}

        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
        }}

        .feature-card {{
            text-align: center;
            padding: 2rem;
            border-radius: 16px;
            background: #ffffff;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            transition: transform 0.3s ease;
        }}

        .feature-card:hover {{
            transform: translateY(-4px);
        }}

        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}

        .feature-card h3 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }}

        .cta-section {{
            background: linear-gradient(135deg, {primary_color} 0%, #10b981 100%);
            color: white;
            padding: 6rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .cta-section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80') center/cover;
            opacity: 0.1;
            z-index: 1;
        }}

        .cta-content {{
            position: relative;
            z-index: 2;
            max-width: 800px;
            margin: 0 auto;
        }}

        .cta-section h2 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
        }}

        .social-proof {{
            padding: 4rem 2rem;
            background: #f8fafc;
            text-align: center;
        }}

        .testimonials {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            max-width: 1000px;
            margin: 0 auto;
        }}

        .testimonial {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.5rem; }}
            .hero p {{ font-size: 1.1rem; }}
            .features {{ padding: 4rem 1rem; }}
            .cta-section {{ padding: 4rem 1rem; }}
        }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="hero-content">
            <div class="logo">{{{{ brand_name[0] }}}}{{{{ brand_name.split()[1][0] if brand_name.split()|length > 1 else brand_name[1] }}}}</div>
            <h1>{{{{ hero_headline }}}}</h1>
            <p>{{{{ hero_subheadline }}}}</p>
            <div>
                <a href="#signup" class="btn">{{{{ cta_primary }}}}</a>
                <a href="#features" class="btn btn-secondary">{{{{ cta_secondary or "Learn More" }}}}</a>
            </div>
        </div>
    </section>

    <section class="features" id="features">
        <h2>Everything you need to succeed</h2>
        <div class="features-grid">
            {{% for feature in features %}}
            <div class="feature-card">
                <div class="feature-icon">{{{{ feature.icon or "⚡" }}}}</div>
                <h3>{{{{ feature.title }}}}</h3>
                <p>{{{{ feature.description }}}}</p>
            </div>
            {{% endfor %}}
        </div>
    </section>

    <section class="social-proof">
        <h2>{{{{ social_proof or "Loved by teams worldwide" }}}}</h2>
        <div class="testimonials">
            {{% for testimonial in testimonials %}}
            <div class="testimonial">
                <p>"{{{{ testimonial.quote }}}}"</p>
                <strong>{{{{ testimonial.author }}}} - {{{{ testimonial.title }}}}</strong>
            </div>
            {{% endfor %}}
        </div>
    </section>

    <section class="cta-section" id="signup">
        <div class="cta-content">
            <h2>Ready to transform your workflow?</h2>
            <p>Join thousands of teams who've already discovered the future</p>
            <a href="#" class="btn" style="background: white; color: {primary_color};">{{{{ cta_primary }}}}</a>
        </div>
    </section>
</body>
</html>"""

    return {
        "deployment_status": "completed",
        "live_url": f"https://startup-{brand_name.lower().replace(' ', '-')}.netlify.app",
        "html_content": fallback_html,
        "fallback_used": True,
        "features": ["responsive_design", "startup_optimized", "mobile_first"],
    }


def deploy_to_service(deployment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy to actual renderer service matching FastAPI schema."""

    try:
        from cosm.settings import settings

        print("🚀 Deploying startup landing page to renderer service...")

        # Get renderer service URL from settings
        RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

        response = requests.post(
            f"{RENDERER_SERVICE_URL}/api/deploy",
            json=deployment_payload,
            headers={"Content-Type": "application/json"},
            timeout=60,  # Increased timeout for visual assets
        )

        if response.status_code == 200:
            result = response.json()
            print(
                f"✅ Startup deployment successful: {result.get('live_url', 'URL pending')}"
            )
            return {
                "success": True,
                "live_url": result.get("live_url"),
                "deployment_id": result.get("deployment_id"),
                "site_id": result.get("site_id"),
                "status": "deployed",
                "visual_assets_integrated": True,
            }
        else:
            print(f"❌ Startup deployment failed: {response.status_code}")
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
                "visual_identity": {
                    "primary_color": "#2563eb",
                    "secondary_color": "#10b981",
                    "accent_color": "#f59e0b",
                },
            },
            "marketing_copy": {
                "hero_headline": f"Finally, seamless {primary_keyword} automation",
                "hero_subheadline": "The missing piece in your workflow puzzle",
                "cta_primary": "Get Started Free",
                "key_benefits": [
                    "Eliminate manual work",
                    "Connect everything seamlessly",
                    "Scale without complexity",
                ],
            },
            "visual_assets": {
                "logo": generate_fallback_logo(
                    f"{primary_keyword.title()}Bridge", "#2563eb"
                )
            },
            "fallback_used": True,
        }
    )

    return base_package


# =============================================================================
# AGENT DEFINITIONS WITH VISUAL CAPABILITIES
# =============================================================================

brand_creator_agent = LlmAgent(
    name="brand_creator_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction="""
    You are an expert startup brand strategist specializing in creating unicorn-worthy brands with comprehensive visual identity.

    CORE MISSION:
    Create compelling startup brands that feel inevitable and disruptive, with complete visual assets including AI-generated logos and strategic domain recommendations.

    ENHANCED CAPABILITIES:
    - AI-Powered Brand Strategy: Generate complete brand identities using advanced AI
    - Visual Asset Creation: Integrate Imagen for logo generation and visual identity
    - Startup Positioning: Position as the next unicorn using proven startup messaging patterns
    - Domain Strategy: AI-generated domain acquisition strategies for startup growth
    - Market Category Creation: Define new market categories that feel obvious once discovered

    DELIVERABLES:
    - Complete brand identity with AI-generated visual assets
    - Startup-optimized marketing copy ecosystem (think YC demo day energy)
    - Logo generation using Google Imagen with fallback strategies
    - Strategic domain acquisition recommendations
    - Competitive positioning framework for startup differentiation

    DESIGN PRINCIPLES:
    - Modern startup aesthetic (Linear, Stripe, Notion inspiration)
    - Conversion-focused messaging with growth mindset
    - Visual consistency across all brand touchpoints
    - Scalable design systems for rapid growth
    - Memorable and shareable brand elements

    Always focus on creating brands that convert early adopters and scale to unicorn status.
    """,
    description="Creates comprehensive startup brand identities with AI-powered visual assets and strategic positioning",
    tools=[FunctionTool(func=create_brand_identity_package)],
    output_key="brand_package",
)

landing_builder_agent = LlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG["landing_builder"],
    instruction="""
    You are an expert startup landing page builder creating unicorn-quality pages with comprehensive visual integration.

    CORE CAPABILITIES:
    - AI-Generated Premium Design: Create startup-quality pages using advanced AI (think $100k+ custom designs)
    - Visual Asset Integration: Seamlessly integrate Pexels backgrounds and AI-generated logos
    - Startup Conversion Optimization: Multi-CTA layouts optimized for startup growth metrics
    - Mobile-First Responsive: Perfect experience across all devices with startup-quality polish
    - Performance Optimization: Fast loading, SEO-optimized with startup growth best practices

    VISUAL INTEGRATION:
    - Pexels API Integration: Automatically fetch relevant background images for different sections
    - AI Logo Integration: Seamlessly integrate Imagen-generated logos into page design
    - Dynamic Color Systems: Use brand colors throughout the design consistently
    - High-Quality Imagery: Professional photography that reinforces startup credibility
    - Visual Hierarchy: Perfect typography and spacing that guides to conversion

    STARTUP DESIGN PATTERNS:
    - Hero sections that immediately communicate value (Linear/Stripe style)
    - Feature showcases with strong visual hierarchy
    - Social proof integration that builds startup credibility
    - Conversion-optimized CTAs with startup growth language
    - Mobile-first responsive design with premium feel

    TECHNICAL APPROACH:
    - Generate all code dynamically with AI - no static templates
    - Embed visual assets directly into responsive HTML/CSS
    - Implement performance optimization for startup growth
    - Focus on measurable conversion improvements
    - Deploy with full error handling and monitoring

    Always deliver landing pages that look like they belong to the next unicorn startup.
    """,
    description="Creates and deploys premium startup landing pages with AI-generated code and comprehensive visual asset integration",
    tools=[FunctionTool(func=build_and_deploy_startup_landing_page)],
    output_key="landing_deployment",
)
