# What-You-See-Is-What-You-Get Indoor Localization (WIL)

![wysiwyg_overview](https://user-images.githubusercontent.com/86873213/170413199-e255c7e4-984e-4b02-b497-edd0833f536b.gif)

Here's a simple demonstration where a human and a mobile robot ([Vstone MegaRover 3.0](https://github.com/szaguldo-kamaz/mecanumcommander)) are moving around and two non-moving objects are placed on the floor, while their sensed poses are being projected onto them.

![move](https://user-images.githubusercontent.com/86873213/169096483-7b093dd0-dec5-4b11-aea6-27626fd298e0.gif)

For gathering the raw pose data HTC Vive trackers were used. The WIL system transforms the raw pose data to be aligned with the real space (previously calibrated) and generates the image to be projected. Raw pose data sources supported: SteamVR, [libsurvive](https://github.com/cntools/libsurvive), ROS messages, UDP packets (see "RemoteUDP" files). See *wil_config.py* for configuring which one to use. IDs of the trackers (LHR-xxxxxxxx) you want to use should be listed in *wil_config.py*. Vive controllers should also work.

Calibration is very simple and easy, just run *wil_calibration_with_floorproj.py*, and you should see something similar:

![calib](https://user-images.githubusercontent.com/86873213/169096461-a1cb6ec3-5acd-4535-baee-974a8c93cbdc.gif)

Usage:  
&nbsp; mouse dragging with left button pressed: adjust x,y offset  
&nbsp; mouse scrollwheel: adjust world orientation offset  
&nbsp; mouse scrollwheel with left button pressed: adjust tracker orientation offset  
&nbsp; keys + - : adjust pixratio  
&nbsp; keys x y r : toggle swap x, y, rotdir  
&nbsp; keys 1..0: select tracker no. 1..10 for individual adjusment  
&nbsp; key Space: select world / unselect tracker  
&nbsp; key Esc : exit without saving calibration parameters  
&nbsp; key Enter : save calibration parameters and exit  

First, try to adjust the world offsets, then (if required) adjust the trackers individually (use the 1..0 keys to select, then mouse drag + scrollwheel).
By default the calibration parameters will be stored in a file called *wil_calibparams-NEW.txt*, the examples (and the calibration application) read the calibration parameters from *wil_calibparams-OK.txt*, be sure to rename or symlink it to use the new parameters file.
To adjust heights (z axis), modify the saved *wil_calibparams.txt* file manually.
If you would like to use the adjusted poses in your application, please see *wil_talker_** as examples.

Even without using floor projection, WIL can possibly serve as a "Room Setup" tool for [libsurive](https://github.com/cntools/libsurvive) (and also for SteamVR, but it already has a "rough" Room Setup component).

Requires Python 3 and PySimpleGUI (`pip install pysimplegui`). And also openvr if you want to use SteamVR as the localization data source (`pip install openvr`).

Also, you can find more details in the [following paper](http://dx.doi.org/10.1109/AIM52237.2022.9863359), also if you find this useful and use it in your research, please cite:

`D. Vincze, M. Niitsuma, "What-You-See-Is-What-You-Get Indoor Localization for Physical Human-Robot Interaction Experiments", in Proc. of the 2022 IEEE/ASME International Conference on Advanced Intelligent Mechatronics (AIM2022), 2022, Sapporo, Japan, pp. 909-914.`

DOI: [10.1109/AIM52237.2022.9863359](http://dx.doi.org/10.1109/AIM52237.2022.9863359)
