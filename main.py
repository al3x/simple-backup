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

import base64, urllib

from betterhandler import *
import wsgiref.handlers

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Auth(BetterHandler):
  def get_token(self, email, password):
    form_fields = {
      'email': email,
      'password': password
    }
    form_data = base64.b64encode(urllib.urlencode(form_fields))

    result = urlfetch.fetch(url='https://simple-note.appspot.com/api/login',
                            method=urlfetch.POST,
                            payload=form_data,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})

    return result

  def post(self):
    email = self.request.get("email")
    password = self.request.get("password")
    result = self.get_token(email, password)

    if (result.status_code is not 200):
      for_template = {
        'autherror': True
      }
      return self.response.out.write(template.render(self.template_path('index.html'), for_template))
    else:
      token = result.content.strip()

      for_template = {
        'token': token
      }
      return self.response.out.write(template.render(self.template_path('auth.html'), for_template))

class FrontPage(BetterHandler):
  def get(self):
    return self.response.out.write(template.render(self.template_path('index.html'), {}))

def main():
  application = webapp.WSGIApplication([('/', FrontPage),
                                        (r'/auth', Auth)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
