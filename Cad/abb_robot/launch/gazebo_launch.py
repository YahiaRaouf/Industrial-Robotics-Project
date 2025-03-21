from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import xacro
import os


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_lab_gazebo = get_package_share_directory("abb_robot")

    # Process the Xacro file to generate URDF
    xacro_file = os.path.join(pkg_lab_gazebo, "urdf", "robot_pkg.urdf")
    doc = xacro.parse(open(xacro_file))
    robot_description = doc.toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    # Joint State Publisher node
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
    )

    # Add the bridge node for mapping the topics between ROS and GZ sim
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # Clock (IGN -> ROS2)
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # Joint states (IGN -> ROS2)
            "/world/empty/model/abb_robot/joint_state@sensor_msgs/msg/JointState[gz.msgs.JointState",
        ],
        remappings=[
            ("/world/empty/model/abb_robot/joint_state", "joint_states"),
        ],
        output="screen",
    )

    # Spawn Entity node
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-name", "abb_robot", "-topic", "/robot_description"],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )
    
    # add the robot controllers for joint trajectory, arm group and hand group controllers
    robot_controller = PathJoinSubstitution( [
        pkg_lab_gazebo,
        "config",
        "joint_controller.yaml", ]
    )
    
    # pass the controllers to the control node to send commands to the controllers 
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controller],
        output="screen",
    )
    
    # Controller Manager Spawner node to launch the joint state broadcaster 
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--param-file", robot_controller], 
    )
    # Controller Manager Spawner node to launch the arm group controller 
    arm_controller_manager_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_group_controller',"--param-file", robot_controller], output='screen'
    )
    # Controller Manager Spawner node to launch the hand group controller 
    hand_controller_manager_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['hand_group_controller', "--param-file", robot_controller], output='screen'
    )

    # Get the meshes path in the install directory
    meshes_path = os.path.join(pkg_lab_gazebo, "meshes")
    return LaunchDescription(
        [
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", meshes_path),
            gazebo,
            spawn_entity,
            bridge,
            robot_state_publisher_node,
            joint_state_publisher_node,
            control_node,
            arm_controller_manager_spawner,
            hand_controller_manager_spawner,
            joint_state_broadcaster_spawner,
        ]
    )
