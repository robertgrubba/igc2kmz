#!/usr/bin/python
#
#   igc2kmz.py  IGC to Google Earth converter
#   Copyright (C) 2008  Tom Payne
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import optparse
import sys

import igc2kmz
import igc2kmz.igc
import igc2kmz.kml
import igc2kmz.photo
import igc2kmz.xc


def add_flight(option, opt, value, parser):
  parser.values.flights.append(igc2kmz.Flight(igc2kmz.igc.IGC(open(value)).track()))


def add_flight_option(option, opt, value, parser):
  setattr(parser.values.flights[-1], option.dest, value)


def add_flight_photo(option, opt, value, parser):
  parser.values.flights[-1].photos.append(igc2kmz.photo.Photo(value))


def add_flight_photo_option(option, opt, value, parser):
  setattr(parser.values.flights[-1].photos[-1], option.dest, value)


def add_flight_xc(option, opt, value, parser):
  parser.values.flights[-1].xc = igc2kmz.xc.XC(open(value))


def main(argv):
  parser = optparse.OptionParser(usage='Usage: %prog [options]', description="IGC to Google Earth converter")
  parser.add_option('-o', '--output', metavar='FILENAME')
  parser.add_option('-z', '--timezone-offset', metavar='HOURS', type='int')
  parser.add_option('-r', '--root', metavar='FILENAME', type='string', action='append', dest='roots')
  parser.add_option('--debug', action='store_true')
  group = optparse.OptionGroup(parser, 'Per-flight options')
  group.add_option('-i', '--igc', metavar='FILENAME', type='string', action='callback', callback=add_flight)
  group.add_option('-n', '--pilot-name', metavar='STRING', type='string', action='callback', callback=add_flight_option)
  group.add_option('-g', '--glider-type', metavar='STRING', type='string', action='callback', callback=add_flight_option)
  group.add_option('-c', '--color', metavar='COLOR', type='string', action='callback', callback=add_flight_option)
  group.add_option('-w', '--width', metavar='INTEGER', type='string', action='callback', callback=add_flight_option)
  group.add_option('-x', '--xc', metavar='FILENAME', type='string', action='callback', callback=add_flight_xc)
  parser.add_option_group(group)
  group = optparse.OptionGroup(parser, 'Per-photo options')
  group.add_option('-p', '--photo', metavar='FILENAME', type='string', action='callback', callback=add_flight_photo)
  group.add_option('-d', '--description', metavar='STRING', type='string', action='callback', callback=add_flight_photo_option)
  parser.add_option_group(group)
  parser.set_defaults(debug=False)
  parser.set_defaults(output='igc2kmz.kmz')
  parser.set_defaults(roots=[])
  parser.set_defaults(timezone_offset=0)
  parser.set_defaults(flights=[])
  options, args = parser.parse_args(argv)
  if len(options.flights) == 0:
    parser.error('no flights specified')
  if len(args) != 1:
    parser.error('extra arguments on command line')
  kmz = igc2kmz.flights2kmz(options.flights, roots=[igc2kmz.kml.Verbatim(open(root).read()) for root in options.roots], timezone_offset=options.timezone_offset)
  kmz.write(options.output, debug=options.debug)


if __name__ == '__main__':
  main(sys.argv)
