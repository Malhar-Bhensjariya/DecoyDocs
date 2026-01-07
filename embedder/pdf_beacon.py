# pdf_beacon.py
# Embed active beacon triggers in PDF files
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfWriter, PdfReader
    from pypdf.generic import DictionaryObject, NameObject, ArrayObject
    HAS_PYPDF = True
except ImportError:
    try:
        from PyPDF2 import PdfFileWriter, PdfFileReader
        from PyPDF2.generic import DictionaryObject, NameObject, ArrayObject
        HAS_PYPDF = True
        PYPDF2_MODE = True
    except ImportError:
        HAS_PYPDF = False
        PYPDF2_MODE = False


def embed_beacon_in_pdf(pdf_path: Path, beacon_url: str, output_path: Optional[Path] = None) -> Path:
    """
    Embed an invisible beacon trigger in a PDF file.
    
    Creates an invisible annotation/link that loads the beacon URL when the PDF is opened.
    Uses PDF JavaScript action or invisible link annotation.
    
    Args:
        pdf_path: Path to input PDF
        beacon_url: URL to trigger (beacon endpoint)
        output_path: Optional output path (defaults to overwriting input)
    
    Returns:
        Path to the modified PDF
    """
    if not HAS_PYPDF:
        raise ImportError(
            "pypdf or PyPDF2 is required for PDF beacon embedding. "
            "Install with: pip install pypdf"
        )
    
    if output_path is None:
        output_path = pdf_path
    
    try:
        # Try pypdf (newer library)
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Method 1: Add invisible link annotation (works when clicked, most reliable)
        first_page = writer.pages[0]
        mediabox = first_page.mediabox
        height = float(mediabox.height)
        link_annotation = DictionaryObject({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Rect"): ArrayObject([0, height - 1, 1, height]),
            NameObject("/Border"): ArrayObject([0, 0, 0]),  # Invisible
            NameObject("/A"): DictionaryObject({
                NameObject("/S"): NameObject("/URI"),
                NameObject("/URI"): beacon_url
            }),
            NameObject("/F"): 4,  # Invisible
        })
        
        if "/Annots" not in first_page:
            first_page[NameObject("/Annots")] = ArrayObject()
        annot_ref = writer._add_object(link_annotation)
        first_page[NameObject("/Annots")].append(annot_ref)
        
        # Method 2: Add JavaScript action (if JS enabled)
        try:
            js_code = f"""
            // Auto-trigger beacon when PDF opens (if JavaScript enabled)
            try {{
                var req = new XMLHttpRequest();
                req.open("GET", "{beacon_url}", true);
                req.send();
            }} catch(e) {{
                try {{
                    fetch("{beacon_url}");
                }} catch(e2) {{
                    var img = new Image();
                    img.src = "{beacon_url}";
                }}
            }}
            """
            writer.add_js(js_code)
            print(f"   JavaScript action added (if JS enabled)")
        except Exception as js_err:
            pass  # JavaScript not available, that's okay
        
        # Write output
        output_path_str = str(output_path)
        with open(output_path_str, "wb") as out_file:
            writer.write(out_file)
        
        print(f"✅ Beacon embedded in PDF: {beacon_url}")
        return output_path
        
    except Exception as e:
        # Fallback: Try simpler approach with just URI action
        print(f"⚠️ Primary method failed ({e}), trying fallback...")
        return _embed_beacon_simple(pdf_path, beacon_url, output_path)


def _embed_beacon_simple(pdf_path: Path, beacon_url: str, output_path: Path) -> Path:
    """Simpler fallback: Add invisible link annotation only."""
    try:
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            new_page = writer.add_page(page)
            
            # Add invisible link on first page only
            if i == 0:
                mediabox = new_page.mediabox
                height = float(mediabox.height)
                
                # Create invisible link annotation
                link_annotation = DictionaryObject({
                    NameObject("/Type"): NameObject("/Annot"),
                    NameObject("/Subtype"): NameObject("/Link"),
                    NameObject("/Rect"): ArrayObject([0, height - 1, 1, height]),
                    NameObject("/Border"): ArrayObject([0, 0, 0]),
                    NameObject("/A"): DictionaryObject({
                        NameObject("/S"): NameObject("/URI"),
                        NameObject("/URI"): beacon_url
                    }),
                    NameObject("/F"): 4  # Invisible
                })
                
                # Add to page annotations
                if "/Annots" not in new_page:
                    new_page[NameObject("/Annots")] = ArrayObject()
                
                annot_ref = writer._add_object(link_annotation)
                new_page[NameObject("/Annots")].append(annot_ref)
        
        output_path_str = str(output_path)
        with open(output_path_str, "wb") as out_file:
            writer.write(out_file)
        
        print(f"✅ Beacon embedded (simple method) in PDF")
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Failed to embed beacon in PDF: {e}")


