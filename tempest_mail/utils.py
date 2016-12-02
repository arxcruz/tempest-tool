import requests


def get_html(url):
    try:
        resp = requests.get(url)
        print resp
        if resp is None:
            raise Exception("Get None as result")
    except Exception as e:
        print("Exception %s" % str(e))
        return
    return resp
