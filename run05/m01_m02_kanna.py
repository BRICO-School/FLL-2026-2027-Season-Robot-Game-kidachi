from pybricks.tools import StopWatch, multitask, run_task, wait
from setup import initialize_robot

stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    """ラン5: M01, M02"""
    await robot.straight(590)  # M01に向けて前進
    await robot.straight(-120)  # M01で後進して奥側の羽を倒す
    await robot.turn(40)  # M02に向けて方向転換
    await robot.straight(220)
    await robot.turn(-85)
    await robot.straight(205, timeout=3000)
    await robot.straight(-210)
    await robot.turn(-45)
    await robot.straight(50)
    await left_lift.run_angle(300, 180)
    await robot.straight(-50)
    await robot.turn(-70)
    await robot.straight(580)

    robot.stop()
    print("# 走行完了！")


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """センサー値を定期的にターミナルに表示する非同期タスク。"""
    global stop_logging
    print("--- センサーログタスク開始 ---")
    logger_timer = StopWatch()
    logger_timer.reset()

    print(
        "time,current_dist_mm,error_angle_deg,current_heading_deg,left_angle_deg,right_angle_deg,angle_diff_deg,"
        "left_speed_dps,right_speed_dps,speed_diff_dps,kp_dist,ki_dist,kd_dist,kp_head,ki_head,kd_head"
    )

    while not stop_logging:
        elapsed_time = logger_timer.time()
        current_dist_mm = robot.distance()
        current_heading_deg = hub.imu.heading()
        left_angle_deg = left_wheel.angle()
        right_angle_deg = right_wheel.angle()
        angle_diff_deg = right_angle_deg - left_angle_deg
        left_speed_dps = left_wheel.speed()
        right_speed_dps = right_wheel.speed()
        speed_diff_dps = right_speed_dps - left_speed_dps

        kp_dist = 1000
        ki_dist = 50
        kd_dist = 10
        kp_head = 2000
        ki_head = 50
        kd_head = 100
        error_angle_deg = 0

        print(
            f"{elapsed_time:.0f},{current_dist_mm:.1f},{error_angle_deg:.1f},{current_heading_deg:.1f},{left_angle_deg:.1f},{right_angle_deg:.1f},{angle_diff_deg:.1f},{left_speed_dps:.1f},{right_speed_dps:.1f},{speed_diff_dps:.1f},{kp_dist:.1f},{ki_dist:.1f},{kd_dist:.1f},{kp_head:.1f},{ki_head:.1f},{kd_head:.1f}"
        )

        await wait(200)

    print("--- センサーログタスク終了 ---")


async def main():
    global stop_logging
    await run(hub, robot, left_wheel, right_wheel, left_lift, right_lift)
    stop_logging = True
    print("--- メインタスク完了、ログタスク終了中 ---")
    await wait(500)


if __name__ == "__main__":
    hub, robot, left_wheel, right_wheel, left_lift, right_lift = initialize_robot()
    run_task(multitask(sensor_logger_task(hub, robot, left_wheel, right_wheel), main()))
