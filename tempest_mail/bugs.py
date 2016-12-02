import utils
from constants import TITLE
from six.moves.html_parser import HTMLParser


class Bug(object):
    def __init__(self, url):
        self.url = url

    def bug_status(self):
        pass


class Bugzilla(Bug):
    def bug_status(self):
        ''' Return status of a bug in BZ'''
        html = utils.get_html(self.url)
        if html:
            text = html.content.decode('utf-8')
            name = TITLE.search(text).group(1) if TITLE.search(text) else ''
            h = HTMLParser()
            name = h.unescape(name)
        else:
            name = ''
        return name, None


class Launchpad(Bug):
    def bug_status(self):
        ''' Return status of a bug in Launchpad'''
        html = utils.get_html(self.url)
        if html:
            text = html.content.decode('utf-8')
            name = TITLE.search(text).group(1) if TITLE.search(text) else ''
        else:
            name = ''
        return name, None


def bug_factory(url):
    ''' Generic check bug status and name'''
    if 'bugzilla.redhat.com' in url:
        conector = Bugzilla
    elif 'bugs.launchpad.net' in url:
        conector = Launchpad
    else:
        raise ValueError('Cannot find a proper connector to {}'.format(url))
    return conector(url)


def connect_to_bug_system(url):
    connect = None
    try:
        connect = bug_factory(url)
    except ValueError as exc:
        print(exc)
    return connect
