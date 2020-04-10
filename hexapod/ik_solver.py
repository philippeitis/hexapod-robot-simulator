#
#
# **********************
# DEFINITIONS
# **********************
# p0: Body contact point
# p1: coxia point / coxia joint (point between coxia limb and femur limb)
# p2: tibia point / tibia joint (point between femur limb and tibia limb)
# p3: foot tip / ground contact
# coxia vector - vector from p0 to p1
# hexapod.coxia - coxia vector length
# femur vector - vector from p1 to p2
# hexapod.femur - femur vector length
# tibia vector - vector from p2 to p3
# hexapod.tibia - tibia vector length
# body_to_foot vector - vector from p0 to p3
# coxia_to_foot vector - vector from p1 to p3
# d: coxia_to_foot_length
# body_to_foot_length
#
# rho
#  -- angle between coxia vector (leg x axis) and body to foot vector
#  -- angle between point p1, p0, and p3. (p0 at center)
# theta
#  --- angle between femur vector and coxia to foot vector
#  --- angle between point p2, p1, and p3. (p1 at center)
# phi
#  --- angle between coxia vector (leg x axis) and coxia to foot vector
#
# beta
#  --- angle between coxia vector (leg x axis) and femur vector
# gamma
#  --- angle between tibia vector and perpendicular vector to femur vector
#  --- positive is counter clockwise
# alpha
#  --- angle between leg coordinate frame and axis defined by line from
#      hexapod's center of gravity to body contact.
#
#
# For CASE 1 and CASE 2:
#   beta = theta - phi
#     beta is positive when phi < theta (case 1)
#     beta is negative when phi > theta (case 2)
# *****************
# Case 1 (beta IS POSITIVE)
# *****************
#
#      ^          (p2)
#      |            *
#  (leg_z_axis)    / |
#      |          /  |
#      |         /   |
#   (p0)    (p1)/    |
#     *------- *-----| ----------------> (leg_x_axis)
#      \       \     |
#        \      \    |
#          \     \   |
#            \    \  |
#              \   \ |
#                \   |
#                  \ * (p3)
#
#
# *****************
# Case 2 (beta is negative)
# *****************
#                           ^
#                           |
#                         (leg_z_axis direction)
# (p0)     (p1)             |
# *------- *----------------|------> (leg_x_axis direction)
# \        |   \
#  \       |    \
#   \      |     \
#    \     |      * (p2)
#     \    |     /
#      \   |    /
#       \  |   /
#        \ |  /
#         \| /
#          *
#
# *****************
# Case 3 (p3 is above p1) then beta = phi + theta
# *****************
#                * (p2)
#               / \
#             /    |
#           /      * (p3)
#         /     /
# *------ *  /
# (p0)   (p1)
#
#
from settings import (
    DEBUG_MODE,
    PRINT_IK_LOCAL_LEG,
    PRINT_IK,
    ALPHA_MAX_ANGLE,
    BETA_MAX_ANGLE,
    GAMMA_MAX_ANGLE,
)
import json
import numpy as np
from copy import deepcopy
from hexapod.const import HEXAPOD_POSE
from hexapod.points import (
    Point,
    length,
    add_vectors,
    scalar_multiply,
    vector_from_to,
    get_unit_vector,
    is_triangle,
    is_counter_clockwise,
    project_vector_onto_plane,
    angle_between,
    angle_opposite_of_last_side,
    rotz,
)

poses = deepcopy(HEXAPOD_POSE)


