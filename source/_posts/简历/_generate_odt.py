#!/usr/bin/env python3
"""Convert _my_work.md to _my_work.odt with Chinese-style formatting and VSCode blue headings."""

import xml.etree.ElementTree as ET
import zipfile, os, shutil, subprocess, sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(SRC_DIR, '_my_work.md')
ODT_PATH = os.path.join(SRC_DIR, '_my_work.odt')
TMP_DIR = '/tmp/odt_work'

NAMESPACES = [
    ('', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'),
    ('style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'),
    ('text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'),
    ('table', 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'),
    ('draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'),
    ('fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'),
    ('xlink', 'http://www.w3.org/1999/xlink'),
    ('dc', 'http://purl.org/dc/elements/1.1/'),
    ('meta', 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0'),
    ('number', 'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0'),
    ('svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'),
    ('chart', 'urn:oasis:names:tc:opendocument:xmlns:chart:1.0'),
    ('dr3d', 'urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0'),
    ('math', 'http://www.w3.org/1998/Math/MathML'),
    ('form', 'urn:oasis:names:tc:opendocument:xmlns:form:1.0'),
    ('script', 'urn:oasis:names:tc:opendocument:xmlns:script:1.0'),
    ('ooo', 'http://openoffice.org/2004/office'),
    ('ooow', 'http://openoffice.org/2004/writer'),
    ('oooc', 'http://openoffice.org/2004/calc'),
    ('dom', 'http://www.w3.org/2001/xml-events'),
    ('xforms', 'http://www.w3.org/2002/xforms'),
    ('xsd', 'http://www.w3.org/2001/XMLSchema'),
    ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
    ('rpt', 'http://openoffice.org/2005/report'),
    ('of', 'urn:oasis:names:tc:opendocument:xmlns:of:1.2'),
    ('xhtml', 'http://www.w3.org/1999/xhtml'),
    ('grddl', 'http://www.w3.org/2003/g/data-view#'),
    ('tableooo', 'http://openoffice.org/2009/table'),
    ('drawooo', 'http://openoffice.org/2010/draw'),
    ('calcext', 'urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0'),
    ('loext', 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0'),
    ('field', 'urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0'),
    ('formx', 'urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0'),
    ('css3t', 'http://www.w3.org/TR/css3-text/'),
]

NS = {
    'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
    'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'svg': 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
}

# VSCode blue palette for headings
VSCODE_BLUE = {
    'Heading_20_1': '#007ACC',
    'Heading_20_2': '#0e639c',
    'Heading_20_3': '#1177bb',
    'Heading_20_4': '#219fd5',
    'Heading_20_5': '#31b4e4',
    'Heading_20_6': '#40c8f0',
}

HEADING_CONFIG = {
    'Heading_20_1': {'font-size': '16pt', 'margin-top': '0.15in', 'margin-bottom': '0.08in'},
    'Heading_20_2': {'font-size': '14pt', 'margin-top': '0.12in', 'margin-bottom': '0.06in'},
    'Heading_20_3': {'font-size': '12pt', 'margin-top': '0.1in', 'margin-bottom': '0.04in'},
}


def register_namespaces():
    for prefix, uri in NAMESPACES:
        ET.register_namespace(prefix, uri)


def md_to_odt():
    print('Step 1/3: Converting Markdown to ODT with pandoc...')
    result = subprocess.run(
        ['pandoc', MD_PATH, '-o', ODT_PATH],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'Error: pandoc failed: {result.stderr}')
        sys.exit(1)
    print('  Done.')


def extract_odt():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)
    with zipfile.ZipFile(ODT_PATH, 'r') as zf:
        zf.extractall(TMP_DIR)


def patch_styles():
    print('Step 2/3: Patching styles (A4, Chinese fonts, VSCode blue)...')
    tree = ET.parse(os.path.join(TMP_DIR, 'styles.xml'))
    root = tree.getroot()

    # Page layout: A4, tight margins
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        if tag == 'page-layout-properties':
            el.set(f'{{{NS["fo"]}}}page-height', '297mm')
            el.set(f'{{{NS["fo"]}}}page-width', '210mm')
            el.set(f'{{{NS["fo"]}}}margin-top', '0.5in')
            el.set(f'{{{NS["fo"]}}}margin-bottom', '0.4in')
            el.set(f'{{{NS["fo"]}}}margin-left', '0.7in')
            el.set(f'{{{NS["fo"]}}}margin-right', '0.7in')

    # Remove footer
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        if tag == 'master-page':
            footer = el.find(f'{{{NS["style"]}}}footer')
            if footer is not None:
                el.remove(footer)

    # Configure headings: Chinese font (SimHei), VSCode blue, bold, no italic
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name in HEADING_CONFIG:
            cfg = HEADING_CONFIG[name]
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is not None:
                tp.set(f'{{{NS["style"]}}}font-name', 'SimHei')
                tp.set(f'{{{NS["style"]}}}font-name-asian', 'SimHei')
                tp.set(f'{{{NS["style"]}}}font-name-complex', 'SimHei')
                tp.set(f'{{{NS["fo"]}}}font-size', cfg['font-size'])
                tp.set(f'{{{NS["fo"]}}}font-weight', 'bold')
                tp.set(f'{{{NS["fo"]}}}color', VSCODE_BLUE.get(name, '#007ACC'))
                tp.attrib.pop(f'{{{NS["style"]}}}font-style-asian', None)
                tp.attrib.pop(f'{{{NS["style"]}}}font-style-complex', None)
                tp.attrib.pop(f'{{{NS["fo"]}}}font-style', None)
            pp = el.find(f'{{{NS["style"]}}}paragraph-properties')
            if pp is None:
                pp = ET.SubElement(el, f'{{{NS["style"]}}}paragraph-properties')
            pp.set(f'{{{NS["fo"]}}}margin-top', cfg['margin-top'])
            pp.set(f'{{{NS["fo"]}}}margin-bottom', cfg['margin-bottom'])

    # Strip italic from remaining headings (4-6)
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name.startswith('Heading_20') and name not in HEADING_CONFIG:
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is not None:
                tp.attrib.pop(f'{{{NS["style"]}}}font-style-asian', None)
                tp.attrib.pop(f'{{{NS["style"]}}}font-style-complex', None)
                tp.attrib.pop(f'{{{NS["fo"]}}}font-style', None)
                tp.set(f'{{{NS["fo"]}}}color', VSCODE_BLUE.get(name, '#007ACC'))

    # Body text: SimSun
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name == 'Text_20_body':
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is None:
                tp = ET.SubElement(el, f'{{{NS["style"]}}}text-properties')
            tp.set(f'{{{NS["style"]}}}font-name', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-asian', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-complex', 'SimSun')
            tp.set(f'{{{NS["fo"]}}}font-size', '11pt')
            pp = el.find(f'{{{NS["style"]}}}paragraph-properties')
            if pp is None:
                pp = ET.SubElement(el, f'{{{NS["style"]}}}paragraph-properties')
            pp.set(f'{{{NS["fo"]}}}margin-top', '0.03in')
            pp.set(f'{{{NS["fo"]}}}margin-bottom', '0.03in')

    # Standard style
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name == 'Standard':
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is None:
                tp = ET.SubElement(el, f'{{{NS["style"]}}}text-properties')
            tp.set(f'{{{NS["style"]}}}font-name', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-asian', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-complex', 'SimSun')
            tp.set(f'{{{NS["fo"]}}}font-size', '10.5pt')

    # Heading parent style
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name == 'Heading':
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is not None:
                tp.set(f'{{{NS["style"]}}}font-name', 'SimHei')
                tp.set(f'{{{NS["style"]}}}font-name-asian', 'SimHei')
                tp.set(f'{{{NS["style"]}}}font-name-complex', 'SimHei')
            pp = el.find(f'{{{NS["style"]}}}paragraph-properties')
            if pp is not None:
                pp.set(f'{{{NS["fo"]}}}margin-top', '0.1in')
                pp.set(f'{{{NS["fo"]}}}margin-bottom', '0.05in')

    # List style
    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        name = el.get(f'{{{NS["style"]}}}name', '')
        if name == 'List':
            tp = el.find(f'{{{NS["style"]}}}text-properties')
            if tp is None:
                tp = ET.SubElement(el, f'{{{NS["style"]}}}text-properties')
            tp.set(f'{{{NS["style"]}}}font-name', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-asian', 'SimSun')
            tp.set(f'{{{NS["style"]}}}font-name-complex', 'SimSun')
            tp.set(f'{{{NS["fo"]}}}font-size', '10.5pt')
            pp = el.find(f'{{{NS["style"]}}}paragraph-properties')
            if pp is None:
                pp = ET.SubElement(el, f'{{{NS["style"]}}}paragraph-properties')
            pp.set(f'{{{NS["fo"]}}}margin-top', '0.02in')
            pp.set(f'{{{NS["fo"]}}}margin-bottom', '0.02in')

    tree.write(os.path.join(TMP_DIR, 'styles.xml'), xml_declaration=True, encoding='UTF-8')
    print('  Done.')


def patch_content():
    tree = ET.parse(os.path.join(TMP_DIR, 'content.xml'))
    root = tree.getroot()

    for el in root.iter():
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        family = el.get(f'{{{NS["style"]}}}family', '')
        if family == 'table-cell':
            props = el.find(f'{{{NS["style"]}}}table-cell-properties')
            if props is not None:
                props.set(f'{{{NS["fo"]}}}padding', '0.03in')
        if family == 'paragraph':
            name = el.get(f'{{{NS["style"]}}}name', '')
            if 'Table' in name:
                pp = el.find(f'{{{NS["style"]}}}paragraph-properties')
                if pp is not None:
                    pp.set(f'{{{NS["fo"]}}}margin-top', '0.02in')
                    pp.set(f'{{{NS["fo"]}}}margin-bottom', '0.02in')

    tree.write(os.path.join(TMP_DIR, 'content.xml'), xml_declaration=True, encoding='UTF-8')


def repack_odt():
    print('Step 3/3: Repacking ODT...')
    os.remove(ODT_PATH)
    with zipfile.ZipFile(ODT_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('mimetype', 'application/vnd.oasis.opendocument.text', compress_type=zipfile.ZIP_STORED)
        for dirpath, dirnames, filenames in os.walk(TMP_DIR):
            for f in filenames:
                if f == 'mimetype':
                    continue
                fp = os.path.join(dirpath, f)
                arcname = os.path.relpath(fp, TMP_DIR)
                zf.write(fp, arcname)
    print('  Done.')


def main():
    register_namespaces()
    md_to_odt()
    extract_odt()
    patch_styles()
    patch_content()
    repack_odt()
    print(f'\nOutput: {ODT_PATH}')


if __name__ == '__main__':
    main()
