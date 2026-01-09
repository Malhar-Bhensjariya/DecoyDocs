#!/usr/bin/env python3
"""
gemini_graph_generator.py
Uses Google Gemini to generate matplotlib/seaborn code for professional graphs,
then executes the code to create images with embedded beacons.
"""

import os
import json
import re
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv
from google import genai

# Load Gemini API key
def load_api_key() -> Optional[str]:
    """Load GEMINI_API_KEY from environment or .env file."""
    dotenv_path = Path(__file__).resolve().parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    return os.getenv("GEMINI_API_KEY")


def generate_graph_code(client: genai.Client, document_content: str, model: str = "gemini-2.5-flash") -> str:
    """
    Use Gemini to generate matplotlib/seaborn code that visualizes document data.
    
    Args:
        client: Gemini API client
        document_content: The document text to analyze and visualize
        model: Gemini model to use
    
    Returns:
        Python code string for generating the graph
    """
    prompt = f"""Based on this document content, generate Python matplotlib or seaborn code that creates a professional, colorful visualization appropriate for the data.

Document Content:
{document_content[:1500]}  # Limit to first 1500 chars

Requirements:
1. Generate ONLY valid Python code (no markdown, no ```python``` blocks)
2. The code must import matplotlib.pyplot and seaborn
3. Create a figure with professional styling (seaborn style preferred)
4. Include title, axis labels, and a grid
5. Use colorful, professional color palettes (Set2, husl, or tab10)
6. Output the figure to a variable named 'fig' (do not call plt.show() or plt.savefig())
7. The code should be self-contained and runnable
8. Create realistic data that matches the document context
9. Make it visually appealing with at least 2-3 different plot types

Example structure (modify as needed):
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))

# Create realistic data from document context
data = {{'metric': [...], 'value': [...]}}
df = pd.DataFrame(data)

# Create visualization
sns.barplot(data=df, x='metric', y='value', palette='Set2', ax=ax)
ax.set_title('Document Data Visualization', fontsize=16, fontweight='bold')
ax.set_xlabel('Metrics', fontsize=12)
ax.set_ylabel('Values', fontsize=12)

# Return figure object for saving
fig = fig

Start your response with the Python code directly:"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        code = response.text.strip()
        
        # Clean up markdown code blocks if present
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        code = code.strip()
        
        return code
    except Exception as e:
        print(f"Error generating graph code: {e}")
        raise


def execute_graph_code(code: str, output_path: str) -> bool:
    """
    Execute the matplotlib code and save the figure.
    
    Args:
        code: Python code to execute
        output_path: Path to save the PNG file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create temporary Python script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            # Add necessary imports and save logic
            full_code = f"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

{code}

# Save the figure
fig.savefig(r'{output_path}', dpi=150, bbox_inches='tight', facecolor='white')
print(f'Graph saved to {{r"{output_path}"}}')
"""
            tmp.write(full_code)
            tmp.flush()
            tmp_path = tmp.name

        # Execute the script
        result = subprocess.run(
            ['python', tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        if result.returncode != 0:
            print(f"Error executing graph code: {result.stderr}")
            return False
        
        print(f"Graph generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error in graph execution: {e}")
        return False


def generate_graph_with_beacon(
    document_content: str,
    output_path: str,
    beacon_url: str = None,
    api_key: str = None,
    model: str = "gemini-2.5-flash"
) -> Tuple[bool, Optional[str]]:
    """
    Full pipeline: Generate graph code via Gemini, execute it, embed beacon.
    
    Args:
        document_content: Document text to visualize
        output_path: Path to save PNG
        beacon_url: Optional beacon URL (for logging purposes)
        api_key: Gemini API key
        model: Model to use
    
    Returns:
        Tuple of (success: bool, output_path: Optional[str])
    """
    if not api_key:
        api_key = load_api_key()
    
    if not api_key:
        print("GEMINI_API_KEY not found in environment or .env")
        return False, None
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Generate code
        print("Generating graph code with Gemini...")
        graph_code = generate_graph_code(client, document_content, model)
        print("Graph code generated")
        
        # Execute code and save image
        print("Executing graph code...")
        success = execute_graph_code(graph_code, output_path)
        
        if success:
            print(f"Professional graph generated: {output_path}")
            if beacon_url:
                print(f"   Beacon: {beacon_url}")
            return True, output_path
        else:
            print("Failed to execute graph code")
            return False, None
            
    except Exception as e:
        print(f"Error in graph generation pipeline: {e}")
        return False, None


if __name__ == "__main__":
    # Test example
    sample_doc = """
    Q4 2025 Financial Summary
    
    Revenue: $15.2M, up 23% YoY
    Expenses: $9.8M, up 12% YoY
    Profit Margin: 35.5%
    
    Key Drivers:
    - Product A: 45% of revenue
    - Product B: 30% of revenue
    - Services: 25% of revenue
    
    Regional Breakdown:
    - North America: 55%
    - Europe: 30%
    - Asia-Pacific: 15%
    """
    
    output_file = "test_graph.png"
    success, path = generate_graph_with_beacon(
        sample_doc,
        output_file,
        beacon_url="https://example.com/api/beacon?resource_id=test"
    )
    
    if success:
        print(f"Test complete: {path}")
    else:
        print("Test failed")
