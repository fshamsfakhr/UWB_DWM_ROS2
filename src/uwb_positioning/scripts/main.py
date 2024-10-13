#!/usr/bin/env python3
import serial
import time
from dwm1001_systemDefinitions import SYS_DEFS
from dwm1001_apiCommands import DWM1001_API_COMMANDS
import rclpy
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from sensor_msgs.msg import Range

class ANValue:
    def __init__(self, name, a, b, c, d, e):
        self.name = name
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

class YourClassName:
    def __init__(self):

        # Initialize ROS2 node
        rclpy.init()
        self.node = rclpy.create_node('uwb_positioning')
        # Declare parameters with default values or types
        self.serial_port_name = self.node.declare_parameter('~serial_port_name', '/dev/ttyACM1').value
        self.serial_baud_rate = self.node.declare_parameter('~serial_baud_rate', 115200).value
        self.serial_port_dwm1001 = serial.Serial(
            port=self.serial_port_name,
            baudrate=self.serial_baud_rate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        # Create ROS2 publisher
        self.AN_publisher = self.node.create_publisher(Range, '/UWB/Ranges', 10)
        self.TG_publisher = self.node.create_publisher(Pose, 'UWB/Pos', 10)

    def start(self):
        self.serial_port_dwm1001.close()
        time.sleep(1)
        self.serial_port_dwm1001.open()
        if self.serial_port_dwm1001.is_open:
            self.initialize_dwm1001_api()
            time.sleep(2)
            self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.LEC)
            self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            print("Reading from port...")

            while True:
                try:
                    serial_read_line = self.serial_port_dwm1001.read_until().decode('utf-8')
                    ans_values = {}
                    current_an = None
                    values = serial_read_line.split(',')
                    for value in values:
                        if value.startswith("AN") or value.startswith("POS"):
                            current_an = value
                            ans_values[current_an] = ANValue(name=current_an, a=None, b=None, c=None, d=None, e=None)
                        elif current_an is not None:
                        # Assign values to the corresponding attributes of the ANValue instance
                            if ans_values[current_an].a is None:
                                ans_values[current_an].a = value
                            elif ans_values[current_an].b is None:
                                ans_values[current_an].b = value
                            elif ans_values[current_an].c is None:
                                ans_values[current_an].c = value
                            elif ans_values[current_an].d is None:
                                ans_values[current_an].d = value
                            elif ans_values[current_an].e is None:
                                ans_values[current_an].e = value


                    # Print the structured AN values
                    for key, value in ans_values.items():
                        # Create an instance of the custom message type
                        if "AN" in value.name:                            
                            msg_an = Range()
                            msg_an.header.frame_id = 'dwm1001'
                            msg_an.field_of_view = 0.0
                            msg_an.min_range = 0.1
                            msg_an.max_range = 50.0
                            msg_an.range = float(value.e)
        
                            self.AN_publisher.publish(msg_an)
                        elif "POS" in value.name:
                            msg_tg = Pose()
                            msg_tg.position.x = float(value.a)
                            msg_tg.position.y = float(value.b)
                            msg_tg.position.z = float(value.c)
                            msg_tg.orientation.x = 0.0
                            msg_tg.orientation.y = 0.0
                            msg_tg.orientation.z = 0.0
                            msg_tg.orientation.w = 1.0
                            
                            self.TG_publisher.publish(msg_tg)

                except serial.SerialException as e:
                    print("Serial Exception:", e)
                    break
        else:
            print("Can't open port: " + str(self.serial_port_dwm1001.name))


    def initialize_dwm1001_api(self):
        self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.RESET)
        self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serial_port_dwm1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)

# Create an instance of your class and call the start method
your_instance = YourClassName()
your_instance.start()
