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
        time.sleep(3.0)
    else:
        logger.error("Planning failed")


def main():
    rclpy.init()
    logger = get_logger("moveit_py.reverse_motion")

    moveit_node = MoveItPy(node_name="moveit_py")
    arm = moveit_node.get_planning_component("arm_group")
    hand = moveit_node.get_planning_component("hand_group")
    logger.info("MoveItPy instance created")

    # Move to zero_pose to initialize safely
    logger.info("Moving to zero_pose to initialize state")
    arm.set_goal_state(configuration_name="zero_pose")
    arm.set_start_state_to_current_state()
    plan_and_execute(moveit_node, arm, logger)

    # close hand before motion sequence
    logger.info("Closing hand before motion sequence")
    hand.set_goal_state(configuration_name="closed_hand")
    hand.set_start_state_to_current_state()
    plan_and_execute(moveit_node, hand, logger)

    # Step through poses in reverse order
    for pose_name in ["position_1 (21P0041)", "position_3 (21P0041)", "position_4 (21P0240)", "position_2 (21P0240)","zero_pose"]:
        logger.info(f"Planning: current → {pose_name}") 
        arm.set_goal_state(configuration_name=pose_name)
        arm.set_start_state_to_current_state()
        plan_and_execute(moveit_node, arm, logger)

    moveit_node.shutdown()
    rclpy.shutdown()


if __name__ == "__main__":
    main()