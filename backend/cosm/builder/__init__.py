"""
Builder Agents - Landing Page Builder + Brand Creator
"""

from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
from litellm import completion
import re
import base64
import json
import time

from cosm.config import MODEL_CONFIG
from cosm.tools.pexels import get_pexels_media, get_curated_pexels_media
from cosm.prompts import BRAND_CREATOR_PROMPT, LANDING_BUILDER_PROMPT
from cosm.settings import settings
from cosm.utils import ResilientLlmAgent

client = Client()


# =============================================================================
# UTILS
# =============================================================================


def safe_json_parse_function_args(args_string: str) -> Dict[str, Any]:
    """
    Safely parse function call arguments with robust error handling.

    Args:
        args_string: Raw JSON string from LLM function call

    Returns:
        Parsed dictionary or empty dict if parsing fails
    """
    if not args_string or args_string.strip() == "":
        return {}

    try:
        # First attempt: direct parsing
        return json.loads(args_string)
    except json.JSONDecodeError as e:
        print(f"Initial JSON parse failed: {e}")

        # Second attempt: clean and retry
        cleaned_args = clean_json_string(args_string)
        try:
            return json.loads(cleaned_args)
        except json.JSONDecodeError as e2:
            print(f"Cleaned JSON parse failed: {e2}")

            # Third attempt: extract valid JSON portion
            extracted_json = extract_valid_json(args_string)
            if extracted_json:
                try:
                    return json.loads(extracted_json)
                except json.JSONDecodeError:
                    pass

            # Final fallback: return empty dict
            print(f"All JSON parsing attempts failed for: {args_string[:100]}...")
            return {}


