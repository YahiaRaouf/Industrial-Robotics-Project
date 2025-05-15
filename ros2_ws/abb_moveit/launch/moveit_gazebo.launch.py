from launch import LaunchDescription
from launch_ros.actions import SetParameter
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from launch.actions import TimerAction
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Launch Gazebo from abb_robot package
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("abb_robot"), "launch/gazebo.launch.py"
            )
        )
    )

    # Launch MoveIt demo from abb_moveit package
    moveit_launch = TimerAction(
        period=5.0,  # Delay in seconds
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("abb_moveit"),
                        "launch/demo.launch.py",
                    )
                )
            )
        ],
    )

    return LaunchDescription(
        [
            # Use simulation time
            SetParameter(name="use_sim_time", value=True),
            # Include both launch files
            gazebo_launch,
            moveit_launch,
        ]
    )
