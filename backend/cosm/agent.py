from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent, BaseAgent
from google.adk.tools import FunctionTool
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import json
from typing_extensions import override

# ----- SELF-CRITICISM TOOLS -----

def generate_self_critique(response: str, criteria: List[str] = None) -> Dict:
    """
    Generates a self-critique of a given response based on specified criteria.
    
    Args:
        response: The response to critique
        criteria: List of criteria to evaluate against
        
    Returns:
        Dictionary with critique analysis
    """
    if criteria is None:
        criteria = ["accuracy", "completeness", "clarity", "relevance", "bias"]
    
    return {
        "status": "success",
        "original_response": response,
        "critique": {
            "overall_score": 7.5,
            "strengths": [
                "Clear structure and logical flow",
                "Addresses main points of the query",
                "Uses appropriate technical language"
            ],
            "weaknesses": [
                "Could provide more specific examples",
                "Some assertions lack supporting evidence",
                "May benefit from alternative perspectives"
            ],
            "suggestions": [
                "Add concrete examples to illustrate key points",
                "Include counterarguments or limitations",
                "Verify claims with additional sources"
            ],
            "criteria_scores": {criterion: 7.0 + (i * 0.2) for i, criterion in enumerate(criteria)}
        }
    }

def search_perspective(topic: str, perspective: str, search_depth: str = "standard") -> Dict:
    """
    Searches for information on a topic from a specific perspective.
    
    Args:
        topic: The topic to research
        perspective: The perspective or angle to take
        search_depth: Depth of search (basic, standard, comprehensive)
        
    Returns:
        Dictionary with perspective-specific research results
    """
    perspective_data = {
        "academic": {
            "sources": ["peer-reviewed journals", "research papers", "academic databases"],
            "findings": [
                "Recent studies show conflicting evidence",
                "Methodology limitations in current research",
                "Need for longitudinal studies"
            ],
            "key_points": [
                "Rigorous methodology is essential",
                "Sample size affects generalizability",
                "Peer review ensures quality"
            ]
        },
        "industry": {
            "sources": ["industry reports", "market analysis", "case studies"],
            "findings": [
                "Market adoption is accelerating",
                "Cost-benefit analysis shows positive ROI",
                "Implementation challenges remain"
            ],
            "key_points": [
                "Practical implementation matters",
                "Financial viability is crucial",
                "Market timing affects success"
            ]
        },
        "skeptical": {
            "sources": ["critical analyses", "failure cases", "limitation studies"],
            "findings": [
                "Previous implementations have failed",
                "Unintended consequences documented",
                "Overhype vs reality gap exists"
            ],
            "key_points": [
                "Consider potential downsides",
                "Historical failures provide lessons",
                "Realistic expectations needed"
            ]
        },
        "optimistic": {
            "sources": ["success stories", "innovation reports", "future projections"],
            "findings": [
                "Breakthrough innovations emerging",
                "Successful implementations growing",
                "Positive trend indicators strong"
            ],
            "key_points": [
                "Innovation drives progress",
                "Success stories demonstrate potential",
                "Future outlook is promising"
            ]
        }
    }
    
    return {
        "status": "success",
        "topic": topic,
        "perspective": perspective,
        "search_depth": search_depth,
        "data": perspective_data.get(perspective, perspective_data["academic"])
    }

def facilitate_debate(arguments: List[Dict], debate_rounds: int = 3) -> Dict:
    """
    Facilitates a structured debate between different perspectives.
    
    Args:
        arguments: List of arguments from different perspectives
        debate_rounds: Number of debate rounds to simulate
        
    Returns:
        Dictionary with debate facilitation results
    """
    return {
        "status": "success",
        "debate_structure": {
            "total_rounds": debate_rounds,
            "participants": len(arguments),
            "format": "structured_exchange"
        },
        "moderation_guidelines": [
            "Address specific points raised by other perspectives",
            "Provide evidence for claims",
            "Acknowledge valid opposing points",
            "Clarify misunderstandings",
            "Focus on substantive disagreements"
        ],
        "synthesis_framework": {
            "common_ground": "Areas of agreement between perspectives",
            "key_differences": "Fundamental disagreements to explore",
            "evidence_gaps": "Areas needing more research",
            "practical_implications": "Real-world consequences of different views"
        }
    }

# Create tool instances
self_critique_tool = FunctionTool(func=generate_self_critique)
perspective_search_tool = FunctionTool(func=search_perspective)
debate_facilitation_tool = FunctionTool(func=facilitate_debate)

# ----- MODEL CONFIGURATION -----
MODEL = "gemini-2.0-flash"

# ----- SELF-CRITIC SUB-AGENTS -----

# Primary responder for self-critic system
primary_responder = LlmAgent(
    name="primary_responder",
    model=MODEL,
    instruction=(
        "You provide initial responses to queries. Be comprehensive but acknowledge "
        "that your response may need refinement. Focus on addressing the main question "
        "with the information available to you."
    ),
    output_key="primary_response"
)

# Self-critic agent
self_critic = LlmAgent(
    name="self_critic",
    model=MODEL,
    instruction=(
        "You are a critic evaluating responses. Analyze the response in state key 'response_to_critique'. "
        "Use the generate_self_critique tool to provide structured feedback. "
        "Be constructive but honest about weaknesses. If the response is satisfactory, state so clearly."
    ),
    tools=[self_critique_tool],
    output_key="self_critique"
)

# Response improver
response_improver = LlmAgent(
    name="response_improver",
    model=MODEL,
    instruction=(
        "You improve responses based on critique. Take the 'improvement_target' from state "
        "and the 'critique_guidance' to create a better version. Address the specific "
        "weaknesses mentioned while preserving the strengths."
    ),
    output_key="improved_response"
)

