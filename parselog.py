#!/usr/bin/env python3

import os
import sys
import re
import argparse
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# colors. yay!
from colorama import init
from colorama import Fore, Back, Style
init()

Base = declarative_base()

logfile = None
table = 'entries'
mysql_user = 'root'
mysql_password = ''
mysql_host = 'localhost'
mysql_port = '3306'
mysql_database = 'parselog'

def parse_arguments():
  global table, logfile, mysql_user, mysql_password, mysql_port, mysql_database

  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--table', dest='table', action='store', help="Set the MySQL table to create and store the entries in (default: entries)")
  parser.add_argument('-s', '--server', dest='server', action='store', help="Set MySQL host (default: localhost)")
  parser.add_argument('-u', '--user', dest='user', action='store', help="Set MySQL user (default: root)")
  parser.add_argument('-p', '--pass', dest='password', action='store', help="Set MySQL password (default: none)")
  parser.add_argument('-P', '--port', dest='port', action='store', help="Set MySQL port (default: 3306)")
  parser.add_argument('-d', '--database', dest='database', action='store', help="Set MySQL database (default: parselog)")
  parser.add_argument('logfile', help='the log file')
  args = parser.parse_args()

  logfile = args.logfile
  if args.table:
    table = args.table

  if args.server:
    mysql_host = args.server
  if args.port:
    mysql_port = args.port
  if args.user:
    mysql_user = args.user
  if args.password:
    mysql_password = args.password
  if args.database:
    mysql_database = args.database

parse_arguments()

# SCHEME: DATABASE_DSN = 'mysql+pymysql://<USER>:<PASS>@<HOST>/<DATABASE>'
# DATABASE_DSN = 'sqlite:///parselog' # for local sqlite database.
DATABASE_DSN = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (mysql_user, mysql_password, mysql_host, mysql_port, mysql_database)

class LogEntry(Base):
  __tablename__ = table
  id = Column(Integer, primary_key=True)
  time_stamp = Column(DateTime)
  auth_user = Column(String(255))
  src_ip = Column(String(16))
  status_code = Column(Integer)
  req_line = Column(String(255))
  categories = Column(String(255))
  rep_level = Column(String(255))
  media_type = Column(String(100))
  bytes_to_client = Column(Integer)
  bytes_from_client = Column(Integer)
  user_agent = Column(String(255))
  virus_name = Column(String(255))
  block_res = Column(String(255))
  application_name = Column(String(255))

def connect_database():
  engine = create_engine(DATABASE_DSN)
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all(engine)
  return Session()

def parse_time_stamp(time_stamp):
  return datetime.strptime(time_stamp, '%d/%b/%Y:%H:%M:%S %z')

def main(filename):
  session = connect_database()

  #time_stamp "auth_user" src_ip status_code "req_line" "categories" "rep_level" "media_type" bytes_to_client bytes_from_client "user_agent" "virus_name" "block_res" "application_name"
  pattern = '\[(?P<time_stamp>.*)\] "(?P<auth_user>.*)" (?P<src_ip>.*) (?P<status_code>\d\d\d) "(?P<req_line>.*)" "(?P<categories>.*)" "(?P<rep_level>.*)" "(?P<media_type>.*)" (?P<bytes_to_client>\d+) (?P<bytes_from_client>\d+) "(?P<user_agent>.*)" "(?P<virus_name>.*)" "(?P<block_res>.*)" "(?P<application_name>.*)"'
  matcher = re.compile(pattern)

  file = open(filename, 'r')

  try:
    lines = 0
    matches = 0

    for line in file:
      lines = lines + 1
      match = re.search(pattern, line, re.IGNORECASE)

      if match:
        matches = matches + 1
        entry = LogEntry()
        entry.time_stamp = parse_time_stamp(match.group('time_stamp'))
        entry.auth_user = match.group('auth_user')
        entry.src_ip = match.group('src_ip')
        entry.status_code = match.group('status_code')
        entry.req_line = match.group('req_line')
        entry.categories = match.group('categories')
        entry.rep_level = match.group('rep_level')
        entry.media_type = match.group('media_type')
        entry.bytes_to_client = match.group('bytes_to_client')
        entry.bytes_from_client = match.group('bytes_from_client')
        entry.user_agent = match.group('user_agent')
        entry.virus_name = match.group('virus_name')
        entry.block_res = match.group('block_res')
        entry.application_name = match.group('application_name')

        session.add(entry)
      else:
        print(Fore.YELLOW + "Ignoring line: %s" % line.strip() + Fore.RESET)

    session.commit()

    print("Log contained %d lines, from which %d were written to database." % (lines, matches))
  except ValueError as e:
    print(Fore.RED + "Misformatted log file:")
    print(e.args)
    print(Fore.RED + "NO entries from log file were written to database!" + Fore.RESET)

if __name__ == '__main__':
  if os.path.isfile(logfile):
    print("Reading log %s" % logfile)
    main(logfile)
