import optparse     # 解析命令行的命令
import socketserver
from conf import settings
from core import server_handler


"""
该文件的代码仅仅只是命令行参数的解析，不涉及其他的内容，当开始启动相应的功能是转到另一个文件去
"""


class ArgvHandler():

    def __init__(self):
       # print("ok")
        self.op = optparse.OptionParser()
        options, args = self.op.parse_args()

        self.verify_args(options, args)


    def verify_args(self, options, args):
        cmd = args[0]
        # 接下来就是要判断cmd对应的方法在该类里有没有，有就执行该方法。
        # 可以用if—else，也可以将可能的值放在字典里，通过字典的方式检查有没有该方法
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            func()          # 这是用的反射的方法，只要下面有cmd对应的方法就可以调用

    def start(self):
        print("workng...")
        s = socketserver.ThreadingTCPServer((settings.IP, settings.PORT),
                                            server_handler.ServerHandler)
                                                # 将一些常量写在设置文件里，方便修改
        s.serve_forever()

