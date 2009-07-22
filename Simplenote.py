#!/usr/bin/env python

import base64, urllib

from google.appengine.api import urlfetch
from django.utils import simplejson

class AuthError(Exception):
  pass

def get_token(email, password):
  form_fields = {
    'email': email,
    'password': password
  }
  form_data = base64.b64encode(urllib.urlencode(form_fields))

  result = urlfetch.fetch(url='https://simple-note.appspot.com/api/login',
                          method=urlfetch.POST,
                          payload=form_data,
                          headers={'Content-Type': 'application/x-www-form-urlencoded'})

  if (result.status_code is not 200):
    raise AuthError
  else:
    return result.content.strip()


def index(token):
  url = "https://simple-note.appspot.com/api/index?auth=%s" % token
  result = urlfetch.fetch(url=url,
                          method=urlfetch.GET)
  notes = simplejson.loads(result.content)
  return notes

