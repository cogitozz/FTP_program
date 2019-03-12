from socket import *
import optparse ,json,os, sys

STATUS_CODE = {
    200:"OK",
    401:"身份验证错误",
    400:"错误请求",
    "800": "文件不完整",
    "801": "文件存在",
    "802": "文件不存在",
}

class ClientHandler():
    def __init__(self):
        self.op = optparse.OptionParser()

        self.op.add_option('-s', '--server', dest='server')
        self.op.add_option('-P', '--port', dest='port')
        self.op.add_option('-u', '--username', dest='username')
        self.op.add_option('-p', '--password', dest='password')     # 自定义命令行格式

        self.options, self.args = self.op.parse_args()
        self.verify_args(self.options, self.args)           # 调用解析命令函数，解析输入的IP地址和端口号
        self.make_connection()                              # 通过解析出的IP地址和端口号进行连接服务器
        self.mainPath = os.path.dirname(os.path.abspath(__file__))  # 得到ftp_client的绝对路劲即FTP_client

    def verify_args(self, options, args):   # 解析命令函数
        server = options.server
        port = options.port
        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            exit("the ort is in 0-6535")

    def make_connection(self):      # 连接服务器函数
        self.client_socket = socket()
        self.client_socket.connect((self.options.server, int(self.options.port)))

#***************************上面是相当于类的初始化内容，包括解析输入的IP地址和端口号，连接服务器*****************************#
#***************************下面是与服务器交互时要用到的对应的函数,******************************#
# 需要什么功能就写对应的函数，在客户端写应该发送什么以及收到服务器返回的结果后怎么处理即可******************************#

    def interactive(self):          # 与服务器进行交互，选择相应函数，首先会进行验证登录函数，
                                    # 然后根据命令选择对应的函数
        print("begin to interactive.....")
        if self.authenticate():
            while 1:
                cmd_info = input("[%s]"%self.current_dir).strip()
                cmd_list = cmd_info.split()     # 将输入的内容拆分
                if hasattr(self, cmd_list[0]):  # 根据输入的动作做相应的函数调用
                    func = getattr(self, cmd_list[0])
                    func(*cmd_list)

    def response(self):         # 接收函数
        data = self.client_socket.recv(1024).decode('utf-8')
        data = json.loads(data)
        return data

# *****************************验证登录***************************************#
    def authenticate(self):     # 验证用户名和密码是否为空
        if self.options.username is None or self.options.pasword is None:
            username = input("username: ")
            password = input("password: ")
            return self.get_auth_result(username, password)
        return self.get_auth_result(self.options.username, self.options.pasword)

    def get_auth_result(self, user, pwd):   # 如果不为空就将相应的操作名和用户名和密码以字典的形式传给服务器进行验证
        data = {
            "action": "auth",
            "username": user,
            "password": pwd
        }
        self.client_socket.send(json.dumps(data).encode('utf-8'))
        response = self.response()
        # print(response)
        print("response:", response["status_code"])
        if response["status_code"] == 200:
            self.user = user
            self.current_dir = user
            print(STATUS_CODE[200])
            return True
        else:
            print(STATUS_CODE[response["status_code"]])
# *****************************验证登录***************************************#

# *****************************文件上传***************************************#
    def put(self, *cmd_list):
        # put 001.png images     # put在命令行的使用格式
        action, local_path, target_path = cmd_list
        local_path = os.path.join(self.mainPath, local_path)    # 将绝对路径与本地要上传的文件路劲拼接为本地路劲，注意这是在要上传的文件与ftp_client同一目录下的写法
        file_name = os.path.basename(local_path)        # 取本地路劲的文件名，dirname()取路劲
        file_size = os.stat(local_path).st_size     # 文件大小

        data = {        # 这个就是服务端能够识别客户端的命令且执行对应函数的原因
            "action": "put",
            "file_name": file_name,
            "file_size": file_size,
            "target_path": target_path
        }

        self.client_socket.send(json.dumps(data).encode('utf-8'))
        is_exist = self.client_socket.recv(1024).decode('utf-8')

        has_sent = 0
        if is_exist == "800":       # 收到服务端发来的文件不完整信息，
            # 文件不完整
            choice = input('the file exist,but not enough,[Y/N]').strip()
            if choice.upper() == "Y":       # 如果选择N则是重新发送
                self.client_socket.sendall("Y".encode('utf-8'))     # 告诉服务端我要接着发送
                continue_position = self.client_socket.recv(1024).decode('utf-8')
                has_sent += int(continue_position)

        elif is_exist == "801":
            # 文件完全存在
            print("文件已存在")
            return
        # else:
        #     pass

        f = open(local_path, "rb")
        f.seek(has_sent)    # 如果收到文件不完整，则从has_sent处接着发送文件
        while has_sent < file_size:     # 如果收到服务端返回的是文件不存在，则从头开始发送文件，
            data = f.read(1024)
            self.client_socket.sendall(data)
            has_sent += len(data)
            self.show_progress(has_sent, file_size)
        f.close()
        print("成功上传")

    # *********************显示进度条*****************************#
    def show_progress(self, has, total):
        self.last = 0
        rate = float(has) / float(total)
        rate_num = int(rate * 100)
        if self.last != rate_num:
            sys.stdout.write("%s%% %s\r" % (rate_num, "#" * rate_num))
        self.last = rate_num
    # *********************显示进度条*********************#
# *****************************文件上传***************************************#


# *****************************命令函数***************************************#

    # ********************ls命令***********************#
    def ls(self, *cmd_list):
        data = {
            "action":"ls"
        }
        self.client_socket.sendall(json.dumps(data).encode('utf-8'))
        data = self.client_socket.recv(1024).decode('utf-8')
        print(data)
    # ********************ls命令***********************#

    # ********************cd命令***********************#
    def cd(self,*cmd_list):
        data = {
            "action":"cd",
            "dirname":cmd_list[1]
        }
        self.client_socket.sendall(json.dumps(data).encode('utf-8'))
        data = self.client_socket.recv(1024).decode('utf-8')
        print(os.path.basename(data))
        self.current_dir = os.path.basename(data)
    # ********************cd命令***********************#

    # ********************mkdir命令***********************#
    def mkdir(self, *cmd_list):
        data = {
            "action": "mkdir",
            "dirname": cmd_list[1]
        }
        self.client_socket.sendall(json.dumps(data).encode('utf-8'))
        data = self.client_socket.recv(1024).decode('utf-8')
    # ********************mkdir命令***********************#

# *****************************命令函数***************************************#

