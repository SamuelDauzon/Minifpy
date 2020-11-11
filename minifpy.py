#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This tool is used to minify and merge js/css files and is created by Samuel Dauzon (https://github.com/SamuelDauzon)
import os
import sys
import ast
import json
import argparse
import locale
import datetime
import time

watchdog_alert = ""

from slimit import minify
from csscompressor import compress
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except:
    print("Watchdog not FOUND. Auto generation on change won't works.")
    watchdog_alert = "(Not available, due to watchdog not found)"

CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

ENCODING = "utf8"
ERROR_LOG_FILE_PATH = os.path.join(CURRENT_FILE_DIR, 'minifpy_error.log')

if not ENCODING:
    ENCODING = locale.getpreferredencoding()


# Exemple minifpy_settings.json
"""
    {
        "js": {
            "minify_files": [
                {"from": "static/js/admin_feature.js", "to":"static/js/admin_feature.min.js"},
            ],
            "merge_files": [
                {"from" : ["static/js/user_feature.js", "static/js/pricing_feature.js"], "to":"static/js/public.js", "to_min": "static/js/public.min.js"}
            ]
        },
        "css" : {
            "minify_files": [
                {"from": "static/css/admin_feature.css", "to":"static/css/admin_feature.min.css"},
            ],
            "merge_files": [
                {"from" : ["static/css/user_feature.css", "static/css/pricing_feature.css"], "to":"static/css/public.css", "to_min": "static/css/public.min.css"}
            ]
        }
    }
"""

class colored_cli:
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    CHECKED = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def fail_str(message):
        return colored_cli.FAIL+message+colored_cli.ENDC

    @staticmethod
    def success_str(message):
        return colored_cli.SUCCESS+message+colored_cli.ENDC

    @staticmethod
    def warning_str(message):
        return colored_cli.WARNING+message+colored_cli.ENDC

    @staticmethod
    def info_str(message):
        return colored_cli.INFO+message+colored_cli.ENDC

    @staticmethod
    def bold_str(message):
        return colored_cli.BOLD+message+colored_cli.ENDC

    @staticmethod
    def checked_str(message):
        return colored_cli.CHECKED+message+colored_cli.ENDC


# Processors
def minify_js(js_content):
    return minify(js_content, mangle=True, mangle_toplevel=False)

def minify_css(css_content):
    return compress(css_content)

# Specific JS
def minify_js_file(minify_js, source, destination):
    if os.path.isfile(source):
        with open(destination, 'w', encoding=ENCODING) as f:
            with open(source, 'r', encoding=ENCODING) as source_file:
                js_source = source_file.read()
                js_minified = minify_js(js_source)
                f.write(js_minified)

        info = os.stat(destination)
        now = datetime.datetime.now()
        last_update_time = datetime.datetime.fromtimestamp(info.st_mtime)
        seconds_since_update = (now-last_update_time).total_seconds()
        if seconds_since_update > 10:
            print(colored_cli.fail_str("ERROR : during generation file : "+str(destination)))
            with open(os.path.join(CURRENT_FILE_DIR, 'minifpy_error.log'), 'a') as f:
                f.write("\nERROR : during generation file : "+str(destination))
        else:
            print(colored_cli.checked_str("SUCCESS : file generation : "+str(destination)))
    else:
        print(colored_cli.info_str("INFO : file does not exists : "+str(destination)))


def merge_minify_js_file(minify_js, file_path_list, to_js, to_min_js, header_path):
    merge_file(file_path_list, to_js, header_path)
    minify_js_file(minify_js, to_js, to_min_js)


