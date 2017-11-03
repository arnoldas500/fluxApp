#!/usr/bin/env

import datetime



def date_generator(sdate, edate, increment=datetime.timedelta(seconds=1)):
  """Generates dates over a range.

  @param sdate: A datetime object indicating the start of the range.

  @param edate: A datetime object indicating the inclusive end of the range.

  @param increment:
    - If this is a datetime.timedelta object, dates are generated that step from
      sdate to edate with an increment of the passed increment.
    - If this is the string "whole_days", dates are generated that represent
      whole days that cover the interval.

  @return: A generated datetime object.
  """
  if increment == "whole_days":
    increment = datetime.timedelta(days=1)
    sdate = datetime.datetime(sdate.year, sdate.month, sdate.day)
  date = sdate
  while date <= edate:
    yield date
    date += increment



epoch = datetime.datetime.utcfromtimestamp(0)
def datetime_to_epoch(dt):
  return (dt - epoch).total_seconds()



if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description="Print a range of dates at a regular interval.")
  parser.add_argument("--sdate", required=True, help="The start date in %Y-%m-%d %H:%M:%S format")
  parser.add_argument("--edate", required=True, help="The end date in %Y-%m-%d %H:%M:%S format")
  parser.add_argument("--interval", required=True, type=int, help="The interval in seconds")
  parser.add_argument("--output_format", default="%Y-%m-%d %H:%M:%S", help="The output format, run through strftime")
  
  args = parser.parse_args()
  
  try:
    sdate = datetime.datetime.strptime(args.sdate, "%Y-%m-%d %H:%M:%S")
    edate = datetime.datetime.strptime(args.edate, "%Y-%m-%d %H:%M:%S")
  except:
    print("* Invalid date format! Use --help to get help.")
    exit(1)
  
  try:
    interval = datetime.timedelta(seconds=args.interval)
  except:
    print("* Interval should be the number of seconds.")
    exit(1)

  for date in date_generator(sdate, edate, interval):
    print(date.strftime(args.output_format))
