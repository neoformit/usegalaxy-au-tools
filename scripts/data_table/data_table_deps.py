"""Parse tool data_table requirements from toolshed XML files."""

import csv
import requests
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup

LIMIT = 200
BASE_URL = 'https://toolshed.g2.bx.psu.edu'
CSV = Path(__file__).parent / 'eu_iuc_tools.tsv'
OUTFILE = CSV.parent / CSV.name.replace('.tsv', '+tables.csv')
TABLES_FIELD_NAME = 'Data tables'


def fetch(gxid):
    """Fetch data table requirement from toolshed XML files.

    Build URL like:
    https://toolshed.g2.bx.psu.edu/
    repos/iuc/abricate/raw-file/tip/abricate.xml

    Where ``tip`` can be replaced with a revision ID.

    >>> gxid = 'toolshed.g2.bx.psu.edu/repos/iuc/bakta/bakta'
    >>> tables = fetch(gxid)
    >>> print(tables)
    """

    data_tables = []
    base, tool_id = gxid.rsplit('/', 1)
    file_paths = _scrape_file_names(base)

    for file_path in file_paths:
        url = BASE_URL + file_path
        print("Fetching URL:", url)
        r = requests.get(url)
        xml = ET.fromstring(r.text)
        if xml.tag not in ('macros', 'tokens'):
            src_tool_id = xml.attrib.get('id')
            if not src_tool_id == tool_id:
                print(f"Skipping {url} - source tool ID '{src_tool_id}' does"
                      f" not match '{tool_id}'")
                continue
        for options in xml.findall('.//options'):
            if options.attrib.get('from_data_table'):
                data_tables.append(options.attrib['from_data_table'])

    return data_tables


def _scrape_file_names(base_path):
    """Scrape list of XML files from the repo file tip webpage."""
    file_paths = []
    tip_url = f'https://{base_path}/file/tip'
    r = requests.get(tip_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for td in soup.find_all('td', class_='filename'):
        path = td.find('a')['href']
        if path.endswith('.xml'):
            file_paths.append(path.replace('/file/', '/raw-file/'))
    return file_paths


def main():
    """Fetch data table requirements and append to tool list."""
    print("Opening CSV:", CSV)
    with open(CSV) as f:
        reader = csv.DictReader(f, delimiter='\t')
        header = reader.fieldnames + [TABLES_FIELD_NAME]
        with open(OUTFILE, 'w') as outf:
            writer = csv.DictWriter(outf, header, delimiter='\t')
            writer.writeheader()
            for i, tool in enumerate(reader):
                print(f"Fetching tool ({i}):", tool['Tool ID'])
                gxid = tool['Tool ID'].rsplit('/', 1)[0]
                tables = fetch(gxid)
                tool[TABLES_FIELD_NAME] = ', '.join(tables)
                print("Fetched tables:", tool[TABLES_FIELD_NAME])
                writer.writerow(tool)
                if i == LIMIT:
                    break


if __name__ == '__main__':
    main()
