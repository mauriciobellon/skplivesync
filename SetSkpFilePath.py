import bpy

class SNA_OT_Setskpfilepath(bpy.types.Operator):
    bl_idname = "sna.setskpfilepath"
    bl_label = "SetSkpFilePath"
    bl_description = "Press to start syncing de selected skp file with Blender"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False
    
    def execute(self, context):
        global ui
        ui['sna_status'] == "selecting"           
        bpy.ops.sna.find_skp('INVOKE_DEFAULT')
        ui['sna_status'] == "stopped"
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)


def register():
    bpy.utils.register_class(SNA_OT_Setskpfilepath)


def unregister():
    bpy.utils.unregister_class(SNA_OT_Setskpfilepath)