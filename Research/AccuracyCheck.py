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

# Mediapipeのセットアップ
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# Tkinterのウィンドウを作成
window = tk.Tk()
window.title("ジェスチャーチェック")

# フォントを作成
custom_font = font.Font(family="Helvetica", size=48)

# 左側のフレームにカメラ映像を表示
left_frame = tk.Frame(window)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)
label = tk.Label(left_frame)
label.pack(expand=True, fill=tk.BOTH)

# 右側のフレームにリストボックスを配置
right_frame = tk.Frame(window)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# リストボックスの作成と配置
gesture_listbox = tk.Listbox(right_frame, height=20, width=30, font=custom_font)
gesture_listbox.pack()

# カメラを起動
cap = cv2.VideoCapture(0)
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

    gesture_listbox.insert(tk.END, Yaw_deg)

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

    gesture_listbox.insert(tk.END, Pitch_deg)

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
            gesture_listbox.insert(tk.END, 1)
            return 1
        elif Uborder >= Pitch and Pitch > Dborder:
            gesture_listbox.insert(tk.END, 4)
            return 4
        else:
            gesture_listbox.insert(tk.END, 7)
            return 7
    elif Lborder <= Yaw and Yaw < Rborder:
        if Pitch > Uborder:
            gesture_listbox.insert(tk.END, 2)
            return 2
        elif Uborder >= Pitch and Pitch > Dborder:
            gesture_listbox.insert(tk.END, 5)
            return 5
        else:
            gesture_listbox.insert(tk.END, 8)
            return 8
    else:
        if Pitch > Uborder:
            gesture_listbox.insert(tk.END, 3)
            return 3
        elif Uborder >= Pitch and Pitch > Dborder:
            gesture_listbox.insert(tk.END, 6)
            return 6
        else:
            gesture_listbox.insert(tk.END, 9)
            return 9
 
# スクリプトの開始時間を記録
start_time = time.time()

# 動作時間（秒単位）
DURATION = 10

# メイン処理
list_LZ = [0]
list_RZ = [0]
results_list = []  # 計測結果のリスト
list_Lv = []
measurement_active = False  # 測定中フラグ
measurement_start_time = None
ok_count = 0
no_count = 0
vok_count = 0
vno_count = 0
look_point = 0
VELOCITY_THRESHOLD = 0.05  # 速度の閾値
is_walking = False  # 現在腕振り判定中かどうか
walking_start_frame = -1  # 腕振りが開始されたフレーム番号
frame_counter = 0

def start_measurement(event):
    """計測開始（キー: 's'）"""
    global measurement_start_time, measurement_active, ok_count, no_count, vok_count, vno_count
    measurement_start_time = time.time()
    measurement_active = True
    ok_count = 0
    no_count = 0
    vok_count = 0
    vno_count = 0

def stop_measurement():
    """計測終了"""
    global measurement_active, results_list, ok_count, no_count, vok_count, vno_count
    measurement_active = False
    results_list.append({'OK': ok_count, 'NO': no_count, 'vOK': vok_count, 'vNO': vno_count})

def stop_program(event):
    """プログラム終了（キー: 'q'）"""
    global results_list
    # 全ての測定結果を出力して終了
    print("All Measurements:")
    for i, result in enumerate(results_list, 1):
        print(f"Measurement {i}: OK={result['OK']}, NO={result['NO']}, vOK={result['vOK']}, vNO={result['vNO']}")
    cap.release()
    window.destroy()

def up_point(event):
    global look_point
    look_point += 1
    print(look_point)

def down_point(event):
    global look_point
    look_point -= 1
    print(look_point)

# キーイベント設定
window.bind('<s>', start_measurement)  # 's'キーで計測開始
window.bind('<q>', stop_program)       # 'q'キーでプログラム終了
window.bind('<n>', up_point)
window.bind('<m>', down_point)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0) as pose:
    def update_frame():
        global list_LZ
        global list_RZ
        global list_Lv
        global measurement_active
        global start_time
        global measurement_start_time
        global ok_count
        global no_count
        global vok_count
        global vno_count
        global is_walking
        global walking_start_frame
        global frame_counter

        # 現在の時間を取得して経過時間を計算
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # 指定時間を超えた場合に停止
        '''
        if elapsed_time > DURATION:
            #print({'OK': ok, 'NO': no})
            plt.plot(list_Lv)
            plt.show()
            window.destroy()  # Tkinterウィンドウを閉じる
            cap.release()  # カメラを解放する
            return
        '''

        ret, frame = cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        
        # OpenCVのBGR画像をRGBに変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Mediapipeでランドマークを検出
        results = pose.process(frame_rgb)
        
        # ランドマークを描画
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        
        # OpenCVのBGR画像をPIL画像に変換
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Tkinterのラベルに画像を設定
        label.imgtk = imgtk
        label.configure(image=imgtk)

        # ジェスチャ検出結果を仮でリストに追加（ここを検出ロジックで更新する）
        gesture_listbox.delete(0, tk.END)
        gesture_listbox.insert(tk.END, elapsed_time)
        if measurement_active:
            gesture_listbox.insert(tk.END, "測定中")

        # 視線ジェスチャ
        gesture_listbox.insert(tk.END, "Look Jesture")
        gesture_listbox.insert(tk.END, look_point)

        if results.pose_landmarks:
            ans = face_angle(results.pose_landmarks.landmark[2], results.pose_landmarks.landmark[5], results.pose_landmarks.landmark[9], results.pose_landmarks.landmark[10],results.pose_landmarks.landmark[0])
            if measurement_active:
                if ans == look_point:
                    vok_count += 1
                else:
                    vno_count += 1

        # 歩行ジェスチャ
        gesture_listbox.insert(tk.END, "Walk Jesture")

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
                    gesture_listbox.insert(tk.END, "OK!")  # 腕振り継続中
                    if measurement_active:
                        ok_count += 1
                else:
                    # ピークが少なくなった場合、腕振り終了と判定
                    is_walking = False  # 腕振り終了
                    # print("腕振り終了（ピーク数による終了判定）")
                    gesture_listbox.insert(tk.END, "NO!")
                    if measurement_active:
                        no_count += 1
            else:
                gesture_listbox.insert(tk.END, "NO!")  # 腕振りしていない場合の出力
                if measurement_active:
                    no_count += 1

        # ループの所要時間計測        
        '''
        end_time = time.time()
        s_time = end_time - current_time
        print(f"update_frame took {s_time:.3f} seconds.")
        '''
        
        # 計測終了判定
        if measurement_active and time.time() - measurement_start_time >= DURATION:
            stop_measurement()

        # 1ms後に再度この関数を呼び出す
        window.after(1, update_frame)
    
    # フレーム更新を開始
    update_frame()
    
    # Tkinterのメインループを開始
    window.mainloop()

# カメラを解放
#cap.release()
