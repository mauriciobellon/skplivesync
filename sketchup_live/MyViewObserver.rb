require 'json'
require 'fileutils'

class MyViewObserver < Sketchup::ViewObserver
  def initialize
    @save_timer = nil
    @delay = 0.5
  end
  def onViewChanged(view)
    if @save_timer
      UI.stop_timer(@save_timer)
      @save_timer = nil
    end
    @save_timer = UI.start_timer(@delay, false) {
      eye = view.camera.eye
      target = view.camera.target
      up = view.camera.up
      perspective = view.camera.perspective?
      fov = view.camera.fov
      width = view.vpwidth
      height = view.vpheight
      ortho_height = view.camera.height
      camera_props = {
        timestamp: Time.now.to_i,
        eye: eye.to_a,
        target: target.to_a,
        up: up.to_a,
        perspective: perspective,
        fov: fov,
        width: width,
        height: height,
        ortho_height: ortho_height
      }
      model_path = Sketchup.active_model.path
      base_dir = File.dirname(model_path)
      file_path = File.join(base_dir, "camera_props.json")
      temp_file_path = File.join(base_dir, "camera_props_temp.json")
      File.write(temp_file_path, camera_props.to_json)
      if File.exist?(file_path)
        FileUtils.rm(file_path)
      end
      File.rename(temp_file_path, file_path)
      puts "Saved view to file"
    }
  end
end
Sketchup.active_model.active_view.add_observer(MyViewObserver.new)