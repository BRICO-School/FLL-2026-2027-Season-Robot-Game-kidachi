from pybricks.tools import multitask, run_task, wait
from setup import initialize_robot

# グローバル終了フラグ
stop_logging = False


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    """
    ラン2: M09, M07
    """
    # ラン2だけ、他のランとは異なり低速で動くようにする
    # 直進速度: 800mm/s * 40% = 320mm/s
    # 回転速度: 200deg/s * 30% = 60deg/s
    robot.settings(straight_speed=320, turn_rate=60)

    # ここにロボットの動作を記述してください

    # M09
    await robot.curve(120, 110)  # 半径120mmで90度カーブ M09に向けて方向転換
    await robot.curve(120, -64)  # 半径120mmで-90度カーブ M09に向けて方向転換

    robot.settings(straight_speed=220)  # M09に向けて前進
    await robot.straight(200)

    await robot.straight(-192)  # M09の台を引っ張って後進

    await wait(200)  # 0.2秒待機

    await robot.curve(710, 10)  # M09に向けて前進

    await wait(150)  # 0.15秒待機

    # 右のタイヤだけを回して回転
    await right_wheel.run_angle(100, 170)  # 速度100で回転 M09の下の台を回転して上げる

    await wait(100)  # 0.1秒待機

    # M07
    await robot.straight(-210)  # 後進でM09から離れる
    await robot.turn(45)  # M07へ向けて方向転換
    await robot.straight(210)  # M07に向けて前進
    await robot.turn(65)  # M07に向けて方向転換
    await robot.straight(90)  # M07に向けて前進

    await right_lift.run_angle(1000, -850)  # 速度1000でリフト操作（台を上げる）
    await robot.straight(100)
    await right_lift.run_angle(800, 720)  # 右のアームを上げる

    # 左側にいくバージョン
    robot.settings(straight_speed=400)
    await robot.straight(-550)
    await robot.turn(58)
    robot.settings(straight_speed=600)  # スピードを600mm/sに上げる
    await robot.straight(-800)
    await robot.turn(-22)
    await robot.straight(-650)

    robot.stop()
    print("# 走行完了！")


async def sensor_logger_task(hub, robot, left_wheel, right_wheel):
    """センサー値を定期的に表示するタスク。"""
    global stop_logging
    print("--- センサーログタスク開始 ---")
    while not stop_logging:
        heading = hub.imu.heading()
        left_deg = left_wheel.angle()
        right_deg = right_wheel.angle()
        dist = robot.distance()
        print(
            f"LOG: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°"
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
