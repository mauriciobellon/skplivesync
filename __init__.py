# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import bpy
from . import SketchupLiveSync, PluginUpdater, StartStopSync, FindSkpFile, SetSkpFilePath, Loop

bl_info = {
    "name" : "SketchUp Live Sync",
    "author" : "Mauricio Faria Bellon", 
    "description" : "An easy way to sync SketchUp to Blender",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 1),
    "location" : "",
    "waring" : "",
    "category" : "3D View",
    "doc_url": "https://www.github.com/mauriciobellon/skplivesync"
}

addon_keymaps = {}

_icons = None

ui = {'sna_status': "stopped", }

fnisskpchanged = {'sna_pathlib': None, 
                  'sna_timestamp_current': 0,
                  'sna_timestamp_last': 0,
                  'sna_return': False, }

last_modification_time = None

def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.skpfilepath = bpy.props.StringProperty(name='SkpFilePath', 
                                                           description='', 
                                                           default='', 
                                                           subtype='FILE_PATH', 
                                                           maxlen=0)
    SketchupLiveSync.register()
    Loop.register()
    PluginUpdater.register()
    StartStopSync.register()
    FindSkpFile.register()
    SetSkpFilePath.register()

def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.skpfilepath
    SketchupLiveSync.unregister()
    Loop.unregister()
    PluginUpdater.unregister()
    StartStopSync.unregister()
    FindSkpFile.unregister()
    SetSkpFilePath.unregister()
