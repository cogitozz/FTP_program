import os, sys
PATH = os.path.dirname(os.path.abspath(__file__))
print(PATH)
sys.path.append(PATH)

from ftp_client import ClientHandler


if __name__ == '__main__':
    client_start = ClientHandler()  # 1、生成一个类，用来调用客户端的一些处理函数。
                                    # 并且初始化一些数据，比如解析命令并连接服务器
    client_start.interactive()  # 2、连接上服务器后与服务器进行交互









