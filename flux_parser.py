#!/usr/bin/env python

import csv
import datetime
import date_utils
import glob
import re

class FluxParser(object):
  def __init__(self, path='/mnt/remote/data/archive/flux/raw/%Y/%m/%d/%Y%m%d_%stid;_%tableid;.csv'):
    self.path = path

  def tables_for_site_on_day(self, stid, when=None):
    '''Returns a list of table IDs that have some data available on a particular day.
    If 'when' is not provided, then the default behavior is to return the list of
    tables active on the most recent available day. Otherwise, pass in a
    datetime.date object.
    '''
    sitepath = re.sub('%stid;', stid, self.path)
    sitepath = re.sub('%tableid;', '*', sitepath)

    d = when if when is not None else datetime.date.today()

    sitepath_dated = d.strftime(sitepath)
    num_table_subs = len(re.findall(r'\*', sitepath_dated))
    first_tableid_begin = sitepath_dated.find('*')
    
    tables = []
    for f in glob.glob(sitepath_dated):
      table_name_length = (len(f) - len(sitepath_dated)) / num_table_subs + 1
      tableid = f[first_tableid_begin:first_tableid_begin+table_name_length]
      tables.append(tableid)

    # Case for if today has no data because it's JUST past 0 UTC.
    if len(tables) == 0 and when is None:
      d -= datetime.timedelta(days=1)
      sitepath_dated = d.strftime(sitepath)
      num_table_subs = len(re.findall(r'\*', sitepath_dated))
      first_tableid_begin = sitepath_dated.find('*')
      for f in glob.glob(sitepath_dated):
        table_name_length = (len(f) - len(sitepath_dated)) / num_table_subs + 1
        tableid = f[first_tableid_begin:first_tableid_begin+table_name_length]
        tables.append(tableid)
    
    return tables

  def fields_in_table_on_day(self, stid, table, when=None):
    '''Returns a list of fields available in a table for a particular day.
    If 'when' is not provided, then the default behavior is to return the list of
    fields available on the most recent available day. Otherwise, pass in a
    datetime.date object.
    '''
    sitepath = re.sub('%stid;', stid, self.path)
    sitepath = re.sub('%tableid;', table, sitepath)

    d = when if when is not None else datetime.date.today()
    sitepath_dated = d.strftime(sitepath)

    fields = []
    try:
      with open(sitepath_dated, 'r') as f:
        fields = csv.reader(f).next()
    except IOError:
      if when is None:
        d -= datetime.timedelta(days=1)
        sitepath_dated = d.strftime(sitepath)
        with open(sitepath_dated, 'r') as f:
          fields = csv.reader(f).next()
      else:
        raise
    return fields

  def get_data(self, stids, tablefields, start, end):
    '''Returns data!
      stids is a sequence of stations requested.
      tablefields is a dict of arrays:
        { 'TABLEID': ['FIELD1', 'FIELD2', 'FIELD3' ..] }
        or, to indicate all fields,
        { 'TABLEID': None }
      start and end must both be datetime.datetime objects indicating the range of
        dates for which data should be retrieved.
      Return value is a dict formatted like so:
      - There is a key for each table. The value for each table is a dict.
      - In the table dicts, there is a key for each field. The value is an array.
      - There will always be "stid" and "datetime" fields, regardless of whether they were requested.
    '''
    start_fmt = start.strftime("%Y-%m-%d %H:%M:%S.%f")
    end_fmt = end.strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {}
    conv = {}
    for table, fields in tablefields.iteritems():
      tablepath = re.sub('%tableid;', table, self.path)
      if table not in data:
        data[table] = {}
        conv[table] = {}
      for stid in stids:
        sitepath = re.sub('%stid;', stid, tablepath)
        for day in date_utils.date_generator(start, end, increment='whole_days'):
          daypath = day.strftime(sitepath)
          try:
            with open(daypath, 'r') as f:
              reader = csv.DictReader(f)
              row_count = 0
              for row in reader:
                if row['datetime'] >= start_fmt and row['datetime'] <= end_fmt:
                  for field, value in row.iteritems():
                    if fields is None or field in fields + ['stid', 'datetime']:
                      if field not in conv[table]:
                        data[table][field] = [None] * row_count
                        if value is None or value == "": # If field is empty, punt on trying to figure out the type.
                          pass
                        else:
                          try:
                            x = float(value) # will raise exception if invalid conversion
                            conv[table][field] = lambda x: float(x)
                          except ValueError:
                            conv[table][field] = lambda x: x
                      try:
                        data[table][field].append(conv[table][field](value) if value != "" else None)
                      except (ValueError, KeyError):
                        data[table][field].append(value)
                  row_count += 1
          except IOError:
            pass
    return data

if __name__ == "__main__":
  parser = FluxParser()
  site = 'FLUX_VOOR'
  tables = parser.tables_for_site_on_day(site)
  for t in tables:
    print t
    for f in parser.fields_in_table_on_day(site, t):
      print "    ", f
  edate = datetime.datetime.now()
  sdate = edate - datetime.timedelta(minutes=30)
  data = parser.get_data([site], {'Time_Series_1Min': ['R_SW_in_Avg','R_SW_out_Avg','CO2','H2O']}, sdate, edate)
  for f, v in data['Time_Series_1Min'].iteritems():
    print f, len(v), v
  #for i in range(len(data['Time_Series_1Min']['datetime'])):
  #  print data['Time_Series_1Min']['stid'][i], data['Time_Series_1Min']['datetime'][i], data['Time_Series_1Min']['R_SW_in_Avg'][i]
