"""Parse tool data_table requirements from toolshed XML files."""

import requests
from xml.etree import ElementTree as ET


def fetch_data_tables(gxid):
    """Fetch data table requirement from toolshed XML files.

    Build URL like:
    https://toolshed.g2.bx.psu.edu/
    repos/iuc/abricate/raw-file/tip/abricate.xml

    Where ``tip`` can be replaced with a revision ID.
    """

    base, xml_name = gxid.rsplit('/', 1)
    url = f'https://{base}/raw-file/tip/{xml_name}.xml'
    r = requests.get(url)
    xml = ET.fromstring(r.text)
    data_tables = []
    for options in xml.findall('.//options'):
        if options.attrib['from_data_table']:
            data_tables.append(options.attrib['from_data_table'])

    return data_tables


if __name__ == '__main__':
    gxid = 'toolshed.g2.bx.psu.edu/repos/iuc/bakta/bakta'
    tables = fetch_data_tables(gxid)
    print("Tables:")
    print(tables)
