#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import Float64
import pyaudio
import time
import speech_recognition as sr
import actionlib
# Brings in the .action file and messages used by the move base action
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

r = sr.Recognizer()
work_state = 1

# Goal dictionary
KeyWord = { "โต๊ะ 1":"Table_1",
            "โต๊ะ 2":"Table_2",
            "โต๊ะ 3":"Table_3",
            "โต๊ะ 4":"Table_4",
            "โต๊ะ 5":"Table_5",
            "โต๊ะ 6":"Table_6",
            "โต๊ะ 7":"Table_7",
            "โต๊ะ 8":"Table_8",
            "โต๊ะ 9":"Table_9"}

# Correct dictionary
Correct ={"ถูก":"right",
          "ผิด":"wrong"}

# Goal position
Goal = {"Table_1":[1.8699,1.4366,1,0.0010],
        "Table_2":[2.2259,1.4089,0,1],
        "Table_3":[4.1345,1.4057,0,1],
        "Table_4":[-0.2529,-2.931,-1,0.0073],
        "Table_5":[1.0844,-3.0429,0,1],
        "Table_6":[3.5716,-2.9831,-1,0.0021],
        "Table_7":[4.9426,-3.0198,0,1],
        "Table_8":[7.4901,0.702,0,1],
        "Table_9":[7.3631,-2.7956,0,1],
        "Counter":[0,0,0.0083,1]}

# movefunction
def movebase_client(map_odom_desire):
    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    goal.target_pose.pose.position.x = map_odom_desire[0]
    goal.target_pose.pose.position.y = map_odom_desire[1]
    goal.target_pose.pose.orientation.z = map_odom_desire[2]
    goal.target_pose.pose.orientation.w = map_odom_desire[3]

    client.send_goal(goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        return client.get_result()   

# publish function
def talker(position):
    pub = rospy.Publisher('/robot/joint1_position_controller/command', Float64, queue_size=10)
    pub.publish(position)

# If the python node is executed as main process (sourced directly)
if __name__ == '__main__':
    try:
        rospy.init_node('movebase_client_py')
       # Initializes a rospy node to let the SimpleActionClient publish and subscribe
    
        while 1:
            # Start state
            if (work_state == 0):
               print("ready to serve")
               work_state = 1

            # Command state
            elif (work_state == 1):  
                try:
                    with sr.Microphone() as source:  
                        print("Say")              
                        audio = r.listen(source, phrase_time_limit=3)
                        print("stop")
                        word = r.recognize_google(audio,language='th')
                        try:
                            print("Are you going to " + KeyWord[word])
                            work_state = 2
                        except:
                            print("Can't understand your voice, Please say again")
                            pass

                except:
                    pass

            # Check command state
            elif (work_state == 2): 
                try:
                    with sr.Microphone() as source:
                        print("Say")                  
                        audio = r.listen(source,phrase_time_limit=3)
                        correct = r.recognize_google(audio,language='th')
                        try:
                            work_state = 3
                        except:
                            print("Can't understand your voice, Please say again")
                            pass
                except:
                    pass
            
            # Check state
            elif (work_state == 3):
                if (correct == "ถูก"):
                    result = movebase_client(Goal[KeyWord[word]])
                    if result:
                        print("Arrive at goal")
                        work_state = 4
                elif(correct == "ผิด"):
                    print("Please say again")
                    work_state = 1
                else:
                    work_state = 2
                    pass

            # Serve state
            elif (work_state == 4):  
                print("Serving")
                action=talker(0.1)
                time.sleep(10)
                action=talker(-0.1)
                print("Back to Counter")
                work_state = 5

            # Back home state
            elif (work_state == 5):
                result = movebase_client(Goal["Counter"])
                if result:
                    print("Arrive at Counter")
                    work_state = 0
            




    except rospy.ROSInterruptException:
        print("Sucession")