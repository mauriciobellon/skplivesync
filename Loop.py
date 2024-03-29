import os
import bpy
import json
import pathlib
import hashlib
from math import atan, pi, tan
import bpy.utils.previews
from mathutils import Vector


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

def sna_fnisskpchanged():
    global fnisskpchanged
    skp_file_pathlib = pathlib.Path(bpy.context.scene.skpfilepath)
    fnisskpchanged['sna_timestamp_current'] = skp_file_pathlib.stat().st_mtime_ns
    if fnisskpchanged['sna_timestamp_current'] == fnisskpchanged['sna_timestamp_last']:
        fnisskpchanged['sna_return'] = False
    else:
        fnisskpchanged['sna_return'] = True
    fnisskpchanged['sna_timestamp_last'] = fnisskpchanged['sna_timestamp_current']
    return fnisskpchanged['sna_return']


def register():
    bpy.utils.register_class(SNA_OT_Timer)
    
def unregister():
    bpy.utils.unregister_class(SNA_OT_Timer)