import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial.tools.list_ports
import serial
from collections import deque
import datetime
import csv
import threading

# 設定 customtkinter 使用暗色主題
ctk.set_appearance_mode("Dark")
distance = 0
def volume(x):
    y = ((170- x)/(170-65))*60
    return y



def detect_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'Arduino' in port.description:
            return port.device
    return None


def init_csv(filename='yeasting_log.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Data'])


def initr_csv(filename='yeasting_log_real.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Data'])        


def start_collecting():
    global ser, collecting
    arduino_port = detect_arduino_port()
    if arduino_port:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        collecting = True
        animate()
    else:
        print("No Arduino detected.")


def stop_collecting():
    global collecting
    if collecting:
        ser.close()
        collecting = False


def animate():
    global line1, ax1, times, data, data1, fig1, canvas1, line2, ax2, fig2,distance
    if collecting and ser.in_waiting:
        line_data = ser.readline().decode('utf-8').strip()
        try:
            distance = int(line_data)
            now = datetime.datetime.now()
            delta_t = (now - start_time).total_seconds()
            if len(times) == 0 or delta_t > times[-1]:
                times.append(delta_t)
                data.append(distance)
                # 添加轉換後的數據到 data1
                y = volume(distance)
                data1.append(y)
                print(f"Volume data: {y}; distance: {distance}")

                with open("yeasting_log.csv", 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([delta_t, distance])
                with open("yeasting_log_real.csv", "a", newline='', encoding='utf-8') as file1:
                    writer1 = csv.writer(file1)
                    writer1.writerow([delta_t, volume(distance)])
                # 更新第一個圖表
                line1.set_data(times, data)
                ax1.set_xlim(times[0], max(1800, times[-1]))
                ax1.figure.canvas.draw()
                # 更新第二個圖表
                line2.set_data(times, data1)  # 確保這裡使用的是 data1
                
                ax2.set_xlim(times[0], max(1800, times[-1]))
                ax2.figure.canvas.draw()  # 繪製第二個圖表的畫布

        except ValueError:
            print(f"Received non-integer value: {line_data}")

    if collecting:
        app.after(500, animate)


def update_distance_label():
    global distance
    distance_label.configure(text=f"距離：{distance} mm")  # 更新標籤上的文本
    volume_label.configure(text=f"體積: {volume(distance):.3f} 平方毫米") 
    side_frame.after(1000, update_distance_label)  # 每1000毫秒（1秒）更新一次

# Initialize for two charts
filename = 'yeasting_log.csv'
times = deque(maxlen=1800)
data = deque(maxlen=1800)
data1 = deque(maxlen=1800)

# Chart 1
fig1 = Figure()
ax1 = fig1.add_subplot(111)
line1, = ax1.plot([], [], lw=2)
ax1.set_ylim(0, 300)  # 可根據您的數據調整
ax1.set_xlim(0, 1800)  # 可根據您的數據調整
ax1.set_xlabel('Time (s)', fontsize=15)
ax1.set_ylabel('Distance (mm)', fontsize=15)
ax1.set_title('Real-Time Distance Measurement Chart', fontsize=24)
line1.set_label('Distance (mm)')
ax1.legend()
# Chart 2 (這裡可以設置第二個圖表的特定屬性)
fig2 = Figure()
ax2 = fig2.add_subplot(111, )
line2, = ax2.plot([], [], lw=2,color='red')
ax2.set_ylim(0, 100)  # 可根據您的數據調整
ax2.set_xlim(0, 1800)  # 可根據您的數據調整
ax2.set_xlabel('Time (s)', fontsize=15)
ax2.set_ylabel('Distance (mm)', fontsize=15)
ax2.set_title('Real-Time Volume Measurement Chart', fontsize=24)
line2.set_label('Volume')
ax2.legend()
start_time = datetime.datetime.now()
collecting = False

# Create GUI
app = ctk.CTk()
app.title("Real-Time Data Visualization")
app.geometry("800x800")  # 增加高度以容納兩個圖表
large_font = ('Helvetica', 20)
# Side frame for buttons
side_frame = ctk.CTkFrame(app)
side_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

# Start and stop buttons inside side frame
start_button = ctk.CTkButton(side_frame, text="Start", command=start_collecting)
start_button.pack(pady=10)

stop_button = ctk.CTkButton(side_frame, text="Stop", command=stop_collecting)
stop_button.pack(pady=10)


distance_label = ctk.CTkLabel(side_frame, text="距離：",font=large_font)
distance_label.pack(pady=20)
volume_label = ctk.CTkLabel(side_frame, text="體積：",font=large_font)

volume_label.pack(pady=20)
# 啟動更新標籤的循環
update_distance_label()



# Embed matplotlib figure for Chart 1
canvas1 = FigureCanvasTkAgg(fig1, master=app)
canvas_widget1 = canvas1.get_tk_widget()
canvas_widget1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Embed matplotlib figure for Chart 2
canvas2 = FigureCanvasTkAgg(fig2, master=app)
canvas_widget2 = canvas2.get_tk_widget()
canvas_widget2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

init_csv()
initr_csv()
app.mainloop()
#------------------------------------------------------------------------------------#
