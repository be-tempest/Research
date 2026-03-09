import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import tkinter as tk
import time
from tkinter import font
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import socket
import json
import warnings
warnings.filterwarnings("ignore")

# Mediapipeのセットアップ
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# ソケット通信の設定
HOST = '127.0.0.1'  # ローカルホスト
PORT = 5005         # 使用ポート
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# カメラを起動
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FPS, 30)

# 顔のYaw角の計算
def face_Yaw(Leye, Reye, nose):
    A = math.sqrt((Leye.x-nose.x) ** 2 + (Leye.y-nose.y) ** 2)
    B = math.sqrt((Reye.x-nose.x) ** 2 + (Reye.y-nose.y) ** 2)
    D = abs((Reye.y-Leye.y)*nose.x + (Leye.x-Reye.x)*nose.y + (Reye.x*Leye.y-Leye.x*Reye.y)) / math.sqrt((Reye.y-Leye.y) ** 2 + (Leye.x-Reye.x) ** 2)

    LineL = math.sqrt(A ** 2 - D ** 2)
    LineR = math.sqrt(B ** 2 - D ** 2)

    if A < B:
        Yaw = math.asin(1 - (LineL/LineR))
    else:
        Yaw = -math.asin(1 - (LineR/LineL))

    Yaw_deg = math.degrees(Yaw)

    return Yaw_deg

# 顔のPitch角の計算
def face_Pitch(Leye, Reye, Lmouth, Rmouth, nose):
    LineU = abs((Reye.y-Leye.y)*nose.x + (Leye.x-Reye.x)*nose.y + (Reye.x*Leye.y-Leye.x*Reye.y)) / math.sqrt((Reye.y-Leye.y) ** 2 + (Leye.x-Reye.x) ** 2)
    LineD = abs((Rmouth.y-Lmouth.y)*nose.x + (Lmouth.x-Rmouth.x)*nose.y + (Rmouth.x*Lmouth.y-Lmouth.x*Rmouth.y)) / math.sqrt((Rmouth.y-Lmouth.y) ** 2 + (Lmouth.x-Rmouth.x) ** 2)

    if LineU < LineD:
        Pitch = math.asin(1 - (LineU/LineD))
    else:
        Pitch = -math.asin(1 - (LineD/LineU))

    Pitch_deg = math.degrees(Pitch)

    return Pitch_deg

# 画面のどこを見ているか
def face_angle(Leye, Reye, Lmouth, Rmouth, nose):
    Lborder = -20
    Rborder = 20
    Uborder = 17
    Dborder = 3

    Yaw = face_Yaw(Leye, Reye, nose)
    Pitch = face_Pitch(Leye, Reye, Lmouth, Rmouth, nose)

    if Yaw < Lborder:
        if Pitch > Uborder:
            return 1
        elif Uborder >= Pitch and Pitch > Dborder:
            return 4
        else:
            return 7
    elif Lborder <= Yaw and Yaw < Rborder:
        if Pitch > Uborder:
            return 2
        elif Uborder >= Pitch and Pitch > Dborder:
            return 5
        else:
            return 8
    else:
        if Pitch > Uborder:
            return 3
        elif Uborder >= Pitch and Pitch > Dborder:
            return 6
        else:
            return 9

# メイン処理
ans = 5
list_LZ = [0]
list_RZ = [0]
results_list = []  # 計測結果のリスト

VELOCITY_THRESHOLD = 0.05  # 速度の閾値
is_walking = False  # 現在腕振り判定中かどうか
walking_start_frame = -1  # 腕振りが開始されたフレーム番号
frame_counter = 0

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0) as pose:
    def update_frame():
        while cap.isOpened():
            global ans
            global list_LZ
            global list_RZ

            global is_walking
            global walking_start_frame
            global frame_counter

            ret, frame = cap.read()
            if not ret:
                return

            frame = cv2.flip(frame, 1)
            
            # OpenCVのBGR画像をRGBに変換
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Mediapipeでランドマークを検出
            results = pose.process(frame_rgb)
            
            if results.pose_landmarks:
                ans = face_angle(results.pose_landmarks.landmark[2], results.pose_landmarks.landmark[5], results.pose_landmarks.landmark[9], results.pose_landmarks.landmark[10],results.pose_landmarks.landmark[0])
                
            # 歩行ジェスチャ
            if results.pose_landmarks:
                # フレームカウンタの更新
                frame_counter += 1

                # 両肘のz座標を取得
                list_LZ.append(results.pose_landmarks.landmark[13].z)
                list_RZ.append(results.pose_landmarks.landmark[14].z)
                
                # 直前の40フレームを記録
                if len(list_LZ) > 40 and len(list_RZ) > 40:
                    list_LZ.pop(0)
                    list_RZ.pop(0)
                        
                    Lpeaks, _ = find_peaks(list_LZ, height=0.01, distance=20)
                    Rpeaks, _ = find_peaks(list_RZ, height=0.01, distance=20)
                    Ltroughs, _ = find_peaks(-np.array(list_LZ), height=0.15, distance=20)
                    Rtroughs, _ = find_peaks(-np.array(list_RZ), height=0.15, distance=20)

                    # ピークと谷の数
                    peaks_number = len(Lpeaks) + len(Rpeaks)
                    troughs_number = len(Ltroughs) + len(Rtroughs)

                    # ピークの数が閾値を超えているか判定
                    if peaks_number + troughs_number > 1:  # ピークが2つ以上なら継続
                        is_walking = True
                    
                    else:
                        # ピークが少なくなった場合、腕振り終了と判定
                        is_walking = False  # 腕振り終了

            # unityへの送信
            data = json.dumps({'walking': is_walking, 'LookPoint': ans})
            sock.sendto(data.encode('utf-8'), (HOST, PORT))
        
    # フレーム更新を開始
    update_frame()

# カメラを解放
#cap.release()