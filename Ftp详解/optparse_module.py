import optparse     # 解析命令行的命令

def optparse_study():
    op = optparse.OptionParser()
    op.add_option("-s", "--server", dest="server")
    op.add_option("-P", "--port", dest="port")      # 自定义命令行格式
    options, args = op.parse_args()
    print(options)
    print(args)
    print(options.server)
    print(options.port)

optparse_study()
# 命令行运行G:\python_study\FTP详解>python optparse_module.py -s 127.0.0.1 -P 8080
            # G:\python_study\FTP详解>python optparse_module.py -s 127.0.0.1 -P 8080 yy uu






