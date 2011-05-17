"""Super simple command line calculator"""
from math import *
import sys

try:
  result = input("calculator")
  print "result = ", result
except:
  print "error occurred...", sys.exc_info()[1]