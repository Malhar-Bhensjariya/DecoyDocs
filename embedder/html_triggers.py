# html_triggers.py
# Generate HTML for visible and hidden beacon triggers in documents

def generate_visible_link_html(beacon_urls: dict, count: int = 3) -> str:
    """
    Generate visible blue hyperlinks that trigger beacon endpoints without opening tabs.
    
    Args:
        beacon_urls: dict with 'fonts', 'assets', 'beacon' keys containing URLs
        count: number of links to generate (default 3)
    
    Returns:
        HTML string with styled links and onclick handlers
    """
    links = []
    endpoints = list(beacon_urls.values())
    
    for i in range(min(count, len(endpoints))):
        url = endpoints[i]
        link_text = ["View Document", "Download Link", "More Information"][i % 3]
        
        html = f'''<a href="javascript:void(0)" 
     style="color: #0066cc; text-decoration: underline; cursor: pointer; font-family: Arial, sans-serif; font-size: 12pt; margin-right: 20px;"
     onclick="fetch('{url}', {{mode: 'no-cors'}}).catch(e => {{}});"
     title="Additional document information">
     {link_text}
</a>'''
        links.append(html)
    
    return " | ".join(links)

def generate_hidden_trigger_html(beacon_url: str, width: int = 100, height: int = 100, x_pos: int = 10, y_pos: int = 10) -> str:
    """
    Generate invisible clickable region that triggers beacon on click.
    Can be positioned absolutely over content.
    
    Args:
        beacon_url: beacon URL to trigger
        width: width in pixels
        height: height in pixels
        x_pos: x position from left
        y_pos: y position from top
    
    Returns:
        HTML with positioned clickable div
    """
    html = f'''<div onclick="fetch('{beacon_url}', {{mode: 'no-cors'}}).catch(e => {{}});"
     style="position: absolute; 
             left: {x_pos}px; 
             top: {y_pos}px; 
             width: {width}px; 
             height: {height}px; 
             cursor: pointer; 
             background: transparent; 
             border: none; 
             z-index: 1;">
</div>'''
    return html

def generate_image_trigger_html(image_path: str, beacon_url: str, alt_text: str = "Document Image") -> str:
    """
    Generate clickable image that triggers beacon on click.
    
    Args:
        image_path: path/URL to image
        beacon_url: beacon URL to trigger
        alt_text: alt text for image
    
    Returns:
        HTML with clickable image
    """
    html = f'''<img src="{image_path}" 
     alt="{alt_text}" 
     style="cursor: pointer; max-width: 100%; display: block;"
     onclick="fetch('{beacon_url}', {{mode: 'no-cors'}}).catch(e => {{}});"
     title="Click to view document details" />'''
    return html

def generate_pdf_beacon_script(beacon_urls: dict) -> str:
    """
    Generate JavaScript for PDF (embedded in HTML converted to PDF).
    Fires beacons on page load and user interaction.
    
    Args:
        beacon_urls: dict with beacon URLs
    
    Returns:
        JavaScript code
    """
    urls = list(beacon_urls.values())
    
    script = '''<script>
    // Fire beacons on load and interaction
    (function() {
        const urls = [%s];
        
        // Fire on page load (after slight delay for PDF rendering)
        setTimeout(() => {
            urls.forEach(url => {
                fetch(url, {mode: 'no-cors'}).catch(e => {});
            });
        }, 500);
        
        // Fire on any click
        document.addEventListener('click', () => {
            const randomUrl = urls[Math.floor(Math.random() * urls.length)];
            fetch(randomUrl, {mode: 'no-cors'}).catch(e => {});
        });
    })();
    </script>''' % ', '.join([f'"{url}"' for url in urls])
    
    return script