# This function computes the joint angles required to
# rotate and translate the hexapod given the parameters given
# - rot_x, rot_y, rot_z are how the hexapod should be rotated
# - percent_x, percent_y, percent_z are the percent shift of the
# center of gravity of the hexapod.
#
# Where the hexapod contacts the ground at its initial state
# will also be the final points of contact by the hexapod and the ground
# unless the leg can't reach it.
#
# ❗❗❗IMPORTANT: The hexapod will be MODIFIED and returned along with
# a dictionary of POSES containing the 18 computed angles
# if the pose is impossible, the the function will output a
# hexapod whose body is detached from its legs, the body having the pose required
# an ALERT message will also be returned explaining why the pose is impossible
#
def inverse_kinematics_update(hexapod, ik_parameters):

    tx = ik_parameters["percent_x"] * hexapod.mid
    ty = ik_parameters["percent_y"] * hexapod.side
    tz = ik_parameters["percent_z"] * hexapod.tibia
    rotx, roty, rotz = (
        ik_parameters["rot_x"],
        ik_parameters["rot_y"],
        ik_parameters["rot_z"],
    )

    hexapod.update_stance(ik_parameters["hip_stance"], ik_parameters["leg_stance"])
    hexapod.detach_body_rotate_and_translate(rotx, roty, rotz, tx, ty, tz)
    detached_hexapod = deepcopy(hexapod)

    if body_contact_shoved_on_ground(hexapod):
        return (
            detached_hexapod,
            None,
            "Impossible rotation at given height. \n body contact shoved on ground",
        )

    x_axis = Point(1, 0, 0)
    legs_up_in_the_air = []

    for i in range(hexapod.LEG_COUNT):
        leg_name = hexapod.legs[i].name
        body_contact = hexapod.body.vertices[i]
        foot_tip = hexapod.legs[i].foot_tip()
        body_to_foot_vector = vector_from_to(body_contact, foot_tip)

        # find the coxia vector which is the vector
        # from body contact point to joint between coxia and femur limb
        projection = project_vector_onto_plane(body_to_foot_vector, hexapod.z_axis)
        unit_coxia_vector = get_unit_vector(projection)
        coxia_vector = scalar_multiply(unit_coxia_vector, hexapod.coxia)

        # coxia point / joint is the point connecting the coxia and tibia limbs
        coxia_point = add_vectors(body_contact, coxia_vector)
        if coxia_point.z < foot_tip.z:
            return (
                detached_hexapod,
                None,
                "Impossible rotation at given height. \n coxia joint shoved on ground",
            )

        # *******************
        # 1. Compute p0, p1 and (possible) p3 wrt leg frame
        # *******************
        p0 = Point(0, 0, 0)
        p1 = Point(hexapod.coxia, 0, 0)

        # Find p3 aka foot tip (ground contact) with respect to the local leg frame
        rho = angle_between(unit_coxia_vector, body_to_foot_vector)
        body_to_foot_length = length(body_to_foot_vector)
        p3x = body_to_foot_length * np.cos(np.radians(rho))
        p3z = -body_to_foot_length * np.sin(np.radians(rho))
        p3 = Point(p3x, 0, p3z)

        # *******************
        # Compute p2, beta, gamma and final p3 wrt leg frame
        # *******************

        # These values are needed to compute
        # p2 aka tibia joint (point between femur limb and tibia limb)
        coxia_to_foot_vector2d = vector_from_to(p1, p3)
        d = length(coxia_to_foot_vector2d)

        # If we can form this triangle this means we probably can reach the target ground contact point
        if is_triangle(hexapod.tibia, hexapod.femur, d):
            # --------------------------------
            # CASE A: a triangle can be formed with
            # coxia to foot vector, hexapod's femur and tibia
            # --------------------------------
            theta = angle_opposite_of_last_side(d, hexapod.femur, hexapod.tibia)
            phi = angle_between(coxia_to_foot_vector2d, x_axis)

            beta = theta - phi  # case 1 or 2
            if p3.z > 0:  # case 3
                beta = theta + phi

            z_ = hexapod.femur * np.sin(np.radians(beta))
            x_ = p1.x + hexapod.femur * np.cos(np.radians(beta))

            p2 = Point(x_, 0, z_)
            femur_vector = vector_from_to(p1, p2)
            tibia_vector = vector_from_to(p2, p3)
            gamma = 90 - angle_between(femur_vector, tibia_vector)

            if p2.z < p3.z:
                return (
                    detached_hexapod,
                    None,
                    f"Can't reach target ground point. \n {leg_name} can't reach it because the ground is blocking the path.",
                )
        else:
            # --------------------------------
            # CASE B: It's impossible to reach target ground point
            # --------------------------------
            if d + hexapod.tibia < hexapod.femur:
                return (
                    detached_hexapod,
                    None,
                    f"Can't reach target ground point. \n {leg_name} leg's Femur length is too long.",
                )
            if d + hexapod.femur < hexapod.tibia:
                return (
                    detached_hexapod,
                    None,
                    f"Can't reach target ground point. \n {leg_name} leg's Tibia length is too long.",
                )

            # Then hexapod.femur + hexapod.tibia < d:
            legs_up_in_the_air.append(leg_name)
            LEGS_TOO_SHORT, msg = legs_too_short(legs_up_in_the_air)
            if LEGS_TOO_SHORT:
                return detached_hexapod, None, msg

            femur_tibia_direction = get_unit_vector(coxia_to_foot_vector2d)
            femur_vector = scalar_multiply(femur_tibia_direction, hexapod.femur)
            p2 = add_vectors(p1, femur_vector)
            tibia_vector = scalar_multiply(femur_tibia_direction, hexapod.tibia)
            p3 = add_vectors(p2, tibia_vector)

            # Find beta and gamma
            gamma = 0.0
            leg_x_axis = Point(1, 0, 0)
            beta = angle_between(leg_x_axis, femur_vector)
            if femur_vector.z < 0:
                beta = -beta

        # Final p1, p2, p3, beta and gamma computed at this point
        not_within_range, alert_msg = beta_gamma_not_within_range(beta, gamma, leg_name)
        if not_within_range:
            return detached_hexapod, None, alert_msg

        # *******************
        # 2. Compute alpha and twist_frame
        # Find frame used to twist the leg frame wrt to hexapod's body contact point's x axis
        # *******************
        alpha, twist_frame = find_twist_frame(hexapod, unit_coxia_vector)
        alpha = compute_twist_wrt_to_world(alpha, hexapod.body.COXIA_AXES[i])
        alpha_limit, alert_msg = angle_above_limit(
            alpha, ALPHA_MAX_ANGLE, leg_name, "coxia angle (alpha)"
        )

        if alpha_limit:
            return detached_hexapod, None, alert_msg

        # *******************
        # 3. Update hexapod points and finally update the pose
        # *******************
        points = [p0, p1, p2, p3]
        might_print_points(points, leg_name)

        # Convert points from local leg coordinate frame to world coordinate frame
        for point in points:
            point.update_point_wrt(twist_frame)
            if DEBUG_MODE:
                assert hexapod.body_rotation_frame is not None
            point.update_point_wrt(hexapod.body_rotation_frame)
            point.move_xyz(body_contact.x, body_contact.y, body_contact.z)

        if DEBUG_MODE:
            sanity_leg_lengths_check(hexapod, leg_name, points)

        # Update hexapod's points to what we computed
        update_hexapod_points(hexapod, i, points)

        poses[i]["coxia"] = alpha
        poses[i]["femur"] = beta
        poses[i]["tibia"] = gamma

    might_print_ik(poses, ik_parameters, hexapod)
    return hexapod, poses, None


