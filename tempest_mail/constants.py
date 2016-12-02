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
