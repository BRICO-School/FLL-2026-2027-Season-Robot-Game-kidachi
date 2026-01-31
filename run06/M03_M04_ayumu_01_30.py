from pybricks.tools import StopWatch, multitask, run_task, wait
from setup import initialize_robot

stop_logging = False
IS_CURRENT = True


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
#######################################
    # ここにロボットの動作を記述してください

    # 作業位置まで前進（55cm）
    await robot.straight(400)
    # 右に90度回転
    await robot.turn(35)
    await robot.straight(200)
    await robot.turn(-35)
    await robot.straight(270)
    await robot.turn(75)
    # 左アームを下げる
    await left_lift.run_angle(800, 2000)
    # 右アームを下げる
    # await right_lift.run_angle(800, -2000)

    await robot.straight(100)
    # 右アームを上げる
    # await right_lift.run_angle(800, 2000)
    # 回転後に前進（10cm）
    # await robot.straight(100)

    # # 作業位置まで前進（10cm）
    # await robot.straight(100)

    # # 左アームを上げる
    # await left_lift.run_angle(500, -100)
    # # 右アームを上げる
    # await right_lift.run_angle(500, 1000)

    # # 元の位置に戻る（10cm）
    # await robot.straight(-100)
    
    # await left_lift.run_angle(500, 1200)

    # 走行終了
    robot.stop()
    print("# 走行完了！")
##########################################


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """センサー値を定期的にターミナルに表示する非同期タスク。"""
    global stop_logging
    print("--- センサーログタスク開始 ---")
    logger_timer = StopWatch()
    logger_timer.reset()

    while not stop_logging:
        elapsed_time = logger_timer.time()
        heading = hub.imu.heading()
        left_deg = left_wheel.angle()
        right_deg = right_wheel.angle()
        dist = robot.distance()
        print(
            f"LOG[{elapsed_time:5.0f}ms]: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°"
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
