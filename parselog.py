#!/usr/bin/env python3

import os
import sys
import re
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

# SCHEME: DATABASE_DSN = 'mysql+pymysql://<USER>:<PASS>@<HOST>/<DATABASE>'
# DATABASE_DSN = 'sqlite:///parselog' # for local sqlite database.
DATABASE_DSN = 'mysql+pymysql://root@localhost/parselog'

class LogEntry(Base):
  __tablename__ = 'entries'
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
  if len(sys.argv) < 2:
    print("Usage: ./%s <logfile>" % str(sys.argv[0]))
    sys.exit(1)
    
  filename = str(sys.argv[1])
  if os.path.isfile(filename):
    print("Reading log %s" % filename)
    main(filename)
