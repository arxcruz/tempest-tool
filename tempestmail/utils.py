import datetime
import re
import requests

import tempestmail.constants as constants

from six.moves.urllib.parse import urljoin


def compare_tests(failures):
    ''' Detect fails covered by bugs and new'''
    covered, new = [], []
    for fail in failures:
        for test in constants.TESTS:
            if re.search(test, fail):
                covered.append(fail)
    new = [fail for fail in failures if fail not in covered]
    return covered, new


def get_html(url):
    try:
        resp = requests.get(url)
        print(resp)
        if resp is None:
            raise Exception("Get None as result")
    except Exception as e:
        print("Exception %s" % str(e))
        return
    return resp


def get_tests_results(console):
    ''' Get results of tests from console'''
    failed = [constants.TESTRE.search(l).group(1)
              for l in console.splitlines() if constants.FAILED in l]
    ok = [constants.TESTRE.search(l).group(1)
          for l in console.splitlines() if constants.OK in l]
    errors = [constants.TESTRE.search(l).group(1)
              for l in console.splitlines() if constants.ERROR in l]
    # all_skipped = [TESTRE.search(l).group(1)
    #               for l in console.splitlines() if SKIPPED in l]
    return failed, ok, errors


def get_console(job_url):
    ''' Get console page of job'''
    def _good_result(res):
        if res is None or int(res.status_code) not in (200, 404):
            return False
        else:
            return True

    def _get_date(c):
        text = c.splitlines()
        # find last line with timestamp
        for l in text[::-1]:
            if constants.TIMEST.match(l):
                return datetime.datetime.strptime(
                    constants.TIMEST.search(l).group(1),
                    "%Y-%m-%d %H:%M")
        return None

    url = urljoin(job_url, "console.html.gz")
    res = get_html(url)
    if not _good_result(res):
        print("Error getting console %s" % url)
        # Try again
        res = get_html(url)
        if not _good_result(res):
            return (None, None, None)
    elif int(res.status_code) == 404:
        url = urljoin(job_url, "console.html")
        res = get_html(url)
        if not _good_result(res):
            # Try again
            res = get_html(url)
            if not _good_result(res):
                print("Error getting console %s" % url)
                return (None, None, None)
    console = res.content.decode('utf-8')
    # with open("/tmp/console", "wt") as f:
    #    f.write(console)
    date = _get_date(console)
    return console, date, url
