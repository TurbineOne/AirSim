# In settings.json first activate computer vision mode:
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

import setup_path
import airsim

import pprint
import os
import time
import math
import tempfile
import random

pp = pprint.PrettyPrinter(indent=4)

client = airsim.VehicleClient()
client.confirmConnection()

mrclient = airsim.MultirotorClient()
mrclient.confirmConnection()
mrclient.enableApiControl(True)
mrclient.armDisarm(True)

airsim.wait_key('Press any key to takeoff')
mrclient.takeoffAsync()

mrclient.moveToPositionAsync(0, 0, 0, 5)

airsim.wait_key('Press any key to set camera-0 gimbal to 15-degree pitch')
#camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(math.radians(15), 0, 0)) #radians
#client.simSetCameraPose("0", camera_pose)

airsim.wait_key('Press any key to get camera parameters')
for camera_name in range(5):
    camera_info = client.simGetCameraInfo(str(camera_name))
    print("CameraInfo %d:" % camera_name)
    pp.pprint(camera_info)

tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_cv_mode")
print ("Saving images to %s" % tmp_dir)
try:
    os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise

airsim.wait_key('Press any key to get images')
for x in range(500): # do few times
    x = random.randrange(0,2000)/100; # some random number
    y = random.randrange(0,2000)/100; # some random number
    z = 0-(random.randrange(0,700)/100); # some random number
    client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, z), airsim.to_quaternion(x / 3.0, 0, x / 3.0)), True)

    responses = client.simGetImages([
        airsim.ImageRequest("front_left", airsim.ImageType.Scene),
        airsim.ImageRequest("front_right", airsim.ImageType.Scene),
        airsim.ImageRequest("front_center", airsim.ImageType.Segmentation),
        airsim.ImageRequest("front_center", airsim.ImageType.DepthPerspective),
        airsim.ImageRequest("front_center", airsim.ImageType.DepthVis),
        airsim.ImageRequest("front_center", airsim.ImageType.DisparityNormalized),
        ])

    for i, response in enumerate(responses):
        filename = os.path.join(tmp_dir, str(x) + "_" + str(y) + "_" + str(z) + "_" + str(i))
        if response.pixels_as_float:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_float), pprint.pformat(response.camera_position)))
            airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
        else:
            print("Type %d, size %d, pos %s" % (response.image_type, len(response.image_data_uint8), pprint.pformat(response.camera_position)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)

    pose = client.simGetVehiclePose()
    pp.pprint(pose)


# currently reset() doesn't work in CV mode. Below is the workaround
client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0)), True)