def clean_json_string(json_str: str) -> str:
    """
    Clean common JSON formatting issues.
    """
    # Remove extra whitespace
    json_str = json_str.strip()

    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    # Fix common quote issues
    json_str = re.sub(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', json_str)

    # Remove control characters
    json_str = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", json_str)

    return json_str


def extract_valid_json(text: str) -> Optional[str]:
    """
    Extract the first valid JSON object from a string.
    """
    # Find potential JSON start
    start_indices = [i for i, char in enumerate(text) if char == "{"]

    for start in start_indices:
        brace_count = 0
        for i, char in enumerate(text[start:], start):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    potential_json = text[start : i + 1]
                    try:
                        json.loads(potential_json)
                        return potential_json
                    except json.JSONDecodeError:
                        continue

    return None


# =============================================================================
# ADVANCED BRAND CREATOR AGENT
# =============================================================================


def create_brand_identity(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Creates a brand identity with AI-powered strategy, visual assets, and competitive analysis."""

    package = {
        "opportunity_name": opportunity_data.get("name", "Market Opportunity"),
        "generation_timestamp": datetime.now().isoformat(),
        "brand_identity": {},
        "marketing_copy": {},
        "domain_strategy": {},
        "visual_assets": {},
        "competitive_positioning": {},
        "brand_guidelines": {},
        "marketing_channels": {},
        "content_strategy": {},
        "conversion_strategy": {},
    }

    try:
        print("🎨 Creating comprehensive AI-powered brand ecosystem...")

        # Extract and enrich market context
        market_context = {
            "keywords": opportunity_data.get("keywords", [])[:5],
            "target_audience": opportunity_data.get(
                "target_audience", "business users"
            ),
            "pain_points": opportunity_data.get("pain_points", [])[:5],
            "opportunity_score": opportunity_data.get("opportunity_score", 0.7),
            "market_size": opportunity_data.get("market_size", "emerging"),
            "competitive_landscape": opportunity_data.get("competitors", [])[:3],
            "funding_stage": opportunity_data.get("funding_stage", "pre-seed"),
        }

        # Generate comprehensive brand strategy with advanced AI
        brand_package = generate_advanced_brand_strategy(market_context)

        if brand_package and not brand_package.get("error"):
            package.update(brand_package)

            # Generate enhanced visual identity
            brand_name = package.get("brand_identity", {}).get("brand_name", "")
            if brand_name:
                print("🎨 Generating enhanced visual identity...")

                # Create logo variations
                logo_variations = generate_logo_variations(
                    brand_name, package.get("brand_identity", {})
                )
                package["visual_assets"]["logo_variations"] = logo_variations

                # Generate brand colors palette
                color_palette = generate_color_palette(
                    package.get("brand_identity", {})
                )
                package["visual_assets"]["color_palette"] = color_palette

                # Create typography system
                typography_system = generate_typography_system()
                package["visual_assets"]["typography_system"] = typography_system

                # Generate brand guidelines
                brand_guidelines = generate_brand_guidelines(package)
                package["brand_guidelines"] = brand_guidelines

                # Enhanced domain recommendations with SEO analysis
                package["domain_strategy"] = generate_advanced_domain_strategy(
                    brand_name, market_context
                )

                # Content marketing strategy
                package["content_strategy"] = generate_content_strategy(
                    package.get("brand_identity", {}), market_context
                )

                # Conversion optimization strategy
                package["conversion_strategy"] = generate_conversion_strategy(
                    package.get("brand_identity", {}), market_context
                )

            print("✅ Comprehensive brand ecosystem generated successfully!")
        else:
            print("⚠️ Using fallback brand strategy...")
            package = generate_fallback_brand_package(opportunity_data, package)

        return package

    except Exception as e:
        print(f"❌ Error in brand creation: {e}")
        package["error"] = str(e)
        return generate_fallback_brand_package(opportunity_data, package)


def robust_completion(model: str, messages: list, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Wrapper around completion() with enhanced error handling and retries.
    """
    max_retries = 3
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            response = completion(model=model, messages=messages[:1048576], **kwargs)

            # Validate response structure
            if response and hasattr(response, "choices") and response.choices:
                return response
            else:
                raise ValueError("Invalid response structure")

        except json.JSONDecodeError as e:
            print(f"JSON decode error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return None

        except Exception as e:
            print(f"Completion error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return None

        # Exponential backoff
        if attempt < max_retries - 1:
            delay = base_delay * (2**attempt)
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    return None


def generate_advanced_brand_strategy(market_context: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered comprehensive brand strategy generation with advanced market positioning."""

    try:
        brand_prompt = f"""
        Create a comprehensive startup brand strategy for a high-potential market opportunity.

        MARKET INTELLIGENCE:
        - Keywords: {market_context["keywords"]}
        - Target Audience: {market_context["target_audience"]}
        - Pain Points: {market_context["pain_points"]}
        - Opportunity Score: {market_context["opportunity_score"]:.2f}
        - Market Size: {market_context["market_size"]}
        - Competitive Landscape: {market_context["competitive_landscape"]}
        - Funding Stage: {market_context["funding_stage"]}

        ADVANCED BRAND STRATEGY:
        Create a brand that positions as the category-defining startup. Think unicorn potential with venture-scale thinking.
        Position as the inevitable future of this space - not just solving a problem, but reimagining the entire category.

        Generate a comprehensive JSON response:
        {{
            "brand_identity": {{
                "brand_name": "1-2 word category-defining name (think Notion, Figma, Stripe)",
                "tagline": "powerful 2-4 word manifesto",
                "brand_manifesto": "We believe [vision]. We're building [category] for [future state]",
                "value_proposition": "The only [category] that [unique capability] without [traditional barrier]",
                "mission_statement": "To [transform industry] by [unique approach] for [global impact]",
                "vision_statement": "A world where [transformed state] is the default",
                "brand_personality": {{
                    "voice": "visionary, confident, inevitable",
                    "tone": "bold yet approachable, future-focused",
                    "characteristics": ["category-defining", "inevitable", "transformative", "accessible"],
                    "brand_archetype": "The Revolutionary"
                }},
                "visual_identity": {{
                    "primary_color": "#modern sophisticated hex",
                    "secondary_color": "#complementary sophisticated hex",
                    "accent_color": "#vibrant distinctive hex",
                    "gradient_primary": "linear-gradient(135deg, #color1, #color2)",
                    "font_primary": "Inter, system-ui, sans-serif",
                    "font_heading": "Cal Sans, Poppins, sans-serif",
                    "font_mono": "JetBrains Mono, Fira Code, monospace",
                    "logo_style": "minimalist, memorable, scalable, timeless"
                }}
            }},
            "marketing_copy": {{
                "hero_headline": "The [category] that [transforms outcome]",
                "hero_subheadline": "Join [number]K+ [audience] who've discovered the future of [category]",
                "problem_statement": "[Current painful reality] is broken. We're fixing it.",
                "solution_statement": "Introducing [brand] - [revolutionary approach] that [outcome]",
                "key_benefits": [
                    "[Outcome] in [timeframe] - guaranteed",
                    "Zero [current pain point] - ever",
                    "[10x improvement] vs [old way]",
                    "[Unique capability] no one else has"
                ],
                "social_proof": "Trusted by [audience] at [company types]",
                "cta_primary": "Start Building",
                "cta_secondary": "See the Magic",
                "cta_waitlist": "Join 10K+ on Waitlist",
                "testimonial_hook": "\"This changes everything\" - [Customer Type]"
            }},
            "competitive_positioning": {{
                "category_creation": "The first [new category] purpose-built for [modern need]",
                "vs_legacy_players": "[Legacy] is yesterday. [Brand] is tomorrow.",
                "differentiation_matrix": [
                    "[Competitor A]: Complex → We: Simple",
                    "[Competitor B]: Slow → We: Instant",
                    "[Competitor C]: Expensive → We: Accessible",
                    "Everyone else: Incremental → We: Revolutionary"
                ],
                "moat_statement": "The only platform with [defensible unique capability]",
                "market_timing": "Why now: [market shift] + [technology enabler] = [opportunity]"
            }},
            "marketing_channels": {{
                "primary_channels": ["Product Hunt", "Twitter/X", "LinkedIn", "Developer Communities"],
                "content_pillars": ["Thought Leadership", "Product Education", "Industry Insights", "Community Building"],
                "launch_sequence": ["Stealth → Waitlist → Beta → Product Hunt → Scale"],
                "virality_mechanics": ["Referral program", "Public metrics", "Template marketplace"]
            }}
        }}

        Focus on venture-scale ambition. Think YC Demo Day energy meets enterprise-grade credibility.
        """

        response = robust_completion(
            model=MODEL_CONFIG["brand_creator"],
            api_key=settings.GOOGLE_API_KEY,
            messages=[{"role": "user", "content": brand_prompt[:1048576]}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=3000,
        )

        if response and response.choices[0].message.content:
            return safe_json_parse_function_args(response.choices[0].message.content)
        else:
            return {"error": "Empty AI response"}

    except Exception as e:
        print(f"❌ Error in advanced brand generation: {e}")
        return {"error": str(e)}


def generate_logo_variations(
    brand_name: str, brand_identity: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate multiple logo variations for different use cases."""

    try:
        print(f"🎨 Generating logo variations for {brand_name}...")

        visual_identity = brand_identity.get("visual_identity", {})
        primary_color = visual_identity.get("primary_color", "#2563eb")

        variations = {}

        # Primary logo
        variations["primary"] = generate_logo_with_imagen(brand_name, brand_identity)

        # Horizontal version
        horizontal_prompt = f"""
        Create a horizontal logo for "{brand_name}".
        Style: Clean, horizontal layout, modern startup aesthetic
        Colors: {primary_color} primary, minimal color usage
        Format: Wide aspect ratio, scalable design
        """

        # Icon-only version
        icon_prompt = f"""
        Create an icon-only logo for "{brand_name}".
        Style: Symbol/icon only, no text, minimal and memorable
        Colors: {primary_color}, works as app icon
        Format: Square, highly recognizable symbol
        """

        # Light/dark variations
        variations["horizontal"] = generate_custom_logo(horizontal_prompt)
        variations["icon_only"] = generate_custom_logo(icon_prompt)
        variations["light_version"] = create_light_logo_variation(
            brand_name, primary_color
        )
        variations["dark_version"] = create_dark_logo_variation(
            brand_name, primary_color
        )

        return variations

    except Exception as e:
        print(f"❌ Error generating logo variations: {e}")
        return {"error": str(e)}


def generate_color_palette(brand_identity: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive color palette system."""

    visual_identity = brand_identity.get("visual_identity", {})
    primary = visual_identity.get("primary_color", "#2563eb")
    secondary = visual_identity.get("secondary_color", "#10b981")
    accent = visual_identity.get("accent_color", "#f59e0b")

    return {
        "primary_palette": {
            "50": lighten_color(primary, 0.95),
            "100": lighten_color(primary, 0.9),
            "200": lighten_color(primary, 0.8),
            "300": lighten_color(primary, 0.6),
            "400": lighten_color(primary, 0.4),
            "500": primary,
            "600": darken_color(primary, 0.2),
            "700": darken_color(primary, 0.4),
            "800": darken_color(primary, 0.6),
            "900": darken_color(primary, 0.8),
        },
        "semantic_colors": {
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#3b82f6",
        },
        "neutral_palette": {
            "white": "#ffffff",
            "gray_50": "#f9fafb",
            "gray_100": "#f3f4f6",
            "gray_200": "#e5e7eb",
            "gray_300": "#d1d5db",
            "gray_400": "#9ca3af",
            "gray_500": "#6b7280",
            "gray_600": "#4b5563",
            "gray_700": "#374151",
            "gray_800": "#1f2937",
            "gray_900": "#111827",
            "black": "#000000",
        },
        "gradients": {
            "primary": f"linear-gradient(135deg, {primary}, {secondary})",
            "hero": f"linear-gradient(135deg, {primary}15, {secondary}25)",
            "accent": f"linear-gradient(135deg, {accent}, {primary})",
        },
    }


def generate_typography_system() -> Dict[str, Any]:
    """Generate a comprehensive typography system."""

    return {
        "font_stacks": {
            "primary": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "heading": "Cal Sans, 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif",
            "mono": "JetBrains Mono, 'Fira Code', Consolas, Monaco, monospace",
        },
        "type_scale": {
            "xs": "0.75rem",  # 12px
            "sm": "0.875rem",  # 14px
            "base": "1rem",  # 16px
            "lg": "1.125rem",  # 18px
            "xl": "1.25rem",  # 20px
            "2xl": "1.5rem",  # 24px
            "3xl": "1.875rem",  # 30px
            "4xl": "2.25rem",  # 36px
            "5xl": "3rem",  # 48px
            "6xl": "3.75rem",  # 60px
            "7xl": "4.5rem",  # 72px
            "8xl": "6rem",  # 96px
            "9xl": "8rem",  # 128px
        },
        "line_heights": {
            "none": "1",
            "tight": "1.25",
            "snug": "1.375",
            "normal": "1.5",
            "relaxed": "1.625",
            "loose": "2",
        },
        "font_weights": {
            "thin": "100",
            "extralight": "200",
            "light": "300",
            "normal": "400",
            "medium": "500",
            "semibold": "600",
            "bold": "700",
            "extrabold": "800",
            "black": "900",
        },
    }


def generate_brand_guidelines(package: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive brand guidelines."""

    brand_identity = package.get("brand_identity", {})

    return {
        "logo_usage": {
            "minimum_size": "24px width for digital, 0.5 inch for print",
            "clear_space": "Equal to the height of the logo mark on all sides",
            "backgrounds": ["White", "Light gray (#f9fafb)", "Dark navy (#1e293b)"],
            "dont_use": [
                "Don't stretch",
                "Don't rotate",
                "Don't add effects",
                "Don't change colors",
            ],
        },
        "color_usage": {
            "primary_use": "Headlines, CTAs, key UI elements",
            "secondary_use": "Supporting elements, icons, accents",
            "accessibility": "All combinations meet WCAG AA standards",
            "contrast_ratios": {
                "primary_on_white": "4.5:1",
                "text_on_primary": "4.5:1",
            },
        },
        "typography_usage": {
            "hierarchy": {
                "h1": "5xl-6xl, semibold, heading font",
                "h2": "3xl-4xl, semibold, heading font",
                "h3": "xl-2xl, medium, heading font",
                "body": "base-lg, normal, primary font",
                "caption": "sm, normal, primary font",
            },
            "line_spacing": "1.5 for body text, 1.2 for headings",
        },
        "voice_guidelines": {
            "tone": brand_identity.get("brand_personality", {}).get("tone", ""),
            "characteristics": brand_identity.get("brand_personality", {}).get(
                "characteristics", []
            ),
            "do_say": [
                "We believe",
                "Transform",
                "Future",
                "Inevitable",
                "Revolutionary",
            ],
            "dont_say": ["Traditional", "Legacy", "Complicated", "Eventually", "Maybe"],
        },
        "imagery_style": {
            "style": "Clean, modern, aspirational",
            "composition": "Minimal, lots of white space, geometric",
            "color_treatment": "Natural colors with brand accent overlays",
            "photography": "High-quality, professional, diverse, authentic",
        },
    }


def generate_advanced_domain_strategy(
    brand_name: str, market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Advanced domain strategy with SEO and marketing considerations."""

    try:
        base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

        domain_strategy = {
            "primary_domains": [
                {
                    "domain": f"{base_name}.com",
                    "priority": "critical",
                    "cost_estimate": "$15-25/year",
                    "seo_value": "highest",
                    "rationale": "Primary brand domain - essential for credibility",
                },
                {
                    "domain": f"{base_name}.io",
                    "priority": "high",
                    "cost_estimate": "$40-60/year",
                    "seo_value": "high",
                    "rationale": "Tech startup standard - developer credibility",
                },
                {
                    "domain": f"get{base_name}.com",
                    "priority": "medium",
                    "cost_estimate": "$15-25/year",
                    "seo_value": "medium",
                    "rationale": "Marketing funnel domain",
                },
            ],
            "marketing_domains": [
                {
                    "domain": f"try{base_name}.com",
                    "use_case": "trial signups, demos",
                    "priority": "medium",
                    "campaign_type": "acquisition",
                },
                {
                    "domain": f"{base_name}app.com",
                    "use_case": "app downloads, mobile",
                    "priority": "low",
                    "campaign_type": "mobile",
                },
                {
                    "domain": f"go{base_name}.com",
                    "use_case": "campaign tracking, UTM shortener",
                    "priority": "low",
                    "campaign_type": "performance",
                },
            ],
            "defensive_domains": [
                f"{base_name}.net",
                f"{base_name}.org",
                f"{base_name}.ai",
                f"{base_name}hq.com",
            ],
            "seo_strategy": {
                "primary_keywords": market_context.get("keywords", [])[:3],
                "domain_authority_plan": "Build DA through content, backlinks, consistent branding",
                "subdomain_strategy": {
                    "blog": f"blog.{base_name}.com",
                    "docs": f"docs.{base_name}.com",
                    "api": f"api.{base_name}.com",
                    "status": f"status.{base_name}.com",
                },
            },
            "acquisition_timeline": {
                "phase_1": "Secure .com and .io immediately",
                "phase_2": "Acquire marketing domains pre-launch",
                "phase_3": "Defensive registrations post-traction",
                "budget_total": "$500-1000 year 1, $200-400 ongoing",
            },
        }

        return domain_strategy

    except Exception as e:
        print(f"❌ Error in advanced domain strategy: {e}")
        return generate_fallback_domain_strategy(brand_name)


def generate_content_strategy(
    brand_identity: Dict[str, Any], market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate comprehensive content marketing strategy."""

    return {
        "content_pillars": {
            "thought_leadership": {
                "themes": [
                    "Industry transformation",
                    "Future of work",
                    "Technology trends",
                ],
                "formats": ["Long-form posts", "Industry reports", "Predictions"],
                "frequency": "2x per week",
            },
            "product_education": {
                "themes": ["How-to guides", "Best practices", "Use cases"],
                "formats": ["Tutorials", "Video demos", "Case studies"],
                "frequency": "3x per week",
            },
            "community_building": {
                "themes": ["User stories", "Behind the scenes", "Team insights"],
                "formats": ["User spotlights", "Team content", "Community highlights"],
                "frequency": "Daily",
            },
        },
        "channel_strategy": {
            "twitter": {
                "focus": "Thought leadership, real-time engagement",
                "posting_frequency": "3-5x daily",
                "content_mix": "70% industry insights, 20% product, 10% personal",
            },
            "linkedin": {
                "focus": "Professional content, B2B networking",
                "posting_frequency": "1x daily",
                "content_mix": "50% thought leadership, 30% product education, 20% company updates",
            },
            "blog": {
                "focus": "SEO, deep expertise, lead generation",
                "posting_frequency": "2x weekly",
                "content_mix": "60% educational, 25% thought leadership, 15% product",
            },
        },
        "launch_content": {
            "pre_launch": [
                "Stealth mode teasers",
                "Problem exploration content",
                "Founder story",
                "Industry trend analysis",
            ],
            "launch_week": [
                "Product Hunt launch",
                "Demo videos",
                "Customer stories",
                "Behind-the-scenes content",
            ],
            "post_launch": [
                "User onboarding content",
                "Advanced tutorials",
                "Community building",
                "Thought leadership",
            ],
        },
    }


def generate_conversion_strategy(
    brand_identity: Dict[str, Any], market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate conversion optimization strategy."""

    return {
        "funnel_stages": {
            "awareness": {
                "channels": ["Organic social", "SEO", "PR", "Content marketing"],
                "metrics": [
                    "Reach",
                    "Impressions",
                    "Brand mentions",
                    "Organic traffic",
                ],
                "optimization": "Content quality, SEO, social engagement",
            },
            "interest": {
                "channels": ["Blog", "Newsletter", "Webinars", "Free tools"],
                "metrics": ["Email signups", "Content engagement", "Time on site"],
                "optimization": "Lead magnets, content personalization",
            },
            "consideration": {
                "channels": ["Product demos", "Free trials", "Case studies"],
                "metrics": ["Demo requests", "Trial signups", "Sales qualified leads"],
                "optimization": "Demo quality, trial experience, social proof",
            },
            "conversion": {
                "channels": ["Sales team", "Self-serve signup", "Onboarding"],
                "metrics": ["Conversion rate", "Deal size", "Time to close"],
                "optimization": "Sales process, pricing, onboarding experience",
            },
        },
        "optimization_tactics": {
            "landing_pages": [
                "A/B test headlines",
                "Optimize CTA placement",
                "Test social proof elements",
                "Mobile optimization",
            ],
            "email_marketing": [
                "Drip campaigns",
                "Behavioral triggers",
                "Personalization",
                "Segmentation",
            ],
            "social_proof": [
                "Customer testimonials",
                "Usage statistics",
                "Media mentions",
                "Team credentials",
            ],
        },
        "kpis": {
            "acquisition": "Cost per acquisition < $50",
            "activation": "30-day active user rate > 80%",
            "retention": "6-month retention > 40%",
            "referral": "Viral coefficient > 0.5",
        },
    }


# Helper functions for color manipulation
def lighten_color(hex_color: str, factor: float) -> str:
    """Lighten a hex color by a factor (0-1)."""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    lightened = tuple(int(c + (255 - c) * factor) for c in rgb)
    return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"


def darken_color(hex_color: str, factor: float) -> str:
    """Darken a hex color by a factor (0-1)."""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    darkened = tuple(int(c * (1 - factor)) for c in rgb)
    return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


def generate_custom_logo(prompt: str) -> Dict[str, Any]:
    """Generate custom logo with given prompt."""
    # Simplified implementation - in real scenario would use Imagen API
    return {
        "logo_base64": "",
        "logo_url": "",
        "style": "custom generated",
        "prompt_used": prompt[:100] + "...",
        "status": "generated",
    }


def create_light_logo_variation(brand_name: str, color: str) -> Dict[str, Any]:
    """Create light theme logo variation."""
    return generate_fallback_logo(brand_name, color)


def create_dark_logo_variation(brand_name: str, color: str) -> Dict[str, Any]:
    """Create dark theme logo variation."""
    return generate_fallback_logo(brand_name, "#ffffff")


# =============================================================================
# ENHANCED LANDING PAGE BUILDER
# =============================================================================


def build_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build conversion-optimized startup landing page with advanced features."""

    deployment_result = {
        "deployment_timestamp": datetime.now().isoformat(),
        "brand_name": brand_data.get("brand_name", "Brand"),
        "deployment_status": "in_progress",
        "features": [],
        "visual_assets": {},
        "performance_metrics": {},
        "seo_optimization": {},
        "conversion_elements": {},
    }

    try:
        print("🚀 Building startup landing experience with advanced features...")

        # Get curated visual assets
        print("📸 Curating visual assets...")
        visual_assets = get_premium_visual_assets(brand_data, copy_data)
        deployment_result["visual_assets"] = visual_assets

        # Generate advanced landing page with AI
        print("🤖 Generating landing page with advanced AI...")
        landing_html = generate_landing_page_with_ai(brand_data, visual_assets)

        # Generate comprehensive content data
        content_data = generate_advanced_content_data(brand_data, copy_data)

        # Add conversion optimization features
        conversion_features = generate_conversion_features(brand_data, copy_data)
        deployment_result["conversion_elements"] = conversion_features

        # SEO optimization
        seo_data = generate_seo_optimization(brand_data, copy_data, content_data)
        deployment_result["seo_optimization"] = seo_data

        # Performance optimization
        performance_config = generate_performance_config()
        deployment_result["performance_metrics"] = performance_config

        # Prepare advanced deployment payload
        deployment_payload = {
            "site_name": f"{brand_data.get('brand_name', 'startup').lower().replace(' ', '-')}",
            "assets": {
                "html_template": landing_html,
                "css_styles": "",  # CSS embedded in HTML for performance
                "javascript": "",  # JS embedded in HTML for performance
                "config": {
                    "responsive": True,
                    "conversion_optimized": True,
                    "seo_ready": True,
                    "mobile_first": True,
                    "startup_optimized": True,
                    "performance_optimized": True,
                    "accessibility_compliant": True,
                    "analytics_ready": True,
                },
            },
            "content_data": content_data,
            "visual_assets": deployment_result["visual_assets"],
            "conversion_elements": conversion_features,
            "seo_optimization": seo_data,
            "meta_data": {
                "title": f"{content_data['brand_name']} - {content_data['tagline']}",
                "description": content_data.get("description", "")[:160],
                "site_type": "premium_startup_landing",
                "og_image": visual_assets.get("hero_bg", {}).get("url", ""),
                "schema_markup": generate_schema_markup(content_data),
            },
            "analytics": {
                "tracking_enabled": True,
                "conversion_goals": ["signup", "waitlist", "demo", "trial"],
                "startup_metrics": True,
                "ab_testing_ready": True,
                "heatmap_tracking": True,
            },
        }

        # Deploy to enhanced service
        deploy_result = deploy_to_premium_service(deployment_payload)

        if deploy_result.get("success"):
            deployment_result.update(
                {
                    "deployment_status": "completed",
                    "live_url": deploy_result.get("live_url"),
                    "deployment_id": deploy_result.get("deployment_id"),
                    "features": [
                        "conversion_optimized",
                        "seo_ready",
                        "mobile_first",
                        "curated_visuals",
                        "ai_generated_content",
                        "performance_optimized",
                        "accessibility_compliant",
                        "analytics_ready",
                        "ab_testing_ready",
                    ],
                    "performance_score": deploy_result.get("performance_score", 95),
                    "seo_score": deploy_result.get("seo_score", 98),
                }
            )
            print("✅ Premium startup landing experience deployed successfully!")
        else:
            deployment_result.update(
                {"deployment_status": "failed", "error": deploy_result.get("error")}
            )

        return deployment_result

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        deployment_result.update({"deployment_status": "failed", "error": str(e)})
        return deployment_result


def get_premium_visual_assets(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Curate premium visual assets with advanced search and filtering."""

    try:
        # Advanced search terms based on brand positioning
        search_strategy = {
            "hero": {
                "primary": ["modern office", "team collaboration", "innovation"],
                "tech": ["artificial intelligence", "technology", "data visualization"],
                "saas": ["software interface", "dashboard", "productivity"],
                "fintech": ["financial technology", "digital banking", "crypto"],
                "healthcare": [
                    "medical technology",
                    "healthcare innovation",
                    "telemedicine",
                ],
            },
            "features": {
                "primary": ["user interface", "product design", "user experience"],
                "tech": ["code editor", "terminal", "development"],
                "business": ["business meeting", "strategy", "growth"],
            },
            "testimonials": {
                "primary": ["happy customers", "business success", "testimonials"],
                "corporate": ["corporate team", "enterprise", "professional"],
            },
            "cta": {
                "primary": ["success", "growth", "achievement"],
                "startup": ["startup team", "celebration", "launch"],
            },
        }

        # Determine category based on brand context
        category = determine_visual_category(brand_data, copy_data)

        visual_assets = {}

        # Fetch hero assets with fallback strategy
        print("📸 Fetching premium hero visuals...")
        hero_search_terms = search_strategy["hero"].get(
            category, search_strategy["hero"]["primary"]
        )

        for term in hero_search_terms:
            hero_images = get_pexels_media(term, "images", 5, orientation="landscape")
            if hero_images.get("images"):
                # Filter for high quality and relevance
                filtered_images = filter_images(hero_images["images"])
                if filtered_images:
                    visual_assets["hero_bg"] = filtered_images[0]
                    visual_assets["hero_alternatives"] = filtered_images[1:3]
                    break

        # Fetch feature section visuals
        print("📸 Fetching feature section visuals...")
        feature_terms = search_strategy["features"].get(
            category, search_strategy["features"]["primary"]
        )
        feature_images = get_pexels_media(
            feature_terms[0], "images", 3, orientation="landscape"
        )
        if feature_images.get("images"):
            visual_assets["features_bg"] = filter_images(feature_images["images"])[0]

        # Fetch testimonial visuals
        print("📸 Fetching testimonial visuals...")
        testimonial_images = get_pexels_media(
            search_strategy["testimonials"]["primary"][0],
            "images",
            3,
            orientation="square",
        )
        if testimonial_images.get("images"):
            visual_assets["testimonials_bg"] = filter_images(
                testimonial_images["images"]
            )

        # Fetch CTA section visuals
        print("📸 Fetching CTA visuals...")
        cta_terms = search_strategy["cta"].get(
            category, search_strategy["cta"]["primary"]
        )
        cta_images = get_pexels_media(
            cta_terms[0], "images", 2, orientation="landscape"
        )
        if cta_images.get("images"):
            visual_assets["cta_bg"] = filter_images(cta_images["images"])[0]

        # Add curated fallbacks if needed
        if not visual_assets:
            curated = get_curated_pexels_media("images", 5)
            if curated.get("images"):
                filtered_curated = filter_images(curated["images"])
                visual_assets["hero_bg"] = (
                    filtered_curated[0]
                    if filtered_curated
                    else get_fallback_visual_assets()["hero_bg"]
                )

        print(f"✅ Successfully curated {len(visual_assets)} premium visual assets")
        return visual_assets

    except Exception as e:
        print(f"❌ Error curating premium visuals: {e}")
        return get_fallback_visual_assets()


def filter_images(images: List[Dict]) -> List[Dict]:
    """Filter images for premium quality and relevance."""
    filtered = []

    for img in images:
        # Quality filters
        width = img.get("width", 0)
        height = img.get("height", 0)

        # Minimum resolution requirements
        if width >= 1920 and height >= 1080:
            # Add quality score based on various factors
            quality_score = calculate_image_quality_score(img)
            if quality_score >= 0.7:  # 70% quality threshold
                img["quality_score"] = quality_score
                filtered.append(img)

    # Sort by quality score
    filtered.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    return filtered


def calculate_image_quality_score(image: Dict) -> float:
    """Calculate quality score for an image based on multiple factors."""
    score = 0.0

    # Resolution score (30%)
    width = image.get("width", 0)
    height = image.get("height", 0)
    resolution_score = min((width * height) / (1920 * 1080), 1.0)
    score += resolution_score * 0.3

    # Aspect ratio score (20%) - prefer 16:9 or close
    if width and height:
        aspect_ratio = width / height
        ideal_ratio = 16 / 9
        ratio_score = 1.0 - abs(aspect_ratio - ideal_ratio) / ideal_ratio
        score += max(ratio_score, 0) * 0.2

    # Photographer score (25%) - prefer known photographers
    photographer = image.get("photographer", "")
    if photographer and len(photographer) > 3:
        score += 0.25

    # URL quality (25%) - prefer shorter, cleaner URLs
    url = image.get("url", "")
    if url and len(url.split("/")) <= 6:  # Clean URL structure
        score += 0.25

    return min(score, 1.0)


def determine_visual_category(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> str:
    """Determine the visual category based on brand context."""
    brand_name = brand_data.get("brand_name", "").lower()
    value_prop = brand_data.get("value_proposition", "").lower()

    # Technology indicators
    tech_keywords = ["ai", "tech", "data", "software", "platform", "api", "code", "dev"]
    if any(keyword in brand_name or keyword in value_prop for keyword in tech_keywords):
        return "tech"

    # Financial technology
    fintech_keywords = ["finance", "payment", "banking", "crypto", "money", "wallet"]
    if any(
        keyword in brand_name or keyword in value_prop for keyword in fintech_keywords
    ):
        return "fintech"

    # Healthcare
    health_keywords = ["health", "medical", "care", "wellness", "therapy", "patient"]
    if any(
        keyword in brand_name or keyword in value_prop for keyword in health_keywords
    ):
        return "healthcare"

    # SaaS/Business tools
    saas_keywords = [
        "workflow",
        "productivity",
        "business",
        "team",
        "collaboration",
        "management",
    ]
    if any(keyword in brand_name or keyword in value_prop for keyword in saas_keywords):
        return "saas"

    return "primary"


def extract_industry_keywords(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> List[str]:
    """Extract industry-specific keywords from brand data."""
    keywords = []

    # From brand data
    if "keywords" in copy_data:
        keywords.extend(copy_data["keywords"][:3])

    # From value proposition
    value_prop = brand_data.get("value_proposition", "")
    if value_prop:
        # Extract key terms (simplified NLP)
        words = re.findall(r"\b\w{4,}\b", value_prop.lower())
        keywords.extend(words[:3])

    return list(set(keywords))


def generate_landing_page_with_ai(
    brand_data: Dict[str, Any],
    visual_assets: Dict[str, Any],
) -> str:
    """Generate premium startup landing page with advanced AI and modern design patterns."""

    try:
        logo_data = brand_data.get("logo_variations", {}).get("primary", {})
        visual_identity = brand_data.get("visual_identity", {})

        landing_prompt = f"""
        Create a premium, conversion-optimized startup landing page for: {brand_data.get("brand_name", "Brand")}

        DESIGN REQUIREMENTS - PREMIUM STARTUP AESTHETIC:
        - Inspired by top unicorns: Linear, Stripe, Notion, Figma, Vercel
        - Modern glassmorphism with subtle depth and layering
        - Micro-interactions and smooth animations
        - Perfect typography hierarchy with excellent readability
        - Mobile-first responsive design that looks perfect on all devices
        - High-converting CTAs with psychological triggers
        - Advanced CSS Grid and Flexbox layouts
        - Progressive enhancement for performance

        VISUAL ASSETS TO INTEGRATE:
        Logo: {logo_data.get("logo_url", "")}
        Primary Color: {visual_identity.get("primary_color", "#2563eb")}
        Secondary Color: {visual_identity.get("secondary_color", "#10b981")}
        Accent Color: {visual_identity.get("accent_color", "#f59e0b")}
        Gradient: {visual_identity.get("gradient_primary", "linear-gradient(135deg, #2563eb, #10b981)")}

        BACKGROUND IMAGES:
        Hero: {visual_assets.get("hero_bg", {}).get("url", "")}
        Features: {visual_assets.get("features_bg", {}).get("url", "")}
        CTA: {visual_assets.get("cta_bg", {}).get("url", "")}

        CONTENT VARIABLES (use Jinja2 syntax):
        - {{{{ brand_name }}}} - brand name
        - {{{{ tagline }}}} - compelling tagline
        - {{{{ hero_headline }}}} - conversion-focused headline
        - {{{{ hero_subheadline }}}} - supporting subheadline
        - {{{{ value_proposition }}}} - unique value proposition
        - {{{{ cta_primary }}}} - primary CTA text
        - {{{{ cta_secondary }}}} - secondary CTA text
        - {{{{ features }}}} - array of feature objects
        - {{{{ testimonials }}}} - array of testimonial objects
        - {{{{ social_proof }}}} - social proof statement

        CONVERSION OPTIMIZATION FEATURES:
        1. Above-the-fold optimization with clear value prop
        2. Social proof elements (testimonials, logos, metrics)
        3. Scarcity and urgency elements
        4. Progressive disclosure of information
        5. Multiple CTA placements with different psychological triggers
        6. Risk reversal elements (guarantees, free trials)
        7. Trust signals (security badges, certifications)

        SECTIONS TO INCLUDE:
        1. Navigation Bar (sticky, glassmorphism effect)
        2. Hero Section (compelling headline, subheadline, dual CTAs, hero image/video)
        3. Social Proof Bar (logos of customers/press mentions)
        4. Problem Statement (pain points visualization)
        5. Solution Overview (product preview with benefits)
        6. Features Grid (3-column, icon + title + description)
        7. How It Works (3-step process with animations)
        8. Testimonials Carousel (rotating customer stories)
        9. Pricing Preview (simple, clear, compelling)
        10. FAQ Section (address common objections)
        11. Final CTA Section (urgency + scarcity)
        12. Footer (comprehensive links, trust signals)

        MODERN DESIGN PATTERNS:
        - Glassmorphism cards with backdrop-filter
        - Smooth scroll with intersection observer animations
        - Parallax effects on hero section
        - Gradient overlays and mesh backgrounds
        - Custom CSS animations and transitions
        - Dark mode toggle capability
        - Progressive image loading
        - Advanced typography with proper spacing

        TECHNICAL REQUIREMENTS:
        - Semantic HTML5 structure
        - CSS Grid and Flexbox for layouts
        - CSS Custom Properties for theming
        - Intersection Observer for animations
        - Proper accessibility (ARIA labels, focus management)
        - Optimized for Core Web Vitals
        - Progressive enhancement

        Create complete HTML with embedded CSS and JavaScript. Use the latest web standards and best practices.
        Make it feel like a $100M+ startup that just raised Series A.

        CRITICAL: Use proper Jinja2 template syntax for all dynamic content.
        Return ONLY the complete HTML code with no markdown formatting.
        """

        print(f" Landing page prompt size: {len(landing_prompt)}")

        response = robust_completion(
            model=MODEL_CONFIG["landing_builder"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": landing_prompt[:1048176]}],
            temperature=0.7,
            stream=False,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            html_content = safe_json_loads(response.choices[0].message.content.strip())

            # Clean up response
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0].strip()
            elif "```" in html_content:
                html_content = html_content.split("```")[1].strip()

            # Add advanced features to the HTML
            html_content = inject_advanced_features(html_content, brand_data)

            return html_content

    except Exception as e:
        print(f"❌ Error generating premium landing page: {e}")

    return ""


def inject_advanced_features(html_content: str, brand_data: Dict[str, Any]) -> str:
    """Inject advanced features into the HTML content."""

    # Add advanced meta tags for SEO and social
    meta_tags = f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="{brand_data.get('visual_identity', {}).get('primary_color', '#2563eb')}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://images.pexels.com">
    <link rel="dns-prefetch" href="https://api.example.com">
    """

    # Add advanced JavaScript for interactions
    advanced_js = """
    <script>
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Advanced CTA tracking
        document.querySelectorAll('.btn-primary').forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Track conversion event
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'cta_click', {
                        'event_category': 'conversion',
                        'event_label': this.textContent.trim(),
                        'button_location': this.dataset.location || 'unknown'
                    });
                }
            });
        });
    });
    </script>
    """

    # Inject meta tags after <head>
    if "<head>" in html_content:
        html_content = html_content.replace("<head>", f"<head>{meta_tags}")

    # Inject advanced JavaScript before closing body tag
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{advanced_js}</body>")

    return html_content


def generate_advanced_content_data(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate advanced content data with personalization and optimization."""

    try:
        content_prompt = f"""
        Generate comprehensive, conversion-optimized content for a premium startup landing page.

        Brand: {brand_data.get("brand_name", "")}
        Value Prop: {brand_data.get("value_proposition", "")}
        Market Context: {copy_data.get("market_context", {})}
        Competitive Positioning: {brand_data.get("competitive_positioning", {})}

        Create JSON with advanced content strategy:
        {{
            "brand_name": "{brand_data.get('brand_name', 'Startup')}",
            "tagline": "compelling, memorable tagline under 6 words",
            "hero_headline": "conversion-focused headline that hooks in 3 seconds",
            "hero_subheadline": "supporting subheadline that builds desire",
            "value_proposition": "clear unique value proposition statement",
            "description": "SEO-optimized description under 160 characters",
            "problem_statement": "pain point that resonates with target audience",
            "solution_statement": "how your product uniquely solves the problem",
            "features": [
                {{
                    "title": "Feature 1",
                    "description": "benefit-focused description with outcome",
                    "icon": "⚡",
                    "metric": "10x faster"
                }},
                {{
                    "title": "Feature 2",
                    "description": "benefit-focused description with outcome",
                    "icon": "🚀",
                    "metric": "99% uptime"
                }},
                {{
                    "title": "Feature 3",
                    "description": "benefit-focused description with outcome",
                    "icon": "💎",
                    "metric": "$50K saved"
                }}
            ],
            "how_it_works": [
                {{"step": 1, "title": "Connect", "description": "One-click integration"}},
                {{"step": 2, "title": "Configure", "description": "AI-powered setup"}},
                {{"step": 3, "title": "Scale", "description": "10x growth guaranteed"}}
            ],
            "testimonials": [
                {{
                    "quote": "This completely transformed our workflow. 10x ROI in 30 days.",
                    "author": "Sarah Chen",
                    "title": "VP Engineering",
                    "company": "TechCorp",
                    "avatar": "/images/testimonial-1.jpg",
                    "rating": 5
                }},
                {{
                    "quote": "The best investment we've made. Pays for itself every month.",
                    "author": "Michael Rodriguez",
                    "title": "Head of Operations",
                    "company": "ScaleUp Inc",
                    "avatar": "/images/testimonial-2.jpg",
                    "rating": 5
                }}
            ],
            "social_proof": {{
                "customer_count": "10,000+",
                "customer_type": "growing companies",
                "metrics": [
                    {{"value": "99.9%", "label": "Uptime"}},
                    {{"value": "< 50ms", "label": "Response Time"}},
                    {{"value": "10x", "label": "Performance Boost"}}
                ],
                "press_mentions": ["TechCrunch", "Product Hunt", "Forbes"]
            }},
            "cta_primary": "Start Free Trial",
            "cta_secondary": "See Demo",
            "cta_waitlist": "Join Waitlist",
            "pricing_preview": {{
                "price": "Free",
                "period": "to start",
                "highlight": "No credit card required",
                "features": ["Unlimited usage", "24/7 support", "Free forever plan"]
            }},
            "faq": [
                {{"q": "How quickly can I get started?", "a": "Under 60 seconds with our one-click setup."}},
                {{"q": "Is there a free trial?", "a": "Yes! Free forever plan with no credit card required."}},
                {{"q": "What kind of support do you offer?", "a": "24/7 chat support and dedicated success manager."}}
            ],
            "urgency_elements": {{
                "limited_time": "50% off for first 100 customers",
                "scarcity": "Only 23 spots left in beta",
                "social_proof": "1,247 people signed up this week"
            }}
        }}

        Make it venture-scale ambitious with clear conversion psychology.
        """

        response = robust_completion(
            model=MODEL_CONFIG["brand_creator"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": content_prompt[:1048576]}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=3000,
        )

        if response and response.choices[0].message.content:
            from cosm.discovery.explorer_agent import safe_json_loads

            return safe_json_loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error generating advanced content data: {e}")

    # Fallback content
    return generate_fallback_content_data(brand_data, copy_data)


def generate_conversion_features(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate conversion optimization features."""

    return {
        "ab_testing": {
            "headline_variations": [
                "The [category] that [transforms outcome]",
                "Finally, [outcome] that just works",
                "Stop [pain point]. Start [benefit]",
            ],
            "cta_variations": [
                "Start Free Trial",
                "Get Started Free",
                "Try It Free Now",
                "Join Free Beta",
            ],
            "color_variations": [
                brand_data.get("visual_identity", {}).get("primary_color", "#2563eb"),
                brand_data.get("visual_identity", {}).get("accent_color", "#f59e0b"),
                "#10b981",
            ],
        },
        "psychological_triggers": {
            "scarcity": "Limited beta access - only 50 spots remaining",
            "urgency": "Early bird pricing ends in 48 hours",
            "social_proof": "Join 10,000+ companies already using [brand]",
            "authority": "Backed by top VCs and industry leaders",
            "reciprocity": "Free plan forever - no strings attached",
        },
        "trust_signals": {
            "security": ["SOC 2 Compliant", "GDPR Ready", "256-bit SSL"],
            "guarantees": ["30-day money back", "99.9% uptime SLA"],
            "certifications": ["ISO 27001", "Privacy Shield"],
            "social_proof": ["Featured in TechCrunch", "Product Hunt #1"],
        },
        "conversion_widgets": {
            "exit_intent_popup": {
                "trigger": "mouse leave",
                "offer": "Get our startup playbook before you go",
                "cta": "Download Free Guide",
            },
            "scroll_cta": {
                "trigger": "50% scroll",
                "message": "Ready to transform your workflow?",
                "cta": "Start Free Trial",
            },
            "time_based_popup": {
                "trigger": "60 seconds",
                "offer": "Want a personal demo?",
                "cta": "Book Demo Call",
            },
        },
    }


def generate_seo_optimization(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any], content_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate comprehensive SEO optimization data."""

    brand_name = brand_data.get("brand_name", "Startup")
    keywords = copy_data.get("keywords", [])

    return {
        "meta_tags": {
            "title": f"{brand_name} - {content_data.get('tagline', 'Revolutionary Platform')}",
            "description": content_data.get(
                "description",
                f"{brand_name} - Transform your workflow with our innovative platform",
            ),
            "keywords": ",".join(keywords[:10]),
            "canonical": f"https://{brand_name.lower()}.com",
            "robots": "index, follow",
        },
        "open_graph": {
            "og:title": f"{brand_name} - {content_data.get('hero_headline', 'Transform Your Workflow')}",
            "og:description": content_data.get(
                "hero_subheadline", "The platform that changes everything"
            ),
            "og:type": "website",
            "og:url": f"https://{brand_name.lower()}.com",
            "og:image": "https://example.com/og-image.jpg",
            "og:site_name": brand_name,
        },
        "twitter_card": {
            "twitter:card": "summary_large_image",
            "twitter:title": f"{brand_name} - {content_data.get('tagline', '')}",
            "twitter:description": content_data.get("hero_subheadline", ""),
            "twitter:image": "https://example.com/twitter-image.jpg",
        },
        "structured_data": generate_schema_markup(content_data),
        "technical_seo": {
            "sitemap": f"https://{brand_name.lower()}.com/sitemap.xml",
            "robots_txt": f"https://{brand_name.lower()}.com/robots.txt",
            "favicon": f"https://{brand_name.lower()}.com/favicon.ico",
            "apple_touch_icon": f"https://{brand_name.lower()}.com/apple-touch-icon.png",
        },
    }


def generate_schema_markup(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate JSON-LD structured data markup."""

    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": content_data.get("brand_name", "Startup"),
        "description": content_data.get("description", ""),
        "url": f"https://{content_data.get('brand_name', 'startup').lower()}.com",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "priceValidUntil": "2025-12-31",
            "availability": "https://schema.org/InStock",
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "ratingCount": "1247",
            "bestRating": "5",
        },
        "provider": {
            "@type": "Organization",
            "name": content_data.get("brand_name", "Startup"),
            "url": f"https://{content_data.get('brand_name', 'startup').lower()}.com",
        },
    }


def generate_performance_config() -> Dict[str, Any]:
    """Generate performance optimization configuration."""

    return {
        "core_web_vitals": {
            "lcp_target": "< 2.5s",
            "fid_target": "< 100ms",
            "cls_target": "< 0.1",
        },
        "optimization_techniques": [
            "Critical CSS inlining",
            "Image lazy loading",
            "Font preloading",
            "Resource hints (preconnect, dns-prefetch)",
            "Gzip compression",
            "Browser caching",
            "CDN delivery",
        ],
        "monitoring": {
            "lighthouse_score_target": "> 95",
            "page_load_time_target": "< 3s",
            "time_to_interactive_target": "< 5s",
        },
        "progressive_enhancement": {
            "offline_support": False,
            "service_worker": False,
            "critical_css": True,
            "lazy_loading": True,
        },
    }


def deploy_to_premium_service(deployment_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy to rendering service."""

    try:
        from cosm.settings import settings

        print("🚀 Deploying startup landing page...")

        RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

        response = requests.post(
            f"{RENDERER_SERVICE_URL}/api/deploy",
            json=deployment_payload,
            headers={"Content-Type": "application/json"},
            timeout=90,
        )

        if response.status_code == 200:
            result = response.json()
            print(
                f"✅ Premium deployment successful: {result.get('live_url', 'URL pending')}"
            )
            return {
                "success": True,
                "live_url": result.get("live_url"),
                "deployment_id": result.get("deployment_id"),
                "site_id": result.get("site_id"),
                "status": "deployed",
                "performance_score": result.get("performance_score", 95),
                "seo_score": result.get("seo_score", 98),
                "conversion_score": result.get("conversion_score", 92),
            }
        else:
            print(f"❌ Premium deployment failed: {response.status_code}")
            return {
                "success": False,
                "error": f"Premium deployment failed: {response.status_code} - {response.text}",
                "status": "failed",
            }

    except requests.exceptions.Timeout:
        print("❌ deployment timeout")
        return {
            "success": False,
            "error": "deployment timeout",
            "status": "timeout",
        }
    except requests.exceptions.ConnectionError:
        print("❌ Connection error to premium renderer service")
        return {
            "success": False,
            "error": "Cannot connect to premium renderer service - check RENDERER_SERVICE_URL",
            "status": "connection_error",
        }
    except Exception as e:
        print(f"❌ Premium deployment error: {e}")
        return {
            "success": False,
            "error": f"Premium deployment error: {str(e)}",
            "status": "error",
        }


def generate_fallback_brand_package(
    opportunity_data: Dict[str, Any], base_package: Dict[str, Any]
) -> Dict[str, Any]:
    """Fallback when AI generation fails."""

    keywords = opportunity_data.get("keywords", ["solution"])
    primary_keyword = keywords[0] if keywords else "transform"

    # Generate more sophisticated fallback
    brand_name = f"{primary_keyword.title()}Flow"

    base_package.update(
        {
            "brand_identity": {
                "brand_name": brand_name,
                "tagline": "Transform. Scale. Succeed.",
                "brand_manifesto": f"We believe every {primary_keyword} should be effortless. We're building the future of workflow automation.",
                "value_proposition": f"The only {primary_keyword} platform that delivers 10x results without the complexity",
                "mission_statement": f"To revolutionize how teams work by making {primary_keyword} automation accessible to everyone",
                "vision_statement": "A world where manual work is obsolete and teams focus on what matters most",
                "brand_personality": {
                    "voice": "innovative, confident, empowering",
                    "tone": "professional yet approachable, future-focused",
                    "characteristics": [
                        "transformative",
                        "reliable",
                        "innovative",
                        "accessible",
                    ],
                    "brand_archetype": "The Innovator",
                },
                "visual_identity": {
                    "primary_color": "#2563eb",
                    "secondary_color": "#10b981",
                    "accent_color": "#f59e0b",
                    "gradient_primary": "linear-gradient(135deg, #2563eb, #10b981)",
                    "font_primary": "Inter, system-ui, sans-serif",
                    "font_heading": "Cal Sans, Poppins, sans-serif",
                    "font_mono": "JetBrains Mono, monospace",
                },
            },
            "marketing_copy": {
                "hero_headline": f"The {primary_keyword} platform that changes everything",
                "hero_subheadline": "Join 10,000+ teams who've discovered the future of productivity",
                "problem_statement": f"Traditional {primary_keyword} tools are broken. We're fixing them.",
                "solution_statement": f"Introducing {brand_name} - the revolutionary platform that transforms {primary_keyword} forever",
                "key_benefits": [
                    "10x faster implementation",
                    "Zero manual configuration",
                    "Scales automatically with your team",
                    "Enterprise-grade security included",
                ],
                "cta_primary": "Start Free Trial",
                "cta_secondary": "Watch Demo",
                "social_proof": "Trusted by industry leaders worldwide",
            },
            "competitive_positioning": {
                "category_creation": f"The first next-generation {primary_keyword} platform built for modern teams",
                "vs_legacy_players": "Legacy tools are yesterday. We're building tomorrow.",
                "differentiation_matrix": [
                    "Competitors: Complex → We: Simple",
                    "Competitors: Slow → We: Instant",
                    "Competitors: Expensive → We: Accessible",
                ],
                "moat_statement": f"The only platform with AI-powered {primary_keyword} automation",
            },
            "visual_assets": {
                "logo_variations": {
                    "primary": generate_fallback_logo(brand_name, "#2563eb"),
                    "horizontal": generate_fallback_logo(brand_name, "#2563eb"),
                    "icon_only": generate_fallback_logo(brand_name[0], "#2563eb"),
                },
                "color_palette": generate_color_palette(
                    {"visual_identity": {"primary_color": "#2563eb"}}
                ),
                "typography_system": generate_typography_system(),
            },
            "domain_strategy": generate_advanced_domain_strategy(
                brand_name, {"keywords": keywords}
            ),
            "brand_guidelines": generate_brand_guidelines(
                {
                    "brand_identity": {
                        "brand_personality": {
                            "tone": "professional yet approachable, future-focused",
                            "characteristics": [
                                "transformative",
                                "reliable",
                                "innovative",
                                "accessible",
                            ],
                        }
                    }
                }
            ),
            "content_strategy": generate_content_strategy(
                {"brand_personality": {"tone": "innovative, confident"}},
                {"keywords": keywords},
            ),
            "conversion_strategy": generate_conversion_strategy(
                {"brand_personality": {"tone": "innovative, confident"}},
                {"keywords": keywords},
            ),
            "fallback_used": True,
            "enhancement_level": "premium",
        }
    )

    return base_package


def generate_fallback_content_data(
    brand_data: Dict[str, Any], copy_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate fallback content data when AI fails."""

    brand_name = brand_data.get("brand_name", "Startup")

    return {
        "brand_name": brand_name,
        "tagline": "Transform Your Workflow",
        "hero_headline": "The platform that changes everything",
        "hero_subheadline": "Join thousands of teams who've discovered the future of productivity",
        "description": f"{brand_name} - Transform your workflow with our revolutionary platform. Join 10K+ teams already succeeding.",
        "problem_statement": "Traditional tools are broken and holding your team back",
        "solution_statement": f"{brand_name} revolutionizes how modern teams collaborate and scale",
        "features": [
            {
                "title": "Lightning Fast",
                "description": "10x faster than traditional solutions with instant results",
                "icon": "⚡",
                "metric": "10x faster",
            },
            {
                "title": "Zero Configuration",
                "description": "Works perfectly out of the box with AI-powered setup",
                "icon": "🚀",
                "metric": "0 setup time",
            },
            {
                "title": "Enterprise Ready",
                "description": "Bank-level security with enterprise-grade reliability",
                "icon": "💎",
                "metric": "99.9% uptime",
            },
        ],
        "how_it_works": [
            {
                "step": 1,
                "title": "Connect",
                "description": "One-click integration with your existing tools",
            },
            {
                "step": 2,
                "title": "Configure",
                "description": "AI automatically optimizes your workflow",
            },
            {
                "step": 3,
                "title": "Scale",
                "description": "Watch your productivity soar with guaranteed results",
            },
        ],
        "testimonials": [
            {
                "quote": "This completely transformed our workflow. We saw 10x ROI in the first month.",
                "author": "Sarah Chen",
                "title": "VP Engineering",
                "company": "TechCorp",
                "avatar": "/images/testimonial-1.jpg",
                "rating": 5,
            },
            {
                "quote": "The best investment we've made this year. It pays for itself every week.",
                "author": "Michael Rodriguez",
                "title": "Head of Operations",
                "company": "ScaleUp Inc",
                "avatar": "/images/testimonial-2.jpg",
                "rating": 5,
            },
        ],
        "social_proof": {
            "customer_count": "10,000+",
            "customer_type": "growing companies",
            "metrics": [
                {"value": "99.9%", "label": "Uptime"},
                {"value": "< 50ms", "label": "Response Time"},
                {"value": "10x", "label": "Performance Boost"},
            ],
            "press_mentions": ["TechCrunch", "Product Hunt", "Forbes"],
        },
        "cta_primary": "Start Free Trial",
        "cta_secondary": "Watch Demo",
        "cta_waitlist": "Join Waitlist",
        "pricing_preview": {
            "price": "Free",
            "period": "to start",
            "highlight": "No credit card required",
            "features": ["Unlimited usage", "24/7 support", "Free forever plan"],
        },
        "faq": [
            {
                "q": "How quickly can I get started?",
                "a": "Under 60 seconds with our one-click setup.",
            },
            {
                "q": "Is there a free trial?",
                "a": "Yes! Free forever plan with no credit card required.",
            },
            {
                "q": "What kind of support do you offer?",
                "a": "24/7 chat support and dedicated success manager.",
            },
        ],
        "urgency_elements": {
            "limited_time": "50% off for first 100 customers",
            "scarcity": "Only 23 spots left in beta",
            "social_proof": "1,247 people signed up this week",
        },
    }


def get_fallback_visual_assets() -> Dict[str, Any]:
    """Fallback visual assets when API fails."""

    return {
        "hero_bg": {
            "url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=2074&q=80",
            "alt": "Modern startup office space with collaborative team",
            "photographer": "Unsplash",
            "source": "fallback",
            "quality_score": 0.8,
        },
        "features_bg": {
            "url": "https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
            "alt": "Technology and innovation workspace",
            "photographer": "Unsplash",
            "source": "fallback",
            "quality_score": 0.8,
        },
        "cta_bg": {
            "url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
            "alt": "Team celebrating success and growth",
            "photographer": "Unsplash",
            "source": "fallback",
            "quality_score": 0.8,
        },
    }


# Include the original generate_logo_with_imagen and generate_fallback_logo functions
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

        Style: {logo_style}, clean, professional, memorable
        Colors: Primary {primary_color}, use 1-2 colors max
        Format: Simple geometric shape or wordmark
        Inspiration: Think Stripe, Linear, Notion - clean and iconic

        Requirements:
        - Scalable vector-style design
        - Works on light and dark backgrounds
        - No complex details or gradients
        - Modern SaaS startup aesthetic
        - Highly memorable and recognizable
        """

        # Generate image with Imagen
        image_response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=logo_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_low_and_above",
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
    """Generate enhanced fallback logo using CSS/SVG."""

    # Create sophisticated text-based logo
    initials = "".join([word[0].upper() for word in brand_name.split()[:2]])
    if len(initials) == 1:
        initials = brand_name[:2].upper()

    # Create gradient and shadow effects
    svg_logo = f"""
    <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{darken_color(primary_color, 0.2)};stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.1"/>
            </filter>
        </defs>
        <rect width="120" height="120" rx="24" fill="url(#logoGrad)" filter="url(#shadow)"/>
        <text x="60" y="75" font-family="Inter, -apple-system, sans-serif" font-size="42"
              font-weight="700" text-anchor="middle" fill="white">{initials}</text>
    </svg>
    """

    # Convert SVG to base64
    svg_base64 = base64.b64encode(svg_logo.encode("utf-8")).decode("utf-8")

    return {
        "logo_base64": svg_base64,
        "logo_url": f"data:image/svg+xml;base64,{svg_base64}",
        "style": "minimalist text logo with gradient",
        "colors": [primary_color],
        "format": "SVG",
        "generated_with": "fallback_svg_enhanced",
        "status": "fallback",
    }


def generate_fallback_domain_strategy(brand_name: str) -> Dict[str, Any]:
    """Enhanced fallback domain strategy."""
    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    return {
        "primary_domains": [
            {
                "domain": f"{base_name}.com",
                "priority": "critical",
                "cost_estimate": "$15-25/year",
                "seo_value": "highest",
                "rationale": "Primary brand domain - essential for credibility and SEO",
            },
            {
                "domain": f"{base_name}.io",
                "priority": "high",
                "cost_estimate": "$40-60/year",
                "seo_value": "high",
                "rationale": "Tech startup standard - appeals to developers and tech audience",
            },
            {
                "domain": f"get{base_name}.com",
                "priority": "medium",
                "cost_estimate": "$15-25/year",
                "seo_value": "medium",
                "rationale": "Marketing and conversion-focused domain for campaigns",
            },
        ],
        "marketing_domains": [
            {
                "domain": f"try{base_name}.com",
                "use_case": "trial signups and product demos",
                "priority": "medium",
                "campaign_type": "acquisition",
            },
            {
                "domain": f"{base_name}app.com",
                "use_case": "mobile app downloads and app store redirects",
                "priority": "low",
                "campaign_type": "mobile",
            },
        ],
        "defensive_domains": [
            f"{base_name}.net",
            f"{base_name}.org",
            f"{base_name}.ai",
        ],
        "acquisition_strategy": {
            "phase_1": "Secure .com and .io immediately upon naming decision",
            "phase_2": "Acquire marketing domains 2-4 weeks before launch",
            "phase_3": "Defensive registrations after achieving product-market fit",
            "budget_estimate": "$300-600 total first year",
        },
    }


# =============================================================================
# ENHANCED AGENT DEFINITIONS
# =============================================================================

brand_creator_agent = ResilientLlmAgent(
    name="brand_creator_agent",
    model=MODEL_CONFIG["landing_builder"],
    instruction=BRAND_CREATOR_PROMPT
    + """

    ENHANCED CAPABILITIES:
    - Create comprehensive brand ecosystems with visual identity systems
    - Generate multiple logo variations and complete color palettes
    - Develop advanced brand guidelines and voice/tone frameworks
    - Provide strategic domain recommendations with SEO considerations
    - Create content marketing strategies and conversion optimization plans
    - Generate competitive positioning and category creation strategies

    DELIVERABLES:
    - Complete brand identity package with visual assets
    - Brand guidelines document with usage specifications
    - Domain acquisition strategy with timeline and budget
    - Content strategy with channel-specific recommendations
    - Conversion optimization framework with psychological triggers
    - Competitive differentiation matrix and market positioning

    Focus on creating venture-scale brands that feel inevitable and category-defining.
    Think unicorn potential with sophisticated execution.
    """,
    description="Creates comprehensive startup brand identities with advanced AI-powered visual assets, strategic positioning, and conversion optimization",
    tools=[FunctionTool(func=create_brand_identity)],
    output_key="brand_package",
)


landing_builder_agent = ResilientLlmAgent(
    name="landing_builder_agent",
    model=MODEL_CONFIG["landing_builder"],
    instruction=LANDING_BUILDER_PROMPT
    + """

    ENHANCED CAPABILITIES:
    - Build premium, conversion-optimized landing pages with advanced design patterns
    - Integrate sophisticated visual assets and brand systems
    - Implement modern web technologies (glassmorphism, micro-interactions, animations)
    - Create mobile-first responsive experiences optimized for all devices
    - Add comprehensive SEO optimization and performance enhancements
    - Include advanced conversion elements (A/B testing, psychological triggers, trust signals)
    - Generate schema markup and structured data for maximum discoverability

    TECHNICAL FEATURES:
    - Modern CSS Grid and Flexbox layouts
    - Intersection Observer animations and smooth scrolling
    - Progressive image loading and performance optimization
    - Accessibility compliance (WCAG guidelines)
    - Core Web Vitals optimization
    - Advanced JavaScript interactions and tracking

    CONVERSION OPTIMIZATION:
    - Multiple CTA placements with psychological triggers
    - Social proof elements and trust signals
    - Scarcity and urgency mechanics
    - Risk reversal and guarantee messaging
    - Progressive disclosure and information hierarchy

    Create landing pages that feel like $100M+ startups with enterprise-grade polish.
    """,
    description="Creates and deploys startup landing pages with advanced AI-generated code, comprehensive visual asset integration, and conversion optimization",
    tools=[FunctionTool(func=build_landing_page)],
    output_key="landing_package",
)
