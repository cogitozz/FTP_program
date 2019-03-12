import os,sys


PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PATH = os.path.dirname(os.path.dirname(__file__))
print(PATH)
sys.path.append(PATH)       # 为了能够直接使用from core import main


from core import main
if __name__ == '__main__':
    main.ArgvHandler()











