# -*- coding: UTF-8 -*-

import requests
import fnmatch
import logging
import yaml
import logging.config
import os

log = logging.getLogger("main_logger")


def setup_logging(default_path='config.yaml', default_level=logging.INFO):
    path = default_path
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)



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
        print "%-8d samples in %s" % (len(self.sample[filename]), filename)

    def load_from_dir(self, dirname, filename_pattern):
        for test_file in all_files(dirname, filename_pattern):
            self.load_from_file(test_file)

    def get_loaded_samples(self):
        return self.sample

    def sample_iter(self):
        for smpl_fn, smpl_lns in self.sample.iteritems():
            for smpl_ln in smpl_lns:
                yield smpl_fn, smpl_ln[0], smpl_ln[1]


class CSampleRunner(object):
    def __init__(self):
        self.url_sample = None
        self.url_payload = None

    def run(self):
        pass

    def set_url_sample(self, url_sample):
        self.url_sample = url_sample

    def set_url_payload(self, url_payload):
        self.url_payload = url_payload

    def generate_url(self):
        if not self.url_payload:
            print
        for templ in self.url_sample.sample_iter():
            for pld in self.url_payload.sample_iter():
                yield templ[2].replace("{{.payload}}", pld[2])

    def header_test(self):
        pass

    def body_test(self):
        pass


if __name__ == "__main__":
    setup_logging("./log_conf.yaml")
    sqli_samples = CSample()
    sqli_samples.load_from_dir("./data", "sqli*")

    url_tpl = CSample()
    url_tpl.load_from_file("./data/url-sample.tpl")

    runner = CSampleRunner()
    runner.set_url_sample(url_tpl)
    runner.set_url_payload(sqli_samples)

    for test_url in runner.generate_url():
        try:
            r = requests.get(test_url, headers={"User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"})
            if r.status_code == 200:
                print "\n%s\nstatus code: %d\n" % (test_url, r.status_code)
            else:
                print "\n%s\nstatus code: %d blocked.\n" % (test_url, r.status_code)
        except requests.exceptions.ConnectionError, e:
            print "\n%s\nerror: %s\n" % (test_url, e)

