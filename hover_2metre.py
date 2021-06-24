#!/usr/bin/env python


import rospy
import sys
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import*
from mavros_msgs.srv import CommandBool, SetMode
from mavros_msgs.msg import State

current_state = State()
    
def FCU_callback(msg): #you should write callback before code initialisation bcoz the callback in subscriber structure needs to know what term is this 
    global current_state #global the variable to use it anywhere 
    current_state = msg #storing message headers in the variable current state 



#node initialisation 
rospy.init_node("off_node",anonymous = True)
local_pos_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size = 10 )
state_sub = rospy.Subscriber('/mavros/state', State, FCU_callback)    

arming_client = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool)
set_mode_client = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode) 
#service strucutre 
''' variable = rospy.ServiceProxy('topic name ', msgtype.topic)
'''


rate = rospy.Rate(20)      


while not current_state.connected: #'''checking if the connection is established or not 
                                   #and trying to exit the loop thats the reason we are making it to false to exit from it easily'''
    print(current_state.connected)
    rate.sleep()   


pose = PoseStamped() #assigning posestamped data to a variable ... posestamped contains position and angular values 

pose.pose.position.x = 0
pose.pose.position.y = 0
pose.pose.position.z = 2 #making pose.pose.position.z = 2 so that it can fly to 2metres



for i in range(100): #we need to send setpoints to drone to set it into OFFBOARD 
    local_pos_pub.publish(pose)
    rate.sleep()

offb_set_mode = SetMode() #assigning the setmode type to a variable ... setmode contains data that is helpful to change modes 
offb_set_mode.custom_mode = "OFFBOARD" #to know why we used .custom_mode extension read the msg files of setmode in mavros px4
arm_cmd = CommandBool() #same as set mode...but it is used to arm the drone

arm_cmd.value = True # to know wht we took .value extension read commandbool msg data in mavros 

def dis_arm(): #i have written a function to disarm the drone 
    disarm_cmd = CommandBool()
    while (current_state.armed):
        arm = arming_client(False) #check the command bool msg data why we took arming_client extension and .success extension
        if arm.success:
            print("vechile disarmed ")

def off_board():# function to send the drone to offboard mode
    offb = set_mode_client(0,offb_set_mode.custom_mode) #check the setmode data in mavros to know why we used set_mode_clientand .mode_sent
    if offb.mode_sent:
        print("offboard enable")
    last_request = rospy.get_rostime()

def arming():# function to arm the drone
    arm = arming_client(arm_cmd.value)  #check the CommandBool data in mavros to know why we used arming client and .success
     
    if arm.success:
        print("vechile armed")

    last_request = rospy.get_rostime()




last_request = rospy.get_rostime() # rospy.time.now() returns to wall clock ..that means 

while not rospy.is_shutdown():

    while(current_state.mode != "OFFBOARD" and (rospy.get_rostime()-last_request > rospy.Duration(5))):
        off_board()

        
   
    while (not current_state.armed and (rospy.get_rostime()-last_request > rospy.Duration(5))):
        arming()
        

    
    while (pose.pose.position.z > 1.5 and (rospy.get_rostime()-last_request > rospy.Duration(15))):
        pose.pose.position.z = 0
        print("Drone has reached its peak position and required time limit is satisfied")


        last_request = rospy.Time.now()

    local_pos_pub.publish(pose)


    while (pose.pose.position.z < 0.2 and (rospy.get_rostime()-last_request > rospy.Duration(5))):
        dis_arm()
        
        

    
rate.sleep() # it is used to sleep if the last loop is success   
        
        
        
if __name__=='__main__':
    
    try:
        
        rospy.spin()
        
    except KeyboardInterrupt:
        print("Shutting down") 



