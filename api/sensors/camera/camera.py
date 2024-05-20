from flask import render_template_string, jsonify, send_from_directory
import subprocess
import os

class Camera:
    def capture_images(self):
        find_cameras = os.path.expanduser('~/garden-of-eden/bin/find_usb_cameras.sh')
        capture_images = os.path.expanduser('~/garden-of-eden/bin/capture_cameras.sh')
        try:
            # find cameras
            find_cameras_result = subprocess.run([find_cameras], capture_output=True, text=True)
            # if success
            if find_cameras_result.returncode == 0:
                    # capture images
                    capture_images_result = subprocess.run([capture_images], capture_output=True, text=True)
                    # if success
                    if capture_images_result.returncode == 0:
                        return f'Script executed successfully: {capture_images_result.stdout}', 200
                    else:
                        return f'Error in capture images execution: {capture_images_result.stderr}', 500
            else:
                return f'Error in find camera execution: {find_cameras_result.stderr}', 500
        except Exception as e:
            return str(e), 500

    def get_image(self, filename):
        return send_from_directory('/tmp', filename, mimetype='image/jpeg')

    def list_images(self):
        # List all files in the image directory that end with '.jpg' or '.jpeg'
        images = [filename for filename in os.listdir('/tmp')
                if filename.lower().endswith(('.jpg', '.jpeg'))]
        return jsonify(images)