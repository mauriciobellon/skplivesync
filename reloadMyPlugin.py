import os
import bpy
import shutil

plugin_name = 'sketchup_live'
addon_dir = os.path.join('C:\\Users\\mauricio\\OneDrive\\Code\\skplivesync\\sketchup_live')
addons_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons')


if plugin_name in bpy.context.preferences.addons:       
    bpy.ops.preferences.addon_remove(module=plugin_name)
    shutil.copytree(addon_dir,  os.path.join(addons_dir, plugin_name))
    bpy.ops.preferences.addon_enable(module=plugin_name)

else:
    shutil.copytree(addon_dir,  os.path.join(addons_dir, plugin_name))
    bpy.ops.preferences.addon_enable(module=plugin_name)
    
    
