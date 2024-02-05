import os
import bpy
import shutil
import requests
import zipfile
import io


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
        
        print("Renaming Extracted masterfolder")
        addon_extracted_path = os.path.join(temp_extract_path, 'skplivesync-master')
        os.rename(addon_extracted_path, os.path.join(temp_extract_path, plugin_name))
        
        addon_extracted_path = os.path.join(temp_extract_path, plugin_name)
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


def register():
    bpy.utils.register_class(SNA_OT_Update_Plugin)


def unregister():
    bpy.utils.unregister_class(SNA_OT_Update_Plugin)