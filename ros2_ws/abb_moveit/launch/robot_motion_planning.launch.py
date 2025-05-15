import os 
from ament_index_python.packages import get_package_share_directory 
from launch import LaunchDescription 
from launch_ros.actions import Node 
from launch.actions import DeclareLaunchArgument, ExecuteProcess 
from launch.substitutions import LaunchConfiguration 
from moveit_configs_utils import MoveItConfigsBuilder 


def generate_launch_description(): 
    moveit_config = ( 
        MoveItConfigsBuilder( 
        robot_name="abb_robot", package_name="abb_moveit" 
        ) 
        .robot_description(file_path="config/abb_robot.urdf.xacro") 
        .moveit_cpp( 
        file_path=get_package_share_directory("abb_moveit") 
        + "/config/robot_motion_planning_python.yaml" 
        ) 
        .to_moveit_configs() 
    ) 

    example_file = DeclareLaunchArgument( 
        "example_file", 
        default_value="main.py",
        description="Python API tutorial file name", 
    ) 
 
    moveit_py_node = Node( 
        name="moveit_py", 
        package="abb_moveit", 
        executable=LaunchConfiguration("example_file"), 
        output="both", 
        parameters=[moveit_config.to_dict(), 
        {"use_sim_time": True}], 
    ) 

    robot_state_publisher = Node( 
        package="robot_state_publisher", 
        executable="robot_state_publisher", 
        name="robot_state_publisher", 
        output="log", 
        parameters=[moveit_config.robot_description, 
        {"use_sim_time": True}], 
    ) 
 
    ros2_controllers_path = os.path.join( 
        get_package_share_directory("abb_moveit"), 
        "config", 
        "ros2_controllers.yaml", 
    ) 
    ros2_control_node = Node( 
        package="controller_manager", 
        executable="ros2_control_node", 
        parameters=[ros2_controllers_path], 
        remappings=[ 
            ("/controller_manager/robot_description", "/robot_description"), 
        ], 
        output="log", 
    ) 
    load_controllers = [] 
    for controller in [ 
        "arm_group_controller", 
        "hand_group_controller", 
        "joint_state_broadcaster", 
    ]: 
        load_controllers += [ 
            ExecuteProcess( 
                cmd=["ros2 run controller_manager spawner {}".format(controller)], 
                shell=True, 
                output="log", 
            ) 
        ] 
        
    return LaunchDescription( 
        [ 
            example_file, 
            robot_state_publisher, 
            moveit_py_node,  
            ros2_control_node, 
        ] 
        + load_controllers 
    )