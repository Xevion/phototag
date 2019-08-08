# from libxmp import file_to_dict
import os, sys, re

basepath = "E:\\Photography\\Colorado 2019\\"
ext_filter = lambda file : file.endswith('.NEF')
mainPattern = r'<dc:subject>\n\s+<rdf:Bag>\n(?:     <rdf:li>.+<\/rdf:li>\n)*\s+<\/rdf:Bag>\n\s+<\/dc:subject>\n'
subPattern = r'<rdf:li>(.*)</rdf:li>\n'
subFormatPattern = '     <rdf:li>{}</rdf:li>\n'

def getXMP(file, basepath=None):
    xmpFile = file.rfind('.')
    xmpFile = file[:xmpFile] + '.xmp'
    if basepath:
        xmpFile = os.path.join(basepath, xmpFile)
    return xmpFile

def writeTags(tags, filename):
    fullpath = os.path.join(basepath, getXMP(filename))
    if not os.path.exists(fullpath):
        raise FileNotFoundError(f'No XMP file found for {filename}.')
    data = open(fullpath, 'r').read()

    # Detect and find the <dc:Subject: part
    match = re.search(mainPattern, data)
    if not match:
        addition = """\n   <dc:subject>\n    <rdf:Bag>\n    </rdf:Bag>\n   </dc:subject>"""
        look = data.find('</dc:creator>') + 13
        data = data[:look] + addition + data[look:]
        match = re.search(mainPattern, data)

    print(os.path.join(basepath, filename))
    print(fullpath)
    print('. . .')
 
    # Get last matching tag
    submatch = None
    for submatch in re.finditer(subPattern, match.group(0)):
        pass
    # Calculate very end
    spanend = match.span()[0] + (submatch.span()[1] if submatch else 0)
   # add tags to end
    data = data[:spanend] + ''.join(subFormatPattern.format(tag) for tag in tags) + data[spanend:]
    # Write file to disk
    open(fullpath, 'w').write( data)

files = os.listdir(basepath)
print(f'Total Files: {len(files)}')
files = list(filter(ext_filter, files))
print(f'Total Files after .NEF filter: {len(files)}')

xmps = [file for file in files if os.path.exists(getXMP(file, basepath=basepath))]
print(f'Total .NEF files with .XMP pair: {len(xmps)}')
print(f'{len(xmps)} x 2 == {len(xmps) * 2}')

select = files[43]
writeTags(['helpgod', 'ohfuck'], select)
print(select) 