# WYSIWYG Indoor Localization
#   Gather pose/button information via ROS
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import rospy
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped
from WIL_LocDataBase   import WILLocDataBase


class WILLocDataROS(WILLocDataBase):

    class WILLocDataROSsubscriber:

        def __init__(self, topic, msgtype):
            self.rossub = rospy.Subscriber(topic, msgtype, self.ros_get_pose);
            self.pose = None;

        def ros_get_pose(self, rosmsg):
            pose_pos = rosmsg.pose.pose.position;
            pose_ori = rosmsg.pose.pose.orientation;
            self.pose = [ pose_pos.x, pose_pos.y, pose_pos.z, pose_ori.x, pose_ori.y, pose_ori.z, pose_ori.w ];

        def get_pose(self):
            return self.pose;


    def __init__(self, roomsize):
        WILLocDataBase.__init__(self, roomsize);
        self.ros_subscribers = {};
        rospy.init_node('wil');

    def update(self):

        for serial in self.ros_subscribers.keys():
            self.tracked_objects[serial]['pose'] = self.ros_subscribers[serial].get_pose();
#            self.tracked_objects[serial]['timecode'] = time.time();
# add button support later...
#            self.tracked_objects[serial]['button'] = 0;

        return 0

    def add_tracker_by_serial(self, trackerserial):
        if trackerserial not in self.tracked_objects.keys():
            topic = '/vive/%s_pose'%(trackerserial.replace('-','_'));
#            msgtype = Pose;
            msgtype = PoseWithCovarianceStamped;
            self.ros_subscribers[trackerserial] = self.WILLocDataROSsubscriber(topic, msgtype);
            self.tracked_objects[trackerserial] = {'timecode':0, 'pose':None, 'button':0};
            self.all_tracked_objs_have_valid_pose = False;
            return self.WILTracker(trackerserial, self);
