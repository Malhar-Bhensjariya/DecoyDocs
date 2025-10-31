import zipfile
import uuid
from pathlib import Path

# Replace these
NGROK_URL = "https://jody-unquavering-unhostilely.ngrok-free.dev"
FILE_UUID = "DOC-LINK-001"

out_file = f"Decoy_linked_{FILE_UUID}.docx"
beacon_url = f"{NGROK_URL}/beacon/{FILE_UUID}.png"

# Minimal document.xml with a drawing that references r:link="rId1"
# This is a pared-down valid document body containing a picture reference;
# Word will resolve the r:link relationship to the external target.
document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    <w:p>
      <w:r>
        <w:t>Confidential Report — internal use only</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <!-- Inline drawing referencing external image relationship by r:link -->
        <w:drawing>
          <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
            <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:blipFill>
                    <a:blip r:link="rId1"/>
                  </pic:blipFill>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    <w:sectPr/>
  </w:body>
</w:document>'''

# Minimal [Content_Types].xml
content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

# Minimal _rels/.rels to point to /word/document.xml
rels_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdDoc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

# word/_rels/document.xml.rels — this is where we put the external image relationship
# Note TargetMode="External" and Type as image relationship.
document_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{beacon_url}" TargetMode="External"/>
</Relationships>'''

# Build the .docx (zip file)
with zipfile.ZipFile(out_file, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    # content types
    z.writestr('[Content_Types].xml', content_types)
    # root relationships
    z.writestr('_rels/.rels', rels_rels)
    # word/document.xml
    z.writestr('word/document.xml', document_xml)
    # word/_rels/document.xml.rels
    z.writestr('word/_rels/document.xml.rels', document_rels)

print("Saved:", out_file)
print("Beacon URL:", beacon_url)
print("Open the .docx in Word to test. If Word auto-loads external images, beacon will fire.")
