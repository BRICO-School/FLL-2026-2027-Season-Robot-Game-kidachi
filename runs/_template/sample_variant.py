"""
バリアント用のサンプル。
runXX 配下では main.py と同じ階層に置き、ACTIVE_VARIANT で指定します。
"""

from pybricks.tools import wait

# stop_logging を持つと、main 側がセンサーロガー停止を面倒みてくれます
stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    """
    ここにロボットの動作を記述してください。
    """
    # 例: await robot.straight(400)

    robot.stop()
    print("# 走行完了！")


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """
    センサー値を定期的に表示する場合のサンプル。
    必要なければこの関数ごと削除してください。
    """
    global stop_logging
    print("--- センサーログタスク開始 ---")
    while not stop_logging:
        print(f"LOG: dist={robot.distance():.1f}mm heading={hub.imu.heading():.1f}deg")
        await wait(200)
    print("--- センサーログタスク終了 ---")
