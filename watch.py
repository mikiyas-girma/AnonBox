
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("Detected code modification. Restarting server...")
            restart_server()


def restart_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process.wait()
    print("Starting server...")
    server_process = subprocess.Popen(["python3", "src/flask_app.py"])


if __name__ == "__main__":
    project_dir = '.'
    observer = Observer()
    observer.schedule(MyHandler(), path=project_dir, recursive=True)
    observer.start()

    server_process = None
    restart_server()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
