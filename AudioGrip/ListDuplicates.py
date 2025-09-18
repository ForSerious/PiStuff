import globals as g
import xml.etree.ElementTree as ET

if __name__ == '__main__':
    tree = ET.parse(g.STATSPATH)
    root = tree.getroot()
    files = root.findall('File')
    have = {}
    duplicates = []
    for file in files:
        key = str(file.find('Uri').text[28:]).lower()
        found = have.get(key, False)
        have[key] = True
        if found:
            duplicates.append(key)
    for item in duplicates:
        print(item)