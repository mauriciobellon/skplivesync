import os
import bpy
import json
import shutil
import requests
import pathlib
import hashlib
import zipfile
import io
from math import atan, pi, tan
import bpy.utils.previews
from mathutils import Vector
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty


bl_info = {
    "name" : "SketchUp Live Sync",
    "author" : "Mauricio Faria Bellon", 
    "description" : "An easy way to sync SketchUp to Blender",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "waring" : "",
    "doc_url": "www.github.com/mauriciobellon/skplivesync",
    "tracker_url": "", 
    "category" : "3D View" 
}
addon_keymaps = {}
_icons = None
ui = {'sna_status': "stopped", }
fnisskpchanged = {'sna_pathlib': None, 
                  'sna_timestamp_current': 0,
                  'sna_timestamp_last': 0,
                  'sna_return': False, }

last_modification_time = None

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
    
class SNA_OT_Stop_Syncing(bpy.types.Operator):
    bl_idname = "sna.stop_syncing"
    bl_label = "Stop Syncing"
    bl_description = "It will stop the sync process"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return not False
    def execute(self, context):
        if bpy.app.timers.is_registered(Timer):
            bpy.app.timers.unregister(Timer)
            print('Stoped Sync')
        ui['sna_status'] = "stopped"
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)






class SNA_OT_Update_Plugin(bpy.types.Operator):
    bl_idname = "sna.update_plugin"
    bl_label = "Update Plugin"
    bl_description = "Press to update the plugin"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False
        
    def execute(self, context):
        plugin_name = 'skplivesync'
        github_url = "https://codeload.github.com/mauriciobellon/skplivesync/zip/refs/heads/master"

        # Informar o início do processo de atualização
        print('Updating Plugin from GitHub')

        # Download do arquivo zip do plugin do GitHub
        try:
            r = requests.get(github_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            scripts_path = bpy.utils.user_resource('SCRIPTS')
            addons_path = os.path.join(scripts_path, 'addons')
            temp_extract_path = os.path.join(addons_path, 'temp_skplivesync')
            z.extractall(path=temp_extract_path)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download or extract plugin: {e}")
            return {"CANCELLED"}

        addon_extracted_path = os.path.join(temp_extract_path, 'skplivesync-master')
        final_addon_path = os.path.join(addons_path, plugin_name)

        # Mover o diretório extraído para o local correto e limpar diretório temporário
        if os.path.exists(final_addon_path):
            shutil.rmtree(final_addon_path)
        shutil.move(addon_extracted_path, addons_path)
        shutil.rmtree(temp_extract_path)  # Limpa o diretório temporário

        # Atualizar e habilitar o plugin
        bpy.ops.preferences.addon_refresh()
        if plugin_name in bpy.context.preferences.addons:
            bpy.ops.preferences.addon_remove(module=plugin_name)
        bpy.ops.preferences.addon_enable(module=plugin_name)
        bpy.ops.preferences.addon_refresh()

        print('Done Updating Plugin')
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)




    
    

class SNA_OT_Start_Syncing(bpy.types.Operator):
    bl_idname = "sna.start_syncing"
    bl_label = "Start Syncing"
    bl_description = "Press to start syncing de selected skp file with Blender"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False
    def execute(self, context):
        print(bpy.context.scene.skpfilepath)
        if bpy.context.scene.skpfilepath:
            if not bpy.app.timers.is_registered(Timer):        
                bpy.app.timers.register(Timer)
                print('Started Sync')
            else:
                print('Alread Syncing')
            ui['sna_status'] = "started"
        else:
            print('No file selected')
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)


class SNA_Find_SKP(Operator, ImportHelper):
    bl_idname = "sna.find_skp" 
    bl_label = "Find .skp to Sync"
    filename_ext = ".skp"
    filter_glob: StringProperty(
        default="*.skp",
        options={'HIDDEN'},
        maxlen=255,
    )
    def execute(self, context):
        bpy.context.scene.skpfilepath = self.filepath
        return {'FINISHED'}

class SNA_OT_Setskpfilepath(bpy.types.Operator):
    bl_idname = "sna.setskpfilepath"
    bl_label = "SetSkpFilePath"
    bl_description = "Press to start syncing de selected skp file with Blender"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False
    
    def execute(self, context):
        ui['sna_status'] == "selecting"           
        bpy.ops.sna.find_skp('INVOKE_DEFAULT')
        ui['sna_status'] == "stopped"
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)
    
