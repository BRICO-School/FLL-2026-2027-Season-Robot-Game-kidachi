from pybricks.tools import StopWatch, multitask, run_task, wait
from setup import initialize_robot

# グローバル終了フラグ
stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    #######################################
    # ここにロボットの動作を記述してください

    # # M08

    # # 最初の目標地点まで前進（450mm）
    # print(">>> 実行: await robot.straight(450)")
    # await robot.straight(450)

    # # 右アームを下げる（速度500、角度-360度）
    # print(">>> 実行: await right_lift.run_angle(500,-1100)")
    # await right_lift.run_angle(500, -360)

    # await wait(100)  # 0.1秒待機

    # # 右アームを下げる（速度500、角度-360度）
    # print(">>> 実行: await right_lift.run_angle(500,-1100)")
    # await right_lift.run_angle(500, -360)

    # await wait(100)  # 0.1秒待機

    # # 右アームを下げる（速度500、角度-360度）
    # print(">>> 実行: await right_lift.run_angle(500,-1100)")
    # await right_lift.run_angle(500, -360)

    # M07
    # 左アーム下げる
    print(">>> 実行: await left_lift.run_angle(500, -360)")
    await left_lift.run_angle(500, -360)

    # 前進
    print(">>> 実行: await robot.straight(100)")
    await robot.straight(100)

    # 左アームを上げる
    print(">>> 実行: await left_lift.run_angle(500, 360)")
    await left_lift.run_angle(500, -150)



    pass  # 何も実行しない場合の構文エラー回避

    ##########################################


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """
    センサー値を定期的にターミナルに表示する非同期タスク。
    他のタスク（ロボットの移動）と並行して実行されます。
    """
    print("--- センサーログタスク開始 ---")
    # 経過時間測定用のタイマーを開始
    logger_timer = StopWatch()
    logger_timer.reset()

    global stop_logging
    while not stop_logging:  # プログラムが終了するまで継続的にログを出力
        elapsed_time = logger_timer.time()
        heading = hub.imu.heading()
        left_deg = left_wheel.angle()
        right_deg = right_wheel.angle()
        dist = robot.distance()
        print(
            f"LOG[{elapsed_time:5.0f}ms]: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°"
        )
        await wait(200)  # 200ミリ秒待機して、他のタスクに実行を譲る


async def main():
    global stop_logging
    await run(hub, robot, left_wheel, right_wheel, left_lift, right_lift)
    stop_logging = True
    print("--- メインタスク完了、ログタスク終了中 ---")
    await wait(500)


if __name__ == "__main__":
    hub, robot, left_wheel, right_wheel, left_lift, right_lift = initialize_robot()
    run_task(multitask(sensor_logger_task(hub, robot, left_wheel, right_wheel), main()))
