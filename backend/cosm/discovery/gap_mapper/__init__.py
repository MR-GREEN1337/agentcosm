"""
Enhanced Gap Mapper Agent with Gemini-powered extraction
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.load_web_page import load_web_page
from google.genai import Client, types
from typing import Dict, List, Any
import json
from datetime import datetime

# Initialize Gemini client
client = Client()


def extract_signal_themes_with_gemini(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract themes and patterns using Gemini analysis"""
    try:
        # Prepare signal content for analysis
        signal_content = []
        for signal in signals[:20]:  # Limit to prevent token overflow
            signal_content.append(
                {
                    "content": signal.get("content", "")[:500],  # Limit content length
                    "source": signal.get("source", "unknown"),
                    "type": signal.get("type", "unknown"),
                }
            )

        prompt = f"""
        Analyze these market signals and extract key themes, patterns, and opportunities.

        Signals: {json.dumps(signal_content, indent=2)}

        Extract and return a JSON object with:
        - workflow_gaps: Array of specific workflow problems mentioned
        - technology_needs: Array of missing technologies or capabilities
        - integration_points: Array of systems/tools that need to connect
        - pain_point_clusters: Array of related pain points grouped by theme
        - opportunity_areas: Array of potential business opportunities
        - market_segments: Array of specific user groups affected
        - urgency_indicators: Array of signals showing urgent need

        Focus on finding patterns that indicate liminal market opportunities.
        Only return the JSON object, no other text.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini theme extraction: {e}")

    return {
        "workflow_gaps": [],
        "technology_needs": [],
        "integration_points": [],
        "pain_point_clusters": [],
        "opportunity_areas": [],
        "market_segments": [],
        "urgency_indicators": [],
    }


def identify_workflow_intersections_with_gemini(
    signals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Identify workflow intersection points using Gemini"""
    try:
        # Prepare content focusing on workflow mentions
        workflow_signals = []
        for signal in signals[:15]:
            content = signal.get("content", "").lower()
            if any(
                keyword in content
                for keyword in [
                    "workflow",
                    "process",
                    "integration",
                    "switch",
                    "between",
                ]
            ):
                workflow_signals.append(
                    {
                        "content": signal.get("content", "")[:300],
                        "source": signal.get("source", "unknown"),
                    }
                )

        if not workflow_signals:
            return []

        prompt = f"""
        Analyze these workflow-related signals to identify intersection points where multiple tools, systems, or processes need to work together.

        Workflow Signals: {json.dumps(workflow_signals, indent=2)}

        Extract and return a JSON array of workflow intersections, each with:
        - intersection_type: Type of intersection (tool_integration, process_handoff, data_transfer, etc.)
        - tools_involved: Array of tools/systems mentioned
        - friction_points: Specific problems at the intersection
        - frequency_indicator: How often this intersection problem appears (high/medium/low)
        - automation_potential: Potential for automation (high/medium/low)
        - business_impact: Potential business impact of solving this intersection

        Only return the JSON array, no other text.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini workflow intersection analysis: {e}")

    return []


def find_technology_gaps_with_gemini(
    signals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Find technology gaps using Gemini analysis"""
    try:
        # Filter for signals mentioning missing technology or capabilities
        tech_signals = []
        for signal in signals[:15]:
            content = signal.get("content", "").lower()
            if any(
                keyword in content
                for keyword in [
                    "missing",
                    "doesn't exist",
                    "no solution",
                    "need",
                    "lacking",
                    "wish there was",
                ]
            ):
                tech_signals.append(
                    {
                        "content": signal.get("content", "")[:300],
                        "source": signal.get("source", "unknown"),
                    }
                )

        if not tech_signals:
            return []

        prompt = f"""
        Analyze these signals to identify technology gaps - missing capabilities, tools, or solutions that users need.

        Signals: {json.dumps(tech_signals, indent=2)}

        Extract and return a JSON array of technology gaps, each with:
        - gap_category: Category of the gap (integration, automation, analytics, UI/UX, etc.)
        - missing_capability: Specific capability that's missing
        - affected_users: Type of users affected by this gap
        - current_workarounds: How users currently work around this gap
        - market_size_indicator: Estimated market size (large/medium/small)
        - technical_complexity: Complexity to build solution (high/medium/low)
        - competitive_landscape: Existing solutions (none/few/many)

        Only return the JSON array, no other text.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini technology gap analysis: {e}")

    return []


def identify_liminal_spaces_with_gemini(
    connection_map: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Identify liminal market spaces using Gemini analysis"""
    try:
        prompt = f"""
        Analyze this market connection data to identify liminal spaces - opportunities that exist between established market categories.

        Connection Data: {json.dumps(connection_map, indent=2)}

        A liminal space is characterized by:
        - Existing between two or more established categories
        - Having unmet needs that don't fit traditional solutions
        - Representing transformation opportunities
        - Having users who are underserved by current options

        Extract and return a JSON array of liminal spaces, each with:
        - space_description: Clear description of the liminal space
        - adjacent_categories: Established categories this space sits between
        - unmet_needs: Specific needs not addressed by current solutions
        - target_users: Who would benefit from solutions in this space
        - opportunity_size: Estimated opportunity size (large/medium/small)
        - market_readiness: How ready the market is (high/medium/low)
        - solution_complexity: Complexity of building solutions (high/medium/low)
        - differentiation_potential: Potential for differentiation (high/medium/low)

        Only return the JSON array, no other text.
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
        print(f"Error in Gemini liminal space identification: {e}")

    return []


def analyze_convergence_opportunities_with_gemini(
    signals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Analyze industry/domain convergence using Gemini"""
    try:
        # Extract signals that mention multiple domains or industries
        convergence_signals = []
        for signal in signals[:20]:
            convergence_signals.append(
                {
                    "content": signal.get("content", "")[:400],
                    "source": signal.get("source", "unknown"),
                }
            )

        prompt = f"""
        Analyze these signals to identify convergence opportunities where different industries, technologies, or domains are coming together.

        Signals: {json.dumps(convergence_signals, indent=2)}

        Look for patterns indicating:
        - Cross-industry technology adoption
        - Hybrid solutions combining multiple domains
        - New use cases at industry intersections
        - Technology transfer opportunities

        Extract and return a JSON object with:
        - convergence_trends: Array of convergence trends identified
        - cross_pollination_opportunities: Array of technology transfer opportunities
        - hybrid_solutions: Array of potential hybrid solution opportunities
        - timing_indicators: Array of signals showing timing for convergence
        - barrier_analysis: Common barriers to convergence mentioned
        - success_factors: Factors that enable successful convergence

        Only return the JSON object, no other text.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.3
            ),
        )

        if response and response.text:
            return json.loads(response.text)

    except Exception as e:
        print(f"Error in Gemini convergence analysis: {e}")

    return {
        "convergence_trends": [],
        "cross_pollination_opportunities": [],
        "hybrid_solutions": [],
        "timing_indicators": [],
        "barrier_analysis": [],
        "success_factors": [],
    }


def map_signal_connections_enhanced(
    signals_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Enhanced signal mapping using Gemini for sophisticated analysis
    """
    connection_map = {
        "timestamp": datetime.now().isoformat(),
        "signal_count": len(signals_data),
        "gemini_analysis": {},
        "workflow_intersections": [],
        "technology_gaps": [],
        "convergence_analysis": {},
        "liminal_spaces": [],
        "opportunity_score": 0.0,
    }

    try:
        if not signals_data:
            return connection_map

        print("🧠 Running Gemini-powered signal analysis...")

        # Extract themes using Gemini
        connection_map["gemini_analysis"] = extract_signal_themes_with_gemini(
            signals_data
        )

        # Identify workflow intersections
        connection_map["workflow_intersections"] = (
            identify_workflow_intersections_with_gemini(signals_data)
        )

        # Find technology gaps
        connection_map["technology_gaps"] = find_technology_gaps_with_gemini(
            signals_data
        )

        # Analyze convergence opportunities
        connection_map["convergence_analysis"] = (
            analyze_convergence_opportunities_with_gemini(signals_data)
        )

        # Identify liminal spaces
        connection_map["liminal_spaces"] = identify_liminal_spaces_with_gemini(
            connection_map
        )

        # Calculate enhanced opportunity score
        connection_map["opportunity_score"] = calculate_enhanced_opportunity_score(
            connection_map
        )

        print(f"✅ Identified {len(connection_map['liminal_spaces'])} liminal spaces")
        print(f"🎯 Opportunity score: {connection_map['opportunity_score']:.2f}")

        return connection_map

    except Exception as e:
        print(f"Error in enhanced signal mapping: {e}")
        connection_map["error"] = str(e)
        return connection_map