class SNA_OT_Timer(bpy.types.Operator):
    bl_idname = "sna.timer"
    bl_label = "Timer"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    key_properties = ['diffuse_color', 'specular_intensity']
    global last_modification_time
    @classmethod
    def poll(cls, context):
        return not False
    
    def execute(self, context):
        true_when_changed_0_9a7b7 = sna_fnisskpchanged()
        if true_when_changed_0_9a7b7:
            print("")
            print("Updating")
            ui['sna_status'] = "syncing"
            class ExecuteSketchUpLive:
                def __init__(self, skp_file_path):
                    self.last_modification_time = 0
                    self.max_retries = 5
                    self.key_properties = ['diffuse_color', 'specular_intensity']
                    self.skp_file = skp_file_path
                    
                def setActiveCamera(self):
                    cameras_obj = [cam for cam in bpy.data.objects if cam.type == 'CAMERA']
                    for cam in cameras_obj:
                        if cam.name == "Active Camera":
                            bpy.context.scene.camera = cam
                            break
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            break
                
                def limitedDissolve(self):
                    bpy.ops.mesh.primitive_cube_add()
                    cube = bpy.context.selected_objects[0]
                    cube.name = "MyLittleCube"
                    for obj in bpy.data.collections['Sketchup'].all_objects:
                        obj.select_set(True)
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.dissolve_limited()
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.data.objects['MyLittleCube'].select_set(True)
                    bpy.ops.object.delete()

                def store_materials_state(self):
                    materials_state = {}
                    for mat in bpy.data.materials:
                        materials_state[mat.name] = {prop.identifier: getattr(mat, prop.identifier) for prop in mat.bl_rna.properties if not prop.is_readonly}
                    return materials_state

                def compare_and_restore_state(self, prev_state):
                    for mat_name, properties in prev_state.items():
                        if mat_name in bpy.data.materials:
                            mat = bpy.data.materials[mat_name]
                            for prop, value in properties.items():
                                if hasattr(mat, prop):
                                    setattr(mat, prop, value)
                                else:
                                    print(f"Property {prop} not found on material {mat_name}")
                        else:
                            print(f"Material {mat_name} not found")

                def update_materials(self, obj):
                    if obj.material_slots:
                        for slot in obj.material_slots:
                            if slot.material.use_nodes:
                                if slot.material.node_tree.nodes:
                                    continue
                                else:
                                    slot.material = self.get_or_create_material(slot.material.name, slot.material)
                            else:
                                slot.material = self.get_or_create_material(slot.material.name, slot.material)

                def get_or_create_material(self, name, material):
                    if name in bpy.data.materials:
                        existing_material = bpy.data.materials[name]
                        existing_properties_hash = self.hash_properties(existing_material)

                        if existing_properties_hash == self.hash_properties(material):
                            return existing_material
                        else:
                            name += "_" + hashlib.sha256(str(self.properties(material)).encode()).hexdigest()
                    
                    return bpy.data.materials.new(name=name)

                def properties(self, material):
                    return {prop.identifier: getattr(material, prop.identifier) for prop in material.bl_rna.properties if not prop.is_readonly}

                def hash_properties(self, material):
                    return hashlib.sha256(str(self.properties(material)).encode()).hexdigest()
                
                def recur_layer_collection(self, layer_coll, coll_name):
                    found = None
                    if (layer_coll.name == coll_name):
                        return layer_coll
                    for layer in layer_coll.children:
                        found = self.recur_layer_collection(layer, coll_name)
                        if found:
                            return found
                
                def deleteExistingCollection(self):
                    name = "Sketchup"
                    coll = bpy.data.collections.get(name)
                    if coll is None:
                        coll = bpy.data.collections.new(name)
                    else:
                        bpy.data.collections.remove(bpy.data.collections[name])
                        coll = bpy.data.collections.new(name)
                    if not bpy.context.scene.user_of_id(coll):
                        bpy.context.collection.children.link(coll)

                    layer_collection = bpy.context.view_layer.layer_collection
                    layer_coll = self.recur_layer_collection(layer_collection, 'Sketchup')
                    bpy.context.view_layer.active_layer_collection = layer_coll

                    bpy.ops.outliner.orphans_purge(do_recursive=True)

                    modified_objects = []
                    for obj in coll.all_objects:
                        if obj.parent is not None:
                            modified_objects.append(obj)
                        else:
                            obj.select_set(True)
                            bpy.ops.object.delete()
                    return coll, modified_objects
                
                def save(self):
                    bpy.ops.wm.save_mainfile()
                
                def update(self):

                    try:
                        bpy.ops.object.mode_set(mode='OBJECT')
                    except:
                        pass
                    
                    coll, modified_objects = self.deleteExistingCollection()

                    bpy.ops.import_scene.skp(filepath=self.skp_file,
                                            filter_glob="*.skp",
                                            import_camera=True,
                                            reuse_material=True,
                                            max_instance=10000,
                                            dedub_type='FACE',
                                            dedub_only=False,
                                            scenes_as_camera=True,
                                            import_scene="",
                                            reuse_existing_groups=True)

                    for obj in coll.all_objects:
                        self.update_materials(obj)
                        for obj in modified_objects:
                            obj.parent = coll
                            
                    self.limitedDissolve()        
                    self.setActiveCamera()
                    #self.save()

            live = ExecuteSketchUpLive(bpy.context.scene.skpfilepath)
            live.update()
            ui['sna_status'] = "started"
            print("Updated")
            print("")
        else:
            global last_modification_time
            # Check if camera properties file was modified
            camera_props_path =  os.path.join(os.path.dirname(os.path.abspath(bpy.context.scene.skpfilepath)), 'camera_props.json')
            if os.path.exists(camera_props_path):
                modification_time = os.path.getmtime(camera_props_path)

                if last_modification_time is None or modification_time > last_modification_time:
                    last_modification_time = modification_time
                    
                    # Load camera properties
                    with open(camera_props_path, "r") as f:
                        camera_props = json.load(f)

                    # Get camera vectors
                    eye = Vector(camera_props['eye'])
                    target = Vector(camera_props['target'])
                    up = Vector(camera_props['up'])          
                    z = eye - target
                    x = up.cross(z)
                    y = z.cross(x)
                    angle = camera_props['fov'] * 3.01675/173
                    camera = bpy.data.objects["Active Camera"]
                    camera.matrix_world.col[0] = x.to_4d()
                    camera.matrix_world.col[1] = y.to_4d()
                    camera.matrix_world.col[2] = z.to_4d()
                    camera.location = eye*0.0254
                    bpy.context.scene.render.resolution_x = camera_props['width']
                    bpy.context.scene.render.resolution_y = camera_props['height']
                    bpy.context.scene.render.pixel_aspect_x = 1.0
                    bpy.context.scene.render.pixel_aspect_y = 1.0
                    camera.data.sensor_fit = 'VERTICAL'
                    camera.data.sensor_width = 36.0
                    camera.data.sensor_height = 36.0
                    camera.scale = Vector((1, 1, 1))
                    if camera_props['perspective']:
                        camera.data.type = 'PERSP'
                        camera.data.angle = angle
                    else:
                        camera.data.type = 'ORTHO'
                        
                        ortho_scale = camera_props['ortho_height'] * 0.0254
                        
                        camera.data.ortho_scale = ortho_scale
                    
                    cameras_obj = [cam for cam in bpy.data.objects if cam.type == 'CAMERA']
                    for cam in cameras_obj:
                        if cam.name == "Active Camera":
                            bpy.context.scene.camera = cam
                            break
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            bpy.ops.view3d.view_center_camera({
                                'area': bpy.context.screen.areas[0],
                                'region': bpy.context.screen.areas[0].regions[0],})
                            break
                    
                    
                    
                    
                    print("Camera Updated")
            
        return {"FINISHED"}
    
    last_modification_time = None
    
    def invoke(self, context, event):
        return self.execute(context)

