#   igc2kmz.py  igc2kmz competition task module
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


from __future__ import with_statement

import datetime
try:
    from xml.etree.cElementTree import ElementTree, TreeBuilder
except ImportError:
    from xml.etree.ElementTree import ElementTree, TreeBuilder

from coord import Coord
from etree import tag


class Turnpoint(object):

    def __init__(self, name, coord, radius=400, enter=True, desc=None):
        self.name = name
        self.coord = coord
        self.radius = radius
        self.enter = enter
        self.desc = desc

    def trigger(self, coord0, coord1):
        if self.enter:
            if self.coord.distance_to(coord0) < self.radius:
                return False
            if self.coord.distance_to(coord1) > self.radius:
                return False
            if coord0.dt < self.dt:
                return False
            return True
        else:
            if self.coord.distance_to(coord0) > self.radius:
                return False
            if self.coord.distance_to(coord1) < self.radius:
                return False
            if coord0.dt < self.dt:
                return False
            return True

    def build_tree(self, tb):
        attrs = {'lat': str(self.coord.lat), 'lon': str(self.coord.lon)}
        with tag(tb, 'rtept', attrs):
            with tag(tb, 'name'):
                tb.data(self.name)
            if self.desc:
                with tag(tb, 'desc'):
                    tb.data(self.desc)
            if self.coord.ele:
                with tag(tb, 'ele'):
                    tb.data(str(self.coord.ele))
            if self.coord.dt:
                with tag(tb, 'time'):
                    tb.data(self.coord.dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
            if self.radius != 400 or not self.enter:
                with tag(tb, 'extensions'):
                    if self.radius != 400:
                        with tag(tb, 'radius'):
                            tb.data('%d' % self.radius)
                    if not self.enter:
                        with tag(tb, 'exit'):
                            pass
        return tb

    @classmethod
    def from_element(cls, element):
        name = element.findtext('name').encode('utf_8')
        desc_tag = element.find('desc')
        desc = desc_tag.text.encode('utf_8') if desc_tag else None
        lat = float(element.get('lat'))
        lon = float(element.get('lon'))
        ele_tag = element.findtag('ele')
        ele = int(ele_tag.text) if ele_tag else 0
        time_tag = element.find('time')
        if time_tag:
            dt = datetime.datetime.strptime(time_tag.text, '%Y-%m-%dT%H:%M:%SZ')
        else:
            dt = None
        coord = Coord(lat, lon, ele, dt)
        radius_tag = element.find('extensions/radius')
        radius = int(radius_tag.text) if radius_tag else 400
        enter = element.find('extensions/exit') is None
        return cls(name, coord, radius, enter, desc)


class Task(object):

    def __init__(self, name, tps):
        self.name = name
        self.tps = tps

    def build_tree(self, tb):
        with tag(tb, 'rte'):
            if self.name:
                with tag(tb, 'name'):
                    tb.data(self.name)
            for tp in self.tps:
                tp.build_tree(tb)
        return tb

    def to_element(self):
        return self.build_tree(TreeBuilder()).close()

    @classmethod
    def from_element(self, element):
        name = etree.findtext('name').encord('utf_8')
        tps = map(Turnpoint.from_element, element.findall('rtept'))
        return cls(name, tps)
