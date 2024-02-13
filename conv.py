import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
from threading import Thread
import os

class CustomStyle(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('clam')
        self.configure('.', background='#333333', foreground='#ffffff')
        self.configure('TButton', padding=10, relief='flat', foreground='#ffffff', background='#666666')
        self.configure('TLabel', padding=10, relief='flat', foreground='#ffffff', background='#333333')
        self.configure('TCheckbutton', padding=10, relief='flat', foreground='#ffffff', background='#333333')
        self.configure('Horizontal.TProgressbar', troughcolor='#444444', bordercolor='#444444', background='#007acc', foreground='#007acc')
        self.map('Horizontal.TProgressbar', background=[('active', '#005f87'), ('disabled', '#666666')])

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Converter")
        self.root.geometry("520x300")
        self.style = CustomStyle()

        self.input_file = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.use_cuda = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # Input File Selector
        ttk.Label(self.root, text="Select Input Video:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(self.root, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=10, pady=10)

        # Output Directory Selector
        ttk.Label(self.root, text="Select Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(self.root, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=10, pady=10)

        # CUDA Checkbox
        self.cuda_checkbox = ttk.Checkbutton(self.root, text="CUDA", variable=self.use_cuda)
        self.cuda_checkbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        # Convert Button
        self.convert_button = ttk.Button(self.root, text="Convert", state=tk.DISABLED, command=self.start_conversion)
        self.convert_button.grid(row=3, column=0, columnspan=3, pady=10)

        # Progressbar
        self.progressbar = ttk.Progressbar(self.root, style="Horizontal.TProgressbar", orient="horizontal", mode="determinate", length=500)
        self.progressbar.grid(row=4, column=0, columnspan=3, pady=10, padx=10)

    def browse_input(self):
        input_file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv;*.ts;*.mov")])
        if input_file:
            self.input_file.set(input_file)
            self.update_convert_button_state()

    def browse_output(self):
        output_directory = filedialog.askdirectory()
        if output_directory:
            self.output_directory.set(output_directory)
            self.update_convert_button_state()

    def update_convert_button_state(self):
        if self.input_file.get() and self.output_directory.get():
            self.convert_button["state"] = tk.NORMAL
        else:
            self.convert_button["state"] = tk.DISABLED

    def start_conversion(self):
        input_file = self.input_file.get()
        output_directory = self.output_directory.get()
        output_filename = os.path.splitext(os.path.basename(input_file))[0] + "_conv.mp4"
        output_file = os.path.join(output_directory, output_filename)

        input_file_size = os.path.getsize(input_file)

        cmd = ["ffmpeg", "-i", input_file, "-c:v", "h264_nvenc" if self.use_cuda.get() else "libx264", output_file]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Process started : " + output_file)
        def update_progress():
            output_file_size = 0
            while True:
                if os.path.exists(output_file):
                    output_file_size = os.path.getsize(output_file)
                    progress_percent = (output_file_size / input_file_size) * 100
                    self.progressbar['value'] = progress_percent
                    print('Progress: {:.2f}%'.format(progress_percent))
                if output_file_size >= input_file_size:
                    break
            print("Process ended : " + output_file)
        thread = Thread(target=update_progress)
        thread.start()

        # Use a separate thread to wait for the process to finish
        def wait_for_completion():
            process.communicate()
            thread.join()

        wait_thread = Thread(target=wait_for_completion)
        wait_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()