def Timer():
    bpy.ops.sna.timer()
    return 1

def sna_fnisskpchanged():
    skp_file_pathlib = pathlib.Path(bpy.context.scene.skpfilepath)
    fnisskpchanged['sna_timestamp_current'] = skp_file_pathlib.stat().st_mtime_ns
    if fnisskpchanged['sna_timestamp_current'] == fnisskpchanged['sna_timestamp_last']:
        fnisskpchanged['sna_return'] = False
    else:
        fnisskpchanged['sna_return'] = True
    fnisskpchanged['sna_timestamp_last'] = fnisskpchanged['sna_timestamp_current']
    return fnisskpchanged['sna_return']

def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.skpfilepath = bpy.props.StringProperty(name='SkpFilePath', 
                                                           description='', 
                                                           default='', 
                                                           subtype='FILE_PATH', 
                                                           maxlen=0)
    bpy.utils.register_class(SNA_PT_SketchUpLiveSync)
    bpy.utils.register_class(SNA_OT_Stop_Syncing)
    bpy.utils.register_class(SNA_OT_Start_Syncing)
    bpy.utils.register_class(SNA_OT_Setskpfilepath)
    bpy.utils.register_class(SNA_OT_Timer)
    bpy.utils.register_class(SNA_OT_Update_Plugin)
    bpy.utils.register_class(SNA_Find_SKP)

def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.skpfilepath
    bpy.utils.unregister_class(SNA_PT_SketchUpLiveSync)
    bpy.utils.unregister_class(SNA_OT_Stop_Syncing)
    bpy.utils.unregister_class(SNA_OT_Start_Syncing)
    bpy.utils.unregister_class(SNA_OT_Setskpfilepath)
    bpy.utils.unregister_class(SNA_OT_Timer)
    bpy.utils.unregister_class(SNA_OT_Update_Plugin)
    bpy.utils.unregister_class(SNA_Find_SKP)