# Specific CSS
def minify_css_file(minify_css, source, destination):
    if os.path.isfile(source):
        with open(destination, 'w', encoding=ENCODING) as f:
            with open(source, 'r', encoding=ENCODING) as source_file:
                css_source = source_file.read()
                css_minified = minify_css(css_source)
                f.write(css_minified)

        info = os.stat(destination)
        now = datetime.datetime.now()
        last_update_time = datetime.datetime.fromtimestamp(info.st_mtime)
        seconds_since_update = (now-last_update_time).total_seconds()
        if seconds_since_update > 10:
            print(colored_cli.fail_str("ERROR : during generation file : "+str(destination)))
            with open(os.path.join(CURRENT_FILE_DIR, 'minifpy_error.log'), 'a') as f:
                f.write("\nERROR : during generation file : "+str(destination))
        else:
            print(colored_cli.checked_str("SUCCESS : file generation : "+str(destination)))
    else:
        print(colored_cli.info_str("INFO : file does not exists : "+str(destination)))

def merge_minify_css_file(minify_css, file_path_list, to_css, to_min_css, header_path):
    merge_file(file_path_list, to_css, header_path)
    minify_css_file(minify_css, to_css, to_min_css)

# General
def merge_file(file_path_list, destination, header_path):
    with open(destination, 'w', encoding=ENCODING) as f:
        if header_path:
            with open(header_path, 'r', encoding=ENCODING) as header_file:
                f.write(header_path.read())
        for file_path in file_path_list:
            with open(file_path, 'r', encoding=ENCODING) as source_file:
                f.write(source_file.read())

def get_relative_path_file(file_path):
    if os.sep == "/":
        if file_path[0] == "/":
            file_path = file_path[(len(CURRENT_FILE_DIR)+1):]
    else:
        if file_path[:2] == "C:":
            file_path = file_path[(len(CURRENT_FILE_DIR)+1):]
        file_path = file_path.replace(os.sep, "/")
    return file_path

def get_os_path(file_path):
    if os.sep == "/":
        return file_path.replace("\\", os.sep)
    else:
        return file_path.replace("/", os.sep)

def get_extension(file_path):
    if file_path.lower().endswith('.js'):
        return ".js"
    elif file_path.lower().endswith('.css'):
        return ".css"
    return None

def minify_file_settings(settings_minify_file):
    from_file = os.path.join(CURRENT_FILE_DIR, get_os_path(settings_minify_file['from']))
    to_file = os.path.join(CURRENT_FILE_DIR, get_os_path(settings_minify_file['to']))
    if args.verbose:
        print("===== Minify to file =====")
        print(to_file)
    if get_extension(from_file) == ".js":
        minify_js_file(minify_js, from_file, to_file)
    elif get_extension(from_file) == ".css":
        minify_css_file(minify_css, from_file, to_file)

def merge_minify_file_settings(settings_merge_file):
    to_file = os.path.join(CURRENT_FILE_DIR, get_os_path(settings_merge_file['to']))
    to_min_file = os.path.join(CURRENT_FILE_DIR, get_os_path(settings_merge_file['to_min']))
    if args.verbose:
        print("===== Merge & Minify to file =====")
        print(to_min_file)
    file_path_list = []
    for file_path in settings_merge_file['from']:
        file_path_list.append(
            os.path.join(CURRENT_FILE_DIR, get_os_path(file_path))
            )
    if get_extension(to_file) == ".js":
        merge_minify_js_file(minify_js, file_path_list, to_file, to_min_file, None)
    elif get_extension(to_file) == ".css":
        merge_minify_css_file(minify_css, file_path_list, to_file, to_min_file, None)

def get_settings_file_extension(settings, extension):
    settings_minify_files = []
    settings_merge_files = []
    if extension[1:] in settings:
        extension_settings = settings[extension[1:]]
        if 'minify_files' in extension_settings:
            settings_minify_files = extension_settings['minify_files']
        if 'merge_files' in extension_settings:
            settings_merge_files = extension_settings['merge_files']

    return settings_minify_files, settings_merge_files

