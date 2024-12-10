# -*- coding: utf-8 -*-
#!/usr/bin/python

import time
import random
import json
import requests
import hmac
import hashlib
import base64
import psutil

# Auth: Slash
# JFrog Connect 平台 HTTP 配置
CONNECT_SERVER = "https://api.connect.jfrog.io/api/v2"  # JFrog Connect Api
PROJECT_KEY = "chinafrogs"  # 项目 key
DEVICE_ID = "d-00f5-6955"  # 设备 ID
ACCESS_TOKEN = "eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYiLCJraWQiOiJsYkpadzNJUU13WXBBSWNRa01RRjN0dlA2Yml5M3dWcXdrQ0txUkxLaXhRIn0.eyJzdWIiOiJqZmFjQDAxZTlycTMza3ljMHQxMWtwangybmcwemo1L3VzZXJzL3NsYXNoIiwic2NwIjoiYXBwbGllZC1wZXJtaXNzaW9ucy9hZG1pbiIsImF1ZCI6IipAKiIsImlzcyI6ImpmZmVAMDFlOXJxMzNreWMwdDExa3BqeDJuZzB6ajUiLCJpYXQiOjE3MzI0MzQyMTEsImp0aSI6ImUwMzI0ZmY2LTJkZmQtNDA2OC05NTMzLWIzNjNmNDE2Y2EzMSJ9.UOZda8AfywSmj3l0GOHh_SUHnWFeShtiHEGFCo1PzThJTPxmgyM8OfrFDlVmuHSOoMgAqHUi3toWOEDs7xc_QysOT5RWp1d4O3UbGEi5-r_6AOCHWFiEMjXX1J1r2D54TWeTtKlP9cvQOMfMBngGXaA6YQYWtRLlPqVC2YCvqLvfDY9u2UDvjz2pHs0ne5V9QTdF9APCR73suWMh6qw99UWK84CiRxk77oP1fa01jLMq1pMligia48RT2ZmxmZz_YfmO1V3PdqCBtzyI-SePn60Q-R3ZtweQ-LDLBdroifQacPizjFLoE2ebHg1zJF72L8DjWqaD-qhc4Pc1rJ78Kw"  # JPD access token

class SimulatedRobot:
    def __init__(self):
        self.battery_level = 100  # 电量
        self.status = "stopped"  # 状态: rest, cleaning, paused
        self.position = (0, 0)  # 当前位置 (x, y)
        self.cleaned_area = 0  # 清扫面积
        self.runtime = ""

    def start_cleaning(self):
        if self.battery_level > 10:
            self.status = "cleaning"
            print("The robot is starting to clean ...")
        else:
            print("Low battery! Can't start cleaning!")
            self.report_event("low_battery", {"battery_level": "self.battery_level"})

    def stop_cleaning(self):
        self.status = "rest"
        print("Stop cleaning...")

    def simulate_cleaning(self):
        if self.status == "cleaning":
            # 随机移动并清扫
            self.position = (
                self.position[0] + random.randint(-100, 100),
                self.position[1] + random.randint(-100, 100),
            )
            self.cleaned_area += random.randint(1, 5)
            self.battery_level -= 1
            print(f"In the process of cleaning... Current Location: {self.position}, Cleared area: {self.cleaned_area}㎡, Battery level: {self.battery_level}%")
            if self.battery_level <= 10:
                print("Low battery! Can't start cleaning!")
                self.stop_cleaning()

    def report_property(self):

        # 获取设备运行时长
       self.get_uptime_from_proc()
       print("Running time: " + self.runtime)

        # 上报 data 数据到 JFrog Connect
        payload = {
            "app_parameters": [
                {"name": "runtime", "value": self.runtime},
                {"name": "status", "value": self.status},
                {"name": "cleaned_area", "value": str(self.cleaned_area) + " square meters"},
                {"name": "battery_level", "value": str(self.battery_level)}
            ]
        }

        print("Battery level: " + str(self.battery_level) + "%")
        print("Robot status: " + self.status)
        print("Location: " + str(self.position))
        print("Cleaned area: " + str(self.cleaned_area) + "㎡")

        send_data_api =  "/" + PROJECT_KEY + "/monitor/" + DEVICE_ID
        self._send_to_jfrog_connect(send_data_api, payload)

    def report_event(self, event_name, event_details):
        # 上报事件到 JFrog Connect
        payload = {
            "app_parameters": [
                {"name": "low_battery", "value": self.status}
            ]
        }
        send_event_api =  "/" + PROJECT_KEY + "/monitor/" + DEVICE_ID
        self._send_to_jfrog_connect(send_event_api, payload)

    def _send_to_jfrog_connect(self, endpoint, payload):
        # 构建 HTTP 请求
        url = CONNECT_SERVER + endpoint
        print(url)
        headers = self._generate_headers()
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                print(f"Monitoring data has been pushed to JFrog Connect: {response.json()}")
            else:
                print(f"Send data to JFrog Connect failed: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Send data to JFrog Connect failed: {str(e)}")

    def _generate_headers(self):
        # 构建 HTTP Headers
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ACCESS_TOKEN
        }
    
    def get_uptime_from_proc(self):
        with open("/proc/uptime", "r") as file:
            uptime_seconds = float(file.readline().split()[0])
            days = int(uptime_seconds // 86400)  # 1 day = 86400 seconds
            hours = int((uptime_seconds % 86400) // 3600)  # 1 hour = 3600 seconds
            minutes = int((uptime_seconds % 3600) // 60)  # 1 minute = 60 seconds
            self.runtime = f"{days} days, {hours} hours, {minutes} minutes"


# 模拟主逻辑
if __name__ == "__main__":
    robot = SimulatedRobot()

    while True:
        user_input = input("Please enter the execution command for the robot vacuum cleaner (start/stop/status/exit): ")
        if user_input == "start":
            robot.start_cleaning()
        elif user_input == "stop":
            robot.stop_cleaning()
        elif user_input == "status":
            robot.report_property()
        elif user_input == "exit":
            break
        else:
            print("reinput execution command.")

        # 模拟运行
        robot.simulate_cleaning()
        time.sleep(1)

