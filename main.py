#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import logging
import utils
import urllib
import webapp2

from google.appengine.ext import db

class Route(db.Model):
    time_stamp = db.DateTimeProperty()
    data = db.StringProperty()

class RoutesRecorder(webapp2.RequestHandler):
    def get(self):
        routes = urllib.urlopen('http://bus.rice.edu/json/routes.php').read()
        

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello curious person!')
        self.response.write('There\'s not much here! Goto https://github.com/'
                            'rice-university/rice-bus-tracker')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/record/routes', RoutesRecorder)
], debug=True)