def get_impacted_file_for_file(file_path, settings=None):
    impacted_file_list = []
    if not settings:
        settings = get_settings()
    extension = get_extension(file_path)
    if settings and extension:
        file_path = get_relative_path_file(file_path)
        settings_minify_files, settings_merge_files = get_settings_file_extension(settings, extension)
        
        for settings_minify_file in settings_minify_files:
            if settings_minify_file['from'] == file_path:
                if not settings_minify_file['to'] in impacted_file_list:
                    impacted_file_list.append(settings_minify_file['to'])

        for settings_merge_file in settings_merge_files:
            for from_file in settings_merge_file['from']:
                if from_file == file_path:
                    if not settings_merge_file['to'] in impacted_file_list:
                        impacted_file_list.append(settings_merge_file['to'])
                    if not settings_merge_file['to_min'] in impacted_file_list:
                        impacted_file_list.append(settings_merge_file['to_min'])
    return impacted_file_list


def manage_minify_file_project(file_path, extension, settings):
    file_path = get_relative_path_file(file_path)
    settings_minify_files, settings_merge_files = get_settings_file_extension(settings, extension)

    for settings_minify_file in settings_minify_files:
        if settings_minify_file['from'] == file_path:
            minify_file_settings(settings_minify_file)

    for settings_merge_file in settings_merge_files:
        for from_file in settings_merge_file['from']:
            if from_file == file_path:
                merge_minify_file_settings(settings_merge_file)

def manage_minify_all_file_project(settings):
    for extension in ['.js', '.css']:

        settings_minify_files, settings_merge_files = get_settings_file_extension(settings, extension)

        for settings_minify_file in settings_minify_files:
            minify_file_settings(settings_minify_file)

        for settings_merge_file in settings_merge_files:
            merge_minify_file_settings(settings_merge_file)

def minify_file(file_path):
    if get_extension(file_path) == ".js":
        minify_js_file(minify_js, file_path, file_path[:-3]+".min.js")

def manage_file_changes(file_path, settings):
    if settings:
        manage_minify_file_project(file_path, get_extension(file_path), settings)
    if not settings:
        minify_file(file_path)

def check_errors():
    if os.path.isfile(ERROR_LOG_FILE_PATH):
        print(colored_cli.fail_str("ERROR : during file minifying. See log file : "+str(ERROR_LOG_FILE_PATH)))
        sys.exit(1)
    else:
        print(colored_cli.success_str("SUCCESS : Minified files with success"))

def get_settings():
    settings = None
    try:
        with open(os.path.join(CURRENT_FILE_DIR, 'minifpy_settings.json'), 'r') as f:
            settings_json = f.read()
            settings = ast.literal_eval(settings_json)
    except FileNotFoundError:
        pass
    return settings

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Minifpy to minify and merge JS/CSS files")
    parser.add_argument("-f", "--file_path", help="File to minify", default='')
    parser.add_argument("-p", "--project", action='store_true', help="Minify all project depending on minifpy_settings.json")
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("-r", "--auto_reload", action='store_true', help="Daemon to minify for changed file "+watchdog_alert)
    args = parser.parse_args()

    if watchdog_alert:
        args.auto_reload = False

    print(colored_cli.info_str("Minifpy started"))

    if os.path.isfile(ERROR_LOG_FILE_PATH):
        os.remove(ERROR_LOG_FILE_PATH)

    settings = get_settings()
    if args.file_path:
        manage_file_changes(args.file_path, settings)
    elif args.auto_reload:
        class AutoRunHandler(FileSystemEventHandler):
            def on_modified(self, event):
                print("file %s modified" % event.src_path)
                if get_extension(event.src_path) and ".min." not in event.src_path:
                    settings = get_settings()
                    manage_file_changes(event.src_path, settings)

        observer = Observer()
        observer.schedule(AutoRunHandler(), path=CURRENT_FILE_DIR, recursive=True)
        observer.start()
        try:
            while "Daemon to observe file modification":
                time.sleep(0.5)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    elif settings:
        manage_minify_all_file_project(settings)
    check_errors()
    
