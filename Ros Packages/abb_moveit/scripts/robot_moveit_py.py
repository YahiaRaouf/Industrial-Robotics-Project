#!/usr/bin/env python3
import time
import rclpy
from rclpy.logging import get_logger

# moveit python library
from moveit.core.robot_state import RobotState
from moveit.planning import (
    MoveItPy,
    MultiPipelinePlanRequestParameters,
)


def plan_and_execute(
    robot,
    planning_component,
    logger,
    single_plan_parameters=None,
    multi_plan_parameters=None,
    sleep_time=0.0,
):
    # plan to goal
    logger.info("Planning trajectory")
    if multi_plan_parameters is not None:
        plan_result = planning_component.plan(
            multi_plan_parameters=multi_plan_parameters
        )
    elif single_plan_parameters is not None:
        plan_result = planning_component.plan(
            single_plan_parameters=single_plan_parameters
        )
    else:
        plan_result = planning_component.plan()

    # execute the plan
    if plan_result:
        logger.info("Executing plan")
        robot_trajectory = plan_result.trajectory
        robot.execute(robot_trajectory, controllers=[])
    else:
        logger.error("Planning failed")
        time.sleep(sleep_time)


def main():
    rclpy.init()
    logger = get_logger("moveit_py.pose_goal")
    # instantiate MoveItPy instance and get planning component
    robot_py_node = MoveItPy(node_name="moveit_py")
    robotic_arm = robot_py_node.get_planning_component("arm_group")
    logger.info("MoveItPy instance created")
    # set plan start state using predefined state
    robotic_arm.set_start_state(configuration_name="zero_pose")
    # set pose goal using predefined state
    robotic_arm.set_goal_state(configuration_name="pose_pick")
    # plan to goal
    plan_and_execute(robot_py_node, robotic_arm, logger, sleep_time=3.0)

    # Instantiate a RobotState instance using the current robot model
    robot_model = robot_py_node.get_robot_model()
    robot_state = RobotState(robot_model)
    # randomize the robot state
    robot_state.set_to_random_positions()
    # set plan start state to current state
    robotic_arm.set_start_state_to_current_state()
    # set goal state to the initialized robot state
    logger.info("Set goal state to the initialized robot state")
    robotic_arm.set_goal_state(robot_state=robot_state)
    # plan to goal
    plan_and_execute(robot_py_node, robotic_arm, logger, sleep_time=3.0)

    # set plan start state to current state
    robotic_arm.set_start_state_to_current_state()
    # set pose goal with PoseStamped message
    robotic_arm.set_goal_state(configuration_name="zero_pose")
    # initialize multi-pipeline plan request parameters
    multi_pipeline_plan_request_params = MultiPipelinePlanRequestParameters(
        robot_py_node, ["ompl_rrtc", "pilz_lin", "chomp_planner"]
    )
    
if __name__ == "__main__":
    main()
    rclpy.shutdown()
    # plan to goal