def update_hexapod_points(hexapod, leg_id, points):
    points[0].name = hexapod.legs[leg_id].p0.name
    points[1].name = hexapod.legs[leg_id].p1.name
    points[2].name = hexapod.legs[leg_id].p2.name
    points[3].name = hexapod.legs[leg_id].p3.name

    hexapod.legs[leg_id].p0 = points[0]
    hexapod.legs[leg_id].p1 = points[1]
    hexapod.legs[leg_id].p2 = points[2]
    hexapod.legs[leg_id].p3 = points[3]


def find_twist_frame(hexapod, unit_coxia_vector):
    twist = angle_between(unit_coxia_vector, hexapod.x_axis)
    is_ccw = is_counter_clockwise(unit_coxia_vector, hexapod.x_axis, hexapod.z_axis)
    if is_ccw:
        twist = -twist

    twist_frame = rotz(twist)
    return twist, twist_frame


def compute_twist_wrt_to_world(alpha, coxia_axis):
    alpha = (alpha - coxia_axis) % 360
    if alpha > 180:
        alpha = alpha - 360
    elif alpha < -180:
        alpha = 360 + alpha

    return alpha


def body_contact_shoved_on_ground(hexapod):
    for i in range(hexapod.LEG_COUNT):
        body_contact = hexapod.body.vertices[i]
        foot_tip = hexapod.legs[i].foot_tip()
        if body_contact.z < foot_tip.z:
            return True
    return False


