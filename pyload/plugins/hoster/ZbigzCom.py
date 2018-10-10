# -*- coding: utf-8 -*-
import random
import re
import time
import urllib.parse
from builtins import range, str

from ..internal.Hoster import Hoster
from ..internal.misc import json


class ZbigzCom(Hoster):
    __name__ = "ZbigzCom"
    __type__ = "hoster"
    __version__ = "0.03"
    __status__ = "testing"

    __pattern__ = r'https?://.+\.torrent|magnet:\?.+'
    __config__ = [("activated", "bool", "Activated", False)]

    __description__ = """Zbigz.com hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("GammaC0de", "nitzo2001[AT}yahoo[DOT]com")]

    def jquery_call(self, url, file_id, call_id, **kwargs):
        current_millis = int(time.time() * 1000)
        json_callback = "jQuery" + call_id + "_" + str(current_millis)

        urlp = urllib.parse.urlparse(url)
        get_params = kwargs.copy()
        get_params.update(urllib.parse.parse_qs(urlp.query))

        get_params['hash'] = file_id
        get_params['jsoncallback'] = json_callback
        get_params['_'] = current_millis

        jquery_data = self.load(
            urlp.scheme +
            "://" +
            urlp.netloc +
            urlp.path,
            get=get_params)

        m = re.search(r"{}\((.+?)\);".format(json_callback, jquery_data))

        return json.loads(m.group(1)) if m else None

    def sleep(self, sec):
        for _i in range(sec):
            if self.pyfile.abort:
                break
            time.sleep(1)

    def process(self, pyfile):
        self.data = self.load("http://m.zbigz.com/myfiles",
                              post={'url': pyfile.url})

        if "Error. Only premium members are able to download" in self.data:
            self.fail(_("File can be downloaded by premium users only"))

        m = re.search(r'&hash=(\w+)"', self.data)
        if m is None:
            self.fail("Hash not found")

        file_id = m.group(1)
        call_id = "".join(random.choice("0123456789") for _x in list(range(20)))

        self.pyfile.setCustomStatus("torrent")
        self.pyfile.setProgress(0)

        json_data = self.jquery_call(
            "http://m.zbigz.com/core/info.php", file_id, call_id)
        if json_data is None:
            self.fail("Unexpected jQuery response")

        if 'faultString' in json_data:
            self.fail(json_data['faultString'])

        pyfile.name = json_data['info']['name'] + \
            (".zip" if len(json_data['files']) > 1 else "")
        pyfile.size = json_data['info']['size']

        while True:
            json_data = self.jquery_call(
                "http://m.zbigz.com/core/info.php", file_id, call_id)
            if json_data is None:
                self.fail("Unexpected jQuery response")

            if 'faultString' in json_data:
                self.fail(json_data['faultString'])

            progress = int(json_data['info']['progress'])
            pyfile.setProgress(progress)

            if json_data['info']['state'] != "downloading" or progress == 100:
                break

            self.sleep(5)

        pyfile.setProgress(100)

        if len(json_data['files']) == 1:
            download_url = "http://m.zbigz.com/file/{}/0".format(file_id)

        else:
            self.data = self.load("http://m.zbigz.com/file/{}/-1".format(file_id))

            m = re.search(
                r'\'(http://\w+.zbigz.com/core/zipstate.php\?hash={}&did=(\w+)).+?\'' %
                file_id, self.data)
            if m is None:
                self.fail("Zip state URL not found")

            zip_status_url = m.group(1)
            download_id = m.group(2)

            m = re.search(
                r'\'(http://\w+.zbigz.com/z/{}/.+?)\'' %
                download_id, self.data)
            if m is None:
                self.fail("Zip download URL not found")

            download_url = m.group(1)

            self.pyfile.setCustomStatus("zip")
            self.pyfile.setProgress(0)

            while True:
                json_data = self.jquery_call(zip_status_url, file_id, call_id)
                if json_data is None:
                    self.fail("Unexpected jQuery response")

                if 'faultString' in json_data:
                    self.fail(json_data['faultString'])

                progress = int(json_data['proc'])

                self.pyfile.setProgress(progress)

                if progress == 100:
                    break

                self.sleep(5)

        self.download(download_url)

        self.load("http://m.zbigz.com/delete.php?hash={}".format(file_id))