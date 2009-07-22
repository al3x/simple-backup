#!/usr/bin/env python

from betterhandler import *
import Simplenote
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Auth(BetterHandler):
  def post(self):
    email = self.request.get("email")
    password = self.request.get("password")

    try:
      token = Simplenote.get_token(email, password)
    except AuthError:
      for_template = {
        'autherror': True
      }
      return self.response.out.write(template.render(self.template_path('index.html'),
                                                     for_template))
    else:
      index = Simplenote.index(token)

      for_template = {
        'body': index
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
