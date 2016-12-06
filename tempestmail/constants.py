import re

HREF = re.compile('href="([^"]+)"')
JOBRE = re.compile('[a-z0-9]{7}/')
TESTRE = re.compile('(tempest\.[^ \(\)]+)')
TIMEST = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}\.\d+ \|')
TITLE = re.compile('<title>(.*?)</title>')

FAILED = "... FAILED"
OK = "... ok"
ERROR = "... ERROR"
SKIPPED = "... SKIPPED"

TESTS = {
    'tempest.scenario.test_volume_boot_pattern.*':
        'http://bugzilla.redhat.com/1272289',
    'tempest.api.identity.*v3.*':
        'https://bugzilla.redhat.com/1266947',
    '.*test_external_network_visibility':
        'https://bugs.launchpad.net/tripleo/+bug/1577769',
}
