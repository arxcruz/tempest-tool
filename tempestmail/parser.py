import requests


class ParserJob(object):
    def __index__(self, job):
        self.job = job

    def get_html(url):
        try:
            resp = requests.get(url)
            if resp is None:
                raise Exception("Get None as result")
        except Exception as e:
            print("Exception %s" % str(e))
            return
        return resp
