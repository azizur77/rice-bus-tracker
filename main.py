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

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

import datetime
import json
import logging
import utils
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import taskqueue

class Routes(db.Model):
    time_stamp = db.DateTimeProperty()
    data = db.TextProperty()

class Buses(db.Model):
    time_stamp = db.DateTimeProperty()
    data = db.TextProperty()

class RoutesRecorder(webapp2.RequestHandler):
    def post(self):
        data = urllib.urlopen('http://bus.rice.edu/json/routes.php').read()
        now_rounded = utils.roundTime(datetime.datetime.now(), roundTo=1)
        Routes(time_stamp=now_rounded, data=data).put()

class BusesRecorder(webapp2.RequestHandler):
    def post(self):
        data = urllib.urlopen('http://bus.rice.edu/json/buses.php').read()
        now_rounded = utils.roundTime(datetime.datetime.now(), roundTo=1)
        Buses(time_stamp=now_rounded, data=data).put()

class BusesHandler(webapp2.RequestHandler):
    def get(self):
        # Fetch buses data from a minute ago
        buses = None
        minute_ago = utils.roundTime(
            datetime.datetime.now() - datetime.timedelta(seconds=60),
            roundTo=1)
        retries = 0
        while not buses and retries < 10:
            buses = Buses.gql('WHERE time_stamp=:1', minute_ago).get()
            minute_ago += datetime.timedelta(seconds=1)
            retries += 1

        if buses:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(buses.data)
        else:
            self.response.out.write('Couldn\'t find data. Sorry!')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello curious person!')
        self.response.write('There\'s not much here! Goto https://github.com/'
                            'rice-university/rice-bus-tracker')

class RecorderScheduler(webapp2.RequestHandler):
    """
    Schedules 60 recording tasks per recorder every minute through cron job,
    so that a record is made every second.
    """
    def get(self):
        for i in range(60):
            for url in ['/record/routes', '/record/buses']:
                taskqueue.add(url=url,
                              countdown=i)

        logging.info('Enqueued 60 record tasks.')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/buses', BusesHandler),
    ('/record/routes', RoutesRecorder),
    ('/record/buses', BusesRecorder),
    ('/tasks/recorder', RecorderScheduler)
], debug=True)
