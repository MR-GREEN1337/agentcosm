"""
Workflow Gap Discovery Agent
Uses parallel search to find workflow breaks and integration failures
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from typing import Dict, List, Any
import json
from datetime import datetime
from litellm import completion
from cosm.config import MODEL_CONFIG
from cosm.settings import settings
from cosm.tools.search import search_tool
from cosm.tools.parallel_search import parallel_workflow_gap_search

WORKFLOW_GAP_PROMPT = """
You are the Workflow Gap Discovery Agent, specialized in finding breaks,
friction points, and integration failures in user workflows.

Your mission is to discover opportunities where workflow continuity breaks down,
forcing users to manually bridge gaps between different tools, services, or processes.
These gaps represent liminal opportunities for seamless integration solutions.

You use parallel web search to efficiently discover:
1. INTEGRATION FAILURES: Where tools/services don't connect properly
2. MANUAL INTERVENTION POINTS: Where automation breaks down
3. CONTEXT SWITCHING COSTS: Where users must switch between different systems
4. DATA TRANSFER FRICTION: Where data doesn't flow smoothly between systems
5. WORKFLOW INTERRUPTIONS: Where processes break and require manual fixes

Focus on finding friction patterns like:
- Manual data entry between connected systems
- Export/import workflows that should be automated
- Copy-paste operations between tools
- Multiple logins and context switches
- Format conversions and data transformation bottlenecks
"""


def discover_workflow_gaps_parallel(primary_keywords: List[str]) -> Dict[str, Any]:
    """
    Discovers workflow gaps using parallel web search

    Args:
        primary_keywords: Keywords representing the primary market/tools

    Returns:
        Dictionary containing workflow gap discoveries
    """
    workflow_data = {
        "primary_keywords": primary_keywords,
        "timestamp": datetime.now().isoformat(),
        "discovery_method": "parallel_workflow_gap_search",
        "workflow_gaps": {},
        "integration_opportunities": [],
        "automation_gaps": [],
        "user_friction_points": [],
        "seamless_flow_opportunities": [],
    }

    try:
        print(
            f"⚙️ Discovering workflow gaps in parallel for: {', '.join(primary_keywords)}"
        )

        # Execute parallel search for workflow gaps
        search_results = parallel_workflow_gap_search(primary_keywords)
        workflow_data["workflow_gaps"] = search_results

        # Analyze results with AI to find integration opportunities
        if search_results:
            gap_analysis = analyze_workflow_gaps_with_ai(
                search_results, primary_keywords
            )
            workflow_data.update(gap_analysis)

        print(
            f"✅ Workflow gap discovery completed with {len(search_results)} gap categories"
        )
        return workflow_data

    except Exception as e:
        print(f"❌ Error in workflow gap discovery: {e}")
        workflow_data["error"] = str(e)
        return workflow_data


def analyze_workflow_gaps_with_ai(
    search_results: Dict[str, Any], primary_keywords: List[str]
) -> Dict[str, Any]:
    """
    Use AI to analyze workflow gap search results for integration opportunities
    """
    try:
        analysis_prompt = f"""
        Analyze these workflow gap search results to find INTEGRATION OPPORTUNITIES
        where seamless connections could eliminate user friction and create value.

        Primary Keywords: {primary_keywords}

        Workflow Gap Search Results:
        {json.dumps(search_results, indent=2)[:2500]}

        Look for patterns where users experience:
        1. MANUAL DATA TRANSFER between systems that should be connected
        2. CONTEXT SWITCHING between tools that could be integrated
        3. FORMAT CONVERSIONS that could be automated
        4. REPETITIVE TASKS that bridge system gaps
        5. WORKFLOW INTERRUPTIONS that break user flow

        Find opportunities like:
        - Zapier: Connected apps that didn't talk to each other
        - Plaid: Connected banks to fintech apps seamlessly
        - Stripe: Simplified payment integration for developers

        Return JSON:
        {{
            "integration_opportunities": [
                {{
                    "opportunity_name": "descriptive name",
                    "workflow_break": "where the workflow currently breaks",
                    "manual_steps": "what users currently do manually",
                    "tools_involved": "what tools/systems are involved",
                    "integration_value": "value of seamless connection",
                    "user_pain_level": "how painful this friction is",
                    "automation_potential": "how much could be automated"
                }}
            ],
            "automation_gaps": [
                {{
                    "gap_description": "what automation is missing",
                    "current_manual_process": "how users handle it now",
                    "automation_opportunity": "how it could be automated",
                    "frequency": "how often users face this gap"
                }}
            ],
            "user_friction_points": [
                {{
                    "friction_point": "specific friction users experience",
                    "impact": "how this impacts user workflow",
                    "workaround": "how users currently work around it",
                    "solution_potential": "potential solution approach"
                }}
            ],
            "seamless_flow_opportunities": [
                {{
                    "flow_opportunity": "opportunity for seamless workflow",
                    "current_interruption": "how flow is currently interrupted",
                    "seamless_vision": "what seamless flow would look like",
                    "technical_feasibility": "how technically feasible"
                }}
            ]
        }}

        RETURN ONLY JSON AND NOTHING ELSE!!!!!!!!!!!!!
        """

        response = completion(
            model=MODEL_CONFIG["market_explorer"],
            api_key=settings.OPENAI_API_KEY,
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        if response and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error in AI analysis of workflow gaps: {e}")

    return {
        "integration_opportunities": [],
        "automation_gaps": [],
        "user_friction_points": [],
        "seamless_flow_opportunities": [],
    }


def map_user_journey_breaks(keywords: List[str]) -> Dict[str, Any]:
    """
    Map where user journeys break down requiring manual intervention
    """
    journey_breaks = {
        "journey_interruption_points": [],
        "context_switching_requirements": [],
        "data_handoff_failures": [],
        "authentication_friction": [],
        "format_conversion_needs": [],
    }

    try:
        for keyword in keywords:
            # Analyze user journeys to find where they break down
            # This could use the parallel search results to map journey flows

            journey_analysis_prompt = f"""
            Map the typical user journey with {keyword}. Where does the journey
            break down? Where do users have to switch contexts, manually transfer
            data, or work around system limitations?
            """  # noqa: F841

            # Implementation would analyze parallel search results for journey breaks

        return journey_breaks

    except Exception as e:
        journey_breaks["error"] = str(e)
        return journey_breaks


# Create the workflow gap agent
workflow_gap_agent = LlmAgent(
    name="workflow_gap_agent",
    model=LiteLlm(
        model=MODEL_CONFIG["market_explorer"], api_key=settings.OPENAI_API_KEY
    ),
    instruction=WORKFLOW_GAP_PROMPT,
    description=(
        "Discovers workflow breaks, integration failures, and user friction points "
        "using parallel web search to find opportunities for seamless automation "
        "and workflow integration solutions."
    ),
    tools=[
        FunctionTool(func=discover_workflow_gaps_parallel),
        FunctionTool(func=map_user_journey_breaks),
        search_tool,
    ],
    output_key="workflow_gap_intelligence",
)