def calculate_enhanced_opportunity_score(connection_map: Dict[str, Any]) -> float:
    """Calculate enhanced opportunity score using Gemini analysis results"""
    score = 0.0

    try:
        # Gemini analysis contribution (0-0.4)
        gemini_analysis = connection_map.get("gemini_analysis", {})
        opportunity_areas = len(gemini_analysis.get("opportunity_areas", []))
        urgency_indicators = len(gemini_analysis.get("urgency_indicators", []))

        score += min(opportunity_areas * 0.05, 0.2)
        score += min(urgency_indicators * 0.04, 0.2)

        # Workflow intersections (0-0.2)
        intersections = connection_map.get("workflow_intersections", [])
        high_impact_intersections = len(
            [i for i in intersections if i.get("business_impact") == "high"]
        )
        score += min(high_impact_intersections * 0.1, 0.2)

        # Technology gaps (0-0.2)
        tech_gaps = connection_map.get("technology_gaps", [])
        large_market_gaps = len(
            [g for g in tech_gaps if g.get("market_size_indicator") == "large"]
        )
        score += min(large_market_gaps * 0.1, 0.2)

        # Liminal spaces (0-0.2)
        liminal_spaces: List[Dict[str, Any]] = connection_map.get("liminal_spaces", [])
        high_readiness_spaces = len(
            [
                space
                for space in liminal_spaces
                if space.get("market_readiness") == "high"
            ]
        )
        score += min(high_readiness_spaces * 0.1, 0.2)

        return min(score, 1.0)

    except Exception as e:
        print(f"Error calculating enhanced opportunity score: {e}")
        return 0.0


