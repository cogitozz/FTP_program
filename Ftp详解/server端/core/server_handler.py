import socketserver, json, os
import configparser     # 用来操作配置文件
from conf  import  settings

STATUS_CODE = {
    200:"OK",
    401:"身份验证错误",
    400:"错误请求",
    "800": "文件不完整",
    "801": "文件存在",
    "802": "文件不存在",
}

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while 1:
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode('utf-8'))     #  1、得到输入的命令
# data的形式如下
# data = {"action":"auth",
#        "username":"yuan",
#        "password":123
#        }

            if data.get("action"):      # 2、取命令对应的函数并执行
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    func(**data)
                else:
                    print("Invalid cmd")
            else:
                print("Invalid cmd")

    # ***************************下面是收到客户端发来的命令做相应的处理的函数，一个命令对应相应的函数,******************************#
    def send_response(self, state_code):        # 因为会有许多操作要返回数据到客户端，
                                                # 所以直接写一个发送数据到客户端的函数，用到的时候直接调用
        response = {'status_code': state_code}
        self.request.sendall(json.dumps(response).encode('utf-8'))

#********************验证登录******************************#
    def auth(self, **data):
        print(data)
        username = data["username"]
        password = data['password']

        user = self.authenticate(username, password)
        if user:
            self.send_response(200)
        else:
            self.send_response(401)

    def authenticate(self, user, pwd):
        cfg = configparser.ConfigParser()       # 将一些信息写在配置文件中，使用的时候可以直接用，而且便于添加和修改，这其实就是和数据库是一样的，只是这里调用的是配置文件，也可以从数据库中提取数据
        cfg.read(settings.ACCOUNT_PATH)

        if user in cfg.sections():
            if cfg[user]["Password"] == pwd:
                self.user = user        # 这个保证可以在其他的函数中使用user
                self.mainPath = os.path.join(settings.BASE_DIR, "home", self.user)  # 很重要
                print(STATUS_CODE[200])
                return user
#********************验证登录******************************#

# ********************上传文件******************************#
    def put(self, **data):
        print("data",data)  # 可以看到在命令行输入的内容被转换为字典的形式
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path = data.get("target_path")

        abs_path = os.path.join(self.mainPath, target_path, file_name)
        print(abs_path)     # 得到要将文件上传到服务端的存放地址

        has_received = 0
        if os.path.exists(abs_path): # 判断文件在不在
            file_has_size = os.stat(abs_path).st_size
            if file_has_size < file_size:
                # 断点续传
                self.request.sendall("800".encode('utf-8'))     # 告诉客户端文件不完整
                choice = self.request.recv(1024).decode('utf-8')
                if choice == "Y":                               #   收到客户端发来的接着上传的命令
                    self.request.sendall(str(file_has_size).encode('utf-8'))    # 告诉客户端服务端接收了多少文件
                    has_received += file_has_size
                    f = open(abs_path, "ab")
                else:       # 如果客户端选择N，则打开这个不完整的文件从头开始重新写入，覆盖掉原来不完整的内容
                    f = open(abs_path, "wb")

            else:
                self.request.sendall("801".encode('utf-8'))
                return

        else:
            self.request.sendall('802'.encode('utf-8'))     # 如果文件不存在则告诉客户端文件不存在
            f = open(abs_path, "wb")        # 并且在服务端对应位置新建一个该文件

        while has_received < file_size:
            try:
                data = self.request.recv(1024)      # 接收客户端发送来的文件
            except Exception as e:
                break
            f.write(data)           # 并写入到服务端新建的那个文件里
            has_received += len(data)

        f.close()
# ********************上传文件******************************#

# ********************命令函数******************************#

    # ********************ls命令***********************#
    def ls(self, **data):
        file_list = os.listdir(self.mainPath)
        file_str = "\n".join(file_list)
        if not len(file_list):
            file_str = '<empty dir>'
        self.request.sendall(file_str.encode('utf-8'))
    # ********************ls命令***********************#

    # ********************cd命令***********************#
    def cd(self, **data):
        dirname = data.get("dirname")
        if dirname == "..":
            self.mainPath = os.path.dirname(self.mainPath)
        else:
            self.mainPath = os.path.join(self.mainPath, dirname)
        self.request.sendall(self.mainPath.encode('utf-8'))
    # ********************cd命令***********************#

    # ********************mkdir命令***********************#
    def mkdir(self, **data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainPath,dirname)
        if not os.path.exists(path):
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
            self.request.sendall("success".encode('utf-8'))
        else:
            self.request.sendall("dirname exist".encode('utf-8'))
    # ********************mkdir命令***********************#

# ********************命令函数******************************#