# ----- DEBATE SUB-AGENTS -----

debate_academic = LlmAgent(
    name="debate_academic",
    model=MODEL,
    description="Argues from an academic research perspective with emphasis on rigorous methodology",
    instruction=(
        "You are an academic researcher participating in a debate. Your role is to:\n"
        "1. Use the search_perspective tool to research the topic from an academic angle\n"
        "2. Present arguments based on peer-reviewed research and scientific methodology\n"
        "3. Critique other perspectives for lack of rigor or evidence\n"
        "4. Acknowledge limitations in current research\n"
        "Store your arguments in state with key 'academic_argument'"
    ),
    tools=[perspective_search_tool],
    output_key="academic_argument"
)

debate_industry = LlmAgent(
    name="debate_industry",
    model=MODEL,
    description="Argues from a practical industry implementation perspective",
    instruction=(
        "You are an industry practitioner participating in a debate. Your role is to:\n"
        "1. Use the search_perspective tool to research the topic from an industry angle\n"
        "2. Present arguments based on practical implementation and business value\n"
        "3. Challenge academic perspectives for lack of real-world applicability\n"
        "4. Focus on cost-benefit analysis and market realities\n"
        "Store your arguments in state with key 'industry_argument'"
    ),
    tools=[perspective_search_tool],
    output_key="industry_argument"
)

debate_skeptic = LlmAgent(
    name="debate_skeptic",
    model=MODEL,
    description="Argues from a critical skeptical perspective highlighting risks and limitations",
    instruction=(
        "You are a critical skeptic participating in a debate. Your role is to:\n"
        "1. Use the search_perspective tool to research potential problems and limitations\n"
        "2. Present arguments highlighting risks, failures, and unintended consequences\n"
        "3. Challenge overly optimistic claims from other perspectives\n"
        "4. Advocate for caution and thorough risk assessment\n"
        "Store your arguments in state with key 'skeptical_argument'"
    ),
    tools=[perspective_search_tool],
    output_key="skeptical_argument"
)

debate_optimist = LlmAgent(
    name="debate_optimist",
    model=MODEL,
    description="Argues from an optimistic perspective focusing on potential and opportunities",
    instruction=(
        "You are an optimistic innovator participating in a debate. Your role is to:\n"
        "1. Use the search_perspective tool to research success stories and future potential\n"
        "2. Present arguments highlighting opportunities and positive outcomes\n"
        "3. Counter pessimistic views with evidence of progress and innovation\n"
        "4. Advocate for bold action and embracing new possibilities\n"
        "Store your arguments in state with key 'optimistic_argument'"
    ),
    tools=[perspective_search_tool],
    output_key="optimistic_argument"
)

# Debate moderator
debate_moderator = LlmAgent(
    name="debate_moderator",
    model=MODEL,
    instruction=(
        "You moderate debates between different perspectives. Use the facilitate_debate tool "
        "to structure the discussion. Encourage participants to address each other's points "
        "directly and provide evidence for their claims. Identify areas where more information is needed."
    ),
    tools=[debate_facilitation_tool],
    output_key="moderation_guidance"
)

# Synthesis agent
synthesis_agent = LlmAgent(
    name="synthesis_agent",
    model=MODEL,
    instruction=(
        "You synthesize the results of multi-perspective debates. Analyze all arguments "
        "in state and identify: 1) Areas of consensus, 2) Key disagreements, "
        "3) Evidence gaps, 4) Practical implications. Provide a balanced summary "
        "that acknowledges the complexity of the issue."
    ),
    output_key="debate_synthesis"
)

# ----- WORKFLOW SUB-AGENTS -----

# Self-critic workflow
self_critic_workflow = SequentialAgent(
    name="self_critic_workflow",
    sub_agents=[primary_responder, self_critic, response_improver]
)

# Parallel debate workflow
parallel_debaters = ParallelAgent(
    name="parallel_debaters",
    sub_agents=[debate_academic, debate_industry, debate_skeptic, debate_optimist]
)

# Complete debate workflow
debate_workflow = SequentialAgent(
    name="debate_workflow",
    sub_agents=[parallel_debaters, debate_moderator, synthesis_agent]
)

# Final integrator
final_integrator = LlmAgent(
    name="final_integrator",
    model=MODEL,
    instruction=(
        "You integrate insights from both self-criticism and multi-perspective debate. "
        "Use the 'improved_response' and 'debate_synthesis' from state to "
        "create a comprehensive final response that incorporates multiple viewpoints "
        "and addresses potential weaknesses identified through self-criticism."
    ),
    output_key="integrated_final_response"
)

# ----- MAIN COORDINATOR AGENT -----

root_agent = LlmAgent(
    name="self_critic_debate_coordinator",
    model=MODEL,
    description=(
        "AI-powered agent that combines self-criticism and multi-perspective debate "
        "to provide comprehensive analysis of complex topics from multiple angles."
    ),
    instruction=(
        "You are a coordinator for a sophisticated analysis system that combines "
        "self-criticism and multi-perspective debate. Your process works in phases:\n\n"
        
        "1. SELF-CRITICISM PHASE: First, run the self_critic_workflow to generate, "
        "critique, and improve an initial response to the user's query.\n\n"
        
        "2. DEBATE PHASE: Next, run the debate_workflow to explore the topic from "
        "multiple perspectives (academic, industry, skeptical, optimistic) and "
        "synthesize different viewpoints.\n\n"
        
        "3. INTEGRATION PHASE: Finally, run the final_integrator to combine insights "
        "from both phases into a comprehensive response.\n\n"
        
        "For each phase, clearly announce what you're doing and summarize the results "
        "before moving to the next phase. Always use the sub-agents to perform the actual work."
    ),
    sub_agents=[self_critic_workflow, debate_workflow, final_integrator]
)