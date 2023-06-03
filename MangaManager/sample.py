import json
import logging
import os
import re
import sys

from common.models import ComicInfo
from ExternalSources.MetadataSources import ScraperFactory


path = sys.argv[1]
files = os.listdir(path)
series_info = {
    'query': sys.argv[2] if len(sys.argv) > 2 else None,
    'files': {},
}

for file in files:
    series_info['files'][file] = {
        'type': file.split('.')[-1],
        'name': '.'.join(file.split('.')[:-1]),
    }

    file_parts = series_info['files'][file]['name'].split(' ')
    name_parts = []
    name_complete = False
    volume = None

    for part in file_parts:
        # parse volume
        if re.search("^v?\d+$", part):
            name_complete = True
            series_info['files'][file]['volume'] = int(part.lstrip('v'))

        # parse year
        elif re.search("^\(\d{4}\)$", part):
            name_complete = True
            series_info['files'][file]['year'] = int(part.strip('()'))

        if not name_complete and not re.search("^\(|\[\.*\)|\]$", part):
            name_parts.append(part)

    if not series_info['query']:
        series_info['query'] = ' '.join(name_parts)

query = series_info['query']
print(f'Searching for {query}')

scraper = ScraperFactory().get_scraper("AniList")
cinfo = ComicInfo()
cinfo.series = query
ret_cinfo = scraper.get_cinfo(cinfo)

if not ret_cinfo:
    print('Not found')
    sys.exit()

series_info.update(ret_cinfo.__dict__)
file_info = series_info.pop('files')
for file in sorted(file_info.keys()):
    print(file)
    for field in ['volume', 'year', 'type']:
        print(' => {}: {}'.format(field, file_info[file][field]))
print(json.dumps(series_info, indent=2))

input("Press Enter to continue")

# TODO: set volume and year and output for each file
print(ret_cinfo.to_xml())
