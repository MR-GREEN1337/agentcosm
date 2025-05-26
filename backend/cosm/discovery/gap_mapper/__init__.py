"""
Gap Mapper Agent - Maps connections between signals to identify market opportunities
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search, load_web_page
from typing import Dict, List, Any
import re
from datetime import datetime
from collections import defaultdict
from cosm.prompts import GAP_MAPPER_PROMPT

def map_signal_connections(signals_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Maps connections between different market signals to identify opportunities
    
    Args:
        signals_data: List of market signals from various sources
        
    Returns:
        Dictionary containing mapped connections and identified opportunities
    """
    connection_map = {
        "timestamp": datetime.now().isoformat(),
        "signal_count": len(signals_data),
        "connection_clusters": [],
        "workflow_intersections": [],
        "technology_gaps": [],
        "integration_opportunities": [],
        "convergence_points": [],
        "liminal_spaces": [],
        "opportunity_score": 0.0
    }
    
    try:
        if not signals_data:
            return connection_map
        
        # Extract keywords and themes from all signals
        signal_themes = extract_signal_themes(signals_data)
        
        # Find clusters of related signals
        connection_map["connection_clusters"] = find_signal_clusters(signals_data, signal_themes)
        
        # Identify workflow intersections
        connection_map["workflow_intersections"] = identify_workflow_intersections(signals_data)
        
        # Find technology gaps
        connection_map["technology_gaps"] = find_technology_gaps(signals_data)
        
        # Identify integration opportunities
        connection_map["integration_opportunities"] = find_integration_opportunities(signals_data)
        
        # Find convergence points
        connection_map["convergence_points"] = find_convergence_points(signals_data)
        
        # Identify liminal spaces
        connection_map["liminal_spaces"] = identify_liminal_spaces(connection_map)
        
        # Calculate opportunity score
        connection_map["opportunity_score"] = calculate_connection_opportunity_score(connection_map)
        
        return connection_map
        
    except Exception as e:
        print(f"Error in map_signal_connections: {e}")
        connection_map["error"] = str(e)
        return connection_map

