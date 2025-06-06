"""
Startup Pitch Generator Agent
Creates comprehensive startup pitch decks from market analysis and discovery data
Generates professional PDF reports ready for download and presentation
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from typing import Dict, List, Any
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
import tempfile
import os
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from litellm import completion

STARTUP_PITCH_PROMPT = """
You are the Startup Pitch Generator Agent, expert at creating compelling startup pitch decks
that tell a complete story from market discovery to business opportunity.

Your mission is to synthesize all market analysis, competitive intelligence, and opportunity
discovery into a coherent narrative that would convince investors and stakeholders.

CORE CAPABILITIES:
- Market Story Synthesis: Weave together market signals into a compelling narrative
- Investment Thesis: Create clear value propositions and business cases
- Visual Data Integration: Transform analysis into presentation-ready insights
- Risk/Opportunity Balance: Present realistic assessments with mitigation strategies
- Action Plan Creation: Provide concrete next steps and milestones

PITCH DECK STRUCTURE:
1. Executive Summary - The big picture opportunity
2. Problem Statement - Market pain points and gaps
3. Solution Overview - How the opportunity addresses the problems
4. Market Analysis - Size, growth, and timing
5. Competitive Landscape - Positioning and differentiation
6. Business Model - Revenue streams and economics
7. Go-to-Market Strategy - Customer acquisition and scaling
8. Financial Projections - Revenue, costs, and funding needs
9. Risk Assessment - Key risks and mitigation strategies
10. Team & Execution - Capabilities and next steps

Focus on creating investor-grade presentations that demonstrate deep market understanding
and clear paths to building successful businesses.
"""


def generate_startup_pitch_deck(
    market_analysis: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    brand_data: Dict[str, Any],
    competitive_data: Dict[str, Any],
    additional_context: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive startup pitch deck from all analysis data

    Args:
        market_analysis: Market research and analysis results
        opportunity_data: Liminal opportunities and signals
        brand_data: Brand identity and positioning
        competitive_data: Competitive landscape analysis
        additional_context: Any additional context or requirements

    Returns:
        Dictionary containing PDF data and presentation metadata
    """
    pitch_result = {
        "generation_timestamp": datetime.now().isoformat(),
        "pitch_deck_ready": False,
        "pdf_data": None,
        "presentation_metadata": {},
        "executive_summary": {},
        "investment_thesis": {},
        "next_steps": [],
        "file_info": {},
    }

    try:
        print("📊 Generating comprehensive startup pitch deck...")

        # Phase 1: Synthesize narrative with AI
        print("🧠 Creating investment narrative...")
        narrative_synthesis = create_investment_narrative_with_ai(
            market_analysis, opportunity_data, brand_data, competitive_data
        )

        # Phase 2: Extract key metrics and data points
        print("📈 Processing key metrics...")
        key_metrics = extract_key_metrics_for_presentation(
            market_analysis, opportunity_data, competitive_data
        )

        # Phase 3: Create executive summary
        print("💡 Crafting executive summary...")
        executive_summary = create_executive_summary(narrative_synthesis, key_metrics)

        # Phase 4: Generate PDF pitch deck
        print("📄 Generating PDF presentation...")
        pdf_data = generate_pitch_deck_pdf(
            narrative_synthesis, key_metrics, executive_summary, brand_data
        )

        # Phase 5: Create presentation metadata
        presentation_metadata = {
            "title": executive_summary.get("opportunity_name", "Market Opportunity"),
            "subtitle": executive_summary.get("tagline", "Investment Opportunity"),
            "pages": 12,  # Standard pitch deck length
            "format": "PDF",
            "target_audience": "investors_stakeholders",
            "presentation_style": "professional_startup_pitch",
            "generated_by": "COSM_AI_Analysis",
            "data_sources": list(
                set(
                    [
                        "market_analysis",
                        "competitive_intelligence",
                        "liminal_discovery",
                        "brand_strategy",
                    ]
                )
            ),
        }

        pitch_result.update(
            {
                "pitch_deck_ready": True,
                "pdf_data": pdf_data,
                "presentation_metadata": presentation_metadata,
                "executive_summary": executive_summary,
                "investment_thesis": narrative_synthesis.get("investment_thesis", {}),
                "next_steps": narrative_synthesis.get("recommended_actions", []),
                "file_info": {
                    "filename": f"{executive_summary.get('opportunity_name', 'opportunity').lower().replace(' ', '_')}_pitch_deck.pdf",
                    "size_bytes": len(pdf_data) if pdf_data else 0,
                    "mime_type": "application/pdf",
                    "download_ready": True,
                },
            }
        )

        print("✅ Startup pitch deck generated successfully!")
        return pitch_result

    except Exception as e:
        print(f"❌ Error generating pitch deck: {e}")
        pitch_result["error"] = str(e)
        return pitch_result


