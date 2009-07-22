#!/usr/bin/env python

import csv, Simplenote, StringIO, wsgiref.handlers, yaml

from betterhandler import *
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class Auth(BetterHandler):
  def post(self):
    email = self.request.get('email')
    password = self.request.get('password')

    try:
      token = Simplenote.get_token(email, password)
    except Simplenote.AuthError:
      for_template = {
        'autherror': True
      }
      return self.response.out.write(template.render(self.template_path('index.html'),
                                                     for_template))
    else:
      index = Simplenote.index(token)
      note_ids = []

      for note in index:
        if note['deleted'] == False:
          note_ids.append(note['key'])

      for_template = {
        'note_count': len(index),
        'token': token,
        'note_ids': ','.join(note_ids),
      }
      return self.response.out.write(template.render(self.template_path('auth.html'),
                                                     for_template))


class Export(BetterHandler):
  def txt(self, notes):
    for_template = {
      'notes': notes
    }

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.txt')
    self.response.out.write(template.render(self.template_path('txt'),
                                            for_template))

  def csv(self, notes):
    output = StringIO.StringIO()
    writer = csv.writer(output)

    for note in notes:
      row = [note['created'].strftime("%b %d %Y %H:%M:%S"),
             note['modified'].strftime("%b %d %Y %H:%M:%S"),
             note['content']]
      writer.writerow(row)

    csvout = output.getvalue()
    output.close()

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.csv')
    self.response.out.write(csvout)

  def json(self, notes):
    for note in notes:
      note['created'] = note['created'].strftime("%b %d %Y %H:%M:%S")
      note['modified'] = note['modified'].strftime("%b %d %Y %H:%M:%S")

    output = simplejson.dumps(notes)

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.json')
    self.response.out.write(output)

  def xml(self, notes):
    for_template = {
      'notes': notes
    }

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.xml')
    self.response.out.write(template.render(self.template_path('xml'),
                                            for_template))

  def enex(self, notes):
    for_template = {
      'notes': notes
    }

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.enex')
    self.response.out.write(template.render(self.template_path('enex'),
                                            for_template))

  def yaml(self, notes):
    yamlnotes = []

    for note in notes:
      d = {}

      d[str(note['key'])] = {
        'created': note['created'],
        'modified': note['modified'],
        'content': note['content']
      }

      yamlnotes.append(d)

    output = yaml.dump(yamlnotes, default_flow_style=False)

    self.response.headers["Content-Type"] = "application/octet-stream"
    self.response.headers.add_header("Content-Disposition",
                                     'attachment; filename=simplenote-export.yaml')
    self.response.out.write(output)

  def post(self):
    token = self.request.get('token')
    format = self.request.get('format')
    note_ids = self.request.get('note_ids').split(',')

    notes = []

    for key in note_ids:
      note = Simplenote.get_note(key, token)
      notes.append(note)

    for_template = {
      'notes': notes
    }

    if format == 'txt':
      self.txt(notes)
    elif format == 'csv':
      self.csv(notes)
    elif format == 'json':
      self.json(notes)
    elif format == 'xml':
      self.xml(notes)
    elif format == 'yaml':
      self.yaml(notes)
    elif format == 'enex':
      self.enex(notes)

class FrontPage(BetterHandler):
  def get(self):
    return self.response.out.write(template.render(self.template_path('index.html'),
                                                   {}))


def main():
  application = webapp.WSGIApplication([('/', FrontPage),
                                        ('/auth', Auth),
                                        ('/export', Export)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
