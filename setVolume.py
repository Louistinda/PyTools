import tkinter as tk
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 调节音量
def set_volume(volume):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
    volume_object.SetMasterVolumeLevelScalar(volume / 100, None)

# 创建主窗口
root = tk.Tk()
root.title("音量调节")

# 创建音量滑动条
volume_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=300)
volume_scale.pack()

# 音量调节函数
def adjust_volume(event):
    volume = volume_scale.get()
    set_volume(volume)

# 绑定滑动条事件
volume_scale.bind("<B1-Motion>", adjust_volume)

# 运行主循环
root.mainloop()