def legs_too_short(legs):
    # True when
    # if three of her left legs are up or
    # if three of her right legs are up or
    # if four legs are up
    if len(legs) >= 4:
        return True, f"Unstable. Too many legs off the floor. \n {legs}"

    if len(legs) == 3:
        leg_positions = [leg.split("-")[0] for leg in legs]
        if leg_positions.count("left") == 3:
            return True, f"Unstable. All left legs off the ground. \n {legs}"
        if leg_positions.count("right") == 3:
            return True, f"Unstable. All right legs off the ground. \n {legs}"

    return False, None


def angle_above_limit(angle, angle_range, leg_name, angle_name):
    if np.abs(angle) > angle_range:
        return (
            True,
            f"The {angle_name} (of {leg_name} leg) required \n \
      to do this pose is above the range of motion. \n \
      Required: {angle} degrees. Limit: {angle_range} degrees.",
        )

    return False, None


def beta_gamma_not_within_range(beta, gamma, leg_name):
    beta_limit, alert_msg = angle_above_limit(
        beta, BETA_MAX_ANGLE, leg_name, "beta angle (beta)"
    )
    if beta_limit:
        return True, alert_msg

    gamma_limit, alert_msg = angle_above_limit(
        gamma, GAMMA_MAX_ANGLE, leg_name, "gamma angle (gamma)"
    )
    if gamma_limit:
        return True, alert_msg

    return False, None


def might_print_ik(poses, ik_parameters, hexapod):
    if not PRINT_IK:
        return

    print("█████████████████████████████")
    print("█ START INVERSE KINEMATICS  █")
    print("█████████████████████████████")

    print(".....................")
    print("... ik_parameters: ")
    print(".....................")

    print(json.dumps(ik_parameters, indent=4))

    print(".....................")
    print("... poses: ")
    print(".....................")

    print(json.dumps(poses, indent=4))

    print(".....................")
    print("... hexapod: ")
    print(".....................")

    hexapod.print()
    print("█████████████████████████████")
    print("█ END INVERSE KINEMATICS    █")
    print("█████████████████████████████")


def sanity_leg_lengths_check(hexapod, leg_name, points):
    coxia = length(vector_from_to(points[0], points[1]))
    femur = length(vector_from_to(points[1], points[2]))
    tibia = length(vector_from_to(points[2], points[3]))

    assert np.isclose(
        hexapod.coxia, coxia, atol=1
    ), f"wrong coxia vector length. {leg_name} coxia:{coxia}"
    assert np.isclose(
        hexapod.femur, femur, atol=1
    ), f"wrong femur vector length. {leg_name} femur:{femur}"
    assert np.isclose(
        hexapod.tibia, tibia, atol=1
    ), f"wrong tibia vector length. {leg_name} tibia:{tibia}"


def might_print_points(points, leg_name):
    if not PRINT_IK_LOCAL_LEG:
        return

    print()
    print(leg_name, "leg")
    print(f"...p0: {points[0]}")
    print(f"...p1: {points[1]}")
    print(f"...p2: {points[2]}")
    print(f"...p3: {points[3]}")
    print()
