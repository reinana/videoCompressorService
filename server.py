import socket
import json
import os
import subprocess
import time

# サーバのホストとポート
HOST = 'localhost'
PORT = 12345

stream_rate = 4096
# FFMPEGのパス
FFMPEG_PATH = 'path/to/ffmpeg'
if not os.path.exists(FFMPEG_PATH):
    os.makedirs(FFMPEG_PATH)

# サポートされているサービス
SERVICES = ['compress', 'change_resolution', 'change_aspect_ratio', 'convert_to_audio', 'create_gif']
COMPRESS_RATE = {'High': 23, 'Medium': 30, 'Low': 40}

# FFMPEGを使用して動画を圧縮する
def compress_video(original_path, value):
    print("compress function")
    compressed_path = f'{FFMPEG_PATH}/compressed.mp4'
    command = ['ffmpeg', "-i", original_path, "-crf", f'{COMPRESS_RATE[value]}', compressed_path]
    subprocess.call(command)
    return compressed_path
# 動画の解像度を変更する
def change_resolution(value, data_length):
    pass
# 動画の縦横比を変更する
def change_aspect_ratio():
    pass
# 動画をオーディオに変換する
def convert_to_audio():
    pass
# 時間範囲から GIFを作成する
def create_gif():
    pass

def handle_client_connection(client_socket):
    # クライアントからのデータを受け取る
    data = client_socket.recv(1024)
    print(data)
    time.sleep(1)
    request = json.loads(data.decode('utf-8'))
    r_type = request['type']
    value = request['value']
    data_length = int(request['data_length'])
    print(data_length)

    # 動画のファイルを受け取って保存
    with open(f'{FFMPEG_PATH}/original-data.mp4', mode='ab') as f:
        while data_length > 0:
            data = client_socket.recv(data_length if data_length <= stream_rate else stream_rate)
            f.write(data)
            data_length = data_length - len(data)
    subprocess.call(["ffprobe", f'{FFMPEG_PATH}/original-data.mp4'])
    # 動画ファイルを圧縮する
    if r_type == 'compress':
        file_path = compress_video(f'{FFMPEG_PATH}/original-data.mp4', value)
    # 動画の解像度を変更する
    elif r_type == 'change_resolution':
        file_path = change_resolution(f'{FFMPEG_PATH}/original-data.mp4', value)


    # 動画の縦横比を変更する
    elif r_type == 'change_aspect_ratio':
        file_path = change_aspect_ratio(f'{FFMPEG_PATH}/original-data.mp4', value)


    # 動画をオーディオに変換する
    elif r_type == 'convert_to_audio':
        file_path = compress_video(f'{FFMPEG_PATH}/original-data.mp4', value)


    # 時間範囲から GIFを作成する
    elif r_type == 'create_gif':
        file_path = create_gif(f'{FFMPEG_PATH}/original-data.mp4', value)

    # ファイルをクライアントに送信する
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0,0)

        response = {'type': r_type, 'data_length': filesize}
        print(response)
        client_socket.sendall(json.dumps(response).encode('utf-8'))
        time.sleep(1)
        if filesize > pow(2,32):
            raise Exception('File must be below 2GB.')
        
        data = f.read(4096)
        while data:
            client_socket.send(data)
            data = f.read(4096)

    # クライアントとの接続を閉じる
    client_socket.close()

def start_server():
    # サーバソケットを作成し、接続を待機する
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server listening on {HOST}:{PORT}')

    while True:
        # クライアントからの接続を受け入れる
        client_socket, address = server_socket.accept()
        print(f'Connected to client: {address}')

        # クライアントとの通信を処理する
        handle_client_connection(client_socket)

if __name__ == '__main__':
    start_server()
