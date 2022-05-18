# What-You-See-Is-What-You-Get Indoor Localization (WIL)

Here's a simple demonstration where a human and a mobile robot (Vstone MegaRover 3.0) are moving around and two non-moving objects are placed on the floor, while their sensed poses are being projected onto them.

![move](https://user-images.githubusercontent.com/86873213/169096483-7b093dd0-dec5-4b11-aea6-27626fd298e0.gif)

For gathering the raw pose data HTC Vive trackers were used. The WIL system transforms the raw pose data to be aligned with the real space (previously calibrated) and generates the image to be projected. Raw pose data sources supported: SteamVR, libsurvive, ROS messages, raw UDP packets (see "RemoteUDP" files). See *wil_config.py* for configuring which one to use. IDs of the trackers (LHR-xxxxxxxx) you want to use should be listed in *wil_config.py*.

Calibration is very simple and easy, just run *wil_calibration_with_floorproj.py*, and you should see something similar:

![calib](https://user-images.githubusercontent.com/86873213/169096461-a1cb6ec3-5acd-4535-baee-974a8c93cbdc.gif)

Usage:  
&nbsp; mouse dragging with left button pressed: adjust x,y offset  
&nbsp; mouse scrollwheel: adjust world orientation offset  
&nbsp; mouse scrollwheel with left button pressed: adjust object orientation offset  
&nbsp; keys + - : adjust pixratio  
&nbsp; keys x y r : toggle swap x, y, rotdir  
&nbsp; key Esc : exit without saving calibration parameters  
&nbsp; key Enter : save calibration parameters and exit  

If you would like to use the adjusted poses in your application, please see *wil_talker_** as examples.

Even without using floor projection, WIL can possibly serve as a "Room Setup" tool for libsurive (and also for SteamVR, but it already has a "rough" Room Setup component).

Requires Python 3 and PySimpleGUI (`pip install pysimplegui`).

Also, you can find more details in the following paper, also if you find this useful and use it in your research, please cite (currently in press):

`D. Vincze, M. Niitsuma, "What-You-See-Is-What-You-Get Indoor Localization for Physical Human-Robot Interaction Experiments", in Proc. of the 2022 IEEE/ASME International Conference on Advanced Intelligent Mechatronics (AIM2022), 2022, Sapporo, Japan (in press).`
