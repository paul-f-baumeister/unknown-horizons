# ###################################################
# Copyright (C) 2009 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
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

__all__ = ['building', 'unit', 'sounds']

from horizons.util import WorldObject

class GenericCommand(object):
	"""Code generator for trivial commands on an object.
	It saves an object's world id, and executes a method specified as string on it in __call__

	Use like this to call obj.mymethod(42, 1337):

	class MyCommand(GenericCommand):
	  def __init__(self, obj):
	    super(MyCommand,self).__init__(obj, "mymethod", 42, 1337)
	 """
	def __init__(self, obj, method, *args):
		self.obj_id = obj.getId()
		self.method = method
		self.args = args

	def __call__(self, issuer):
		obj = WorldObject.get_object_by_id(self.obj_id)
		getattr(obj, self.method)(*self.args)
