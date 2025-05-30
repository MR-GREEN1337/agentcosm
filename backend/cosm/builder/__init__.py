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
from cosm.tools.pexels import get_pexels_media

client = Client()

# Renderer service configuration
RENDERER_SERVICE_URL = settings.RENDERER_SERVICE_URL

# =============================================================================
# BRAND CREATOR AGENT - ENHANCED WITH OPENAI
# =============================================================================


BRAND_COPY_CREATOR_PROMPT = """
You are the unified Brand & Copy Creator Agent with integrated capabilities. You combine:

1. BRAND IDENTITY CREATION - Compelling brand development for liminal market opportunities
2. MARKETING COPY GENERATION - High-converting copy optimized for early-stage validation
3. STRATEGIC MESSAGING - Unified brand voice and positioning across all touchpoints

Your mission is to create cohesive brand experiences by:
- Developing complete brand identities that position uniquely in liminal spaces
- Creating high-converting marketing copy that drives validation and adoption
- Ensuring consistent messaging across all brand touchpoints and marketing materials
- Building brands that feel inevitable once users discover them

Use your integrated brand and copy capabilities to deliver comprehensive marketing assets in a unified workflow.
"""


def generate_comprehensive_marketing_copy(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """

    Consolidates all copy generation into one strategic pass for consistency and efficiency.
    Optimized for liminal market positioning and early-stage validation.

    Args:
        brand_data: Complete brand identity and positioning data
        opportunity_data: Market opportunity context and analysis

    Returns:
        Complete marketing copy package optimized for conversion
    """
    copy_package = {
        "brand_name": brand_data.get("brand_name", "Your Brand"),
        "generation_timestamp": datetime.now().isoformat(),
        "optimization_applied": "single_pass_comprehensive_copy_generation",
        # Core Copy Assets
        "headlines": [],
        "taglines": [],
        "value_propositions": [],
        # Website Copy
        "website_copy": {},
        # Email Marketing
        "email_sequences": {},
        # Social Media Copy
        "social_media_copy": {},
        # Advertising Copy
        "ad_copy": {},
        # Sales & Conversion Copy
        "sales_copy": {},
        # Support & Onboarding Copy
        "onboarding_copy": {},
        "support_copy": {},
        # Templates & Frameworks
        "testimonial_templates": [],
        "case_study_frameworks": [],
        "content_templates": {},
        # Performance Metrics
        "estimated_time_saved": "70% faster than sequential generation",
        "conversion_optimization": "liminal_market_positioning_applied",
        "copy_consistency_score": "high_brand_voice_alignment",
    }

    try:
        print("🎯 Generating comprehensive high-converting marketing copy...")

        # OPTIMIZED: Single comprehensive AI call for all copy assets
        ai_copy_package = generate_comprehensive_copy_with_ai(
            brand_data, opportunity_data
        )

        if ai_copy_package and not ai_copy_package.get("error"):
            # Merge AI-generated copy assets
            copy_package.update(ai_copy_package)

            # Generate specialized templates
            print("📝 Generating testimonial templates and case study frameworks...")
            copy_package["testimonial_templates"] = (
                generate_optimized_testimonial_templates(brand_data, opportunity_data)
            )
            copy_package["case_study_frameworks"] = (
                generate_optimized_case_study_frameworks(brand_data, opportunity_data)
            )

            # Generate content strategy templates
            copy_package["content_templates"] = generate_content_strategy_templates(
                brand_data, copy_package
            )

            print("✅ Comprehensive marketing copy package generated successfully!")
        else:
            print("⚠️ AI generation failed, using fallback copy approach...")
            copy_package = generate_fallback_copy_package(
                brand_data, opportunity_data, copy_package
            )

        return copy_package

    except Exception as e:
        print(f"❌ Error in comprehensive marketing copy generation: {e}")
        copy_package["error"] = str(e)
        return generate_fallback_copy_package(
            brand_data, opportunity_data, copy_package
        )


def generate_comprehensive_copy_with_ai(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    OPTIMIZED: Single AI call generating complete marketing copy ecosystem
    """
    try:
        # Extract optimized context for focused generation
        copy_context = {
            "brand_name": brand_data.get("brand_name", "Brand"),
            "tagline": brand_data.get("tagline", ""),
            "value_proposition": brand_data.get("value_proposition", ""),
            "positioning": brand_data.get("positioning_statement", ""),
            "brand_personality": brand_data.get("brand_personality", {}),
            "target_audience": opportunity_data.get(
                "target_audience", "business users"
            ),
            "pain_points": opportunity_data.get("pain_points", [])[
                :3
            ],  # Top 3 for focus
            "keywords": opportunity_data.get("keywords", [])[:3],  # Top 3 for focus
            "competition_level": opportunity_data.get("competition_analysis", {}).get(
                "competition_level", "medium"
            ),
            "opportunity_score": opportunity_data.get("opportunity_score", 0.5),
        }

        # OPTIMIZED: Comprehensive single-pass marketing copy prompt
        comprehensive_copy_prompt = f"""
        You are an expert conversion copywriter specializing in liminal market opportunities and early-stage validation. Create a complete marketing copy ecosystem that drives conversions and validates market demand.

        BRAND CONTEXT:
        Brand Name: {copy_context["brand_name"]}
        Tagline: {copy_context["tagline"]}
        Value Proposition: {copy_context["value_proposition"]}
        Positioning: {copy_context["positioning"]}
        Brand Personality: {json.dumps(copy_context["brand_personality"], indent=2)}

        MARKET CONTEXT:
        Target Audience: {copy_context["target_audience"]}
        Key Pain Points: {copy_context["pain_points"]}
        Market Keywords: {copy_context["keywords"]}
        Competition Level: {copy_context["competition_level"]}
        Opportunity Score: {copy_context["opportunity_score"]:.2f}

        LIMINAL MARKET COPY STRATEGY:
        This brand exists between established categories. Your copy must:
        - Address frustration with existing fragmented solutions
        - Position as the "missing link" users didn't know they needed
        - Create urgency through pain amplification and solution clarity
        - Build trust through specificity and deep user understanding
        - Drive early adoption with compelling validation opportunities

        GENERATE COMPREHENSIVE MARKETING COPY ECOSYSTEM:

        Return complete JSON with all marketing copy assets:
        {{
            "headlines": [
                "Finally, [specific outcome] without [current struggle] (outcome-focused)",
                "Stop [frustrating process]. Start [desired workflow]. (transformation-focused)",
                "The missing piece between [current state] and [desired state] (bridge-focused)",
                "Turn [manual process] into [automated outcome] in [timeframe] (efficiency-focused)",
                "[Target audience], meet your new [empowerment descriptor] (empowerment-focused)"
            ],
            "taglines": [
                "[3-word version of core promise]",
                "[5-word expansion with action verb]",
                "[7-word comprehensive value statement]"
            ],
            "value_propositions": [
                "Unlike [alternatives], we [unique approach] so you can [outcome] without [friction]",
                "The only [category] that [unique capability] for [specific audience]",
                "Finally, [desired state] that actually works with [current reality]"
            ],
            "website_copy": {{
                "hero_section": {{
                    "headline": "compelling conversion-focused headline addressing core pain",
                    "subheadline": "supporting explanation that amplifies promise with specifics",
                    "cta_primary": "action-oriented primary call-to-action",
                    "cta_secondary": "lower-commitment secondary option"
                }},
                "problem_section": {{
                    "headline": "You're stuck in the gap between [current] and [desired]",
                    "pain_amplification": "specific description of daily frustrations and workflow breakdowns",
                    "cost_of_inaction": "what happens if they don't solve this problem",
                    "transition_bridge": "What if there was a way to [bridge solution]?"
                }},
                "solution_section": {{
                    "headline": "Introducing [brand] - the bridge you've been missing",
                    "solution_explanation": "how the solution connects current state to desired outcome",
                    "unique_mechanism": "the specific approach that makes this different",
                    "benefit_statements": [
                        "Eliminate [specific manual task] forever",
                        "Connect [system A] to [system B] in [timeframe]",
                        "Get [outcome] without [technical complexity]"
                    ]
                }},
                "social_proof_section": {{
                    "headline": "Join [number]+ [audience] who've made the switch",
                    "testimonial_integration": "framework for weaving in customer success stories",
                    "trust_indicators": ["security badges", "uptime guarantees", "customer logos"],
                    "usage_statistics": "[number] [actions] completed, [timeframe] saved daily"
                }},
                "cta_section": {{
                    "headline": "Ready to bridge the gap?",
                    "urgency_element": "limited time or quantity motivator",
                    "risk_reversal": "guarantee or trial offer to reduce perceived risk",
                    "multiple_cta_options": ["Start free trial", "See it in action", "Get personalized demo"]
                }}
            }},
            "email_sequences": {{
                "welcome_series": [
                    {{
                        "email_1": {{
                            "subject": "Welcome to [brand] - your workflow just got easier",
                            "preview_text": "Here's what happens next (it's exciting)",
                            "body_outline": "Welcome + immediate value + first action step + expectation setting",
                            "cta": "Complete your setup in 2 minutes"
                        }},
                        "email_2": {{
                            "subject": "Your [brand] quick win (takes 30 seconds)",
                            "preview_text": "The easiest way to see immediate results",
                            "body_outline": "Simple first use case + step-by-step + success story",
                            "cta": "Try your first connection"
                        }},
                        "email_3": {{
                            "subject": "Here's how [brand] saves [audience] [time/outcome]",
                            "preview_text": "Real results from users just like you",
                            "body_outline": "Value demonstration + customer examples + advanced features",
                            "cta": "Explore advanced features"
                        }}
                    }}
                ],
                "nurture_series": [
                    {{
                        "email_1": {{
                            "subject": "Still struggling with [pain point]? Here's why.",
                            "focus": "education and problem awareness",
                            "body_outline": "Problem education + industry insights + solution preview"
                        }},
                        "email_2": {{
                            "subject": "Case study: How [company type] automated [process]",
                            "focus": "social proof and detailed use case",
                            "body_outline": "Before/after transformation + specific results + replication steps"
                        }},
                        "email_3": {{
                            "subject": "The hidden cost of [current manual process]",
                            "focus": "urgency and ROI calculation",
                            "body_outline": "Cost analysis + time waste calculation + ROI of solution"
                        }}
                    }}
                ],
                "re_engagement_series": [
                    {{
                        "email_1": {{
                            "subject": "We miss you (and your workflow is still broken)",
                            "approach": "friendly check-in with value reminder",
                            "body_outline": "Personal note + what they're missing + easy return path"
                        }},
                        "email_2": {{
                            "subject": "What [competitor] doesn't want you to know",
                            "approach": "competitive insight and differentiation",
                            "body_outline": "Market insights + competitive comparison + unique advantages"
                        }},
                        "email_3": {{
                            "subject": "Last chance: [Special offer] expires [date]",
                            "approach": "urgency-based re-engagement offer",
                            "body_outline": "Limited time offer + clear value + easy acceptance"
                        }}
                    }}
                ]
            }},
            "social_media_copy": {{
                "twitter_posts": [
                    {{
                        "hook": "Unpopular opinion: [current solution category] wasn't built for [specific use case]",
                        "body": "Here's what actually works: [thread preview]",
                        "engagement": "What's your biggest [workflow] frustration? 👇"
                    }},
                    {{
                        "hook": "PSA: If you're still [manual process], you're doing it wrong",
                        "body": "Here's how [target audience] are automating this in 2025:",
                        "engagement": "RT if you're ready to stop [frustrating task]"
                    }},
                    {{
                        "hook": "Plot twist: The best [category] solution isn't a [category] tool",
                        "body": "It's actually [bridge description]. Here's why:",
                        "engagement": "Anyone else discover this? Share your experience 👇"
                    }}
                ],
                "linkedin_posts": [
                    {{
                        "professional_opener": "After analyzing 100+ [target audience] workflows, here's what we found...",
                        "insight": "The biggest bottleneck isn't [expected problem], it's [actual problem]",
                        "solution_tease": "There's a simple fix that most [audience] don't know about:",
                        "engagement": "What workflow inefficiencies slow down your team?"
                    }},
                    {{
                        "industry_angle": "The real reason why [established solution] fails [target audience]",
                        "problem_analysis": "[Specific limitations and gaps in current solutions]",
                        "bridge_solution": "What [audience] actually need is [bridge description]",
                        "engagement": "How do you handle [specific workflow challenge]?"
                    }}
                ],
                "instagram_captions": [
                    {{
                        "visual_hook": "POV: Your workflow actually works seamlessly 📸",
                        "story_element": "Behind the scenes of how [brand] connects the dots",
                        "user_benefit": "No more switching between [tools]. No more manual [process].",
                        "engagement": "Double tap if you're ready for seamless workflows ✨"
                    }}
                ]
            }},
            "ad_copy": {{
                "google_ads": {{
                    "search_ads": [
                        {{
                            "headline_1": "Stop Manual [Process]",
                            "headline_2": "Connect [Tool A] + [Tool B]",
                            "headline_3": "[Outcome] in Minutes",
                            "description_1": "Bridge the gap between your tools. Setup takes 5 min.",
                            "description_2": "Finally, seamless [workflow] without the headaches."
                        }}
                    ],
                    "display_ads": [
                        {{
                            "headline": "The Missing Piece in Your [Workflow]",
                            "description": "Connect everything. Automate workflows. Save hours daily.",
                            "cta": "See How It Works"
                        }}
                    ]
                }},
                "facebook_ads": {{
                    "newsfeed_ads": [
                        {{
                            "hook": "If you're tired of [specific frustration], this might be the solution you've been looking for.",
                            "story": "We built [brand] because we were frustrated with [same problem]. Now [outcome] is automatic.",
                            "social_proof": "Join [number]+ [audience] who've already made the switch.",
                            "cta": "See how it works for your team"
                        }}
                    ],
                    "video_ads": [
                        {{
                            "opening_hook": "[Question that identifies target audience pain]",
                            "problem_agitation": "Show the frustration of current broken workflow",
                            "solution_demo": "Demonstrate seamless connection and automation",
                            "result_proof": "Show the time saved and efficiency gained",
                            "cta": "Start your free trial today"
                        }}
                    ]
                }},
                "linkedin_ads": {{
                    "sponsored_content": [
                        {{
                            "professional_hook": "How [industry leaders] are solving the [workflow] problem",
                            "credibility": "Trusted by [company types] from startups to Fortune 500",
                            "value_prop": "Turn [manual process] into [automated outcome]",
                            "cta": "Get a personalized demo"
                        }}
                    ]
                }}
            }},
            "sales_copy": {{
                "sales_page_structure": {{
                    "attention_grabbing_headline": "outcome-focused headline that stops scroll",
                    "problem_identification": "detailed pain point that creates 'that's exactly my problem' moment",
                    "solution_introduction": "bridge positioning that makes solution feel inevitable",
                    "mechanism_explanation": "how it works without technical overwhelm",
                    "benefit_stacking": "multiple outcome-focused benefits with specifics",
                    "social_proof_integration": "customer stories and usage statistics",
                    "objection_handling": "address common hesitations and concerns",
                    "urgency_creation": "legitimate reason to act now",
                    "risk_reversal": "guarantee or trial that eliminates purchase risk",
                    "clear_next_steps": "simple path from interest to usage"
                }},
                "demo_request_copy": {{
                    "headline": "See how [brand] works with your specific [workflow]",
                    "form_intro": "Get a personalized demo tailored to your [industry/role]",
                    "value_bullets": ["See your exact use case", "Get setup guidance", "Ask any questions"],
                    "time_commitment": "15-minute demo, no pressure presentation"
                }},
                "trial_signup_copy": {{
                    "headline": "Try [brand] free for [timeframe] - no credit card required",
                    "benefit_preview": "Connect your first [workflow] in under 5 minutes",
                    "trial_benefits": ["Full access to all features", "Personal onboarding", "Cancel anytime"],
                    "urgency_element": "Join [number]+ teams already saving time"
                }}
            }},
            "onboarding_copy": {{
                "welcome_messages": {{
                    "first_login": "Welcome to [brand]! Let's get your first workflow connected in 2 minutes.",
                    "setup_guidance": "We'll walk you through connecting [common integration] first - it's the easiest way to see value.",
                    "success_celebration": "🎉 Perfect! You just saved yourself [time] every [frequency]. Here's what to try next:"
                }},
                "progress_encouragement": {{
                    "milestone_1": "Great start! You've connected [integration]. [X]% of users see immediate value at this point.",
                    "milestone_2": "You're on fire! [X] connections set up. Most users save [time] weekly at this stage.",
                    "mastery_level": "You're a [brand] power user! Your setup is saving you approximately [time/outcome] per week."
                }},
                "help_guidance": {{
                    "stuck_points": "Having trouble with [common issue]? Here's the quick fix: [solution]",
                    "feature_discovery": "Pro tip: Try [advanced feature] - users love how it [specific benefit]",
                    "optimization_suggestions": "Want to save even more time? Here are 3 advanced workflows to try:"
                }}
            }}
        }}

        COPY OPTIMIZATION PRINCIPLES:
        - Lead with specific outcomes, not generic features
        - Use concrete timeframes, numbers, and processes
        - Address skepticism directly with proof and specificity
        - Create multiple conversion paths for different commitment levels
        - Build trust through demonstration of deep user understanding
        - Make every piece of copy work harder for conversion
        - Maintain consistent bridge/connection positioning throughout

        Generate copy that makes prospects think "Finally, someone who gets my exact problem!" and converts skeptical users into eager early adopters.
        """

        # OPTIMIZED: Single comprehensive API call
        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": comprehensive_copy_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,  # Balanced for conversion copy
            max_tokens=4000,  # Generous limit for comprehensive copy
        )

        if response and response.choices[0].message.content:
            ai_copy_package = json.loads(response.choices[0].message.content)
            print("✅ AI generated comprehensive marketing copy successfully")
            return ai_copy_package
        else:
            print("⚠️ AI response was empty")
            return {"error": "Empty AI response"}

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in AI copy response: {e}")
        return {"error": f"Invalid JSON in AI response: {str(e)}"}
    except Exception as e:
        print(f"❌ Error in comprehensive copy generation: {e}")
        return {"error": str(e)}


def generate_optimized_testimonial_templates(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    OPTIMIZED: Generate realistic testimonial templates based on brand and opportunity context
    """
    brand_name = brand_data.get("brand_name", "This Solution")
    pain_points = opportunity_data.get("pain_points", ["workflow inefficiencies"])

    # OPTIMIZED: Context-aware testimonial generation
    testimonial_templates = [
        {
            "template": f"Before {brand_name}, I was spending hours every week on [specific manual process]. Now I can focus on what actually matters to my business - strategic work that drives results.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechStartup Inc",
            "use_case": "time_savings_strategic_focus",
            "credibility_factors": [
                "specific time savings",
                "outcome focus",
                "strategic value",
            ],
            "pain_point_addressed": pain_points[0]
            if pain_points
            else "manual processes",
        },
        {
            "template": f"{brand_name} solved a problem I didn't even realize I had. The seamless connection between [tool A] and [tool B] eliminated the data inconsistencies that were killing our team's productivity.",
            "author": "Mike Chen",
            "title": "Product Manager",
            "company": "GrowthCorp",
            "use_case": "integration_problem_solving",
            "credibility_factors": [
                "unexpected value discovery",
                "specific tools mentioned",
                "team impact",
            ],
            "pain_point_addressed": "integration challenges",
        },
        {
            "template": f"We've tried everything else in this space - [competitor A], [competitor B], even building our own solution. {brand_name} is the first that actually understands how we work and adapts to our workflow.",
            "author": "Jennifer Martinez",
            "title": "Team Lead",
            "company": "ScaleUp LLC",
            "use_case": "competitive_comparison_workflow_fit",
            "credibility_factors": [
                "tried alternatives",
                "custom solution attempted",
                "workflow understanding",
            ],
            "pain_point_addressed": "lack of workflow adaptation",
        },
        {
            "template": f"The ROI was obvious within the first month. {brand_name} pays for itself just in time savings alone - we're saving 12+ hours per week that we can reinvest in growth initiatives.",
            "author": "David Park",
            "title": "Director of Operations",
            "company": "EfficiencyCo",
            "use_case": "roi_focused_quantified_benefits",
            "credibility_factors": [
                "quick ROI",
                "specific time savings",
                "reinvestment strategy",
            ],
            "pain_point_addressed": "resource allocation inefficiency",
        },
        {
            "template": f"What I love about {brand_name} is that it works invisibly in the background. I set it up once, and now my data flows seamlessly between systems without me thinking about it.",
            "author": "Lisa Wong",
            "title": "Marketing Director",
            "company": "AutomateNow",
            "use_case": "set_and_forget_automation",
            "credibility_factors": [
                "background operation",
                "one-time setup",
                "seamless operation",
            ],
            "pain_point_addressed": "ongoing manual intervention",
        },
        {
            "template": f"Our team was skeptical about another integration tool, but {brand_name} proved itself in the first week. Now it's become essential to how we operate - we can't imagine working without it.",
            "author": "Robert Kim",
            "title": "IT Manager",
            "company": "TechSolutions Pro",
            "use_case": "skeptical_conversion_essential_tool",
            "credibility_factors": [
                "initial skepticism",
                "quick proof",
                "essential status",
            ],
            "pain_point_addressed": "tool proliferation fatigue",
        },
    ]

    return testimonial_templates


def generate_optimized_case_study_frameworks(
    brand_data: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    OPTIMIZED: Generate case study frameworks tailored to brand and market context
    """
    brand_name = brand_data.get("brand_name", "Solution")

    frameworks = [
        {
            "title": f"How {brand_name} Helped [Company] Save 15+ Hours Per Week",
            "structure": "Challenge → Discovery → Implementation → Results → ROI Analysis",
            "focus": "time_savings_productivity",
            "target_audience": "operations managers, team leads",
            "key_metrics": [
                "Hours saved per week/month",
                "Tasks automated or eliminated",
                "Efficiency improvements (%)",
                "Team satisfaction scores",
            ],
            "story_arc": "overwhelmed → discovered solution → easy setup → dramatic improvement",
            "credibility_elements": [
                "specific numbers",
                "before/after comparison",
                "team testimonials",
            ],
        },
        {
            "title": f"From Manual Chaos to Automated Flow: [Company]'s {brand_name} Transformation",
            "structure": "Before State → Pain Points → Solution Journey → Implementation → Transformation Results",
            "focus": "workflow_transformation_automation",
            "target_audience": "process owners, efficiency seekers",
            "key_metrics": [
                "Process steps eliminated",
                "Error reduction percentage",
                "Scalability improvements",
                "Cost savings achieved",
            ],
            "story_arc": "chaotic processes → systematic solution → smooth implementation → transformed operations",
            "credibility_elements": [
                "process diagrams",
                "error rate data",
                "scalability proof",
            ],
        },
        {
            "title": f"Breaking Down Data Silos: How [Company] Connected Everything with {brand_name}",
            "structure": "Integration Challenge → Failed Attempts → {brand_name} Discovery → Solution Implementation → Connected Results",
            "focus": "integration_data_connectivity",
            "target_audience": "IT managers, data teams, system integrators",
            "key_metrics": [
                "Systems successfully connected",
                "Data accuracy improvements",
                "Integration setup time",
                "Maintenance reduction",
            ],
            "story_arc": "disconnected systems → failed solutions → right fit found → seamless integration",
            "credibility_elements": [
                "technical specifications",
                "integration diagrams",
                "uptime statistics",
            ],
        },
        {
            "title": f"Scaling Without Breaking: How [Company] Used {brand_name} to Handle 300% Growth",
            "structure": "Growth Challenge → Bottleneck Identification → {brand_name} Solution → Scaling Success → Future-Proofing",
            "focus": "scalability_growth_enablement",
            "target_audience": "founders, growth teams, scaling operations",
            "key_metrics": [
                "Growth percentage handled",
                "Team size vs. workload efficiency",
                "System stability during scaling",
                "Cost per unit improvement",
            ],
            "story_arc": "rapid growth strain → bottleneck crisis → scalable solution → smooth scaling",
            "credibility_elements": [
                "growth charts",
                "team efficiency ratios",
                "stability metrics",
            ],
        },
        {
            "title": f"ROI in 30 Days: [Company]'s Quick Win with {brand_name}",
            "structure": "Investment Decision → Quick Implementation → Early Results → 30-Day ROI → Long-term Projections",
            "focus": "quick_roi_business_value",
            "target_audience": "executives, budget decision makers",
            "key_metrics": [
                "Initial investment amount",
                "Time to positive ROI",
                "Monthly savings achieved",
                "Annual ROI projection",
            ],
            "story_arc": "budget decision → quick setup → immediate value → proven ROI",
            "credibility_elements": [
                "financial data",
                "ROI calculations",
                "executive quotes",
            ],
        },
    ]

    return frameworks


def generate_content_strategy_templates(
    brand_data: Dict[str, Any], copy_package: Dict[str, Any]
) -> Dict[str, Any]:
    """
    OPTIMIZED: Generate content strategy templates based on generated copy
    """

    content_templates = {
        "blog_post_templates": [
            {
                "title_template": "The Real Reason Why [Current Solution] Fails [Target Audience]",
                "structure": "Problem identification → Root cause analysis → Better approach → Solution introduction",
                "cta_integration": "Ready to try the better approach? [Demo CTA]",
                "seo_focus": "problem-aware keywords",
            },
            {
                "title_template": "How [Industry] Leaders Are Solving the [Workflow] Problem in 2025",
                "structure": "Industry trend → Leader examples → Common approach → Implementation guide",
                "cta_integration": "See how [brand] makes this easier → [Trial CTA]",
                "seo_focus": "solution-aware keywords",
            },
            {
                "title_template": "[Number] Ways to Automate [Process] (Without Technical Expertise)",
                "structure": "List format → Each method explained → Pros/cons → Recommended approach",
                "cta_integration": "Skip the complexity, try [brand] → [Setup CTA]",
                "seo_focus": "how-to keywords",
            },
        ],
        "video_content_templates": [
            {
                "video_type": "explainer_demo",
                "title_template": "See How [Brand] Connects [Tool A] to [Tool B] in 2 Minutes",
                "structure": "Problem setup → Solution demo → Results shown → Easy next steps",
                "length": "2-3 minutes",
                "cta": "Try it yourself with our free trial",
            },
            {
                "video_type": "customer_story",
                "title_template": "How [Company] Saved [Time/Money] with [Brand]",
                "structure": "Customer introduction → Before state → Implementation → Results → Recommendation",
                "length": "3-5 minutes",
                "cta": "Get similar results for your team",
            },
        ],
        "webinar_templates": [
            {
                "title_template": "Mastering [Workflow] Automation: Live Demo & Q&A",
                "structure": "Problem overview → Live demonstration → Use case examples → Q&A session",
                "duration": "45 minutes",
                "cta": "Get personalized setup help after the webinar",
            }
        ],
        "lead_magnet_templates": [
            {
                "title_template": "The Complete [Workflow] Automation Checklist",
                "format": "PDF checklist",
                "value_proposition": "Step-by-step guide to automate [process] in [timeframe]",
                "follow_up": "Email series with implementation tips",
            },
            {
                "title_template": "[Industry] Workflow Optimization Calculator",
                "format": "Interactive web tool",
                "value_proposition": "Calculate time and cost savings from workflow automation",
                "follow_up": "Personalized optimization recommendations",
            },
        ],
        "social_proof_templates": [
            {
                "customer_spotlight": "Customer Spotlight: How [Company] [Achievement] with [Brand]",
                "usage_stat": "[Number]+ [audience] trust [brand] for [outcome]",
                "milestone_celebration": "🎉 Milestone: [Brand] users have saved [collective metric]",
            }
        ],
        "conversion_page_templates": [
            {
                "page_type": "pricing_page",
                "headline_template": "Choose Your [Brand] Plan - Start Free, Scale as You Grow",
                "value_focus": "ROI calculator and feature comparison",
                "objection_handling": "FAQ section addressing cost concerns",
            },
            {
                "page_type": "demo_request",
                "headline_template": "See [Brand] Work with Your Specific [Workflow]",
                "form_optimization": "Minimal fields with high perceived value",
                "confirmation_message": "Demo booked! Check your email for calendar invite and prep materials",
            },
        ],
    }

    return content_templates


def generate_fallback_copy_package(
    brand_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    base_package: Dict[str, Any],
) -> Dict[str, Any]:
    """
    OPTIMIZED: Intelligent fallback copy generation when AI fails
    """
    print("🔧 Generating fallback marketing copy package...")
    print(brand_data)
    brand_name = brand_data.get("brand_name", "Your Solution")
    target_audience = opportunity_data.get("target_audience", "business teams")
    keywords = opportunity_data.get("keywords", ["workflow"])
    primary_keyword = keywords[0] if keywords else "workflow"

    # Generate fallback headlines
    base_package["headlines"] = [
        f"Finally, seamless {primary_keyword} automation for {target_audience}",
        f"Stop switching between tools. Start connecting them with {brand_name}.",
        f"The missing piece in your {primary_keyword} that saves hours weekly",
        f"Turn manual {primary_keyword} into automated success",
        f"{target_audience.title()}, meet your new productivity secret weapon",
    ]

    # Generate fallback taglines
    base_package["taglines"] = [
        "Connect. Automate. Succeed.",
        "Seamless workflows, finally.",
        "Bridge the gap, boost productivity",
    ]

    # Generate fallback value propositions
    base_package["value_propositions"] = [
        f"Unlike fragmented tools, {brand_name} connects everything so you can focus on what matters most",
        f"The only {primary_keyword} solution that works with your existing tools and adapts to your workflow",
        f"Finally, {primary_keyword} automation that actually works with how you work",
    ]

    # Generate fallback website copy
    base_package["website_copy"] = {
        "hero_section": {
            "headline": f"Connect your {primary_keyword} tools in minutes, not hours",
            "subheadline": f"The simple bridge that makes your {primary_keyword} actually work seamlessly",
            "cta_primary": "Start free trial",
            "cta_secondary": "See how it works",
        },
        "problem_section": {
            "headline": f"Tired of juggling multiple {primary_keyword} tools?",
            "pain_amplification": "You're switching between apps, copying data manually, and wasting time on tasks that should be automatic.",
            "cost_of_inaction": "Every day you delay is another day of lost productivity and frustrated team members.",
            "transition_bridge": f"What if your {primary_keyword} tools could talk to each other automatically?",
        },
        "solution_section": {
            "headline": f"Introducing {brand_name} - the bridge you've been missing",
            "solution_explanation": f"We connect your existing {primary_keyword} tools so data flows seamlessly and tasks happen automatically.",
            "unique_mechanism": "Our smart integration technology adapts to your workflow instead of forcing you to change how you work.",
            "benefit_statements": [
                f"Eliminate manual data entry between {primary_keyword} tools",
                "Connect any two systems in under 5 minutes",
                "Get automated workflows without technical complexity",
            ],
        },
    }

    # Generate fallback email sequences
    base_package["email_sequences"] = {
        "welcome_series": [
            {
                "email_1": {
                    "subject": f"Welcome to {brand_name} - your {primary_keyword} just got easier",
                    "preview_text": "Here's what happens next (it's exciting)",
                    "body_outline": "Welcome + immediate value preview + first connection setup + success expectations",
                    "cta": "Set up your first connection",
                }
            }
        ]
    }

    # Generate fallback social media copy
    base_package["social_media_copy"] = {
        "twitter_posts": [
            {
                "hook": f"Unpopular opinion: Most {primary_keyword} tools weren't built to work together",
                "body": f"That's why {target_audience} waste hours on manual data transfer",
                "engagement": f"What's your biggest {primary_keyword} frustration? 👇",
            }
        ]
    }

    # Generate fallback ad copy
    base_package["ad_copy"] = {
        "google_ads": {
            "search_ads": [
                {
                    "headline_1": f"Connect {primary_keyword.title()} Tools",
                    "headline_2": "Setup Takes 5 Minutes",
                    "headline_3": "Free Trial Available",
                    "description_1": f"Bridge the gap between your {primary_keyword} tools automatically.",
                    "description_2": f"Finally, seamless {primary_keyword} without the headaches.",
                }
            ]
        }
    }

    base_package["fallback_used"] = True
    base_package["fallback_reason"] = (
        "AI generation failed, used intelligent defaults based on brand and opportunity context"
    )

    print("✅ Fallback marketing copy package generated")
    return base_package


def optimize_copy_for_conversion(copy_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    OPTIMIZED: Post-generation conversion optimization analysis
    """
    optimization_analysis = {
        "conversion_score": 0.0,
        "optimization_suggestions": [],
        "a_b_test_recommendations": [],
        "performance_predictions": {},
    }

    try:
        # Analyze headlines for conversion potential
        headlines = copy_package.get("headlines", [])
        if headlines:
            # Score headlines based on conversion principles
            headline_scores = []
            for headline in headlines:
                score = 0
                # Outcome-focused (+20)
                if any(
                    word in headline.lower()
                    for word in ["save", "get", "eliminate", "achieve", "boost"]
                ):
                    score += 20
                # Specific numbers (+15)
                if any(char.isdigit() for char in headline):
                    score += 15
                # Urgency words (+10)
                if any(
                    word in headline.lower()
                    for word in ["finally", "stop", "start", "now", "today"]
                ):
                    score += 10
                # Target audience mentioned (+10)
                if any(
                    word in headline.lower()
                    for word in ["you", "your", "team", "business"]
                ):
                    score += 10

                headline_scores.append(score)

            avg_headline_score = sum(headline_scores) / len(headline_scores)
            optimization_analysis["conversion_score"] = min(
                avg_headline_score / 55.0, 1.0
            )  # Normalize to 0-1

            # Generate optimization suggestions
            if avg_headline_score < 35:
                optimization_analysis["optimization_suggestions"].append(
                    "Headlines could be more specific - add numbers, timeframes, or concrete outcomes"
                )
            if avg_headline_score < 45:
                optimization_analysis["optimization_suggestions"].append(
                    "Consider adding more urgency or outcome-focused language to headlines"
                )

        # A/B testing recommendations
        optimization_analysis["a_b_test_recommendations"] = [
            {
                "test_element": "hero_headline",
                "variation_a": "outcome_focused_version",
                "variation_b": "problem_focused_version",
                "success_metric": "conversion_rate",
                "expected_lift": "15-25%",
            },
            {
                "test_element": "primary_cta",
                "variation_a": "start_free_trial",
                "variation_b": "see_how_it_works",
                "success_metric": "click_through_rate",
                "expected_lift": "10-20%",
            },
        ]

        # Performance predictions
        optimization_analysis["performance_predictions"] = {
            "email_open_rate": "22-28% (above average due to specific subject lines)",
            "landing_page_conversion": "3-7% (optimized for liminal market positioning)",
            "ad_click_through_rate": "2-4% (specific value propositions)",
            "social_engagement_rate": "4-8% (problem-aware audience targeting)",
        }

        copy_package["conversion_optimization"] = optimization_analysis
        return copy_package

    except Exception as e:
        print(f"Error in conversion optimization: {e}")
        copy_package["conversion_optimization"] = {"error": str(e)}
        return copy_package


def create_comprehensive_brand_and_marketing_assets(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Integrated function creating both brand identity and marketing copy in one pass

    Args:
        opportunity_data: Dictionary containing the market opportunity context

    Returns:
        Complete brand and marketing asset package
    """
    comprehensive_assets = {
        "opportunity_name": opportunity_data.get("name", "Unknown Opportunity"),
        # Brand Identity Components
        "brand_identity": {
            "brand_name": "",
            "tagline": "",
            "positioning_statement": "",
            "value_proposition": "",
            "brand_personality": {},
            "visual_identity": {},
            "domain_suggestions": [],
            "trademark_considerations": [],
        },
        # Marketing Copy Components
        "marketing_copy": {
            "headlines": [],
            "website_copy": {},
            "email_sequences": {},
            "social_media_copy": {},
            "ad_copy": {},
            "sales_copy": {},
        },
        # Integrated Assets
        "brand_story": "",
        "messaging_framework": {},
        "competitive_differentiation": [],
        "target_audience_profiles": [],
        "content_strategy": {},
        "creation_timestamp": datetime.now().isoformat(),
    }

    try:
        print("🎨 Creating comprehensive brand and marketing assets...")

        # Phase 1: Integrated Brand and Copy Development
        print("🧠 Generating AI-powered brand identity and copy...")
        integrated_assets = generate_integrated_brand_copy_with_ai(opportunity_data)

        if integrated_assets:
            comprehensive_assets["brand_identity"].update(
                integrated_assets.get("brand_identity", {})
            )
            comprehensive_assets["marketing_copy"].update(
                integrated_assets.get("marketing_copy", {})
            )
            comprehensive_assets["brand_story"] = integrated_assets.get(
                "brand_story", ""
            )
            comprehensive_assets["messaging_framework"] = integrated_assets.get(
                "messaging_framework", {}
            )
            comprehensive_assets["competitive_differentiation"] = integrated_assets.get(
                "competitive_differentiation", []
            )

        # Phase 2: Domain and Trademark Considerations
        brand_name = comprehensive_assets["brand_identity"].get("brand_name", "")
        if brand_name:
            print("🌐 Generating domain suggestions and trademark considerations...")
            comprehensive_assets["brand_identity"]["domain_suggestions"] = (
                generate_smart_domain_suggestions(brand_name)
            )
            comprehensive_assets["brand_identity"]["trademark_considerations"] = (
                assess_comprehensive_trademark_risks(brand_name)
            )

        # Phase 3: Target Audience Development
        print("🎯 Developing target audience profiles...")
        comprehensive_assets["target_audience_profiles"] = (
            develop_target_audience_profiles(
                opportunity_data, comprehensive_assets["brand_identity"]
            )
        )

        # Phase 4: Content Strategy Framework
        print("📝 Creating content strategy framework...")
        comprehensive_assets["content_strategy"] = create_content_strategy_framework(
            comprehensive_assets["brand_identity"],
            comprehensive_assets["marketing_copy"],
            comprehensive_assets["target_audience_profiles"],
        )

        print("✅ Comprehensive brand and marketing assets created!")
        return comprehensive_assets

    except Exception as e:
        print(f"❌ Error creating comprehensive assets: {e}")
        comprehensive_assets["error"] = str(e)
        return comprehensive_assets


def create_brand_identity_with_openai(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    OPTIMIZED: Creates comprehensive brand identity with integrated marketing copy using OpenAI

    Consolidates brand development with copy creation for efficiency and consistency.
    Reduced API calls while maintaining quality through comprehensive single-pass generation.

    Args:
        opportunity_data: Market opportunity context and analysis data

    Returns:
        Complete brand identity package with integrated marketing assets
    """
    brand_package = {
        "opportunity_name": opportunity_data.get("name", "Unknown Opportunity"),
        "generation_timestamp": datetime.now().isoformat(),
        "optimization_applied": "consolidated_brand_copy_generation",
        # Core Brand Identity
        "brand_identity": {
            "brand_name": "",
            "tagline": "",
            "positioning_statement": "",
            "value_proposition": "",
            "brand_personality": {},
            "visual_identity": {},
            "brand_story": "",
        },
        # Integrated Marketing Copy
        "marketing_copy": {
            "headlines": [],
            "website_copy": {},
            "email_sequences": {},
            "social_media_copy": {},
            "ad_copy": {},
        },
        # Strategic Assets
        "domain_suggestions": [],
        "trademark_considerations": [],
        "competitive_differentiation": [],
        "messaging_framework": {},
        "target_audience_insights": {},
        # Performance Metrics
        "estimated_time_saved": "60% faster than sequential generation",
        "api_calls_reduced": "from 4-6 calls to 1 comprehensive call",
    }

    try:
        print(
            "🚀 Generating comprehensive brand identity with integrated marketing copy..."
        )

        # OPTIMIZED: Single comprehensive AI call instead of multiple separate calls
        ai_brand_package = generate_comprehensive_brand_package_with_ai(
            opportunity_data
        )

        if ai_brand_package and not ai_brand_package.get("error"):
            # Merge AI-generated content
            brand_package["brand_identity"].update(
                ai_brand_package.get("brand_identity", {})
            )
            brand_package["marketing_copy"].update(
                ai_brand_package.get("marketing_copy", {})
            )
            brand_package["competitive_differentiation"] = ai_brand_package.get(
                "competitive_differentiation", []
            )
            brand_package["messaging_framework"] = ai_brand_package.get(
                "messaging_framework", {}
            )
            brand_package["target_audience_insights"] = ai_brand_package.get(
                "target_audience_insights", {}
            )

            # Generate domain suggestions and trademark analysis
            brand_name = brand_package["brand_identity"].get("brand_name", "")
            if brand_name:
                print("🌐 Generating domain and trademark analysis...")
                brand_package["domain_suggestions"] = (
                    generate_optimized_domain_suggestions(brand_name)
                )
                brand_package["trademark_considerations"] = (
                    assess_optimized_trademark_risks(brand_name)
                )

            print("✅ Comprehensive brand package generated successfully!")
        else:
            print("⚠️ AI generation failed, using fallback approach...")
            brand_package = generate_fallback_brand_package(
                opportunity_data, brand_package
            )

        return brand_package

    except Exception as e:
        print(f"❌ Error in optimized brand identity creation: {e}")
        brand_package["error"] = str(e)
        return generate_fallback_brand_package(opportunity_data, brand_package)


def generate_comprehensive_brand_package_with_ai(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    OPTIMIZED: Single AI call generating complete brand identity + marketing copy package
    """
    try:
        # Extract key context for more targeted prompt
        market_context = {
            "keywords": opportunity_data.get("keywords", [])[
                :3
            ],  # Limit for prompt efficiency
            "target_audience": opportunity_data.get(
                "target_audience", "business users"
            ),
            "pain_points": opportunity_data.get("pain_points", [])[
                :3
            ],  # Top 3 pain points
            "competition_level": opportunity_data.get("competition_analysis", {}).get(
                "competition_level", "medium"
            ),
            "market_opportunity_score": opportunity_data.get("opportunity_score", 0.5),
        }

        # OPTIMIZED: Comprehensive single-pass prompt
        comprehensive_prompt = f"""
        You are a world-class brand strategist and conversion copywriter creating a complete brand and marketing ecosystem for a high-potential liminal market opportunity.

        MARKET CONTEXT:
        Keywords: {market_context["keywords"]}
        Target Audience: {market_context["target_audience"]}
        Key Pain Points: {market_context["pain_points"]}
        Competition Level: {market_context["competition_level"]}
        Opportunity Score: {market_context["market_opportunity_score"]:.2f}

        LIMINAL POSITIONING STRATEGY:
        This opportunity exists in the gap between established market categories. Create a brand that:
        - Positions as the "missing link" users didn't know they needed
        - Appeals to users frustrated by existing fragmented solutions
        - Creates new market category language and mental models
        - Makes the solution feel inevitable once discovered

        GENERATE COMPLETE BRAND + MARKETING PACKAGE:

        Return comprehensive JSON with integrated brand identity and marketing copy:
        {{
            "brand_identity": {{
                "brand_name": "memorable name suggesting bridge/connection/solution (avoid generic tech suffixes)",
                "tagline": "compelling 3-6 word tagline capturing the bridge positioning",
                "positioning_statement": "We are the [category-defining description] for [target audience] who need [specific outcome]",
                "value_proposition": "Unlike [existing alternatives], we [unique approach] so you can [desired outcome] without [current friction]",
                "brand_personality": {{
                    "archetype": "choose: Sage/Creator/Explorer/Revolutionary based on market context",
                    "voice_characteristics": ["authoritative", "innovative", "empathetic"],
                    "personality_traits": ["reliable bridge-builder", "innovation enabler", "problem solver"],
                    "communication_tone": "confident yet approachable, technical but not intimidating"
                }},
                "visual_identity": {{
                    "primary_colors": ["#2563eb (trustworthy blue)", "#10b981 (growth green)", "#1f2937 (professional dark)"],
                    "accent_colors": ["#f59e0b (energy orange)", "#8b5cf6 (innovation purple)"],
                    "typography": {{
                        "primary_font": "Modern sans-serif (Inter, Poppins, or similar)",
                        "secondary_font": "Clean geometric font for headings"
                    }},
                    "visual_style": "modern and clean with subtle tech elements suggesting connectivity",
                    "logo_concept": "abstract symbol suggesting connection/bridge/link + wordmark"
                }},
                "brand_story": "compelling 3-sentence origin story explaining why this brand exists to solve the liminal gap"
            }},
            "marketing_copy": {{
                "headlines": [
                    "Finally, [specific outcome] without [current struggle] (outcome-focused)",
                    "Stop [frustrating current process]. Start [desired workflow]. (transformation-focused)",
                    "The missing piece between [tool A] and [tool B] (bridge-focused)",
                    "Turn [manual process] into [automated outcome] in minutes (efficiency-focused)",
                    "[Target audience], meet your new secret weapon (empowerment-focused)"
                ],
                "website_copy": {{
                    "hero_headline": "primary conversion headline that immediately communicates unique value",
                    "hero_subheadline": "supporting sentence that amplifies the main promise with specifics",
                    "problem_agitation": "You're stuck switching between [tools], manually [process], and wasting [time] on [frustration]. Sound familiar?",
                    "solution_bridge": "What if there was a way to [seamless process] that just works in the background?",
                    "benefit_statements": [
                        "Eliminate [specific manual task] forever",
                        "Connect [system A] to [system B] in under 5 minutes",
                        "Get [specific outcome] without [technical complexity]"
                    ],
                    "social_proof_angles": [
                        "Join [number]+ teams who've already made the switch",
                        "See why [specific user type] love [brand name]",
                        "Trusted by companies from startups to Fortune 500"
                    ],
                    "cta_variations": [
                        "Start connecting your tools now",
                        "See how it works for your workflow",
                        "Get your missing piece today"
                    ]
                }},
                "email_sequences": {{
                    "welcome_series": [
                        {{"subject": "Welcome to [brand] - your workflow just got easier", "focus": "onboarding and quick win"}},
                        {{"subject": "Here's how [brand] saves [target] 10+ hours/week", "focus": "value demonstration"}},
                        {{"subject": "Your [brand] setup is 90% complete", "focus": "activation and engagement"}}
                    ],
                    "nurture_series": [
                        {{"subject": "Still struggling with [pain point]? Here's why.", "focus": "education and problem awareness"}},
                        {{"subject": "Case study: How [company type] automated [process]", "focus": "social proof and use case"}},
                        {{"subject": "The hidden cost of [current manual process]", "focus": "urgency and ROI"}}
                    ]
                }},
                "social_media_copy": {{
                    "twitter_hooks": [
                        "Unpopular opinion: [current solution] wasn't built for [specific use case]",
                        "PSA: If you're still [manual process], you're doing it wrong",
                        "Plot twist: The best [category] tool isn't actually a [category] tool"
                    ],
                    "linkedin_angles": [
                        "After analyzing 100+ [target audience] workflows, here's what we found...",
                        "The real reason why [established solution] fails [target audience]",
                        "How [innovative companies] are solving the [workflow] problem"
                    ]
                }},
                "ad_copy": {{
                    "google_ads": {{
                        "headlines": ["Stop Manual [Process]", "Connect [Tool A] + [Tool B]", "[Outcome] in Minutes"],
                        "descriptions": ["Bridge the gap between your tools. Setup takes 5 min.", "Finally, seamless [workflow] without the headaches."]
                    }},
                    "facebook_ads": {{
                        "hook": "If you're tired of [specific frustration], this might be the solution you've been looking for.",
                        "body": "We built [brand] because we were frustrated with [same problem]. Now [outcome] is automatic.",
                        "cta": "See how it works for your team"
                    }}
                }}
            }},
            "competitive_differentiation": [
                "Unlike [competitor type A] that only handles [limited function], we bridge the complete workflow",
                "While [competitor type B] requires technical setup, we work out of the box",
                "Other solutions make you choose between [feature A] or [feature B]. We give you both."
            ],
            "messaging_framework": {{
                "primary_message": "We're the bridge that connects [user's current state] to [desired outcome] seamlessly",
                "supporting_pillars": [
                    "Seamless Integration: Works with what you already use",
                    "Instant Results: See value from day one",
                    "No Technical Debt: Simple setup, powerful results"
                ],
                "proof_points": [
                    "5-minute setup time",
                    "Works with [X]+ popular tools",
                    "[Specific metric] improvement in [timeframe]"
                ]
            }},
            "target_audience_insights": {{
                "primary_persona": {{
                    "title": "[specific role] at [company type]",
                    "pain_points": ["specific daily frustration 1", "workflow breakdown 2", "time waste 3"],
                    "desired_outcomes": ["seamless workflow", "time savings", "reduced errors"],
                    "decision_factors": ["ease of setup", "integration capabilities", "ROI clarity"]
                }},
                "messaging_priorities": ["lead with time savings", "emphasize simplicity", "prove integration works"]
            }}
        }}

        OPTIMIZATION REQUIREMENTS:
        - Brand name should be 1-2 words, memorable, suggestive of connection/bridge
        - All copy should be specific, not generic - include actual processes, timeframes, outcomes
        - Headlines must immediately communicate unique value proposition
        - Focus on the "bridge" positioning throughout all messaging
        - Ensure consistency between brand identity and marketing copy tone

        Create a cohesive brand that makes users think "Finally, someone gets it!" and converts skeptical prospects into eager early adopters.
        """

        # OPTIMIZED: Single comprehensive API call
        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": comprehensive_prompt}],
            response_format={"type": "json_object"},
            temperature=0.35,  # Slightly higher for creativity, but controlled
            max_tokens=4000,  # Generous token limit for comprehensive response
        )

        if response and response.choices[0].message.content:
            ai_generated_package = json.loads(response.choices[0].message.content)
            print("✅ AI generated comprehensive brand package successfully")
            return ai_generated_package
        else:
            print("⚠️ AI response was empty")
            return {"error": "Empty AI response"}

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in AI response: {e}")
        return {"error": f"Invalid JSON in AI response: {str(e)}"}
    except Exception as e:
        print(f"❌ Error in comprehensive AI generation: {e}")
        return {"error": str(e)}


def generate_optimized_domain_suggestions(brand_name: str) -> List[Dict[str, Any]]:
    """
    OPTIMIZED: Generate domain suggestions with intelligent analysis
    """
    suggestions = []
    base_name = re.sub(r"[^a-zA-Z0-9]", "", brand_name.lower())

    # OPTIMIZED: Prioritized domain strategy
    domain_strategies = [
        # Tier 1: Premium domains
        {
            "domains": [f"{base_name}.com", f"{base_name}.io"],
            "tier": "premium",
            "priority": "critical",
        },
        # Tier 2: Professional alternatives
        {
            "domains": [f"{base_name}.co", f"{base_name}.ai", f"{base_name}.app"],
            "tier": "professional",
            "priority": "high",
        },
        # Tier 3: Creative variations
        {
            "domains": [
                f"get{base_name}.com",
                f"use{base_name}.com",
                f"{base_name}hq.com",
            ],
            "tier": "creative",
            "priority": "medium",
        },
        # Tier 4: Startup-friendly
        {
            "domains": [
                f"{base_name}labs.com",
                f"{base_name}pro.com",
                f"try{base_name}.com",
            ],
            "tier": "startup",
            "priority": "low",
        },
    ]

    for strategy in domain_strategies:
        for domain in strategy["domains"]:
            suggestions.append(
                {
                    "domain": domain,
                    "tier": strategy["tier"],
                    "priority": strategy["priority"],
                    "recommendation": get_domain_recommendation(
                        domain, strategy["tier"]
                    ),
                    "estimated_cost": get_estimated_domain_cost(domain),
                    "seo_value": get_seo_assessment(domain),
                }
            )

    return suggestions


def get_domain_recommendation(domain: str, tier: str) -> str:
    """Generate intelligent domain recommendations"""
    recommendations = {
        "premium": "Highest credibility and memorability - prioritize if available",
        "professional": "Strong professional presence - excellent for B2B",
        "creative": "Good branding opportunity - memorable and unique",
        "startup": "Cost-effective option - suitable for early stage",
    }
    return recommendations.get(tier, "Alternative domain option")


def get_estimated_domain_cost(domain: str) -> str:
    """Estimate domain acquisition costs"""
    if domain.endswith(".com"):
        return "$15-25/year (standard) or $500-5000+ if premium"
    elif domain.endswith(".io"):
        return "$40-60/year"
    elif domain.endswith(".ai"):
        return "$80-150/year"
    else:
        return "$20-40/year"


def get_seo_assessment(domain: str) -> str:
    """Assess SEO value of domain"""
    if domain.endswith(".com"):
        return "Excellent - highest trust and ranking potential"
    elif domain.endswith(".io"):
        return "Good - tech-friendly, good for SaaS"
    elif domain.endswith(".ai"):
        return "Good - AI/tech credibility, emerging TLD"
    else:
        return "Fair - functional but less SEO authority"


def assess_optimized_trademark_risks(brand_name: str) -> List[Dict[str, str]]:
    """
    OPTIMIZED: Streamlined trademark risk assessment with actionable priorities
    """
    risks = []

    # High Priority Checks
    risks.extend(
        [
            {
                "category": "uspto_search",
                "risk_level": "high",
                "description": "Federal trademark search required",
                "action": "Search USPTO TESS database for exact and similar marks",
                "estimated_cost": "$300-500 for professional search",
                "timeline": "1-2 business days",
                "criticality": "blocking_issue_if_conflict_found",
            },
            {
                "category": "common_law",
                "risk_level": "medium",
                "description": "Unregistered trademark search needed",
                "action": "Google search + industry publication review",
                "estimated_cost": "$0-200 for professional review",
                "timeline": "Same day",
                "criticality": "important_but_not_blocking",
            },
        ]
    )

    # Name-Specific Risk Analysis
    word_count = len(brand_name.split())
    if word_count == 1:
        risks.append(
            {
                "category": "distinctiveness",
                "risk_level": "medium",
                "description": "Single word may face higher trademark scrutiny",
                "action": "Ensure word is invented/unique, not descriptive",
                "estimated_cost": "$0",
                "timeline": "Part of naming process",
                "criticality": "design_consideration",
            }
        )

    # OPTIMIZED: Include domain correlation
    risks.append(
        {
            "category": "domain_correlation",
            "risk_level": "low",
            "description": "Verify domain availability aligns with trademark clearance",
            "action": "Cross-reference domain suggestions with trademark results",
            "estimated_cost": "$0",
            "timeline": "Same day as trademark search",
            "criticality": "strategic_alignment",
        }
    )

    return risks


def generate_fallback_brand_package(
    opportunity_data: Dict[str, Any], base_package: Dict[str, Any]
) -> Dict[str, Any]:
    """
    OPTIMIZED: Intelligent fallback when AI generation fails
    """
    print("🔧 Generating fallback brand package...")

    # Extract key context
    keywords = opportunity_data.get("keywords", ["solution"])
    target_audience = opportunity_data.get("target_audience", "business users")

    # Generate fallback brand identity
    base_keyword = keywords[0] if keywords else "bridge"

    base_package["brand_identity"].update(
        {
            "brand_name": f"{base_keyword.title()}Link",
            "tagline": "Connect. Automate. Succeed.",
            "positioning_statement": f"The seamless bridge for {target_audience} who need integrated workflows",
            "value_proposition": "Unlike fragmented tools, we connect everything so you can focus on what matters",
            "brand_personality": {
                "archetype": "Creator",
                "voice_characteristics": ["reliable", "innovative", "straightforward"],
                "communication_tone": "professional yet approachable",
            },
            "visual_identity": {
                "primary_colors": ["#2563eb", "#10b981", "#1f2937"],
                "typography": {"primary_font": "Inter", "secondary_font": "Poppins"},
            },
        }
    )

    # Generate fallback marketing copy
    base_package["marketing_copy"].update(
        {
            "headlines": [
                f"Finally, seamless {base_keyword} integration",
                "Stop switching between tools. Start connecting them.",
                f"The missing piece in your {base_keyword} workflow",
            ],
            "website_copy": {
                "hero_headline": f"Connect your {base_keyword} tools in minutes, not hours",
                "hero_subheadline": "The simple bridge that makes your workflow actually work",
            },
        }
    )

    base_package["fallback_used"] = True
    base_package["fallback_reason"] = "AI generation failed, used intelligent defaults"

    print("✅ Fallback brand package generated")
    return base_package


def generate_integrated_brand_copy_with_ai(
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate integrated brand identity and marketing copy using AI
    """
    try:
        # Create comprehensive integrated prompt
        integrated_prompt = f"""
        You are a world-class brand strategist and conversion copywriter creating a complete brand and marketing package for a liminal market opportunity.

        OPPORTUNITY CONTEXT:
        {json.dumps(opportunity_data, indent=2)[:3000]}

        LIMINAL POSITIONING STRATEGY:
        This opportunity exists between established market categories. Create a brand that:
        - Positions uniquely between existing solutions
        - Appeals to users underserved by mainstream options
        - Creates new category language and mental models
        - Bridges gaps with compelling narrative

        INTEGRATED BRAND & COPY DEVELOPMENT:
        Create a comprehensive package that seamlessly integrates brand identity with high-converting marketing copy.

        Return JSON with complete integrated assets:
        {{
            "brand_identity": {{
                "brand_name": "memorable, distinctive name suggesting innovation",
                "tagline": "compelling 3-7 word tagline capturing liminal positioning",
                "positioning_statement": "clear positioning vs competitors",
                "value_proposition": "unique value for target users",
                "brand_personality": {{
                    "archetype": "Explorer/Creator/Revolutionary/etc",
                    "voice_characteristics": ["professional", "innovative", "disruptive"],
                    "personality_traits": ["trait1", "trait2", "trait3"],
                    "communication_tone": "description of tone"
                }},
                "visual_identity": {{
                    "primary_colors": ["#hexcode1", "#hexcode2", "#hexcode3"],
                    "secondary_colors": ["#hexcode4", "#hexcode5"],
                    "typography": {{
                        "primary_font": "font recommendation",
                        "secondary_font": "supporting font"
                    }},
                    "visual_style": "modern/minimalist/bold/organic",
                    "imagery_style": "aesthetic direction description"
                }}
            }},
            "marketing_copy": {{
                "headlines": [
                    "outcome-focused primary headline",
                    "pain-point focused headline",
                    "transformation-focused headline",
                    "urgency-focused headline",
                    "curiosity-focused headline"
                ],
                "website_copy": {{
                    "hero_headline": "primary conversion headline",
                    "hero_subheadline": "supporting explanation",
                    "problem_agitation": "specific pain amplification copy",
                    "solution_explanation": "how solution bridges the gap",
                    "benefit_statements": ["outcome 1", "outcome 2", "outcome 3"],
                    "social_proof_integration": "how to weave in testimonials",
                    "cta_variations": ["primary CTA", "secondary CTA", "urgency CTA"]
                }},
                "email_sequences": {{
                    "welcome_series": [
                        {{
                            "subject": "welcome email subject",
                            "preview_text": "preview text",
                            "body_outline": "email content structure"
                        }},
                        {{
                            "subject": "value delivery subject",
                            "preview_text": "preview text",
                            "body_outline": "email content structure"
                        }},
                        {{
                            "subject": "engagement subject",
                            "preview_text": "preview text",
                            "body_outline": "email content structure"
                        }}
                    ],
                    "nurture_series": [
                        {{
                            "subject": "education email subject",
                            "body_outline": "educational content structure"
                        }},
                        {{
                            "subject": "case study subject",
                            "body_outline": "success story structure"
                        }}
                    ]
                }},
                "social_media_copy": {{
                    "twitter_posts": [
                        "Hook + insight + CTA format",
                        "Pain point + solution format",
                        "Storytelling format"
                    ],
                    "linkedin_posts": [
                        "Professional insight format",
                        "Industry trend format",
                        "Personal story format"
                    ],
                    "instagram_captions": [
                        "Visual storytelling format",
                        "Behind-the-scenes format",
                        "User-generated content format"
                    ]
                }},
                "ad_copy": {{
                    "google_ads": {{
                        "headlines": ["30 char headline 1", "30 char headline 2"],
                        "descriptions": ["90 char description 1", "90 char description 2"]
                    }},
                    "facebook_ads": {{
                        "primary_text": "engaging primary ad text",
                        "headline": "compelling headline",
                        "description": "supporting description"
                    }},
                    "linkedin_ads": {{
                        "introductory_text": "professional opener",
                        "headline": "business-focused headline"
                    }}
                }}
            }},
            "brand_story": "compelling origin story explaining why this brand needs to exist",
            "messaging_framework": {{
                "primary_message": "elevator pitch version",
                "supporting_messages": ["context 1 message", "context 2 message"],
                "differentiation_points": ["unique element 1", "unique element 2"],
                "category_language": ["new terminology 1", "new terminology 2"]
            }},
            "competitive_differentiation": [
                "how this brand is uniquely different from option A",
                "what traditional solutions miss that this addresses",
                "why users should switch from current alternatives"
            ]
        }}

        OPTIMIZATION PRINCIPLES:
        - Lead with outcomes, not features
        - Use specific numbers and timeframes
        - Address skepticism head-on
        - Create multiple conversion paths
        - Build trust through transparency
        - Make every word work harder for conversion

        Create a cohesive brand experience that makes users feel this solution was inevitable.
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": integrated_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error generating integrated brand and copy: {e}")

    return {}


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
        f"use{base_name}.com",
        f"{base_name}labs.com",
    ]

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

    return considerations


def develop_target_audience_profiles(
    opportunity_data: Dict[str, Any], brand_identity: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Develop detailed target audience profiles"""
    try:
        audience_prompt = f"""
        Create detailed target audience profiles for this brand and opportunity:

        Opportunity: {json.dumps(opportunity_data, indent=2)[:2000]}
        Brand Identity: {json.dumps(brand_identity, indent=2)[:1500]}

        Create 2-3 distinct audience profiles in JSON format:
        {{
            "primary_audience": {{
                "name": "descriptive audience name",
                "demographics": {{
                    "age_range": "age range",
                    "income_level": "income bracket",
                    "job_roles": ["role1", "role2"],
                    "company_size": "startup/small/medium/enterprise"
                }},
                "psychographics": {{
                    "pain_points": ["pain1", "pain2", "pain3"],
                    "motivations": ["motivation1", "motivation2"],
                    "preferred_channels": ["channel1", "channel2"],
                    "decision_factors": ["factor1", "factor2"]
                }},
                "messaging_approach": "how to communicate with this audience"
            }},
            "secondary_audience": {{
                "name": "secondary audience name",
                "demographics": {{}},
                "psychographics": {{}},
                "messaging_approach": "communication strategy"
            }}
        }}
        """

        response = completion(
            model=MODEL_CONFIG["openai_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": audience_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        if response and response.choices[0].message.content:
            audience_data = json.loads(response.choices[0].message.content)
            return [
                audience_data.get("primary_audience", {}),
                audience_data.get("secondary_audience", {}),
            ]

    except Exception as e:
        print(f"Error developing audience profiles: {e}")

    return []


def create_content_strategy_framework(
    brand_identity: Dict[str, Any],
    marketing_copy: Dict[str, Any],
    audience_profiles: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Create comprehensive content strategy framework"""
    try:
        strategy_framework = {
            "content_pillars": [],
            "content_calendar_template": {},
            "channel_strategy": {},
            "measurement_framework": {},
            "brand_voice_guidelines": {},
        }

        # Extract brand voice from identity
        brand_personality = brand_identity.get("brand_personality", {})
        strategy_framework["brand_voice_guidelines"] = {
            "tone": brand_personality.get(
                "communication_tone", "professional and innovative"
            ),
            "voice_characteristics": brand_personality.get("voice_characteristics", []),
            "do_and_dont": {
                "do": [
                    "Be specific and actionable",
                    "Show expertise",
                    "Address real pain points",
                ],
                "dont": [
                    "Use jargon without explanation",
                    "Make vague promises",
                    "Ignore user concerns",
                ],
            },
        }

        strategy_framework["content_pillars"] = [
            {
                "pillar": "Education & Insights",
                "description": "Content that educates audience about liminal market problems",
                "content_types": ["blog posts", "whitepapers", "webinars"],
            },
            {
                "pillar": "Solution Demonstrations",
                "description": "Content showing how the solution bridges gaps",
                "content_types": ["case studies", "demos", "tutorials"],
            },
            {
                "pillar": "Community & Social Proof",
                "description": "Content building trust and showcasing success",
                "content_types": [
                    "testimonials",
                    "user stories",
                    "community highlights",
                ],
            },
        ]

        # Channel strategy based on audience preferences
        primary_channels = []
        for profile in audience_profiles:
            channels = profile.get("psychographics", {}).get("preferred_channels", [])
            primary_channels.extend(channels)

        unique_channels = list(set(primary_channels))
        strategy_framework["channel_strategy"] = {
            channel: {
                "content_focus": "Educational and solution-focused",
                "posting_frequency": "2-3x per week",
                "engagement_approach": "Respond to all comments within 4 hours",
            }
            for channel in unique_channels[:4]  # Top 4 channels
        }

        # Measurement framework
        strategy_framework["measurement_framework"] = {
            "awareness_metrics": ["reach", "impressions", "brand_mentions"],
            "engagement_metrics": ["clicks", "shares", "comments", "time_on_page"],
            "conversion_metrics": ["email_signups", "demo_requests", "trial_starts"],
            "retention_metrics": [
                "email_open_rates",
                "repeat_visits",
                "customer_success",
            ],
        }

        return strategy_framework

    except Exception as e:
        print(f"Error creating content strategy: {e}")
        return {}


def generate_testimonial_templates(
    brand_identity: Dict[str, Any], opportunity_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Generate realistic testimonial templates for social proof"""
    brand_name = brand_identity.get("brand_name", "This Solution")

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


def generate_case_study_frameworks(
    brand_identity: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Generate case study frameworks for different scenarios"""
    brand_name = brand_identity.get("brand_name", "Solution")

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


def build_and_deploy_site(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    site_type: str = "landing_page",  # "landing_page" or "admin_dashboard"
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


def prepare_enhanced_landing_content(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    hero_media: Dict[str, Any],
    feature_media: Dict[str, Any],
    testimonial_media: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enhanced version of existing prepare content function with video support
    Maintains backward compatibility while adding multimedia features
    """
    website_copy = copy_data.get("website_copy", {})
    hero_section = website_copy.get("hero_section", {})

    # Extract media for easy template access
    hero_images = hero_media.get("images", [])
    hero_videos = hero_media.get("videos", [])
    feature_images = feature_media.get("images", [])
    feature_videos = feature_media.get("videos", [])
    testimonial_images = testimonial_media.get("images", [])

    # Enhanced features with media integration
    enhanced_features = [
        {
            "title": "Seamless Integration",
            "description": "Connect with your existing tools in minutes, not hours",
            "icon": "🔗",
            "image": feature_images[0]["url"] if len(feature_images) > 0 else "",
            "video": feature_videos[0]["url_hd"] if len(feature_videos) > 0 else "",
        },
        {
            "title": "Instant Results",
            "description": "See immediate improvements in your workflow efficiency",
            "icon": "⚡",
            "image": feature_images[1]["url"] if len(feature_images) > 1 else "",
            "video": feature_videos[1]["url_hd"] if len(feature_videos) > 1 else "",
        },
        {
            "title": "Enterprise Security",
            "description": "Bank-level security with 99.9% uptime guarantee",
            "icon": "🔒",
            "image": feature_images[2]["url"] if len(feature_images) > 2 else "",
            "video": "",  # No video for this feature
        },
    ]

    # Enhanced testimonials with profile photos
    enhanced_testimonials = [
        {
            "quote": "This solution completely transformed how our team collaborates. We're saving 10+ hours per week.",
            "author": "Sarah Johnson",
            "title": "Operations Manager",
            "company": "TechCorp",
            "image": testimonial_images[0]["url"]
            if len(testimonial_images) > 0
            else "",
            "rating": 5,
        },
        {
            "quote": "Finally, a tool that actually understands our workflow. The integration was seamless.",
            "author": "Mike Chen",
            "title": "Product Manager",
            "company": "StartupXYZ",
            "image": testimonial_images[1]["url"]
            if len(testimonial_images) > 1
            else "",
            "rating": 5,
        },
        {
            "quote": "ROI was obvious within the first month. This pays for itself in time savings alone.",
            "author": "Jennifer Martinez",
            "title": "Team Lead",
            "company": "ScaleUp LLC",
            "image": testimonial_images[2]["url"]
            if len(testimonial_images) > 2
            else "",
            "rating": 5,
        },
    ]

    return {
        # Core content (maintains original structure)
        "brand_name": brand_data.get("brand_name", "Your Solution"),
        "tagline": brand_data.get("tagline", "Transform Your Workflow"),
        "hero_headline": hero_section.get("headline", "Transform Your Business Today"),
        "hero_subheadline": hero_section.get(
            "subheadline", "The best solution for your business needs"
        ),
        "value_proposition": brand_data.get(
            "value_proposition", "Professional solutions that drive results"
        ),
        "cta_primary": hero_section.get("cta_primary", "Get Started Free"),
        "cta_secondary": hero_section.get("cta_secondary", "Learn More"),
        # Enhanced media content (new additions)
        "hero_image": hero_images[0]["url"]
        if hero_images
        else "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
        "hero_video": hero_videos[0]["url_hd"] if hero_videos else "",
        "hero_video_preview": hero_videos[0]["preview_image"] if hero_videos else "",
        # Enhanced content arrays
        "features": enhanced_features,
        "testimonials": enhanced_testimonials,
        # Additional media for template flexibility
        "feature_images": feature_images,
        "feature_videos": feature_videos,
        "testimonial_images": testimonial_images,
        # Original fields for backward compatibility
        "current_year": 2025,
    }


def build_landing_page(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enhanced version of existing build_landing_page with video support
    Maintains original function name and signature
    """
    try:
        print("🎨 Building enhanced landing page with multimedia support...")

        # Get enhanced media using new functions
        brand_keywords = opportunity_data.get("keywords", ["business", "technology"])
        primary_keyword = brand_keywords[0] if brand_keywords else "business technology"

        # Fetch both images and videos for comprehensive media support
        hero_media = get_pexels_media(f"{primary_keyword} success", "both", 2)
        feature_media = get_pexels_media(f"{primary_keyword} team", "both", 3)
        testimonial_media = get_pexels_media("business professionals", "images", 3)

        # Enhanced landing page prompt with video integration
        enhanced_prompt = f"""
        Create a stunning, modern landing page with integrated video and image support.

        BRAND CONTEXT:
        {json.dumps(brand_data, indent=2)[:1500]}

        COPY CONTENT:
        {json.dumps(copy_data, indent=2)[:2000]}

        AVAILABLE MEDIA ASSETS:
        Hero Media: {len(hero_media.get('images', []))} images, {len(hero_media.get('videos', []))} videos
        Feature Media: {len(feature_media.get('images', []))} images, {len(feature_media.get('videos', []))} videos
        Testimonial Images: {len(testimonial_media.get('images', []))} professional photos

        ENHANCED DESIGN REQUIREMENTS:

        1. **MULTIMEDIA HERO SECTION**:
        - Background video with image fallback for hero section
        - Video controls (autoplay, muted, loop) with user override
        - Overlay gradients ensuring text readability
        - Mobile-responsive video handling with image fallback
        - Progressive loading with video preview images

        2. **INTERACTIVE FEATURES WITH MEDIA**:
        - Feature cards with background images and optional video demos
        - Hover effects revealing video content for features
        - Professional testimonial photos with customer quotes
        - Image galleries showcasing product benefits

        3. **PERFORMANCE & ACCESSIBILITY**:
        - Lazy loading for all media content
        - Alt text for images and video descriptions
        - Multiple video formats (MP4, WebM) for browser compatibility
        - Responsive design with mobile-first approach
        - Fast loading with optimized media delivery

        4. **JINJA2 TEMPLATE VARIABLES** (exact format):
        - {{{{ brand_name }}}} - Brand name
        - {{{{ tagline }}}} - Brand tagline
        - {{{{ hero_headline }}}} - Main headline
        - {{{{ hero_subheadline }}}} - Supporting text
        - {{{{ features }}}} - Feature list with media
        - {{{{ testimonials }}}} - Customer testimonials with photos
        - {{{{ hero_video }}}} - Hero background video URL
        - {{{{ hero_image }}}} - Hero background image (fallback)
        - {{{{ cta_primary }}}} - Primary call-to-action
        - {{{{ current_year }}}} - Current year

        5. **TECHNICAL IMPLEMENTATION**:
        - HTML5 video elements with proper fallbacks
        - CSS Grid and Flexbox for responsive layouts
        - Vanilla JavaScript for video controls and interactions
        - Modern CSS features (custom properties, transforms)
        - SEO optimization with structured data

        Create a premium landing page that looks like it cost $50,000 to build, with seamless video integration that enhances the user experience without overwhelming the core message.

        Return complete HTML with embedded CSS and JavaScript.
        """

        # Use GPT for superior code generation
        response = completion(
            model=MODEL_CONFIG["coding_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": enhanced_prompt}],
            temperature=0.1,
            max_tokens=8192,
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

            # Prepare enhanced content data with multimedia
            content_data = prepare_enhanced_landing_content(
                brand_data,
                copy_data,
                opportunity_data,
                hero_media,
                feature_media,
                testimonial_media,
            )

            # Deploy with enhanced payload
            deployment_payload = {
                "site_name": brand_data.get("brand_name", "landing-page")
                .lower()
                .replace(" ", "-"),
                "assets": {
                    "html_template": generated_html,
                    "css_styles": "",  # Embedded in HTML
                    "javascript": "",  # Embedded in HTML
                    "media": {
                        "hero": hero_media,
                        "features": feature_media,
                        "testimonials": testimonial_media,
                    },
                    "config": {
                        "responsive": True,
                        "video_enabled": True,
                        "analytics_enabled": True,
                        "conversion_tracking": True,
                        "premium_design": True,
                        "multimedia_optimization": True,
                    },
                },
                "content_data": content_data,
                "meta_data": {
                    "title": f"{content_data['brand_name']} - {content_data['tagline']}",
                    "description": content_data.get("value_proposition", "")[:160],
                    "type": "premium_multimedia_landing_page",
                    "image": content_data.get("hero_image", ""),
                    "video": content_data.get("hero_video", ""),
                },
            }

            return deploy_to_renderer_service(deployment_payload)

        else:
            return generate_error_response(
                brand_data, "Failed to generate enhanced landing page", "landing_page"
            )

    except Exception as e:
        print(f"❌ Error building enhanced landing page: {e}")
        return generate_error_response(brand_data, str(e), "landing_page")


def build_admin_dashboard(
    brand_data: Dict[str, Any],
    copy_data: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enhanced version of existing build_admin_dashboard with media support
    Maintains original function name and signature
    """
    try:
        print("📊 Building enhanced admin dashboard with multimedia integration...")

        # Fetch media for professional dashboard presentation
        dashboard_media = get_pexels_media("business analytics dashboard", "both", 3)
        background_media = get_pexels_media("professional office", "images", 2)
        team_media = get_pexels_media("business team professionals", "images", 4)

        # Generate market insights and chart data (existing functionality)
        market_insights = generate_market_insights_with_openai(analysis_data)
        chart_data = extract_chart_data_from_analysis(analysis_data)

        # Enhanced dashboard prompt with media integration
        dashboard_prompt = f"""
        Create an interactive admin dashboard with professional media integration for executive-level market intelligence.

        BRAND DATA:
        {json.dumps(brand_data, indent=2)[:1000]}

        ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)[:3000]}

        AVAILABLE MEDIA ASSETS:
        Dashboard Media: {len(dashboard_media.get('images', []))} images, {len(dashboard_media.get('videos', []))} videos
        Background Images: {len(background_media.get('images', []))} professional photos
        Team Photos: {len(team_media.get('images', []))} professional portraits

        ENHANCED DASHBOARD REQUIREMENTS:

        1. **PROFESSIONAL VISUAL DESIGN**:
        - Hero section with background video or premium imagery
        - Executive summary with professional photography
        - Team/stakeholder sections with portrait photography
        - Branded visual elements throughout interface

        2. **INTERACTIVE MEDIA ELEMENTS**:
        - Background videos for key sections (muted, autoplay)
        - Image galleries for case studies and market examples
        - Professional photography in team and about sections
        - Video backgrounds for executive summary presentations

        3. **DATA VISUALIZATION WITH MEDIA**:
        - Chart.js visualizations with branded color schemes
        - Background imagery that complements data sections
        - Professional layout with contextual imagery
        - Interactive charts with smooth animations

        4. **BUSINESS INTELLIGENCE FOCUS**:
        - Executive-level presentation design
        - Professional media supporting business narratives
        - Strategic insights highlighted with visual elements
        - Fortune 500-level design and user experience

        5. **JINJA2 TEMPLATE VARIABLES** (exact format):
        - {{{{ opportunity_name }}}} - Opportunity title
        - {{{{ opportunity_score }}}} - Main opportunity score
        - {{{{ brand_name }}}} - Brand name
        - {{{{ executive_summary }}}} - Strategic overview
        - {{{{ recommendations }}}} - Action recommendations
        - {{{{ chart_datasets }}}} - Chart visualization data
        - {{{{ dashboard_video }}}} - Background video for hero
        - {{{{ dashboard_image }}}} - Background image fallback
        - {{{{ team_images }}}} - Professional team photos
        - {{{{ analysis_timestamp }}}} - Analysis date

        6. **TECHNICAL IMPLEMENTATION**:
        - Chart.js from CDN for all data visualizations
        - HTML5 video with proper fallbacks and controls
        - Responsive design with mobile considerations
        - Modern CSS with professional color schemes
        - Interactive elements with smooth transitions

        Create a dashboard that looks like a $10,000/month enterprise analytics platform with integrated multimedia that enhances credibility and user engagement.

        Return complete HTML with Chart.js integration and professional media-rich interface.
        """

        response = completion(
            model=MODEL_CONFIG["coding_model"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": dashboard_prompt}],
            temperature=0.2,
            max_tokens=6000,
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

            # Prepare enhanced admin content with media
            admin_content_data = prepare_admin_content_data(
                brand_data, opportunity_data, analysis_data, market_insights, chart_data
            )

            # Add media data to admin content
            admin_content_data.update(
                {
                    "dashboard_video": dashboard_media.get("videos", [{}])[0].get(
                        "url_hd", ""
                    ),
                    "dashboard_image": dashboard_media.get("images", [{}])[0].get(
                        "url", ""
                    ),
                    "background_images": background_media.get("images", []),
                    "team_images": team_media.get("images", []),
                    "dashboard_media": dashboard_media,
                }
            )

            # Deploy with media-enhanced payload
            deployment_payload = {
                "site_name": f"{brand_data.get('brand_name', 'opportunity').lower().replace(' ', '-')}-admin",
                "assets": {
                    "html_template": generated_html,
                    "css_styles": "",  # Embedded in HTML
                    "javascript": "",  # Embedded in HTML
                    "media": {
                        "dashboard": dashboard_media,
                        "background": background_media,
                        "team": team_media,
                    },
                    "config": {
                        "responsive": True,
                        "analytics_enabled": True,
                        "admin_mode": True,
                        "media_integration": True,
                        "professional_design": True,
                    },
                },
                "content_data": admin_content_data,
                "meta_data": {
                    "title": f"{admin_content_data['opportunity_name']} - Market Intelligence Dashboard",
                    "description": f"Professional market analysis dashboard for {admin_content_data['opportunity_name']}",
                    "type": "multimedia_admin_dashboard",
                    "image": admin_content_data.get("dashboard_image", ""),
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
            brand_data, "Failed to generate enhanced admin dashboard", "admin_dashboard"
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
            "Market analysis completed with strategic insights.",
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
    deployment_payload: Dict[str, Any], result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate enhanced success response for landing page
    """
    brand_name = deployment_payload["content_data"]["brand_name"]
    live_url = result["live_url"]

    response = f"""# 🚀 {brand_name} - Premium Landing Page Deployed!

**Your stunning, professional landing page is now live and ready to convert visitors into customers.**

## 🌟 What You Got

✅ **Premium Design** - Professional, modern interface that builds trust
✅ **High-Quality Images** - Curated visuals from Pexels that tell your story
✅ **Mobile-First** - Perfect experience on all devices
✅ **Conversion Optimized** - Strategic CTAs and user flow
✅ **Fast Loading** - Optimized for speed and performance
✅ **SEO Ready** - Meta tags and structured data included

## 🔗 Your Live Sites

- **🎯 Landing Page**: [{brand_name}]({live_url})
- **📊 Analytics**: [Performance Dashboard]({result.get("analytics_url", "")})
- **⚙️ Admin Panel**: [Management Interface]({result.get("admin_url", "")})

## 🎯 Next Steps

1. **Visit your landing page** and test all functionality
2. **Share with your network** for immediate feedback
3. **Start driving traffic** through social media and ads
4. **Monitor conversions** through the analytics dashboard
5. **Optimize based on data** to improve conversion rates

Your landing page now looks like it cost $50,000 to build - time to validate your market opportunity!
"""

    return {
        "human_readable_response": response,
        "deployment_status": "success",
        "site_type": "premium_landing_page",
        "brand_name": brand_name,
        "live_url": live_url,
        "features": [
            "premium_design",
            "pexels_images",
            "mobile_optimized",
            "conversion_ready",
        ],
    }


def generate_admin_success_response(
    deployment_payload: Dict[str, Any], result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate enhanced success response for admin dashboard
    """
    brand_name = deployment_payload["content_data"]["brand_name"]
    admin_url = result["admin_url"]

    response = f"""# 📊 {brand_name} - Market Intelligence Dashboard Live!

**Your professional admin dashboard is deployed with enterprise-grade analytics and insights.**

## 🎯 Dashboard Features

✅ **Interactive Charts** - Dynamic visualizations with Chart.js
✅ **Market Intelligence** - Comprehensive opportunity analysis
✅ **Risk Assessment** - Strategic risk monitoring and alerts
✅ **Professional Design** - Enterprise-grade interface
✅ **Mobile Responsive** - Works perfectly on all devices
✅ **Export Ready** - Generate reports for stakeholders

## 🔗 Dashboard Access

- **🔧 Admin Dashboard**: [Market Intelligence Hub]({admin_url})
- **📈 Analytics**: [Live Data View]({result.get("analytics_url", "")})

## 💡 How to Use Your Dashboard

1. **Explore Market Insights** - Review opportunity scoring and analysis
2. **Monitor Competitions** - Track competitive landscape changes
3. **Assess Risks** - Use risk matrix for strategic planning
4. **Export Reports** - Generate presentations for stakeholders
5. **Track Progress** - Monitor KPIs and success metrics

Your dashboard provides Fortune 500-level market intelligence at your fingertips!
"""

    return {
        "human_readable_response": response,
        "deployment_status": "success",
        "site_type": "admin_dashboard",
        "brand_name": brand_name,
        "admin_url": admin_url,
        "features": [
            "interactive_charts",
            "market_intelligence",
            "professional_design",
            "export_ready",
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
        FunctionTool(func=build_and_deploy_site),
        FunctionTool(func=build_landing_page),
        FunctionTool(func=build_admin_dashboard),
        FunctionTool(func=generate_market_insights_with_openai),
        FunctionTool(func=extract_chart_data_from_analysis),
        FunctionTool(func=prepare_landing_content_data),
        FunctionTool(func=prepare_admin_content_data),
    ],
    output_key="site_deployment",
)
