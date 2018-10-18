#   igc2kmz photo functions
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


import datetime
import os.path
import urllib2
import urlparse

from coord import Coord
import exif


class Photo(object):

    def __init__(self, url, path=None):
        self.url = url
        components = urlparse.urlparse(self.url)
        self.name = os.path.splitext(os.path.basename(components.path))[0]
        if path:
		try:
			file = open(path)
		except:
			file =urllib2.urlopen(path.replace('/var/www/','http://files.leonardo.pgxc.pl/'))
        else:
            file = urllib2.urlopen(self.url) 
            if file.info().typeheader != 'image/jpeg':
                raise RuntimeError, '%s: not an image/jpeg' % self.url
        self.jpeg = exif.JPEG(file)
        if 'DateTimeOriginal' in self.jpeg.exif:
            self.dt = exif.parse_datetime(self.jpeg.exif['DateTimeOriginal'])
        elif 'DateTime' in self.jpeg.exif:
            self.dt = exif.parse_datetime(self.jpeg.exif['DateTime'])
        else:
            self.dt = datetime.datetime(2000, 1, 1)
        if 'GPSVersionID' in self.jpeg.exif:
            lat = exif.parse_angle(self.jpeg.exif['GPSLatitude'])
            if self.jpeg.exif['GPSLatitudeRef'] == 'S\0':
                lat = -lat
            lon = exif.parse_angle(self.jpeg.exif['GPSLongitude'])
            if self.jpeg.exif['GPSLongitudeRef'] == 'W\0':
                lon = -lon
            if 'GPSAltitude' in self.jpeg.exif:
                gps_altitude = self.jpeg.exif['GPSAltitude']
                ele = float(gps_altitude[0]) / gps_altitude[1]
                self.elevation_data = True
            else:
                ele = 0
                self.elevation_data = False
            self.coord = Coord.deg(lat, lon, ele)
        else:
            self.coord = None
            self.elevation_data = None
        if 'UserComment' in self.jpeg.exif:
            user_comment = self.jpeg.exif['UserComment']
            self.description = exif.parse_usercomment(user_comment)
        else:
            self.description = None

    def to_html_img(self):
        return '<img alt="%s" src="%s" height="%d" width="%d"/>' \
               % (self.name, self.url, self.jpeg.height, self.jpeg.height)
