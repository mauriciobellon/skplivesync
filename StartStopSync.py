import bpy


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


def Timer():
    bpy.ops.sna.timer()
    return 1


def register():
    bpy.utils.register_class(SNA_OT_Start_Syncing)
    bpy.utils.register_class(SNA_OT_Stop_Syncing)


def unregister():
    bpy.utils.unregister_class(SNA_OT_Start_Syncing)
    bpy.utils.unregister_class(SNA_OT_Stop_Syncing)