def embed_beacon_in_docx(docx_path: Path, beacon_url: str, output_path: Optional[Path] = None) -> Path:
    """
    Embed an active beacon trigger in a DOCX file using a REMOTE IMAGE.
    
    CRITICAL: When Word/LibreOffice opens the document, it automatically
    tries to load the remote image, which triggers the beacon URL!
    
    This uses manual ZIP/XML editing to embed a remote image reference,
    which is more reliable than python-docx for external images.
    
    Args:
        docx_path: Path to input DOCX
        beacon_url: URL to trigger (will be loaded as an image)
        output_path: Optional output path
    
    Returns:
        Path to modified DOCX
    """
    import zipfile
    import shutil
    import xml.etree.ElementTree as ET
    from io import BytesIO
    
    if output_path is None:
        output_path = docx_path
    
    # Copy source to destination
    if str(docx_path) != str(output_path):
        shutil.copy2(docx_path, output_path)
    
    # Open DOCX as ZIP
    output_path_str = str(output_path)
    tmp_path = output_path_str + '.tmp'
    with zipfile.ZipFile(output_path_str, 'r') as zin:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            # Copy all files except document.xml and its relationships
            for item in zin.infolist():
                if item.filename not in ['word/document.xml', 'word/_rels/document.xml.rels']:
                    zout.writestr(item, zin.read(item.filename))
            
            # Read and modify document.xml
            doc_xml = zin.read('word/document.xml').decode('utf-8')
            root = ET.fromstring(doc_xml)
            
            # Find body element
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                  'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                  'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
                  'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                  'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'}
            
            body = root.find('.//w:body', ns)
            if body is None:
                # Create body if missing
                body = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
                root.append(body)
            
            # Add paragraph with remote image at the end
            para = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
            run = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
            
            # Create drawing with remote image reference
            drawing = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
            inline = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline')
            inline.set('distT', '0')
            inline.set('distB', '0')
            inline.set('distL', '0')
            inline.set('distR', '0')
            
            extent = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')
            extent.set('cx', '1')  # 1 pixel wide
            extent.set('cy', '1')  # 1 pixel tall
            inline.append(extent)
            
            effect_extent = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}effectExtent')
            effect_extent.set('l', '0')
            effect_extent.set('t', '0')
            effect_extent.set('r', '0')
            effect_extent.set('b', '0')
            inline.append(effect_extent)
            
            doc_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
            doc_pr.set('id', '1')
            doc_pr.set('name', 'beacon')
            inline.append(doc_pr)
            
            c_nv_graphic_frame_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}cNvGraphicFramePr')
            inline.append(c_nv_graphic_frame_pr)
            
            graphic = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}graphic')
            graphic_data = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}graphicData')
            graphic_data.set('uri', 'http://schemas.openxmlformats.org/drawingml/2006/picture')
            
            pic = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/picture}pic')
            
            # Required: nvPicPr (non-visual picture properties)
            nv_pic_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/picture}nvPicPr')
            c_nv_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/picture}cNvPr')
            c_nv_pr.set('id', '0')
            c_nv_pr.set('name', 'beacon')
            nv_pic_pr.append(c_nv_pr)
            c_nv_pic_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/picture}cNvPicPr')
            nv_pic_pr.append(c_nv_pic_pr)
            pic.append(nv_pic_pr)
            
            # Required: blipFill (image fill)
            blip_fill = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/picture}blipFill')
            blip = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
            blip.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link', 'rIdBeacon')
            blip_fill.append(blip)
            stretch = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}stretch')
            fill_rect = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}fillRect')
            stretch.append(fill_rect)
            blip_fill.append(stretch)
            pic.append(blip_fill)
            
            # Required: spPr (shape properties)
            sp_pr = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}spPr')
            xfrm = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}xfrm')
            off = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}off')
            off.set('x', '0')
            off.set('y', '0')
            xfrm.append(off)
            ext = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}ext')
            ext.set('cx', '1')
            ext.set('cy', '1')
            xfrm.append(ext)
            sp_pr.append(xfrm)
            prst_geom = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
            prst_geom.set('prst', 'rect')
            av_lst = ET.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}avLst')
            prst_geom.append(av_lst)
            sp_pr.append(prst_geom)
            pic.append(sp_pr)
            
            graphic_data.append(pic)
            graphic.append(graphic_data)
            inline.append(graphic)
            drawing.append(inline)
            run.append(drawing)
            para.append(run)
            body.append(para)
            
            # Write modified document.xml
            doc_xml_new = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            zout.writestr('word/document.xml', doc_xml_new)
            
            # Read and modify relationships
            try:
                rels_xml = zin.read('word/_rels/document.xml.rels').decode('utf-8')
                rels_root = ET.fromstring(rels_xml)
            except KeyError:
                # Create relationships if missing
                rels_root = ET.Element('{http://schemas.openxmlformats.org/package/2006/relationships}Relationships')
            
            # Add remote image relationship
            rel = ET.Element('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
            rel.set('Id', 'rIdBeacon')
            rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
            rel.set('Target', beacon_url)
            rel.set('TargetMode', 'External')
            rels_root.append(rel)
            
            rels_xml_new = ET.tostring(rels_root, encoding='utf-8', xml_declaration=True)
            zout.writestr('word/_rels/document.xml.rels', rels_xml_new)
    
    # Replace original with modified
    shutil.move(tmp_path, output_path_str)
    
    # Validate the DOCX is still a valid ZIP file
    try:
        with zipfile.ZipFile(output_path_str, 'r') as test_zip:
            # Check that required files exist
            required_files = ['word/document.xml', '[Content_Types].xml']
            for req_file in required_files:
                if req_file not in test_zip.namelist():
                    raise ValueError(f"Required file missing in DOCX: {req_file}")
        print(f"✅ Remote image beacon embedded in DOCX (auto-triggers on open!)")
    except Exception as e:
        print(f"⚠️ Warning: DOCX validation failed: {e}")
        print(f"   File may be corrupted. Original file preserved.")
        raise
    
    return output_path