def analyze_workflow_gaps(user_journeys: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes user workflows to identify gaps and friction points
    """
    workflow_analysis = {
        "journey_count": len(user_journeys),
        "common_friction_points": [],
        "tool_switching_patterns": [],
        "manual_processes": [],
        "integration_failures": [],
        "opportunity_areas": [],
        "workflow_efficiency_score": 0.0
    }
    
    try:
        # Analyze each user journey for common patterns
        all_friction_points = []
        tool_switches = []
        manual_tasks = []
        
        for journey in user_journeys:
            journey_content = str(journey).lower()
            
            # Find friction indicators
            friction_keywords = [
                "switch between", "copy paste", "manual", "export import",
                "download upload", "no integration", "doesn't connect",
                "separate tool", "different platform"
            ]
            
            for keyword in friction_keywords:
                if keyword in journey_content:
                    all_friction_points.append({
                        "friction_type": keyword,
                        "context": journey.get("content", "")[:200],
                        "source": journey.get("source", "unknown")
                    })
            
            # Find tool switching patterns
            tool_indicators = ["use", "switch to", "open", "login to", "go to"]
            for indicator in tool_indicators:
                if indicator in journey_content:
                    tool_switches.append({
                        "switch_pattern": indicator,
                        "context": journey.get("content", "")[:150]
                    })
            
            # Find manual processes
            manual_indicators = ["manually", "by hand", "copy", "type", "enter"]
            for indicator in manual_indicators:
                if indicator in journey_content:
                    manual_tasks.append({
                        "manual_task": indicator,
                        "context": journey.get("content", "")[:150]
                    })
        
        # Group and analyze patterns
        workflow_analysis["common_friction_points"] = group_friction_points(all_friction_points)
        workflow_analysis["tool_switching_patterns"] = analyze_tool_patterns(tool_switches)
        workflow_analysis["manual_processes"] = group_manual_processes(manual_tasks)
        workflow_analysis["opportunity_areas"] = identify_automation_opportunities(workflow_analysis)
        workflow_analysis["workflow_efficiency_score"] = calculate_workflow_efficiency(workflow_analysis)
        
        return workflow_analysis
        
    except Exception as e:
        print(f"Error in analyze_workflow_gaps: {e}")
        workflow_analysis["error"] = str(e)
        return workflow_analysis

def find_convergence_opportunities(industry_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Finds opportunities at the convergence of different industries or technologies
    """
    convergence_analysis = {
        "industry_count": len(industry_data),
        "convergence_points": [],
        "cross_pollination_opportunities": [],
        "technology_transfers": [],
        "regulatory_arbitrage": [],
        "market_timing_windows": [],
        "convergence_score": 0.0
    }
    
    try:
        # Extract industry themes and technologies
        industry_themes = {}
        for data in industry_data:
            industry = data.get("industry", "unknown")
            content = str(data).lower()
            
            # Extract key technologies mentioned
            tech_keywords = [
                "ai", "machine learning", "blockchain", "iot", "automation",
                "cloud", "mobile", "api", "integration", "analytics"
            ]
            
            industry_tech = []
            for tech in tech_keywords:
                if tech in content:
                    industry_tech.append(tech)
            
            industry_themes[industry] = {
                "technologies": industry_tech,
                "content": content,
                "data": data
            }
        
        # Find convergence points between industries
        convergence_analysis["convergence_points"] = find_industry_convergence(industry_themes)
        
        # Identify cross-pollination opportunities
        convergence_analysis["cross_pollination_opportunities"] = find_cross_pollination(industry_themes)
        
        # Find technology transfer opportunities
        convergence_analysis["technology_transfers"] = find_tech_transfers(industry_themes)
        
        # Calculate convergence score
        convergence_analysis["convergence_score"] = calculate_convergence_score(convergence_analysis)
        
        return convergence_analysis
        
    except Exception as e:
        print(f"Error in find_convergence_opportunities: {e}")
        convergence_analysis["error"] = str(e)
        return convergence_analysis

def extract_signal_themes(signals: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Extract themes and keywords from signals"""
    themes = defaultdict(list)
    
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        signal_type = signal.get("type", "unknown")
        
        # Extract key phrases (2-3 words)
        words = re.findall(r'\b\w+\b', content)
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:  # Skip very short phrases
                themes[signal_type].append(phrase)
    
    return dict(themes)

def find_signal_clusters(signals: List[Dict[str, Any]], themes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Find clusters of related signals"""
    clusters = []
    
    # Group signals by common keywords
    keyword_groups = defaultdict(list)
    
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        
        # Common clustering keywords
        cluster_keywords = [
            "integration", "workflow", "automation", "api", "data",
            "user experience", "platform", "tool", "process", "efficiency"
        ]
        
        for keyword in cluster_keywords:
            if keyword in content:
                keyword_groups[keyword].append(signal)
    
    # Create clusters from groups with multiple signals
    for keyword, signal_group in keyword_groups.items():
        if len(signal_group) >= 2:
            clusters.append({
                "cluster_theme": keyword,
                "signal_count": len(signal_group),
                "signals": signal_group[:5],  # Limit for readability
                "opportunity_strength": min(len(signal_group) / 3.0, 1.0)
            })
    
    return clusters

def identify_workflow_intersections(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify points where multiple workflows intersect"""
    intersections = []
    
    # Look for signals mentioning multiple tools or processes
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        
        # Common workflow intersection indicators
        intersection_patterns = [
            r'between\s+(\w+)\s+and\s+(\w+)',
            r'from\s+(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+and\s+(\w+)\s+integration',
            r'switch\s+from\s+(\w+)\s+to\s+(\w+)'
        ]
        
        for pattern in intersection_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    intersections.append({
                        "intersection_type": "tool_workflow",
                        "tools": list(match),
                        "evidence": signal.get("content", "")[:200],
                        "source": signal.get("source", "unknown")
                    })
    
    return intersections[:10]  # Limit results

def find_technology_gaps(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find technology gaps mentioned in signals"""
    tech_gaps = []
    
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        
        # Technology gap indicators
        gap_patterns = [
            r'no\s+(\w+)\s+for\s+(\w+)',
            r'missing\s+(\w+)\s+functionality',
            r'need\s+better\s+(\w+)',
            r'lack\s+of\s+(\w+)',
            r'doesn\'t\s+support\s+(\w+)'
        ]
        
        for pattern in gap_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                tech_gaps.append({
                    "gap_type": "technology",
                    "missing_capability": match if isinstance(match, str) else match[0],
                    "context": signal.get("content", "")[:200],
                    "severity": assess_gap_severity(signal)
                })
    
    return tech_gaps[:8]

def find_integration_opportunities(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find integration opportunities from signals"""
    integration_ops = []
    
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        
        integration_indicators = [
            "integration", "connect", "sync", "api", "webhook",
            "export", "import", "bridge", "link", "interface"
        ]
        
        for indicator in integration_indicators:
            if indicator in content:
                integration_ops.append({
                    "opportunity_type": "integration",
                    "integration_need": indicator,
                    "evidence": signal.get("content", "")[:200],
                    "market_size_indicator": estimate_market_size(signal),
                    "implementation_complexity": assess_complexity(signal)
                })
    
    return integration_ops[:6]

def find_convergence_points(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find points where different domains converge"""
    convergence_points = []
    
    # Domain keywords to track
    domains = {
        "productivity": ["task", "project", "workflow", "productivity"],
        "communication": ["chat", "email", "message", "communication"],
        "data": ["data", "analytics", "report", "dashboard"],
        "sales": ["sales", "crm", "lead", "customer"],
        "marketing": ["marketing", "campaign", "social", "content"],
        "finance": ["finance", "accounting", "invoice", "payment"]
    }
    
    # Find signals that mention multiple domains
    for signal in signals:
        content = str(signal.get("content", "")).lower()
        mentioned_domains = []
        
        for domain, keywords in domains.items():
            if any(keyword in content for keyword in keywords):
                mentioned_domains.append(domain)
        
        if len(mentioned_domains) >= 2:
            convergence_points.append({
                "convergence_type": "domain_intersection",
                "domains": mentioned_domains,
                "evidence": signal.get("content", "")[:200],
                "opportunity_potential": len(mentioned_domains) * 0.2
            })
    
    return convergence_points[:5]

def identify_liminal_spaces(connection_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify liminal spaces where opportunities exist"""
    liminal_spaces = []
    
    # Analyze connection patterns to find liminal spaces
    clusters = connection_map.get("connection_clusters", [])
    intersections = connection_map.get("workflow_intersections", [])
    
    # Spaces between established categories
    for cluster in clusters:
        theme = cluster.get("cluster_theme", "")
        signal_count = cluster.get("signal_count", 0)
        
        if signal_count >= 3:  # Strong signal
            liminal_spaces.append({
                "space_type": "between_categories",
                "description": f"Gap in {theme} solutions",
                "evidence_strength": signal_count,
                "market_readiness": calculate_market_readiness(cluster)
            })
    
    # Workflow intersection spaces
    for intersection in intersections:
        tools = intersection.get("tools", [])
        if len(tools) == 2:
            liminal_spaces.append({
                "space_type": "workflow_intersection",
                "description": f"Gap between {tools[0]} and {tools[1]}",
                "evidence_strength": 2,
                "market_readiness": 0.7
            })
    
    return liminal_spaces[:5]

def calculate_connection_opportunity_score(connection_map: Dict[str, Any]) -> float:
    """Calculate overall opportunity score from connections"""
    score = 0.0
    
    # Cluster contribution
    clusters = connection_map.get("connection_clusters", [])
    cluster_score = sum(c.get("opportunity_strength", 0) for c in clusters)
    score += min(cluster_score * 0.2, 0.3)
    
    # Intersection contribution
    intersections = connection_map.get("workflow_intersections", [])
    score += min(len(intersections) * 0.1, 0.2)
    
    # Technology gaps contribution
    tech_gaps = connection_map.get("technology_gaps", [])
    gap_score = sum(g.get("severity", 0.5) for g in tech_gaps)
    score += min(gap_score * 0.1, 0.2)
    
    # Convergence points contribution
    convergence = connection_map.get("convergence_points", [])
    conv_score = sum(c.get("opportunity_potential", 0) for c in convergence)
    score += min(conv_score, 0.2)
    
    # Liminal spaces contribution
    liminal = connection_map.get("liminal_spaces", [])
    liminal_score = sum(l.get("market_readiness", 0) for l in liminal)
    score += min(liminal_score * 0.1, 0.1)
    
    return min(score, 1.0)

def group_friction_points(friction_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group similar friction points"""
    grouped = defaultdict(list)
    
    for point in friction_points:
        friction_type = point.get("friction_type", "unknown")
        grouped[friction_type].append(point)
    
    return [
        {
            "friction_type": ftype,
            "occurrence_count": len(points),
            "examples": points[:3]
        }
        for ftype, points in grouped.items()
        if len(points) >= 2
    ]

def analyze_tool_patterns(tool_switches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze tool switching patterns"""
    patterns = defaultdict(int)
    
    for switch in tool_switches:
        pattern = switch.get("switch_pattern", "unknown")
        patterns[pattern] += 1
    
    return [
        {
            "pattern": pattern,
            "frequency": count,
            "automation_potential": min(count / 5.0, 1.0)
        }
        for pattern, count in patterns.items()
        if count >= 2
    ]

def group_manual_processes(manual_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group and analyze manual processes"""
    grouped = defaultdict(list)
    
    for task in manual_tasks:
        task_type = task.get("manual_task", "unknown")
        grouped[task_type].append(task)
    
    return [
        {
            "process_type": ptype,
            "frequency": len(tasks),
            "automation_opportunity": len(tasks) * 0.2,
            "examples": tasks[:2]
        }
        for ptype, tasks in grouped.items()
        if len(tasks) >= 2
    ]

def identify_automation_opportunities(workflow_analysis: Dict[str, Any]) -> List[str]:
    """Identify top automation opportunities"""
    opportunities = []
    
    # High-frequency manual processes
    manual_processes = workflow_analysis.get("manual_processes", [])
    for process in manual_processes:
        if process.get("frequency", 0) >= 3:
            opportunities.append(f"Automate {process.get('process_type')} processes")
    
    # Common friction points
    friction_points = workflow_analysis.get("common_friction_points", [])
    for friction in friction_points:
        if friction.get("occurrence_count", 0) >= 3:
            opportunities.append(f"Eliminate {friction.get('friction_type')} friction")
    
    return opportunities[:5]

def calculate_workflow_efficiency(workflow_analysis: Dict[str, Any]) -> float:
    """Calculate workflow efficiency score"""
    # Lower friction = higher efficiency
    friction_count = len(workflow_analysis.get("common_friction_points", []))
    manual_count = len(workflow_analysis.get("manual_processes", []))
    
    # Base score reduced by inefficiencies
    efficiency = 1.0 - (friction_count * 0.1) - (manual_count * 0.1)
    return max(efficiency, 0.0)

def find_industry_convergence(industry_themes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find convergence between industries"""
    convergences = []
    
    industries = list(industry_themes.keys())
    
    # Compare each pair of industries
    for i, industry1 in enumerate(industries):
        for industry2 in industries[i+1:]:
            theme1 = industry_themes[industry1]
            theme2 = industry_themes[industry2]
            
            # Find common technologies
            common_tech = set(theme1["technologies"]) & set(theme2["technologies"])
            
            if common_tech:
                convergences.append({
                    "industries": [industry1, industry2],
                    "common_technologies": list(common_tech),
                    "convergence_strength": len(common_tech),
                    "opportunity_type": "technology_convergence"
                })
    
    return convergences

def find_cross_pollination(industry_themes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find cross-pollination opportunities between industries"""
    opportunities = []
    
    # Look for technologies that are strong in one industry but weak in another
    all_technologies = set()
    for theme in industry_themes.values():
        all_technologies.update(theme["technologies"])
    
    for tech in all_technologies:
        industries_with_tech = []
        industries_without_tech = []
        
        for industry, theme in industry_themes.items():
            if tech in theme["technologies"]:
                industries_with_tech.append(industry)
            else:
                industries_without_tech.append(industry)
        
        # If technology is strong in some industries but missing in others
        if len(industries_with_tech) >= 1 and len(industries_without_tech) >= 1:
            opportunities.append({
                "technology": tech,
                "source_industries": industries_with_tech,
                "target_industries": industries_without_tech[:3],
                "transfer_potential": len(industries_without_tech) * 0.2
            })
    
    return opportunities[:5]

def find_tech_transfers(industry_themes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find technology transfer opportunities"""
    transfers = []
    
    # This would be more sophisticated in production
    # For now, identify obvious transfer opportunities
    
    high_tech_industries = []
    low_tech_industries = []
    
    for industry, theme in industry_themes.items():
        tech_count = len(theme["technologies"])
        if tech_count >= 3:
            high_tech_industries.append(industry)
        elif tech_count <= 1:
            low_tech_industries.append(industry)
    
    for high_tech in high_tech_industries:
        for low_tech in low_tech_industries:
            transfers.append({
                "from_industry": high_tech,
                "to_industry": low_tech,
                "transfer_type": "digitization_opportunity",
                "potential": 0.6
            })
    
    return transfers[:3]

def calculate_convergence_score(convergence_analysis: Dict[str, Any]) -> float:
    """Calculate convergence opportunity score"""
    score = 0.0
    
    # Convergence points
    points = convergence_analysis.get("convergence_points", [])
    score += min(len(points) * 0.2, 0.4)
    
    # Cross-pollination opportunities
    cross_poll = convergence_analysis.get("cross_pollination_opportunities", [])
    poll_score = sum(op.get("transfer_potential", 0) for op in cross_poll)
    score += min(poll_score, 0.3)
    
    # Technology transfers
    transfers = convergence_analysis.get("technology_transfers", [])
    transfer_score = sum(t.get("potential", 0) for t in transfers)
    score += min(transfer_score, 0.3)
    
    return min(score, 1.0)

def assess_gap_severity(signal: Dict[str, Any]) -> float:
    """Assess the severity of a technology gap"""
    content = str(signal.get("content", "")).lower()
    
    # High severity indicators
    high_severity_words = ["critical", "urgent", "blocker", "impossible", "broken"]
    medium_severity_words = ["difficult", "challenging", "slow", "inefficient"]
    
    if any(word in content for word in high_severity_words):
        return 0.9
    elif any(word in content for word in medium_severity_words):
        return 0.6
    else:
        return 0.4

def estimate_market_size(signal: Dict[str, Any]) -> str:
    """Estimate market size based on signal characteristics"""
    content = str(signal.get("content", "")).lower()
    source = signal.get("source", "")
    
    # Large market indicators
    if any(word in content for word in ["everyone", "all", "every", "universal"]):
        return "large"
    elif any(word in content for word in ["many", "most", "common", "popular"]):
        return "medium"
    elif "reddit" in source and signal.get("engagement", 0) > 100:
        return "medium"
    else:
        return "small"

def assess_complexity(signal: Dict[str, Any]) -> str:
    """Assess implementation complexity"""
    content = str(signal.get("content", "")).lower()
    
    # Complexity indicators
    if any(word in content for word in ["simple", "easy", "basic", "straightforward"]):
        return "low"
    elif any(word in content for word in ["integration", "api", "sync", "connect"]):
        return "medium"
    elif any(word in content for word in ["complex", "difficult", "enterprise", "custom"]):
        return "high"
    else:
        return "medium"

def calculate_market_readiness(cluster: Dict[str, Any]) -> float:
    """Calculate how ready the market is for a solution"""
    signal_count = cluster.get("signal_count", 0)
    theme = cluster.get("cluster_theme", "")
    
    # More signals = more market readiness
    readiness = min(signal_count / 5.0, 0.8)
    
    # Some themes indicate higher readiness
    high_readiness_themes = ["integration", "automation", "workflow", "efficiency"]
    if theme in high_readiness_themes:
        readiness += 0.2
    
    return min(readiness, 1.0)

# Create the gap mapper agent
gap_mapper_agent = LlmAgent(
    name="gap_mapper_agent",
    model="gemini-2.0-flash",
    instruction=GAP_MAPPER_PROMPT,
    description=(
        "Maps connections between market signals to identify hidden opportunities "
        "in liminal spaces where traditional market categories don't apply."
    ),
    tools=[
        FunctionTool(func=map_signal_connections),
        FunctionTool(func=analyze_workflow_gaps),
        FunctionTool(func=find_convergence_opportunities),
        google_search,
        load_web_page
    ],
    output_key="gap_mapping"
)