def create_investment_narrative_with_ai(
    market_analysis: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    brand_data: Dict[str, Any],
    competitive_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use AI to create compelling investment narrative from all analysis data
    """
    try:
        # Prepare comprehensive analysis for AI
        synthesis_prompt = f"""
        Create a compelling startup investment narrative from this comprehensive market analysis.
        Transform the data into a story that would convince investors to fund this opportunity.

        MARKET ANALYSIS:
        {json.dumps(market_analysis, indent=2)[:2000]}

        OPPORTUNITY DATA:
        {json.dumps(opportunity_data, indent=2)[:2000]}

        BRAND STRATEGY:
        {json.dumps(brand_data, indent=2)[:1500]}

        COMPETITIVE LANDSCAPE:
        {json.dumps(competitive_data, indent=2)[:1500]}

        Create an investment-grade narrative in JSON format:
        {{
            "opportunity_name": "Clear, compelling business name",
            "elevator_pitch": "30-second compelling pitch",
            "problem_statement": {{
                "primary_problem": "Main market problem being solved",
                "problem_scope": "Who is affected and how severely",
                "current_solutions_fail": "Why existing solutions don't work",
                "quantified_pain": "Cost/impact of the problem"
            }},
            "solution_overview": {{
                "core_solution": "What the business does",
                "unique_approach": "How it's different from competitors",
                "key_benefits": ["benefit1", "benefit2", "benefit3"],
                "proof_points": ["evidence1", "evidence2"]
            }},
            "market_opportunity": {{
                "market_size": "TAM/SAM/SOM breakdown",
                "growth_trajectory": "Market growth story",
                "timing_rationale": "Why now is the right time",
                "market_position": "Where this fits in the market"
            }},
            "competitive_advantage": {{
                "differentiation": "Key competitive advantages",
                "barriers_to_entry": "What makes this defensible",
                "network_effects": "How it gets stronger with scale",
                "moat_strategy": "Long-term competitive protection"
            }},
            "business_model": {{
                "revenue_streams": ["stream1", "stream2"],
                "unit_economics": "How money is made per customer",
                "scalability": "How this scales efficiently",
                "monetization_timeline": "When revenue starts flowing"
            }},
            "go_to_market": {{
                "target_customers": "Who to target first",
                "customer_acquisition": "How to acquire customers",
                "sales_strategy": "How to close deals",
                "marketing_approach": "How to build awareness"
            }},
            "financial_projections": {{
                "revenue_forecast": "3-year revenue projection",
                "key_metrics": "Important KPIs to track",
                "funding_needs": "Capital requirements",
                "use_of_funds": "How investment will be used"
            }},
            "risk_mitigation": {{
                "key_risks": ["risk1", "risk2", "risk3"],
                "mitigation_strategies": ["strategy1", "strategy2"],
                "fallback_scenarios": "What if primary plan doesn't work"
            }},
            "investment_thesis": {{
                "investment_highlights": "Top reasons to invest",
                "success_probability": "Why this will likely succeed",
                "exit_potential": "How investors make money",
                "valuation_rationale": "Why this is worth investing in"
            }},
            "recommended_actions": [
                {{
                    "action": "Immediate next step",
                    "timeline": "When to complete",
                    "resources_needed": "What's required",
                    "success_metric": "How to measure success"
                }}
            ]
        }}

        Focus on creating a narrative that:
        1. Clearly explains the opportunity in simple terms
        2. Demonstrates deep market understanding
        3. Shows realistic path to success
        4. Addresses investor concerns proactively
        5. Presents compelling risk/reward ratio

        RETURN ONLY JSON AND NOTHING ELSE!
        """

        response = completion(
            model=MODEL_CONFIG["builder_agents"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": synthesis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,  # Balanced creativity and accuracy
            max_tokens=4000,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error creating investment narrative: {e}")

    # Fallback narrative
    return {
        "opportunity_name": "Market Opportunity",
        "elevator_pitch": "Addressing market gaps through innovative solutions",
        "problem_statement": {
            "primary_problem": "Market analysis indicates significant opportunity",
            "problem_scope": "Multiple user segments affected",
            "current_solutions_fail": "Analysis shows gaps in current solutions",
            "quantified_pain": "Substantial market impact identified",
        },
        "investment_thesis": {
            "investment_highlights": [
                "Market opportunity identified",
                "Competitive analysis completed",
            ],
            "success_probability": "Analysis indicates potential for success",
            "exit_potential": "Multiple exit scenarios possible",
        },
    }


def extract_key_metrics_for_presentation(
    market_analysis: Dict[str, Any],
    opportunity_data: Dict[str, Any],
    competitive_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract and organize key metrics for presentation charts and graphs
    """
    metrics = {
        "market_metrics": {},
        "opportunity_metrics": {},
        "competitive_metrics": {},
        "financial_estimates": {},
        "risk_scores": {},
    }

    try:
        # Extract market metrics
        if market_analysis:
            market_validation = market_analysis.get("market_validation", {})
            market_size = market_validation.get("market_size_analysis", {})

            metrics["market_metrics"] = {
                "tam_estimate": market_size.get("tam_estimate", 0),
                "sam_estimate": market_size.get("sam_estimate", 0),
                "som_estimate": market_size.get("som_estimate", 0),
                "growth_rate": market_size.get("growth_rate", 5.0),
                "confidence_level": market_validation.get("confidence_level", "medium"),
            }

        # Extract opportunity metrics
        if opportunity_data:
            synthesis = opportunity_data.get("synthesis", {})
            opportunities = synthesis.get("breakthrough_opportunities", [])

            if opportunities:
                top_opportunity = opportunities[0]
                metrics["opportunity_metrics"] = {
                    "opportunity_score": top_opportunity.get("opportunity_score", 0.5),
                    "market_readiness": top_opportunity.get(
                        "market_readiness", "medium"
                    ),
                    "implementation_difficulty": top_opportunity.get(
                        "implementation_difficulty", "medium"
                    ),
                    "time_to_market": top_opportunity.get(
                        "time_to_market", "6-12 months"
                    ),
                }

        # Extract competitive metrics
        if competitive_data:
            competition = competitive_data.get("competition_analysis", {})
            metrics["competitive_metrics"] = {
                "competition_level": competition.get("competition_level", "medium"),
                "direct_competitors": len(competition.get("direct_competitors", [])),
                "market_gaps": len(competition.get("market_gaps", [])),
                "competitive_advantage_score": 0.7,  # Default score
            }

        # Generate financial estimates
        tam = metrics["market_metrics"].get("tam_estimate", 1000000)
        sam = metrics["market_metrics"].get("sam_estimate", tam * 0.1)
        som = metrics["market_metrics"].get("som_estimate", sam * 0.05)

        metrics["financial_estimates"] = {
            "year_1_revenue": int(som * 0.1),
            "year_2_revenue": int(som * 0.3),
            "year_3_revenue": int(som * 0.6),
            "funding_needed": int(som * 0.2),
            "customer_acquisition_cost": 100,  # Estimated
            "lifetime_value": 1000,  # Estimated
        }

        # Risk assessment scores
        competition_risk = (
            0.3 if metrics["competitive_metrics"]["competition_level"] == "low" else 0.7
        )
        market_risk = (
            0.2 if metrics["market_metrics"]["confidence_level"] == "high" else 0.5
        )
        execution_risk = 0.4  # Default

        metrics["risk_scores"] = {
            "competition_risk": competition_risk,
            "market_risk": market_risk,
            "execution_risk": execution_risk,
            "overall_risk": (competition_risk + market_risk + execution_risk) / 3,
        }

        return metrics

    except Exception as e:
        print(f"❌ Error extracting metrics: {e}")
        return metrics


def create_executive_summary(
    narrative: Dict[str, Any], metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create executive summary for the pitch deck
    """
    try:
        summary = {
            "opportunity_name": narrative.get("opportunity_name", "Market Opportunity"),
            "tagline": narrative.get(
                "elevator_pitch",
                "Transforming market opportunities into business success",
            ),
            "investment_ask": f"${metrics['financial_estimates']['funding_needed']:,}",
            "market_size": f"${metrics['market_metrics']['tam_estimate']:,}",
            "projected_revenue": {
                "year_1": f"${metrics['financial_estimates']['year_1_revenue']:,}",
                "year_2": f"${metrics['financial_estimates']['year_2_revenue']:,}",
                "year_3": f"${metrics['financial_estimates']['year_3_revenue']:,}",
            },
            "key_highlights": [
                f"${metrics['market_metrics']['tam_estimate']:,} total addressable market",
                f"{metrics['market_metrics']['growth_rate']:.1f}% market growth rate",
                f"{len(narrative.get('solution_overview', {}).get('key_benefits', []))} key competitive advantages",
                f"{metrics['competitive_metrics']['market_gaps']} identified market gaps",
            ],
            "problem_solved": narrative.get("problem_statement", {}).get(
                "primary_problem", "Market opportunity identified"
            ),
            "solution_summary": narrative.get("solution_overview", {}).get(
                "core_solution", "Innovative market solution"
            ),
            "competitive_advantage": narrative.get("competitive_advantage", {}).get(
                "differentiation", "Unique market positioning"
            ),
            "use_of_funds": narrative.get("financial_projections", {}).get(
                "use_of_funds", "Product development and market expansion"
            ),
        }

        return summary

    except Exception as e:
        print(f"❌ Error creating executive summary: {e}")
        return {
            "opportunity_name": "Market Opportunity",
            "tagline": "Business opportunity analysis complete",
        }


def generate_pitch_deck_pdf(
    narrative: Dict[str, Any],
    metrics: Dict[str, Any],
    executive_summary: Dict[str, Any],
    brand_data: Dict[str, Any],
) -> bytes:
    """
    Generate professional PDF pitch deck using ReportLab
    """
    try:
        # Create temporary file for PDF generation
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            # Create PDF document
            doc = SimpleDocTemplate(
                tmp_file.name,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Get styles
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=HexColor("#2563eb"),
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=18,
                spaceAfter=12,
                textColor=HexColor("#1e40af"),
            )

            body_style = ParagraphStyle(
                "CustomBody",
                parent=styles["Normal"],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_JUSTIFY,
            )

            # Build story (content)
            story = []

            # Page 1: Title Page
            story.append(Spacer(1, 2 * inch))
            story.append(
                Paragraph(
                    executive_summary.get("opportunity_name", "Market Opportunity"),
                    title_style,
                )
            )
            story.append(
                Paragraph(
                    executive_summary.get("tagline", "Investment Opportunity"),
                    heading_style,
                )
            )
            story.append(Spacer(1, 1 * inch))
            story.append(
                Paragraph(
                    f"Investment Opportunity: {executive_summary.get('investment_ask', 'TBD')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Market Size: {executive_summary.get('market_size', 'TBD')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style
                )
            )
            story.append(PageBreak())

            # Page 2: Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(
                Paragraph(executive_summary.get("problem_solved", ""), body_style)
            )
            story.append(
                Paragraph(
                    f"Solution: {executive_summary.get('solution_summary', '')}",
                    body_style,
                )
            )
            story.append(Spacer(1, 0.2 * inch))

            # Key highlights
            story.append(Paragraph("Key Highlights:", heading_style))
            for highlight in executive_summary.get("key_highlights", []):
                story.append(Paragraph(f"• {highlight}", body_style))
            story.append(PageBreak())

            # Page 3: Problem Statement
            problem = narrative.get("problem_statement", {})
            story.append(Paragraph("The Problem", heading_style))
            story.append(
                Paragraph(
                    problem.get("primary_problem", "Market opportunity identified"),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Scope: {problem.get('problem_scope', 'Multiple segments affected')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Current Solutions: {problem.get('current_solutions_fail', 'Gaps in existing solutions')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 4: Solution Overview
            solution = narrative.get("solution_overview", {})
            story.append(Paragraph("Our Solution", heading_style))
            story.append(
                Paragraph(
                    solution.get("core_solution", "Innovative solution approach"),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Unique Approach: {solution.get('unique_approach', 'Differentiated strategy')}",
                    body_style,
                )
            )

            story.append(Paragraph("Key Benefits:", body_style))
            for benefit in solution.get("key_benefits", ["Market-driven solution"]):
                story.append(Paragraph(f"• {benefit}", body_style))
            story.append(PageBreak())

            # Page 5: Market Analysis
            market_opp = narrative.get("market_opportunity", {})
            story.append(Paragraph("Market Analysis", heading_style))
            story.append(
                Paragraph(
                    f"Market Size: {market_opp.get('market_size', metrics['market_metrics']['tam_estimate'])}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Growth: {market_opp.get('growth_trajectory', 'Positive growth trajectory')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Timing: {market_opp.get('timing_rationale', 'Market timing favorable')}",
                    body_style,
                )
            )

            # Market size table
            market_data = [
                ["Market Segment", "Size"],
                [
                    "Total Addressable Market (TAM)",
                    f"${metrics['market_metrics']['tam_estimate']:,}",
                ],
                [
                    "Serviceable Addressable Market (SAM)",
                    f"${metrics['market_metrics']['sam_estimate']:,}",
                ],
                [
                    "Serviceable Obtainable Market (SOM)",
                    f"${metrics['market_metrics']['som_estimate']:,}",
                ],
            ]

            market_table = Table(market_data)
            market_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2563eb")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f8fafc")),
                        ("GRID", (0, 0), (-1, -1), 1, black),
                    ]
                )
            )

            story.append(market_table)
            story.append(PageBreak())

            # Page 6: Competitive Advantage
            competitive = narrative.get("competitive_advantage", {})
            story.append(Paragraph("Competitive Advantage", heading_style))
            story.append(
                Paragraph(
                    competitive.get(
                        "differentiation", "Strong competitive positioning"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Barriers to Entry: {competitive.get('barriers_to_entry', 'Defensible position')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Network Effects: {competitive.get('network_effects', 'Scalable advantages')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 7: Business Model
            business_model = narrative.get("business_model", {})
            story.append(Paragraph("Business Model", heading_style))
            story.append(
                Paragraph(
                    f"Revenue Streams: {', '.join(business_model.get('revenue_streams', ['Primary revenue stream']))}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Unit Economics: {business_model.get('unit_economics', 'Positive unit economics')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Scalability: {business_model.get('scalability', 'Highly scalable model')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 8: Financial Projections
            story.append(Paragraph("Financial Projections", heading_style))

            # Revenue projection table
            revenue_data = [
                ["Year", "Projected Revenue"],
                ["Year 1", executive_summary["projected_revenue"]["year_1"]],
                ["Year 2", executive_summary["projected_revenue"]["year_2"]],
                ["Year 3", executive_summary["projected_revenue"]["year_3"]],
            ]

            revenue_table = Table(revenue_data)
            revenue_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#10b981")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f0fdf4")),
                        ("GRID", (0, 0), (-1, -1), 1, black),
                    ]
                )
            )

            story.append(revenue_table)
            story.append(Spacer(1, 0.3 * inch))
            story.append(
                Paragraph(
                    f"Funding Needed: {executive_summary.get('investment_ask', 'TBD')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Use of Funds: {executive_summary.get('use_of_funds', 'Product and market development')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 9: Go-to-Market Strategy
            gtm = narrative.get("go_to_market", {})
            story.append(Paragraph("Go-to-Market Strategy", heading_style))
            story.append(
                Paragraph(
                    f"Target Customers: {gtm.get('target_customers', 'Identified customer segments')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Customer Acquisition: {gtm.get('customer_acquisition', 'Multi-channel approach')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Sales Strategy: {gtm.get('sales_strategy', 'Scalable sales process')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 10: Risk Assessment
            risks = narrative.get("risk_mitigation", {})
            story.append(Paragraph("Risk Assessment & Mitigation", heading_style))

            story.append(Paragraph("Key Risks:", body_style))
            for risk in risks.get(
                "key_risks", ["Market risk", "Execution risk", "Competitive risk"]
            ):
                story.append(Paragraph(f"• {risk}", body_style))

            story.append(Paragraph("Mitigation Strategies:", body_style))
            for strategy in risks.get(
                "mitigation_strategies", ["Risk monitoring", "Contingency planning"]
            ):
                story.append(Paragraph(f"• {strategy}", body_style))
            story.append(PageBreak())

            # Page 11: Investment Thesis
            investment = narrative.get("investment_thesis", {})
            story.append(Paragraph("Investment Thesis", heading_style))

            story.append(Paragraph("Investment Highlights:", body_style))
            for highlight in investment.get(
                "investment_highlights", ["Strong market opportunity"]
            ):
                story.append(Paragraph(f"• {highlight}", body_style))

            story.append(
                Paragraph(
                    f"Success Probability: {investment.get('success_probability', 'Positive outlook based on analysis')}",
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    f"Exit Potential: {investment.get('exit_potential', 'Multiple exit opportunities')}",
                    body_style,
                )
            )
            story.append(PageBreak())

            # Page 12: Next Steps
            story.append(Paragraph("Next Steps", heading_style))
            actions = narrative.get("recommended_actions", [])

            if actions:
                for i, action in enumerate(actions[:5], 1):
                    story.append(
                        Paragraph(
                            f"{i}. {action.get('action', 'Next action step')}",
                            body_style,
                        )
                    )
                    story.append(
                        Paragraph(
                            f"   Timeline: {action.get('timeline', 'TBD')}", body_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f"   Resources: {action.get('resources_needed', 'TBD')}",
                            body_style,
                        )
                    )
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph("1. Validate market assumptions", body_style))
                story.append(Paragraph("2. Develop MVP", body_style))
                story.append(Paragraph("3. Secure initial funding", body_style))
                story.append(Paragraph("4. Build core team", body_style))
                story.append(Paragraph("5. Launch pilot program", body_style))

            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph("Thank you for your consideration.", heading_style))

            # Build PDF
            doc.build(story)

            # Read the generated PDF
            with open(tmp_file.name, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            # Clean up temp file
            os.unlink(tmp_file.name)

            return pdf_data

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        # Return a simple fallback PDF
        return create_fallback_pdf(executive_summary)


def create_fallback_pdf(executive_summary: Dict[str, Any]) -> bytes:
    """
    Create a simple fallback PDF when main generation fails
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            # Create simple PDF
            c = canvas.Canvas(tmp_file.name, pagesize=A4)
            width, height = A4

            # Title
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredText(
                width / 2,
                height - 100,
                executive_summary.get("opportunity_name", "Market Opportunity"),
            )

            # Content
            c.setFont("Helvetica", 12)
            y_position = height - 150

            lines = [
                f"Investment Opportunity: {executive_summary.get('investment_ask', 'TBD')}",
                f"Market Size: {executive_summary.get('market_size', 'TBD')}",
                "",
                "Executive Summary:",
                executive_summary.get(
                    "problem_solved", "Market opportunity identified"
                ),
                "",
                f"Solution: {executive_summary.get('solution_summary', '')}",
                "",
                "Key Highlights:",
            ]

            for highlight in executive_summary.get("key_highlights", [])[:3]:
                lines.append(f"• {highlight}")

            lines.extend(
                [
                    "",
                    f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                    "",
                    "Comprehensive analysis available in full report.",
                ]
            )

            for line in lines:
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:
                    break

            c.save()

            # Read the PDF
            with open(tmp_file.name, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            os.unlink(tmp_file.name)
            return pdf_data

    except Exception as e:
        print(f"❌ Error creating fallback PDF: {e}")
        # Return minimal PDF data as bytes
        return b"PDF generation failed"


def create_presentation_slides_data(
    narrative: Dict[str, Any], metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Create structured slide data for alternative presentation formats
    """
    slides = []

    try:
        # Slide 1: Title
        slides.append(
            {
                "slide_number": 1,
                "title": narrative.get("opportunity_name", "Market Opportunity"),
                "subtitle": narrative.get("elevator_pitch", "Investment Opportunity"),
                "content_type": "title_slide",
                "layout": "centered",
            }
        )

        # Slide 2: Problem
        problem = narrative.get("problem_statement", {})
        slides.append(
            {
                "slide_number": 2,
                "title": "The Problem",
                "content": [
                    problem.get("primary_problem", "Market opportunity identified"),
                    f"Scope: {problem.get('problem_scope', '')}",
                    f"Current Solutions: {problem.get('current_solutions_fail', '')}",
                ],
                "content_type": "bullet_points",
            }
        )

        # Slide 3: Solution
        solution = narrative.get("solution_overview", {})
        slides.append(
            {
                "slide_number": 3,
                "title": "Our Solution",
                "content": [
                    solution.get("core_solution", ""),
                    f"Unique Approach: {solution.get('unique_approach', '')}",
                ]
                + solution.get("key_benefits", []),
                "content_type": "bullet_points",
            }
        )

        # Slide 4: Market Size
        slides.append(
            {
                "slide_number": 4,
                "title": "Market Opportunity",
                "content": {
                    "tam": metrics["market_metrics"]["tam_estimate"],
                    "sam": metrics["market_metrics"]["sam_estimate"],
                    "som": metrics["market_metrics"]["som_estimate"],
                    "growth_rate": metrics["market_metrics"]["growth_rate"],
                },
                "content_type": "market_data",
                "chart_type": "market_size_chart",
            }
        )

        # Slide 5: Competitive Advantage
        competitive = narrative.get("competitive_advantage", {})
        slides.append(
            {
                "slide_number": 5,
                "title": "Competitive Advantage",
                "content": [
                    competitive.get("differentiation", ""),
                    competitive.get("barriers_to_entry", ""),
                    competitive.get("network_effects", ""),
                ],
                "content_type": "bullet_points",
            }
        )

        # Slide 6: Business Model
        business_model = narrative.get("business_model", {})
        slides.append(
            {
                "slide_number": 6,
                "title": "Business Model",
                "content": {
                    "revenue_streams": business_model.get("revenue_streams", []),
                    "unit_economics": business_model.get("unit_economics", ""),
                    "scalability": business_model.get("scalability", ""),
                },
                "content_type": "business_model",
            }
        )

        # Slide 7: Financial Projections
        slides.append(
            {
                "slide_number": 7,
                "title": "Financial Projections",
                "content": {
                    "year_1": metrics["financial_estimates"]["year_1_revenue"],
                    "year_2": metrics["financial_estimates"]["year_2_revenue"],
                    "year_3": metrics["financial_estimates"]["year_3_revenue"],
                    "funding_needed": metrics["financial_estimates"]["funding_needed"],
                },
                "content_type": "financial_chart",
                "chart_type": "revenue_projection",
            }
        )

        # Slide 8: Go-to-Market
        gtm = narrative.get("go_to_market", {})
        slides.append(
            {
                "slide_number": 8,
                "title": "Go-to-Market Strategy",
                "content": [
                    f"Target: {gtm.get('target_customers', '')}",
                    f"Acquisition: {gtm.get('customer_acquisition', '')}",
                    f"Sales: {gtm.get('sales_strategy', '')}",
                ],
                "content_type": "bullet_points",
            }
        )

        # Slide 9: Investment Ask
        investment = narrative.get("investment_thesis", {})
        slides.append(
            {
                "slide_number": 9,
                "title": "Investment Opportunity",
                "content": {
                    "ask_amount": metrics["financial_estimates"]["funding_needed"],
                    "use_of_funds": narrative.get("financial_projections", {}).get(
                        "use_of_funds", ""
                    ),
                    "highlights": investment.get("investment_highlights", []),
                },
                "content_type": "investment_ask",
            }
        )

        # Slide 10: Next Steps
        slides.append(
            {
                "slide_number": 10,
                "title": "Next Steps",
                "content": [
                    action.get("action", "")
                    for action in narrative.get("recommended_actions", [])[:5]
                ],
                "content_type": "bullet_points",
            }
        )

        return slides

    except Exception as e:
        print(f"❌ Error creating slide data: {e}")
        return []


def export_pitch_data_formats(
    narrative: Dict[str, Any],
    metrics: Dict[str, Any],
    executive_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Export pitch data in multiple formats for different use cases
    """
    export_data = {
        "pdf_ready": True,
        "presentation_slides": [],
        "executive_summary_json": {},
        "financial_data_csv": "",
        "one_pager_html": "",
        "investor_email_template": "",
    }

    try:
        # Create presentation slides data
        export_data["presentation_slides"] = create_presentation_slides_data(
            narrative, metrics
        )

        # Executive summary JSON
        export_data["executive_summary_json"] = executive_summary

        # Financial data CSV format
        financial_csv = "Metric,Year 1,Year 2,Year 3\n"
        financial_csv += f"Revenue,{metrics['financial_estimates']['year_1_revenue']},{metrics['financial_estimates']['year_2_revenue']},{metrics['financial_estimates']['year_3_revenue']}\n"
        financial_csv += (
            f"Market Size (TAM),{metrics['market_metrics']['tam_estimate']},,\n"
        )
        financial_csv += (
            f"Funding Needed,{metrics['financial_estimates']['funding_needed']},,\n"
        )
        export_data["financial_data_csv"] = financial_csv

        # One-pager HTML
        one_pager_html = f"""
        <html>
        <head><title>{executive_summary.get('opportunity_name', 'Opportunity')}</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1>{executive_summary.get('opportunity_name', 'Market Opportunity')}</h1>
            <h2>{executive_summary.get('tagline', '')}</h2>

            <h3>The Opportunity</h3>
            <p>{executive_summary.get('problem_solved', '')}</p>

            <h3>Our Solution</h3>
            <p>{executive_summary.get('solution_summary', '')}</p>

            <h3>Market Size</h3>
            <p>Total Addressable Market: {executive_summary.get('market_size', '')}</p>

            <h3>Investment Ask</h3>
            <p>Seeking: {executive_summary.get('investment_ask', '')}</p>
            <p>Use of Funds: {executive_summary.get('use_of_funds', '')}</p>

            <h3>Key Highlights</h3>
            <ul>
        """

        for highlight in executive_summary.get("key_highlights", []):
            one_pager_html += f"<li>{highlight}</li>"

        one_pager_html += """
            </ul>
            <p><em>Generated by COSM AI Market Analysis</em></p>
        </body>
        </html>
        """
        export_data["one_pager_html"] = one_pager_html

        # Investor email template
        email_template = f"""
Subject: Investment Opportunity: {executive_summary.get('opportunity_name', 'Market Opportunity')}

Dear [Investor Name],

I hope this email finds you well. I'm reaching out to share an exciting investment opportunity that has emerged from comprehensive market analysis.

OPPORTUNITY OVERVIEW:
{executive_summary.get('tagline', '')}

THE PROBLEM:
{executive_summary.get('problem_solved', '')}

OUR SOLUTION:
{executive_summary.get('solution_summary', '')}

MARKET OPPORTUNITY:
• Market Size: {executive_summary.get('market_size', '')}
• Investment Ask: {executive_summary.get('investment_ask', '')}

KEY HIGHLIGHTS:
"""

        for highlight in executive_summary.get("key_highlights", []):
            email_template += f"• {highlight}\n"

        email_template += f"""

USE OF FUNDS:
{executive_summary.get('use_of_funds', '')}

I've attached a comprehensive pitch deck with detailed analysis, financial projections, and market validation. I would welcome the opportunity to discuss this further at your convenience.

Best regards,
[Your Name]

This opportunity analysis was generated using advanced AI market intelligence.
"""

        export_data["investor_email_template"] = email_template

        return export_data

    except Exception as e:
        print(f"❌ Error exporting pitch data: {e}")
        return export_data


# Create the startup pitch generator agent
startup_pitch_agent = LlmAgent(
    name="startup_pitch_agent",
    model=MODEL_CONFIG["primary_model"],
    instruction=STARTUP_PITCH_PROMPT,
    description=(
        "Creates comprehensive startup pitch decks and investment presentations from "
        "market analysis and opportunity discovery data. Generates professional PDF "
        "reports ready for download and investor presentations."
    ),
    tools=[
        FunctionTool(func=generate_startup_pitch_deck),
        FunctionTool(func=export_pitch_data_formats),
    ],
    output_key="startup_pitch_package",
)
