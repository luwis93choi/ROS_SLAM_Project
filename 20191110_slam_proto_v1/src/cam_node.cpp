#include <ros/ros.h>

#include <usb_cam/usb_cam.h>
#include <image_transport/image_transport.h>
#include <camera_info_manager/camera_info_manager.h>
#include <sstream>
#include <std_srvs/Empty.h>
#include <string.h>

#include <cv_brige/cv_brige.h>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>

int image_RX_count; // Number of received images

// This callback function will be invoked if image subscriber receives images.
// This function receives images as sensor messages
void imageCallback(const sensor_msgs::ImageConstPtr& msg){

    // In order to utilize OpenCV, we need to image data that is compatible with OpenCV standards.
    // ROS provides cv_bridge as a mean to convert image sensor message into OpenCV-compatible variable.

    cv_bridge::CvImagePtr cv_ptr;   // Image data pointer : cv_bridge turns image sensor message into image object pointer with various info and attributes

    image_RX_count++;   // Increase the number if image is received

    ROS_INFO("imageCallback call count : %d", image_RX_count);
    ROS_INFO("[Image height : %d] [Image width : %d] [Image encoding : %s] \n", msg->height, msg->widht, msg->ending());

    // Use 'cv_bridge' and its 'toCvCopy' in order to convert ROS msgs Image into OpenCV Image
    cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);

    cv::imshow("USB_CAM image", cv_ptr->image);     // Display camera image on the window with title "USB_CAM image"
    // Actual image data is stored in member variable 'image' of CvImagePtr
    // To look up on details of CvImagePtr, refer to ROS sensor_msgs::Image documenation

    cv::waitKey(3); // Maintain the image window until any IO inputs
}

int main(int argc, char** argv){

    // Initialize the node with argc and argv, and Name it as "cam_node"
    ros::init(argc, argv, "cam_node");

    // Declare node handler
    ros::NodeHandle nh;

    // Declare loop rate 10Hz 
    // --> This Rate class will do the best to keep the loop at 10Hz by accounting for the time used by the work done during the loop
    ros::Rate loop_rate(10);

    // In order to transport image data between nodes, we utilize "ImageTransport".
    // ImageTransport class will deliver images between nodes as image sensor messages.
    image_transport::ImageTransport it(nh);

    // Through ImageTransport, image data is delivered as messages.
    // As a result, in order for the node to receive the image data, it has to subscribe the image just as it does for receiving standard messages from other nodes.
    image_transport::Subscriber sub = it.subscribe("/usb_cam/image_raw", 1000, imageCallback);

    // When image subscriber receives images, it will invoke imageCallback function defined above.

    // Use spinOnce in order to handle all the message Callbacks and return them immediately
    ros::spinOnce();

    // While roscore is operational, loop will continue on...
    while(ros::ok()){

        ros::spinOnce();    // Handle all the message Callbacks

        loop_rate.sleep();  // Use sleep in order to run this loop at 10Hz
    }

    cv::destroyWindow("USB CAM image"); // Destroy the image window

    return 0;
}