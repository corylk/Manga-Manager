import json
import logging
import os
import re
import shutil
import sys

from pathlib import Path

from common.models import ComicInfo
from ExternalSources.MetadataSources import ScraperFactory
from src.MetadataManager.MetadataManagerCLI import App
from src.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from src.MetadataManager.MetadataManagerLib import logger, MetadataManagerLib


class App(MetadataManagerLib):
    def __init__(self, file_paths: list[str], query=None):
        self.is_cli = True
        self.selected_files_path = file_paths
        self.query = query
        self.file_info = {}
        self.cinfo_tags.remove('Volume')

    def parse_files(self):
        for file in self.selected_files_path:
            self.file_info[file] = {}
            file_parts = Path(file).stem.split(' ')
            name_parts = []
            name_complete = False
            volume = None

            for part in file_parts:
                # parse volume
                if re.search("^v?\d+$", part):
                    name_complete = True
                    self.file_info[file]['volume'] = str(part.lstrip('v'))

                if not name_complete and not re.search("^\(|\[\.*\)|\]$", part):
                    name_parts.append(part)

            if not self.query:
                self.query = ' '.join(name_parts)

    def update_metadata(self):
        print(f'Searching for {self.query}...')

        cinfo = ComicInfo()
        cinfo.series = self.query
        ret_cinfo = app.fetch_online(cinfo)

        if not ret_cinfo:
            print('Not found')
            return

        print('\nFound series:')
        print(json.dumps(ret_cinfo.__dict__, indent=2))
        self.new_edited_cinfo = ret_cinfo

    def write_volume_tags(self):
        has_changes = False
        prints = []

        for cinfo in self.loaded_cinfo_list:
            volume = self.file_info.get(cinfo.file_path, {}).get('volume', '')

            if cinfo.volume != volume:
                prints.append(f'{cinfo.file_name} => volume {volume}')
                cinfo.volume = volume
                has_changes = True

        if prints:
            print('\nParsed volumes:')
            for p in prints:
                print(p)

        return has_changes

    def import_files(self):
        for cinfo in self.loaded_cinfo_list:
            series = cinfo.cinfo_object.series
            volume = cinfo.cinfo_object.volume
            year = cinfo.cinfo_object.year
            extension = Path(cinfo.file_name).suffix
            new_file = f'{series} {volume}{extension}'
            new_folder = f'/manga/manga_incoming/{series} ({year})'

            if not os.path.exists(new_folder):
                os.mkdir(new_folder)

            shutil.copy(cinfo.file_path, f'{new_folder}/{new_file}')

    def on_missing_rar_tools(self, exception):
        pass

    def on_processed_item(self, loaded_info: LoadedComicInfo):
        pass

    def on_manga_not_found(self, exception, series_name):
        pass

    def on_badzipfile_error(self, exception, file_path):
        pass

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):
        pass


# logger.setLevel(logging.DEBUG)
logger.trace = logger.debug
path = sys.argv[1]
files = os.listdir(path)
query = sys.argv[2] if len(sys.argv) > 2 else None
file_paths = [entry.path for entry in os.scandir(os.path.abspath(path)) if entry.is_file() and re.search("^.*\.(cbr|cbz)$", entry.name)]
app = App(file_paths=file_paths)
app.open_cinfo_list()
app.parse_files()
app.update_metadata()
has_changes = app.merge_changed_metadata(app.loaded_cinfo_list)

if not has_changes:
    print('\nNo series metadata to update')
    app.open_cinfo_list()

has_changes = app.write_volume_tags() or has_changes

if not has_changes:
    print('\nNo volume metadata to update')

input("Press Enter to continue")

app.process()
app.import_files()