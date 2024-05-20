import os
import signal
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, process_cmd):
        super().__init__()
        self.process_cmd = process_cmd
        self.process = self.start_process()

    def start_process(self):
        return subprocess.Popen(self.process_cmd, shell=True, preexec_fn=os.setsid)

    def restart_process(self):
        self.terminate_process()
        self.process = self.start_process()

    def terminate_process(self):
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith('.py') or event.src_path.endswith('.yaml'):
            print(f'File changed: {event.src_path}')
            self.restart_process()

def monitor_directory(path, process_cmd):
    event_handler = FileChangeHandler(process_cmd)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.terminate_process()
    observer.join()



if __name__ == "__main__":
    directory_to_watch = "bot_config/"
    process_command = "python bot_manager/bot_runner.py"
    monitor_directory(directory_to_watch, process_command)