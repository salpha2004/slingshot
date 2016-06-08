#!/usr/bin/python
import shutil
import subprocess
from collections import namedtuple
import os
import optparse
from operator import itemgetter
import sys
import re
import random
import logging
import logging.config
import MySQLdb
from loader import CtLoader
from t_exceptions import FunctionNotInDB
from t_exceptions import XMLNotValid
from tc_generator import TcGenerator
from util import get_path
from testcase_factory import TcFactory
from setting_factory import SettingFactory
from ..db.db_connector import DbConnector


def parse_arguments():
  """ Specify and parse options for slingshot. """
  p1 = subprocess.Popen("nproc", stdout=subprocess.PIPE)
  out = p1.communicate()[0]
  parser = optparse.OptionParser()
  parser.add_option('-u', '--user', dest='db_user', default='slingshot',
          help='database access username (default: slingshot)')
  parser.add_option('-p', '--password', dest='db_passwd', default='slingshot',
          help='database access password (default: slingshot)')
  parser.add_option('-s', '--server', dest='db_host', default='localhost',
          help='database server machine (default: localhost)')
  parser.add_option('-d', '--database', dest='db_name', default='slingshot',
          help='database name (default: slingshot)')
  parser.add_option('-w', '--work_directory', dest='work_dir', default='tmp',
          help='Slingshot work directory (default: \'tmp\' in current directory)')
  parser.add_option('-j', '--jobs', dest='jobs', default=int(out),
          help='number of processing units to parallelize test'
            'case generation process (default: output of \'nproc\')')
  (opts, _) = parser.parse_args()
  return opts

def make(work_dir, jobs):
  # go to working directory to invoke "make".
  os.chdir (work_dir)
  p1 = subprocess.Popen(["make", "-j", str(jobs)], stderr=subprocess.PIPE)
  p2 = subprocess.Popen(["tee", os.path.join("makefile.log")],
    stdin=p1.stderr)
  p1.stderr.close()
  p2.communicate()

def main():
  """ Initialize, generate test cases, finally make them. """

  # Create a logger and load its config
  logging.config.fileConfig(get_path('bin/logging.conf'))
  logger = logging.getLogger(__name__)

  # parse options
  opts = parse_arguments()
  work_dir = os.path.join(os.getcwd(), opts.work_dir)
  db_connection = MySQLdb.connect(host=opts.db_host, user=opts.db_user,
              passwd=opts.db_passwd, db=opts.db_name)
  db_connection.autocommit(True)

  # Create a fresh work directory
  if os.path.exists(work_dir):
    shutil.rmtree(work_dir)
  logger.info("Create a fresh directory to work in.")
  os.makedirs(work_dir)
  
  db = DbConnector(db_connection)
  tc_factory = TcFactory(work_dir)
  s_factory = SettingFactory(db)
  tcg = TcGenerator(db, tc_factory, s_factory, work_dir,
    batch_size=opts.jobs)

  tcg.initialize_testcase_generation()
  function_records = namedtuple('Function', ['id', 'name', 'tcl', 'header',
      'number_of_parameters', 'c_types', 'signature', 'return_type'])
  functions = db.get_functions(function_records)
  for function in functions: # 'function' is a namedtuple representing a function.
    tcg.load_function(function)
    while tcg.testcases_left():
      tcg.generate()
  tcg.finalize_testcase_generation()
  print "Test cases generation done. Now making test application...\n"
  make(work_dir, jobs=opts.jobs)
