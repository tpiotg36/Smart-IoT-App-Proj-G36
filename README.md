# Smart-IoT-App-Proj-G36
For Smart IoT Application Project Submission

This project is created for project submission and all copyright reserved to the group and people behind this project. 
If there's any similar projects or ideas, we apologize and declare that we do not copy anyone's idea or project.

This project helps technical staffs during evening time when the technical staffs are closing the laboratories or tutorial rooms, they will find that a handful of projectors in the laboratories or tutorial rooms are left switched on. Between the times the projectors were left switched on to the time where someone switched it off or projectors go to sleep mode, it actually consuming quite a number lamp hours and electricity or energy. At times of emergency like fire outbreak, staffs are required to perform a manual and visual check on all the laboratories and tutorial rooms to ensure everyone is evacuated. But at a certain time, there might be some mischievous students may be hiding somewhere and even return back to the rooms/laboratories without anyone noticing.  

Please refer to the wiki for hardware setup and explanation on how to use the python code to run the project.

Please download the python files that are required for this project to run motionV2.py and relayoff.py. 

===========================================================================
motionV2.py file
===========================================================================
PS: There are AWS rules enabled in AWS IoT Cloud to help to actuate the LED and Buzzer which in turn help to trigger the script, photo taking and emailing.

This file is the main program which will send the sensor data periodically to AWS IoT. Based on the AWS IoT rules we created, the program will process actuation commands received. If motion detected, LED will flash once and take a photo. This photo will be send to user via email otherwise if there's no motion detected, LED will flash twice. When the light sensor sensed light from Projector, the Buzzer will sound and it will also trigger the relay script to switch off the projector.

===========================================================================
relayoff.py file
===========================================================================
This file will trigger by an AWS rule with act of actuating of buzzer.
