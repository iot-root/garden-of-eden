#!/bin/bash

# Run v4l2-ctl to list devices and capture the output
output=$(v4l2-ctl --list-devices)

# Use awk to parse the output and collect only the first video device under each USB entry
first_usb_video_devices=$(echo "$output" | awk '
BEGIN { in_usb = 0; device_found = 0; }
/usb-/ { 
    in_usb=1;  # Found a USB device section, set flag
    device_found=0;  # Reset device found flag for the new USB section
}
/^$/ { 
    in_usb=0;  # End of a device section
}
in_usb && /\/dev\/video/ && device_found == 0 { 
    print $1;  # Print the first /dev/video path found in the USB section
    device_found=1;  # Set flag to skip further /dev/video lines in this USB section
}
')

# Define the output file name for the generated Bash script
output_file="./bin/capture_cameras.sh"

# Start writing the Bash script
echo "#!/bin/bash" > "$output_file"
echo "" >> "$output_file"

# Get a timestamp for filename uniqueness
timestamp=$(date +%Y%m%d%H%M%S)

# Check if any devices were found and generate the corresponding fswebcam commands
if [ -z "$first_usb_video_devices" ]; then
    echo "echo 'No USB video devices found.'" >> "$output_file"
else
    counter=0
    echo "$first_usb_video_devices" | while read -r device_path; do
        let counter++
        # Create a unique filename using the timestamp and counter
        filename="/tmp/capture_${timestamp}_${counter}.jpg"
        echo "fswebcam -d $device_path -r 2500x1900 -S 2 -F 2 $filename" >> "$output_file"
    done
fi

# Make the generated script executable
chmod +x "$output_file"

# Optionally, display the contents of the generated script
cat "$output_file"
