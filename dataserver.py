#!/usr/bin/env python

from flask import Flask, abort, request, jsonify, make_response, Response
import datetime
import dateutil.parser
import flux_parser
import math
import numpy
import re
import date_utils

app = Flask(__name__)

@app.errorhandler(400)
def not_found(error):
  return make_error('Bad request', 400)

@app.errorhandler(404)
def not_found(error):
  return make_error('Not found', 404)

def make_error(text, code):
  return make_response(jsonify({'response': text}), code)

class HttpError(Exception):
  def __init__(self, message, http_code):
    self.message = message
    self.http_code = http_code
  def __str__(self):
    return "Code {code} - {message}".format(code=self.http_code, message=self.message)



def parse_date(in_date):
  if in_date == 'latest':
    return 'latest'
  elif type(in_date) is str or type(in_date) is unicode:
    return dateutil.parser.parse(in_date)
  elif type(in_date) is float or type(in_date) is int or type(in_date) is long:
    return datetime.datetime.utcfromtimestamp(in_date / 1000)
  raise ValueError



def parse_dates(in_start, in_end):
  try:
    start = parse_date(in_start)
  except:
    raise HttpError("Could not parse 'start' - try 'start': '20151124T2000' or 'start': 1448395200000 or 'start': 'latest'", 400)
  try:
    end = parse_date(in_end)
  except:
    raise HttpError("Could not parse 'end' - try 'end': '20151124T2100' or 'end': 1448398800000 or 'end': 'latest'", 400)
  if start != 'latest' and end != 'latest':
    range = end - start
    if range.total_seconds() < 0:
      raise HttpError("'end' comes before 'start' - try again.", 400)
    if range > datetime.timedelta(days=60):
      raise HttpError("Date range is limited to 60 days.", 400)
  return (start, end)



@app.route("/fluxbeta/tables/<stid>", methods=['GET'])
@app.route("/fluxbeta/tables/<stid>/<asof>", methods=['GET'])
def fluxbeta_tables(stid, asof=None):
  if asof is not None:
    try:
      asof = parse_date(asof)
    except:
      return HttpError("Could not understand date format. Try something like '20170319T124500' or a Unix timestamp (in milliseconds).")
  if not re.match(r'^FLUX_....$', stid):
    return HttpError("Flux station names must begin with FLUX_.")
  parser = flux_parser.FluxParser()
  tables = parser.tables_for_site_on_day(stid, asof.date() if asof is not None else None)
  ret_data = {
    'success': True,
    'response': tables
  }
  return jsonify(ret_data)



@app.route("/fluxbeta/fields/<stid>/<tableid>", methods=['GET'])
@app.route("/fluxbeta/fields/<stid>/<tableid>/<asof>", methods=['GET'])
def fluxbeta_fields(stid, tableid, asof=None):
  if asof is not None:
    try:
      asof = parse_date(asof)
    except:
      return HttpError("Could not understand date format. Try something like '20170319T124500' or a Unix timestamp (in milliseconds), or omit the date.")
  if not re.match(r'^FLUX_....$', stid):
    return HttpError("Flux station names must begin with FLUX_.")
  if len(tableid) > 200 or not re.match(r'^[A-Za-z0-9_]*$', tableid):
    return HttpError("Table ID is invalid.")
  parser = flux_parser.FluxParser()
  tables = parser.tables_for_site_on_day(stid, asof.date() if asof is not None else None)
  if tableid not in tables:
    return HttpError("Table ID is not found.")
  available_fields = parser.fields_in_table_on_day(stid, tableid, asof.date() if asof is not None else None)
  ret_data = {
    'success': True,
    'response': available_fields
  }
  return jsonify(ret_data)



@app.route("/fluxbeta/data/<stid>/<tableid>/<fields>/<start>/<end>", methods=['GET'])
def fluxbeta_data(stid, tableid, fields, start, end):
  start, end = parse_dates(start, end)
  if start == "latest" or end == "latest":
    return HttpError("'latest' keyword not implemented for flux data.")
  if not re.match(r'^FLUX_....$', stid):
    return HttpError("Flux station names must begin with FLUX_.")
  if len(tableid) > 200 or not re.match(r'^[A-Za-z0-9_]*$', tableid):
    return HttpError("Table ID is invalid.")
  parser = flux_parser.FluxParser()
  tables = parser.tables_for_site_on_day(stid, end.date())
  if tableid not in tables:
    return HttpError("Table ID is not found.")
  available_fields = parser.fields_in_table_on_day(stid, tableid, end.date())
  fields = fields.split(",")
  for f in fields:
    if f not in available_fields:
      return HttpError("Field {} is not available for the entire range.".format(f))
  data = parser.get_data([stid], { tableid: fields }, start, end)
  for field, values in data[tableid].iteritems():
    for i, v in enumerate(values):
      if v is not None and not isinstance(v, basestring) and math.isnan(v):
        values[i] = None
  ret_data = {
    'success': True,
    'response': data[tableid]
  }
  return jsonify(ret_data)


if __name__ == "__main__":
  app.debug = True
  app.run(host="0.0.0.0")
