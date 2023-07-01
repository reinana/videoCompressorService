import socket
import json
import os
import subprocess
import time
# Tkinterモジュールのインポート
import tkinter
from tkinter import ttk
from tkinter import filedialog

# サーバのホストとポート
HOST = 'localhost'
PORT = 12345

# サポートされているサービス
SERVICES = ['compress', 'change_resolution', 'change_aspect_ratio', 'convert_to_audio', 'create_gif']
stream_rate = 4096

# RESULTのパス
RESULT_PATH = 'result'
if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)

def handle_file(service_type, video_path, value):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # 取得した画像ファイルをバイナリ形式で読み込む
    with open(video_path, mode='rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0,0)

        request = {'type': service_type, 'value': value, 'data_length': filesize}
        client_socket.send(json.dumps(request).encode('utf-8'))
        # client_socket.send(filesize.to_bytes(4,"big"))
        time.sleep(1)
        if filesize > pow(2,32):
            raise Exception('File must be below 2GB.')
        
        data = f.read(4096)
        while data:
            client_socket.send(data)
            data = f.read(4096)
        

    # サーバからのレスポンスを受け取る
    re_data = client_socket.recv(1024)
    time.sleep(1)
    # レスポンスを解析し、圧縮されたファイルを保存する
    response = json.loads(re_data.decode())
    print(response)
    data_length = int(response['data_length'])
    
    # RESULT_PATHのファイル数を出力
    count_files = sum(os.path.isfile(os.path.join(RESULT_PATH, name)) for name in os.listdir(RESULT_PATH))

    if response['type'] == 'compress':
        with open(f'{RESULT_PATH}/compressed({count_files}).mp4', 'ab') as f:
            while data_length > 0:
                response_file_data = client_socket.recv(data_length if data_length <= stream_rate else stream_rate)
                f.write(response_file_data)
                data_length = data_length - len(response_file_data)
                
        print(f'Compression completed. Compressed video saved as {RESULT_PATH}/compressed({count_files}).mp4')



    # サーバとの接続を閉じる
    client_socket.close()




# ファイルを選択する
def select_file():
    file_path = filedialog.askopenfilename()
    entry_file_path.insert(0, file_path)
    print(file_path)

# GUIの作成
root = tkinter.Tk()
# ウィンドウの名前を設定
root.title('Video Compressor')
# ウィンドウの大きさを設定
# root.geometry("400x200")

#オブジェクトの定義
# Style - Theme
ttk.Style().theme_use('classic')

# Frame 
frame_selectfile = ttk.Frame(
    root, 
    padding=20,
    borderwidth=5, 
    relief='sunken'
)
frame_compress = ttk.Frame(
    root, 
    padding=20,
    relief='ridge'
)
frame_resolution = ttk.Frame(
    root, 
    padding=20,
    relief='ridge'
)
frame_aspect = ttk.Frame(
    root, 
    padding=20,
    relief='ridge'
)
frame_to_audio = ttk.Frame(
    root, 
    padding=20,
    relief='ridge'
)
frame_gif = ttk.Frame(
    root, 
    padding=20,
    relief='ridge'
)
compression_img = tkinter.PhotoImage(file='./images/video_compression.png')
labelimg = ttk.Label(
    root,
    foreground = '#1155ee',
    padding = (5,10),
    font = ('Times New Roman',20),
    wraplength = 400,
    image = compression_img,
    compound = 'left')


# fileを選ぶ
entry_file_path = ttk.Entry(
    frame_selectfile)
# filedaialogを開くボタン
button_select_file = ttk.Button(
    frame_selectfile,
    text = 'Select file',
    command=lambda:select_file())

# Radiobutton 1
v1 = tkinter.StringVar()
rb1 = ttk.Radiobutton(
    frame_compress,
    padding = (15,5),
    text='High',
    value='High',
    variable=v1)

# Radiobutton 2
rb2 = ttk.Radiobutton(
    frame_compress,
    padding = (10,3),
    text='Medium',
    value='Medium',
    variable=v1)
# Radiobutton 3
rb3 = ttk.Radiobutton(
    frame_compress,
    padding = (10,3),
    text='Low',
    value='Low',
    variable=v1)

# Button
compression_button = ttk.Button(
    frame_compress,
    text='compress',
    padding=(10),
    command=lambda : handle_file('compress', entry_file_path.get(), v1.get()))


#レイアウト
labelimg.grid(row=0,column=0)

frame_selectfile.grid(row=1, column=0, pady=30, sticky=tkinter.W + tkinter.E)
frame_compress.grid(row=2, column=0, sticky=tkinter.W + tkinter.E)
frame_resolution.grid(row=3, column=0, sticky=tkinter.W + tkinter.E)
frame_aspect.grid(row=4, column=0, sticky=tkinter.W + tkinter.E)
frame_to_audio.grid(row=5, column=0, sticky=tkinter.W + tkinter.E)
frame_gif.grid(row=6, column=0, sticky=tkinter.W + tkinter.E)

#frame_selectfile
entry_file_path.grid(row=1,column=0) 
button_select_file.grid(row=1,column=2)
# frame_compress
rb1.grid(row=0, column=0) 
rb2.grid(row=0, column=1) 
rb3.grid(row=0, column=2)
compression_button.grid(row=0, column=3)
# frame_resolution
# frame_aspect
# frame_to_audio
# frame_gif


# イベントループ（TK上のイベントを捕捉し、適切な処理を呼び出すイベントディスパッチャ）
root.mainloop()
# 動画ファイルを圧縮する
# 動画の解像度を変更する
# 動画の縦横比を変更する
# 動画をオーディオに変換する
# 時間範囲から GIFを作成する