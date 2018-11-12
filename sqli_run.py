# -*- coding: UTF-8 -*-

import requests

import os
import fnmatch


def all_files(root, patterns='*', single_level=False, yield_folders=False):
    # Expand patterns from semicolon-separated string to list
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break


class SQLiSample(object):
    def __init__(self):
        self.loaded = ""
        self.sample_string = []

    def load_from_file(self, filename):
        sf = open(filename, 'r')
        line_num = 1
        for line in sf:

            if line.strip().startswith("#"):
                continue
            self.sample_string.append((filename, line_num, line))
            line_num += 1

    def load_from_dir(self, dirname, filename_pattern):
        for test_file in all_files(dirname, filename_pattern):
            self.load_from_file(test_file)

    def sample_iter(self):
        for smpl in self.sample_string:
            yield smpl


class CSampleFixture(object):
    def __init__(self):
        pass

    def run(self):
        pass

    def run_sample(self, sample_obj):
        # requests.get()

    def header_test(self):
        pass

    def body_test(self):
        pass


def run_test():
    uri = "http://192.168.25.10"
    method = "GET"
    requests.Request()