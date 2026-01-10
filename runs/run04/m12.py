from pybricks.tools import StopWatch, multitask, run_task, wait
from setup import initialize_robot

stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    """ラン4: M12"""
    # ステップ1: 目標地点に向かって前進
    await robot.straight(350)

    # ステップ2: 位置調整のため少し後退
    await robot.straight(-130)

    # ステップ3: カーブしながら前進（タイムアウト処理付き）
    await robot.curve(850, 25, speed=200, timeout=2000)

    # ステップ4: スタート地点に向けて後退
    await robot.straight(-550, speed=350)

    robot.stop()
    print("# 走行完了！")


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
