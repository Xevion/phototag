# from libxmp import file_to_dict
import os, sys, re

mainPattern = r'<dc:subject>\n\s+<rdf:Bag>\n(?:     <rdf:li>.+<\/rdf:li>\n)*\s+<\/rdf:Bag>\n\s+<\/dc:subject>\n'
subPattern = r'<rdf:li>(.*)</rdf:li>\n'
subFormatPattern = '     <rdf:li>{}</rdf:li>\n'

# Write tags to an XMP file, using regex patterns
def writeXMP(inputPath, outputPath, tags):
    data = open(inputPath, 'r').read()
    # Detect and find the <dc:Subject: part
    match = re.search(mainPattern, data)
    # If it's not found, we just add the tags area right below the creator tag
    if not match:
        addition = """\n   <dc:subject>\n    <rdf:Bag>\n    </rdf:Bag>\n   </dc:subject>"""
        look = data.find('</dc:creator>') + 13
        data = data[:look] + addition + data[look:]
        match = re.search(mainPattern, data)
    # Get last matching tag
    submatch = None
    for submatch in re.finditer(subPattern, match.group(0)):
        pass
    # Calculate very end
    spanend = match.span()[0] + (submatch.span()[1] if submatch else 0)
   # add tags to end
    data = data[:spanend] + ''.join(subFormatPattern.format(tag) for tag in tags) + data[spanend:]
    # Write file to disk
    open(outputPath, 'w+').write( data)