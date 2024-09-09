import tkinter as tk
from tkinter import ttk
from gtts import gTTS
from playsound import playsound
import datetime

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本转语音")
        self.root.geometry("400x450")
        self.root.configure(bg="#E0E0E0")
        self.root.overrideredirect(True)  # 去掉窗口边框
        self.root.attributes('-alpha', 0.9)  # 设置窗口透明度

        self.label = tk.Label(self.root, text="请输入要转换的文本：", bg="#E0E0E0")
        self.label.pack(pady=10)

        self.text_entry = tk.Entry(self.root, width=40)
        self.text_entry.pack(pady=10)

        self.speed_label = tk.Label(self.root, text="语速：", bg="#E0E0E0")
        self.speed_label.pack()
        self.speed_scale = tk.Scale(self.root, from_=0.5, to=2, orient="horizontal", resolution=0.1)
        self.speed_scale.set(1.0)
        self.speed_scale.pack()

        self.volume_label = tk.Label(self.root, text="音量：", bg="#E0E0E0")
        self.volume_label.pack()
        self.volume_scale = tk.Scale(self.root, from_=0, to=1, orient="horizontal", resolution=0.01)
        self.volume_scale.set(0.5)
        self.volume_scale.pack()

        self.convert_button = tk.Button(self.root, text="转换并播放", command=self.convert_and_play, bg="#4CAF50", fg="white")
        self.convert_button.pack()

        self.close_button = tk.Button(self.root, text="关闭", command=self.root.quit, bg="red", fg="white")
        self.close_button.pack(pady=10)

    def convert_and_play(self):
        text = self.text_entry.get()
        speed = self.speed_scale.get()
        volume = self.volume_scale.get()

        if text:
            tts = gTTS(text, lang="zh-cn", slow=speed)
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_file = f"output_{current_time}.mp3"
            
            tts.save(output_file)
            
            playsound(output_file)

            print("转换完成并播放完成")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
