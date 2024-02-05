import bpy
import os
import shutil

class SNA_PT_SketchUpLiveSync(bpy.types.Panel):
    bl_label = 'SketchUp Live Sync'
    bl_idname = 'SNA_PT_SketchUpLiveSync'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'SketchUp Live Sync'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return not (False)
    
    def draw(self, context):
        global ui
        self.assert_sketchup_importer()
        layout = self.layout
        box = layout.box()
        box.alert = False
        box.enabled = True
        box.use_property_split = False
        box.use_property_decorate = False
        box.alignment = 'Expand'.upper()
        box.scale_x = 1.0
        box.scale_y = 1.0
        row = box.row(heading='', align=False)
        row.alert = False
        row.enabled = True
        row.use_property_split = False
        row.use_property_decorate = False
        row.scale_x = 1.0
        row.scale_y = 1.0
        row.alignment = 'Right'.upper()
        if bpy.context.scene.skpfilepath:
            row.label(text=bpy.context.scene.skpfilepath, icon_value=0)
        else:
            row.label(text='Choose a file...', icon_value=0)

        op = row.operator('sna.setskpfilepath', text='', icon_value=108,
                            emboss=False, depress=False)
            

        if bpy.context.scene.skpfilepath:
            if ui['sna_status'] == "started":
                op = layout.operator('sna.stop_syncing', text='Stop',
                                    icon_value=498, emboss=True, 
                                    depress=True)
        
            elif ui['sna_status'] == "syncing":
                op = layout.operator('sna.stop_syncing', text='Syncing', 
                                    icon_value=498, emboss=True, 
                                    depress=True)
            
            elif ui['sna_status'] == "stopped":
                op = layout.operator('sna.start_syncing', text='Start', 
                                    icon_value=495, emboss=True, 
                                    depress=False)
            
        op = layout.operator('sna.update_plugin', text='Update Plugin', 
                                emboss=False, 
                                depress=False)
        
    def assert_sketchup_importer(self):
        plugin_name = 'sketchup_importer'
        if plugin_name not in bpy.context.preferences.addons:
            addons_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons')
            sketchup_live_dir = os.path.join(addons_dir, 'sketchup_live')
            sketchup_importer_dir = os.path.join(sketchup_live_dir, plugin_name)
            shutil.copytree(sketchup_importer_dir,  os.path.join(addons_dir, plugin_name))
            bpy.ops.preferences.addon_enable(module=plugin_name)
            bpy.ops.preferences.addon_refresh()
            
            
def register():
    bpy.utils.register_class(SNA_PT_SketchUpLiveSync)


def unregister():
    bpy.utils.unregister_class(SNA_PT_SketchUpLiveSync)