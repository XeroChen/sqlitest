# -*- coding: UTF-8 -*-

import fnmatch
import logging
import yaml
import logging.config
import os
import sys
import getopt


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


class CRunner(object):
    def __init__(self):
        self.sample = None
        self.payload = None
        self.target = None

    def run(self):
        pass

    def set_sample(self, sample):
        self.sample = sample

    def set_payload(self, payload):
        self.payload = payload

    def set_target(self, target):
        self.target = target


class SQLiURLRunner(CRunner):
    def __init__(self):
        for base in self.__class__.__bases__:
            if hasattr(base, '__init__'):
                base.__init__(self)

    def run(self):
        import requests
        log20x = logging.getLogger("log20x")
        log40x = logging.getLogger("log40x")
        err_log = logging.getLogger("err_logger")
        for test_url in self._generate_url():
            try:
                # print "testing: %s" % test_url
                r = requests.get(test_url, headers={
                    "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"})
                if r.status_code / 200 == 1:
                    log20x.info("[%d] %s" % (r.status_code, test_url))
                elif r.status_code >= 500:
                    err_log.error("[%d] %s" % (r.status_code, test_url))
                else:
                    log40x.info("[%d] %s" % (r.status_code, test_url))

            except requests.exceptions.ConnectionError, e:
                err_log.error("[%s] %s" % (e, test_url))

    def set_sample(self, url_sample):
        self.sample = url_sample

    def set_payload(self, url_payload):
        self.payload = url_payload

    def set_target(self, target):
        self.target = target

    def _generate_url(self):
        if not self.payload:
            print "No payloads found."
            sys.exit(9)
        for templ in self.sample.sample_iter():
            for pld in self.payload.sample_iter():
                yield templ[2].replace("{{.target}}", self.target).replace("{{.payload}}", pld[2])


def usage():
    print "Usage: %s -t <IP or DomainName>" % sys.argv[0]
    print '''This will load SQL injection payloads from ./data directory (files named "sqli-*") \
        and url templates from ./data/url-sample.tpl'''


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:", ["help", "target="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    target = ""

    for opt, param in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-t", "--target"):
            target = param
        else:
            assert False, "unknown option %s" % opt

    if not target:
        print "No target specified. exit"
        sys.exit(9)

    sqli_samples = CSample()
    sqli_samples.load_from_dir("./data", "sqli*")

    url_tpl = CSample()
    url_tpl.load_from_file("./data/url-sample.tpl")

    runner = SQLiURLRunner()
    runner.set_sample(url_tpl)
    runner.set_payload(sqli_samples)
    runner.set_target(target)
    runner.run()


if __name__ == "__main__":
    setup_logging("./log_conf.yaml")
    if len(sys.argv) < 2:
        usage()
        exit(1)
    main()



