import sys
from watchdog.observers import Observer
from watchdog.events import *
import time
import os
import subprocess

def run_script(file):
    process = subprocess.Popen(["python3", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        return process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        return ("", "process time out")
    

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def is_target(self, event):
        return self.is_target_ends(event.src_path) and not event.is_directory

    def is_target_ends(self, path):
        return path.endswith(".scad.py")

    def on_moved(self, event):
        if self.is_target(event):
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))    
            self.on_deleted(event)
            if self.is_target_ends(event.dest_path):
                self.gen_from_py(event.dest_path)
            return
        if self.is_target_ends(event.dest_path):
            self.gen_from_py(event.dest_path)

    def get_target_file_name(self, path):
        return path[:-3]            

    def on_created(self, event):
        if self.is_target(event):
            print("file created:{0}".format(event.src_path))
            self.gen_from_py(event.src_path)
            
    def gen_from_py(self, path):
        print(f"gen from py {path}")
        out, err = run_script(path)
        if err:
            print("run script error: {}".format(err))
            return
        with open(self.get_target_file_name(path), "wb") as f:
            f.write(out)        

    def on_deleted(self, event):
        if self.is_target(event):
            print("file deleted:{0}".format(event.src_path))
            target = self.get_target_file_name(event.src_path)
            if os.path.exists(target):
                os.remove(target)

    def on_modified(self, event):
        if self.is_target(event):
            print("file modified:{0}".format(event.src_path))
            self.gen_from_py(event.src_path)

def observe_scadpy(dir):
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, dir, True)
    observer.start()
    print("start to observe dir: {}".format(dir))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    observe_scadpy(sys.argv[1])
