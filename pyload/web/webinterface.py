#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#   Copyright(c) 2009-2017 pyLoad Team
#   http://www.pyload.org
#
#   This file is part of pyLoad.
#   pyLoad is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   Subjected to the terms and conditions in LICENSE
#
#   @author: RaNaN
###############################################################################

from __future__ import absolute_import
import sys

from os.path import join, abspath, dirname, exists

PROJECT_DIR = abspath(dirname(__file__))
PYLOAD_DIR = abspath(join(PROJECT_DIR, "..", ".."))

import bottle
from bottle import run, app

from .middlewares import StripPathMiddleware, PrefixMiddleware

SETUP = None
PYLOAD = None

from . import ServerThread

if not ServerThread.core:
    if ServerThread.setup:
        SETUP = ServerThread.setup
        config = SETUP.config
    else:
        raise Exception("Could not access pyLoad Core")
else:
    PYLOAD = ServerThread.core.api
    config = ServerThread.core.config

from pyload.utils.JsEngine import JsEngine
JS = JsEngine()

TEMPLATE = config.get('webUI', 'template')
DL_ROOT = config.get('general', 'download_folder')
PREFIX = config.get('webUI', 'prefix')

if PREFIX:
    PREFIX = PREFIX.rstrip("/")
    if PREFIX and not PREFIX.startswith("/"):
        PREFIX = "/" + PREFIX

APP_PATH = "app"
UNAVAILALBE = True

# webUI build is available
if exists(join(PROJECT_DIR, "app", "components")) and exists(join(PROJECT_DIR, ".tmp")) and config.get('webUI', 'develop'):
    UNAVAILALBE = False
elif exists(join(PROJECT_DIR, "dist", "index.html")):
    APP_PATH = "dist"
    UNAVAILALBE = False

DEBUG = config.get("general", "debug_mode") or "-d" in sys.argv or "--debug" in sys.argv
bottle.debug(DEBUG)


# Middlewares
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': False,
    'session.data_dir': './tmp',
    'session.auto': False
}

session = SessionMiddleware(app(), session_opts)
web = StripPathMiddleware(session)

if PREFIX:
    web = PrefixMiddleware(web, prefix=PREFIX)

from . import api_app
from . import cnl_app
from . import setup_app
# Last routes to register,
from . import pyload_app

# Server Adapter
def run_server(host, port, server):
    run(app=web, host=host, port=port, quiet=True, server=server)


if __name__ == "__main__":
    run(app=web, port=8001)