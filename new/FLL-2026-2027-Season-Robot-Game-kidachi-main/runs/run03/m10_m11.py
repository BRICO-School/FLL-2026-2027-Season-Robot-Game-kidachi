import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pybricks.tools import StopWatch, multitask, run_task, wait
from setup import initialize_robot
from utils.runtime import ensure_project_root

ensure_project_root(__file__)

# グローバル終了フラグ
stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    #######################################
    # ここにロボットの動作を記述してください

    # 速度・加速度設定を定義
    # 直進時の設定
    straight_settings = {
        "straight_speed": 400,
        "straight_acceleration": 500,
    }

    # 回転時の設定
    turn_settings = {
        "turn_rate": 240,
        "turn_acceleration": 850,
    }

    # M11
    robot.settings(**turn_settings)
    await robot.turn(-45)

    robot.settings(**straight_settings)
    await robot.straight(300)

    robot.settings(**turn_settings)
    await robot.turn(45)

    robot.settings(**straight_settings)
    await robot.straight(500)

    robot.settings(**turn_settings)
    await robot.turn(26)

    robot.settings(**straight_settings)
    await robot.straight(330)

    await right_lift.run_angle(1000, 180 * 40)

    robot.settings(**straight_settings)
    await robot.straight(-130)

    robot.settings(**turn_settings)
    await robot.turn(-26)

    robot.settings(**straight_settings)
    await robot.straight(225)

    # M10
    robot.settings(**turn_settings)
    await robot.turn(-88)

    robot.settings(straight_speed=100, straight_acceleration=200)
    await robot.straight(148, timeout=2000)

    robot.settings(straight_speed=100, straight_acceleration=200)
    await robot.straight(-148)

    robot.settings(turn_rate=100, turn_acceleration=300)
    await robot.turn(106)

    robot.settings(**straight_settings)
    await robot.straight(-430)
    await robot.turn(-28)
    await robot.straight(-900)

    robot.stop()
    print("# 走行完了！")


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """センサー値を定期的にターミナルに表示する非同期タスク。"""
    global stop_logging
    print("--- センサーログタスク開始 ---")
    logger_timer = StopWatch()
    logger_timer.reset()

    print(
        "time,current_dist_mm,error_angle_deg,current_heading_deg,left_angle_deg,right_angle_deg,"
        "angle_diff_deg,left_speed_dps,right_speed_dps,speed_diff_dps,kp_dist,ki_dist,kd_dist,"
        "kp_head,ki_head,kd_head"
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
            f"{elapsed_time:.0f},{current_dist_mm:.1f},{error_angle_deg:.1f},{current_heading_deg:.1f},"
            f"{left_angle_deg:.1f},{right_angle_deg:.1f},{angle_diff_deg:.1f},"
            f"{left_speed_dps:.1f},{right_speed_dps:.1f},{speed_diff_dps:.1f},"
            f"{kp_dist:.1f},{ki_dist:.1f},{kd_dist:.1f},{kp_head:.1f},{ki_head:.1f},{kd_head:.1f}"
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
