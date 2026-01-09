# packer.py
# Build final PDF via HTML -> wkhtmltopdf
import os
import subprocess
from typing import Tuple, Dict, List
from .utils import ensure_dir, safe_filename, file_checksum
from .html_triggers import (
    generate_visible_link_html,
    generate_hidden_trigger_html,
    generate_image_trigger_html,
    generate_pdf_beacon_script
)
import json

OUTPUT_DIR = "out"

def calculate_safe_positions(graph_width: int = 600, graph_height: int = 400, 
                            graph_x: int = 20, graph_y: int = 100,
                            base_size: int = 100) -> List[Tuple[int, int]]:
    """
    Calculate safe positions for hidden trigger regions (100x100 base.png).
    Ensures no overlap with:
    - Document header (0-80px)
    - Graph image (graph_y to graph_y + graph_height)
    - Footer area
    
    Args:
        graph_width: Width of graph image
        graph_height: Height of graph image
        graph_x: X position of graph
        graph_y: Y position of graph
        base_size: Size of hidden trigger (100x100)
    
    Returns:
        List of (x, y) positions for hidden triggers
    """
    positions = []
    
    # Safe zones to place 100x100 hidden triggers
    # Zone 1: Right side of document (after graph)
    positions.append((graph_x + graph_width + 30, graph_y + 50))  # Right side, mid-graph
    
    # Zone 2: Below graph
    positions.append((graph_x + 50, graph_y + graph_height + 50))
    
    # Zone 3: Right side, below
    positions.append((graph_x + graph_width - 100, graph_y + graph_height + 50))
    
    # Zone 4: Far right corners
    positions.append((850, 200))
    positions.append((850, graph_y + graph_height - 50))
    
    # Zone 5: Between visible content
    positions.append((30, graph_y + graph_height + 150))
    
    return positions


def build_pdf_with_assets(title: str, stego_path: str, beacon_urls: Dict[str, str], 
                         graph_path: str = None, out_name: str = None, 
                         output_dir: str = "out") -> Tuple[str, str]:
    """
    Build PDF with mixed beacon triggers including Gemini-generated graph.
    
    Args:
        title: PDF title
        stego_path: path to steganographic image (LSB embedded)
        beacon_urls: dict with 'fonts', 'assets', 'beacon' beacon URLs
        graph_path: optional path to professional graph image (Gemini-generated)
        out_name: output filename
        output_dir: output directory
    
    Returns:
        tuple of (pdf_path, manifest_path)
    """
    ensure_dir(output_dir)
    out_name = safe_filename(out_name or f"{title}.pdf")
    out_path = os.path.join(output_dir, out_name)

    # Generate all visible trigger types
    visible_links = generate_visible_link_html(beacon_urls, count=3)
    beacon_script = generate_pdf_beacon_script(beacon_urls)

    # Use graph image if available, otherwise use stego image
    main_image_path = graph_path if graph_path else stego_path
    main_image_html = generate_image_trigger_html(
        f"file://{os.path.abspath(main_image_path)}", 
        beacon_urls.get('assets', ''),
        alt_text="Document Analysis"
    )

    # Calculate safe positions for hidden triggers (scattered throughout document)
    safe_positions = calculate_safe_positions()
    
    # Generate multiple hidden trigger HTML elements
    hidden_triggers_html = ""
    for i, (x, y) in enumerate(safe_positions):
        # Cycle through beacon URLs for variety
        beacon_url = list(beacon_urls.values())[i % len(beacon_urls)]
        trigger_html = generate_hidden_trigger_html(beacon_url, x_pos=x, y_pos=y)
        hidden_triggers_html += trigger_html + "\n"

    html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: white;
                max-width: 900px;
            }}
            .header {{ 
                border-bottom: 3px solid #1a237e; 
                padding-bottom: 15px; 
                margin-bottom: 25px;
            }}
            .header h1 {{ 
                margin: 0; 
                color: #1a237e; 
                font-size: 28px;
            }}
            .subtitle {{ 
                color: #666; 
                font-size: 12px; 
                margin-top: 5px;
            }}
            .links {{ 
                margin: 20px 0; 
                padding: 12px; 
                background: #f8f9fa; 
                border-left: 4px solid #1a237e;
                border-radius: 4px;
            }}
            .links strong {{ 
                display: block; 
                margin-bottom: 8px; 
                color: #333;
            }}
            .content {{ 
                margin: 25px 0;
                line-height: 1.6;
            }}
            .graph-section {{ 
                margin: 30px 0; 
                text-align: center;
            }}
            .graph-section h3 {{ 
                color: #1a237e; 
                margin-bottom: 15px;
            }}
            .graph-image {{ 
                max-width: 100%; 
                height: auto; 
                border: 1px solid #ddd; 
                border-radius: 6px;
                margin: 10px 0;
            }}
            .insights {{ 
                background: #f0f4ff; 
                padding: 15px; 
                border-radius: 4px; 
                margin: 20px 0;
                border-left: 4px solid #1a237e;
            }}
            .footer {{ 
                margin-top: 40px; 
                padding-top: 15px; 
                border-top: 1px solid #ccc; 
                color: #999; 
                font-size: 11px;
                text-align: center;
            }}
            /* Position for relative reference - helps with hidden trigger placement */
            .document {{ position: relative; }}
        </style>
      </head>
      <body class="document">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">Confidential - For Authorized Use Only</div>
        </div>
        
        <div class="content">
            <h2>Executive Summary</h2>
            <p>This document contains tracked content with professional data visualization. Access is logged and monitored for security and compliance.</p>
        </div>

        <div class="links">
            <strong>Available Resources:</strong><br/>
            {visible_links}
        </div>

        <div class="insights">
            <h3>Key Insights</h3>
            <p>The following visualization presents comprehensive data analysis with real-time tracking capabilities.</p>
        </div>

        <div class="graph-section">
            <h3>Data Analysis & Metrics</h3>
            {main_image_html}
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                <em>Interactive visualization with embedded tracking</em>
            </p>
        </div>

        <div class="content">
            <h2>Document Details</h2>
            <p>This document is protected with multiple layers of access tracking and monitoring.</p>
            <ul>
                <li>Real-time access logging</li>
                <li>Geographic tracking</li>
                <li>Unauthorized distribution alerts</li>
                <li>Content integrity verification</li>
            </ul>
        </div>

        <div class="footer">
            <p>Generated: 2026-01-09 | Document Protection Active | All access logged</p>
        </div>

        {hidden_triggers_html}
        {beacon_script}
      </body>
    </html>
    """
    
    tmp_html = os.path.join(output_dir, "tmp_embed.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        subprocess.run(["wkhtmltopdf", tmp_html, out_path], check=True, 
                      capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"wkhtmltopdf error: {e.stderr.decode()}")
        raise
    finally:
        if os.path.exists(tmp_html):
            os.remove(tmp_html)

    checksum = file_checksum(out_path)
    manifest = {
        "path": out_path,
        "checksum": checksum,
        "title": title,
        "stego": stego_path,
        "graph": graph_path,
        "beacon_urls": beacon_urls,
        "triggers": {
            "visible_links": 3,
            "hidden_regions": len(safe_positions),
            "graph_image": True,
            "javascript": True,
            "hidden_positions": safe_positions  # Document positions for reference
        }
    }
    manifest_path = out_path + ".manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)
    
    return out_path, manifest_path

