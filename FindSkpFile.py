import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


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


def register():
    bpy.utils.register_class(SNA_Find_SKP)


def unregister():
    bpy.utils.unregister_class(SNA_Find_SKP)