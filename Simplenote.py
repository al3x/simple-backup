#!/usr/bin/env python

import base64, urllib

from datetime import datetime
from google.appengine.api import urlfetch
from django.utils import simplejson

class AuthError(Exception):
  def __init__(self, email, message):
    self.email = email
    self.message = message

class ApiError(Exception):
  def __init__(self, method, message):
    self.method = email
    self.message = message

def mkdatetime(time_str):
  return datetime.strptime(time_str.split('.')[0], "%Y-%m-%d %I:%M:%S")

def get_token(email, password):
  url = 'https://simple-note.appspot.com/api/login'

  form_fields = {
    'email': email,
    'password': password
  }
  payload = base64.b64encode(urllib.urlencode(form_fields))

  result = urlfetch.fetch(url=url,
                          method=urlfetch.POST,
                          payload=payload,
                          headers={'Content-Type': 'application/x-www-form-urlencoded'})

  if (result.status_code == 200):
    return result.content.strip()
  else:
    raise AuthError(email, "Could not authenticate or bad response from server.")

def index(token):
  url = "https://simple-note.appspot.com/api/index?auth=%s" % token
  result = urlfetch.fetch(url=url,
                          method=urlfetch.GET)
  notes = simplejson.loads(result.content)

  if (result.status_code == 200):
    return notes
  else:
    raise ApiError('/index', "Exception retrieving notes from index.")

def search(query, token, max_results=10, offset_index=0):
  url = "https://simple-note.appspot.com/api/search?query=%s&results=%s&offset=%sauth=%s" % (query, max_results, offset_index, token)
  result = urlfetch.fetch(url=url,
                          method=urlfetch.GET)
  notes = simplejson.loads(result.content)

  if (result.status_code == 200):
    return notes
  else:
    raise ApiError('/search', "Exception searching notes for '%s'" % query)

def get_note(key, token):
  url = "https://simple-note.appspot.com/api/note?key=%s&auth=%s" % (key, token)
  result = urlfetch.fetch(url=url,
                          method=urlfetch.GET)

  if (result.status_code == 200):
    note = {
      'content': result.content,
      'key': key,
      'modified': mkdatetime(result.headers['note-modifydate']),
      'created': mkdatetime(result.headers['note-createdate'])
    }
    return note
  else:
    raise ApiError('/note', "Exception retrieving note with key '%s'" % key)

# also supports setting date modified; date format is not documented,
# is presumed to be GMT
def update_note(key, note_body, token):
  url = "https://simple-note.appspot.com/api/note?key=%s&auth=%s" % (key, token)
  payload = base64.b64encode(unicode(note_body))

  result = urlfetch.fetch(url=url,
                          method=urlfetch.POST,
                          payload=payload)
  note = simplejson.loads(result.content)

  if (result.status_code == 200):
    return result.content.strip()
  else:
    raise ApiError('/note', "Exception updating note with key '%s'" % key)

def create_note(note_body, token):
  url = "https://simple-note.appspot.com/api/note?auth=%s" % token
  payload = base64.b64encode(unicode(note_body))

  result = urlfetch.fetch(url=url,
                          method=urlfetch.POST,
                          payload=payload)
  note = simplejson.loads(result.content)

  if (result.status_code == 200):
    return result.content.strip()
  else:
    raise ApiError('/note', 'Exception creating note.')

def delete_note(key, token):
  url = "https://simple-note.appspot.com/api/delete?key=%s&auth=%s" % (key, token)
  result = urlfetch.fetch(url=url,
                          method=urlfetch.GET)
  note = simplejson.loads(result.content)

  if (result.status_code == 200):
    return True
  else:
    raise ApiError('/delete', "Exception deleting note with key '%s'" % key)
