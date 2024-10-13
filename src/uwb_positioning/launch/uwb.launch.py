from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='uwb_positioning',
            executable='main.py',
            name='uwb_positioning',
            output='screen',
            parameters=[
                {'serial_port_name': '/dev/ttyACM1'},
                {'serial_baud_rate': 115200},
            ],
        ),
    ])