# Enhanced Gap Mapper Agent with Gemini
gap_mapper_agent = LlmAgent(
    name="gap_mapper_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are an advanced Gap Mapper Agent specializing in identifying liminal market opportunities using AI-powered analysis.

    Your enhanced capabilities include:
    - Sophisticated pattern recognition using Gemini analysis
    - Deep workflow intersection identification
    - Technology gap analysis with market sizing
    - Liminal space identification between market categories
    - Cross-industry convergence opportunity detection

    Use your tools to map connections between market signals and identify hidden opportunities in the spaces between established categories.

    Focus on finding genuine liminal opportunities that represent:
    - Gaps between existing tool categories
    - Workflow intersection points that create friction
    - Technology needs not met by current solutions
    - Convergence opportunities across industries
    - Underserved market segments between established categories
    """,
    description=(
        "Advanced gap mapper that uses Gemini-powered analysis to identify "
        "sophisticated patterns and liminal opportunities in market signals."
    ),
    tools=[
        FunctionTool(func=map_signal_connections_enhanced),
        FunctionTool(func=extract_signal_themes_with_gemini),
        FunctionTool(func=identify_workflow_intersections_with_gemini),
        FunctionTool(func=find_technology_gaps_with_gemini),
        FunctionTool(func=identify_liminal_spaces_with_gemini),
        FunctionTool(func=analyze_convergence_opportunities_with_gemini),
        google_search,
        load_web_page,
    ],
    output_key="enhanced_gap_mapping",
)
