"""
Code Executor Agent - Executes Python code using subprocess with temp files
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.genai import Client, types
from typing import Dict, List, Any, Optional
import json
import tempfile
import subprocess
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

client = Client()

CODE_EXECUTOR_PROMPT = """
You are a Python code execution and data analysis agent. Your role is to:

1. Generate Python code to solve analytical problems
2. Execute code safely in isolated environments
3. Analyze results and provide insights
4. Handle data processing and visualization tasks

You have access to common Python libraries including:
- pandas, numpy for data analysis
- matplotlib, seaborn for visualization  
- scipy for scientific computing
- requests for HTTP requests
- json, csv for data formats

Always:
- Write clean, well-commented code
- Handle errors gracefully
- Provide clear explanations of results
- Use best practices for data analysis
- Generate visualizations when appropriate

Never:
- Execute potentially dangerous operations
- Access sensitive system resources
- Make network calls to unauthorized endpoints
- Modify system files
"""

def execute_python_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code in a subprocess using temporary files
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary containing execution results, output, and any errors
    """
    result = {
        "success": False,
        "output": "",
        "error": "",
        "execution_time": 0,
        "files_created": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Create temporary directory for execution
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            start_time = datetime.now()
            
            # Write code to temporary file
            code_file = temp_path / "exec_code.py"
            
            # Add safety imports and setup
            safe_code = f"""
import sys
import os
import json
import traceback
from pathlib import Path

# Restrict some dangerous operations
import builtins
original_open = builtins.open

def safe_open(file, mode='r', **kwargs):
    # Only allow operations in temp directory
    if isinstance(file, (str, Path)):
        file_path = Path(file).resolve()
        temp_path = Path(r"{temp_dir}").resolve()
        if not str(file_path).startswith(str(temp_path)):
            raise PermissionError("File access outside temp directory not allowed")
    return original_open(file, mode, **kwargs)

builtins.open = safe_open

# Execution code
try:
{_indent_code(code, 4)}
except Exception as e:
    print(f"EXECUTION_ERROR: {{type(e).__name__}}: {{str(e)}}")
    traceback.print_exc()
"""
            
            code_file.write_text(safe_code, encoding='utf-8')
            
            # Execute the code
            process = subprocess.run(
                [sys.executable, str(code_file)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, 'PYTHONPATH': str(temp_dir)}
            )
            
            end_time = datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            # Capture output
            result["output"] = process.stdout
            if process.stderr:
                result["error"] = process.stderr
            
            # Check for execution errors in output
            if "EXECUTION_ERROR:" in result["output"]:
                result["error"] = result["output"]
                result["output"] = ""
            else:
                result["success"] = process.returncode == 0
            
            # List any files created
            created_files = []
            for file_path in temp_path.iterdir():
                if file_path.name != "exec_code.py":
                    try:
                        # Read small files to include in results
                        if file_path.stat().st_size < 1024 * 1024:  # 1MB limit
                            if file_path.suffix in ['.txt', '.json', '.csv']:
                                created_files.append({
                                    "name": file_path.name,
                                    "size": file_path.stat().st_size,
                                    "content": file_path.read_text(encoding='utf-8')[:10000]  # First 10KB
                                })
                            else:
                                created_files.append({
                                    "name": file_path.name,
                                    "size": file_path.stat().st_size,
                                    "type": "binary"
                                })
                    except Exception as e:
                        created_files.append({
                            "name": file_path.name,
                            "error": str(e)
                        })
            
            result["files_created"] = created_files
            
        except subprocess.TimeoutExpired:
            result["error"] = f"Code execution timed out after {timeout} seconds"
        except Exception as e:
            result["error"] = f"Execution failed: {str(e)}"
            result["traceback"] = traceback.format_exc()
            
    return result

def _indent_code(code: str, spaces: int) -> str:
    """Indent code by specified number of spaces"""
    indent = " " * spaces
    return "\n".join(indent + line for line in code.splitlines())

def analyze_data_with_code(data_description: str, analysis_request: str) -> Dict[str, Any]:
    """
    Generate and execute Python code for data analysis
    
    Args:
        data_description: Description of the data to analyze
        analysis_request: Specific analysis request
        
    Returns:
        Analysis results including generated code and execution output
    """
    try:
        # Generate code using AI
        prompt = f"""
        Generate Python code to perform the following data analysis:
        
        Data Description: {data_description}
        Analysis Request: {analysis_request}
        
        Requirements:
        - Use pandas, numpy, matplotlib as needed
        - Generate clear visualizations if appropriate
        - Include print statements for key results
        - Handle potential errors gracefully
        - Save any plots as PNG files
        
        Return only the Python code, no explanations or markdown formatting.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )
        
        if not response or not response.text:
            return {"error": "Failed to generate analysis code"}
            
        generated_code = response.text.strip()
        
        # Clean up code if it contains markdown formatting
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].strip()
        
        # Execute the generated code
        execution_result = execute_python_code(generated_code)
        
        return {
            "generated_code": generated_code,
            "execution_result": execution_result,
            "data_description": data_description,
            "analysis_request": analysis_request
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def create_visualization(data_dict: Dict[str, Any], chart_type: str, title: str = "") -> Dict[str, Any]:
    """
    Generate code to create visualizations from data
    
    Args:
        data_dict: Dictionary containing data to visualize
        chart_type: Type of chart (bar, line, scatter, histogram, etc.)
        title: Chart title
        
    Returns:
        Visualization results
    """
    try:
        # Convert data dict to code
        data_code = f"data = {json.dumps(data_dict, indent=2)}"
        
        # Generate visualization code
        viz_code = f"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

{data_code}

# Convert to DataFrame if needed
if isinstance(data, dict):
    if 'x' in data and 'y' in data:
        df = pd.DataFrame(data)
    else:
        # Try to create DataFrame from dict
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
else:
    df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))

chart_type = "{chart_type}".lower()
title = "{title}"

if chart_type == "bar":
    if len(df.columns) >= 2:
        plt.bar(df.iloc[:, 0], df.iloc[:, 1])
    else:
        df.iloc[:, 0].value_counts().plot(kind='bar')
elif chart_type == "line":
    if len(df.columns) >= 2:
        plt.plot(df.iloc[:, 0], df.iloc[:, 1])
    else:
        plt.plot(df.iloc[:, 0])
elif chart_type == "scatter":
    if len(df.columns) >= 2:
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
elif chart_type == "histogram":
    plt.hist(df.iloc[:, 0], bins=20)
else:
    # Default to bar chart
    if len(df.columns) >= 2:
        plt.bar(df.iloc[:, 0], df.iloc[:, 1])

plt.title(title if title else f"{chart_type.title()} Chart")
plt.xlabel(df.columns[0] if len(df.columns) > 0 else "X")
if len(df.columns) > 1:
    plt.ylabel(df.columns[1])

plt.tight_layout()
plt.savefig("visualization.png", dpi=150, bbox_inches='tight')
plt.show()

print(f"Visualization saved as visualization.png")
print(f"Data shape: {{df.shape}}")
print(f"Data summary:\\n{{df.describe()}}")
"""
        
        # Execute visualization code
        result = execute_python_code(viz_code)
        
        return {
            "visualization_code": viz_code,
            "execution_result": result,
            "chart_type": chart_type,
            "title": title
        }
        
    except Exception as e:
        return {
            "error": f"Visualization failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def validate_market_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and analyze market research data
    
    Args:
        data: Market data to validate
        
    Returns:
        Validation results and insights
    """
    validation_code = f"""
import pandas as pd
import numpy as np
from datetime import datetime

# Market data to validate
market_data = {json.dumps(data, indent=2)}

print("=== MARKET DATA VALIDATION ===")
print(f"Data received at: {{datetime.now()}}")
print(f"Data type: {{type(market_data)}}")

if isinstance(market_data, dict):
    print(f"\\nData keys: {{list(market_data.keys())}}")
    
    # Validate key fields
    required_fields = ['market_signals', 'competition_analysis', 'demand_validation']
    missing_fields = [field for field in required_fields if field not in market_data]
    
    if missing_fields:
        print(f"\\nMISSING REQUIRED FIELDS: {{missing_fields}}")
    else:
        print("\\n✓ All required fields present")
    
    # Analyze market signals
    if 'market_signals' in market_data:
        signals = market_data['market_signals']
        print(f"\\nMarket Signals Analysis:")
        print(f"  - Number of signals: {{len(signals) if isinstance(signals, list) else 'N/A'}}")
        
        if isinstance(signals, list) and signals:
            signal_types = {{}}
            for signal in signals:
                if isinstance(signal, dict) and 'type' in signal:
                    signal_types[signal['type']] = signal_types.get(signal['type'], 0) + 1
            print(f"  - Signal types: {{signal_types}}")
    
    # Analyze competition
    if 'competition_analysis' in market_data:
        comp = market_data['competition_analysis']
        print(f"\\nCompetition Analysis:")
        if isinstance(comp, dict):
            print(f"  - Competition level: {{comp.get('competition_level', 'Unknown')}}")
            print(f"  - Direct competitors: {{len(comp.get('direct_competitors', []))}}")
    
    # Calculate opportunity score
    if 'opportunity_score' in market_data:
        score = market_data['opportunity_score']
        print(f"\\nOpportunity Score: {{score}}")
        if isinstance(score, (int, float)):
            if score >= 0.7:
                print("  → HIGH POTENTIAL OPPORTUNITY")
            elif score >= 0.4:
                print("  → MODERATE OPPORTUNITY")
            else:
                print("  → LOW POTENTIAL OPPORTUNITY")
    
    print("\\n=== VALIDATION COMPLETE ===")

else:
    print("ERROR: Expected dictionary format for market data")
"""
    
    return execute_python_code(validation_code)

# Create the code executor agent
code_executor_agent = LlmAgent(
    name="code_executor_agent",
    model="gemini-2.0-flash",
    instruction=CODE_EXECUTOR_PROMPT,
    description=(
        "Executes Python code for data analysis, visualization, and "
        "market research validation using secure subprocess execution."
    ),
    tools=[
        FunctionTool(func=execute_python_code),
        FunctionTool(func=analyze_data_with_code),
        FunctionTool(func=create_visualization),
        FunctionTool(func=validate_market_data)
    ],
    output_key="code_execution_results"
)