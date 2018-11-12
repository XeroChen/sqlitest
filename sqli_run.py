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


class CSample(object):
    def __init__(self):
        # self.loaded = []
        self.sample = dict()

    def load_from_file(self, filename):
        sf = open(filename, 'r')
        line_num = 0
        for line in sf:
            line_num += 1
            line = line.partition("#")[0].partition("--")[0].strip()

            if line == "" or line.startswith("#") or line.startswith("--"):
                continue

            if filename not in self.sample:
                self.sample[filename] = [(line_num, line)]
            else:
                self.sample[filename].append((line_num, line))

    def load_from_dir(self, dirname, filename_pattern):
        for test_file in all_files(dirname, filename_pattern):
            self.load_from_file(test_file)

    # def sample_iter(self):
    #     for smpl_fn, smpl_ln in self.sample:
    #         yield smpl_fn, smpl_ln[0], smpl_ln[1]


class CHttpRunner(object):
    def __init__(self):
        self.url_param = ""

    def run(self):
        pass

    def set_url_param(self):
        pass

    def url_test(self, url_sample, payload_sample):
        pass

    def header_test(self):
        pass

    def body_test(self):
        pass


if __name__ == "__main__":
    sqli_samples = CSample()
    sqli_samples.load_from_dir("D:\code\github.com\libinjection\data", "sqli*")
    for smpl_fn,  smpl_lns in sqli_samples.sample.iteritems():
        print "%d samples in %s loaded." % (len(smpl_lns), smpl_fn)
