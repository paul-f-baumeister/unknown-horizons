# ###################################################
# Copyright (C) 2008 The OpenAnno Team
# team@openanno.org
# This file is part of OpenAnno.
#
# OpenAnno is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import fife
import game.main
import math
from game.util import Rect,Point
from game.util import WorldObject

class Building(WorldObject):
	"""Class that represents a building. The building class is mainly a super class for other buildings.
	@param x, y: int position of the building.
	@param owner: Player that owns the building.
	@param instance: fife.Instance - only singleplayer: preview instance from the buildingtool."""
	def __init__(self, x, y, owner, instance = None, **kwargs):
		super(Building, self).__init__(x=x, y=y, owner=owner, instance=instance, **kwargs)
		self.building_position = Rect((Point(x, y)), self.size[0]-1, self.size[1]-1)
		self.x = x
		self.y = y
		self.owner = owner
		self.object_type = 0
		self._instance = self.getInstance(x, y) if instance is None else instance
		self._instance.setId(str(self.getId()))

		self.island = game.main.session.world.get_island(self.x, self.y)
		settlements = self.island.get_settlements(self.x, self.y)
		if len(settlements) == 0:
			self.settlement = self.island.add_settlement(self.x, self.y, self.x + self.size[0] - 1, self.y + self.size[1] - 1, self.radius, owner)
		else:
			self.settlement = settlements[0]

	def remove(self):
		"""Removes the building"""
		#print "BUILDING: REMOVE " + str(self)
		self.settlement.rem_inhabitants(self.inhabitants)
		self.island.remove_building(self)

		for x in xrange(self.x, self.x + self.__class__.size[0]):
			for y in xrange(self.y, self.y + self.__class__.size[1]):
				tile = self.island.get_tile(x,y)
				tile.blocked = False
				tile.object = None
		self._instance.getLocationRef().getLayer().deleteInstance(self._instance)
		#instance is owned by layer...
		#self._instance.thisown = 1

	def get_buildings_in_range(self):
		buildings = self.settlement.buildings
		ret_building = []
		for building in buildings:
			if building == self:
				continue
			if self.building_position.distance( building.building_position ) <= self.radius:
				ret_building.append( building )
		return ret_building

	@classmethod
	def getInstance(cls, x, y, action='default', building=None, layer=2, **trash):
		"""Get a Fife instance
		@param x, y: The coordinates
		@param action: The action, defaults to 'default'
		@param building: This parameter is used for overriding the class that handles the building, setting this to another building class makes the function redirect the call to that class
		@param **trash: sometimes we get more keys we are not interested in
		"""
		if building is not None:
			return building.getInstance(x = x, y = y, action=action, layer=layer, **trash)
		else:
			instance = game.main.session.view.layers[layer].createInstance(cls._object, fife.ModelCoordinate(int(x), int(y), 0))
			fife.InstanceVisual.create(instance)
			location = fife.Location(game.main.session.view.layers[layer])
			location.setLayerCoordinates(fife.ModelCoordinate(int(x + 1), int(y), 0))
			instance.act(action, location, True)
			return instance

	@classmethod
	def getBuildCosts(self, building=None, **trash):
		"""Get the costs for the building
		@param **trash: we normally dont need any parameter, but we get the same as the getInstance function
		"""
		if building is not None:
			return building.getBuildCosts(**trash)
		else:
			return self.costs

	def init(self):
		"""init the building, called after the constructor is run and the building is positioned (the settlement variable is assigned etc)
		"""
		self.settlement.add_inhabitants(self.inhabitants)

	def start(self):
		"""This function is called when the building is built, to start production for example."""
		pass

class Selectable(object):
	def select(self):
		"""Runs neccesary steps to select the building."""
		game.main.session.view.renderer['InstanceRenderer'].addOutlined(self._instance, 255, 255, 255, 1)
		for tile in self.island.grounds:
			if tile.settlement == self.settlement and (max(self.x - tile.x, 0, tile.x - self.x - self.size[0] + 1) ** 2) + (max(self.y - tile.y, 0, tile.y - self.y - self.size[1] + 1) ** 2) <= self.radius ** 2 and any(x in tile.__class__.classes for x in ('constructible', 'coastline')):
				game.main.session.view.renderer['InstanceRenderer'].addColored(tile._instance, 255, 255, 255)
				if tile.object is not None and True: #todo: only highlight buildings that produce something were interested in
					game.main.session.view.renderer['InstanceRenderer'].addColored(tile.object._instance, 255, 255, 255)

	def deselect(self):
		"""Runs neccasary steps to deselect the unit."""
		game.main.session.view.renderer['InstanceRenderer'].removeOutlined(self._instance)
		game.main.session.view.renderer['InstanceRenderer'].removeAllColored()
