# -*- coding: utf-8 -*-
# @author: mkaay

from builtins import _, object, str
from threading import Thread
from traceback import print_exc


class BackendBase(Thread):
    def __init__(self, manager):
        Thread.__init__(self)
        self.m = manager
        self.pyload = manager.pyload
        self.enabled = True
        self.running = False

    def run(self):
        self.running = True
        try:
            self.serve()
        except Exception as e:
            self.pyload.log.error(_("Remote backend error: {}").format(e))
            if self.pyload.debug:
                print_exc()
        finally:
            self.running = False

    def setup(self, host, port):
        pass

    def checkDeps(self):
        return True

    def serve(self):
        pass

    def shutdown(self):
        pass

    def stop(self):
        self.enabled = False  # set flag and call shutdowm message, so thread can react
        self.shutdown()


class RemoteManager(object):
    available = []

    def __init__(self, core):
        self.pyload = core
        self.backends = []

        if self.pyload.remote:
            self.available.append("ThriftBackend")
#        else:
#            self.available.append("SocketBackend")

    def startBackends(self):
        host = self.pyload.config["remote"]["listenaddr"]
        port = self.pyload.config["remote"]["port"]

        for b in self.available:
            klass = getattr(
                __import__(
                    "pyload.remote.{}".format(
                        b), globals(), locals(), [b], -1), b)
            backend = klass(self)
            if not backend.checkDeps():
                continue
            try:
                backend.setup(host, port)
                self.pyload.log.info(_("Starting {name}: {addr}:{port}").format(
                    **{"name": b, "addr": host, "port": port}))
            except Exception as e:
                self.pyload.log.error(_("Failed loading backend {name} | {error}").format(
                    **{"name": b, "error": str(e)}))
                if self.pyload.debug:
                    print_exc()
            else:
                backend.start()
                self.backends.append(backend)

            port += 1
