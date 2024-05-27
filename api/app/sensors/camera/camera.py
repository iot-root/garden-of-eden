from flask import render_template_string, jsonify, send_from_directory
import subprocess
import os

class Camera:
    def capture_images(self):
        find_cameras = os.path.expanduser('~/garden-of-eden/bin/api/find-usb-cameras.sh')
        capture_images = os.path.expanduser('~/garden-of-eden/bin/api/capture-cameras.sh')
        try:
            # find cameras
            find_cameras_result = subprocess.run([find_cameras], capture_output=True, text=True)
            # if success
            if find_cameras_result.returncode == 0:
                    # capture images
                    capture_images_result = subprocess.run([capture_images], capture_output=True, text=True)
                    # if success
                    if capture_images_result.returncode == 0:
                        return jsonify(message='Script executed successfully'), 200
                    else:
                        return jsonify(error='Error in capture images execution'), 500
            else:
                return jsonify('Error in find camera execution'), 500
        except Exception as e:
            return str(e), 500

    def get_image(self, filename):
        home_directory = os.path.expanduser('~/')
        return send_from_directory(home_directory, filename, mimetype='image/jpeg')

    def list_images(self):
        # List all files in the image directory that end with '.jpg' or '.jpeg'
        home_directory = os.path.expanduser('~')
        images = [filename for filename in os.listdir(home_directory)
                if filename.lower().endswith(('.jpg', '.jpeg'))]
        return jsonify(value=images)

    def delete_image(self, filename):
        home_directory = os.path.expanduser('~')
        try:
            os.remove(f"{home_directory}/{filename}")
            return f"File '{filename}' was deleted successfully."
        except FileNotFoundError:
            return f"Error: The file '{filename}' does not exist."
        except PermissionError:
            return f"Error: Permission denied when trying to delete '{filename}'."
        except Exception as e:
            return f"Error: An error occurred while trying to delete '{filename}': {e}"