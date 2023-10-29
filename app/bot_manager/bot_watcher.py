from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotWatcher(FileSystemEventHandler):
    def __init__(self):
        self.observer = Observer()
        self.watch = None
        self.callback = None
        self.enabled = False

    def start_watching_path(self, file_path, reload_callback):
        print(f'watching {file_path}')
        
        if self.watch: 
            self.observer.unschedule(self.watch) 
        
        self.callback = reload_callback
        self.watch = self.observer.schedule(self, path=file_path, recursive=True)
        self.enabled = True

        
    def on_modified(self, event):
        if not self.enabled:
            return
        
        print(f"{event.src_path} modified")
        self.enabled = False 
        self.callback(event.src_path)
            
    def start(self):
        self.observer.start()
        
    def stop(self):
        self.observer.stop()
        self.observer.join()
        
    def resume(self):
        self.enabled = True



# class BotWatcher(FileSystemEventHandler):
#     def __init__(self):
#         self.observer = Observer()
#         self.watches = {}

#     def start_watching_path(self, file_path, reload_callback, file_extensions = None):
#         print(f'watching {file_path} {file_extensions}')

#         self.stop_watching_path(file_path)

#         self.watches[file_path] = {
#             'watch': self.observer.schedule(self, path=file_path, recursive=True), 
#             'callback': reload_callback,
#             'extensions': file_extensions
#         }

#     def stop_watching_path(self, file_path):
#         watch = self.watches.get(file_path)
#         if (watch is not None):
#             print(f'stop watching {file_path}')
#             self.observer.unschedule(watch['watch']) 
#             del self.watches[file_path]
        

#     def on_modified(self, event):
#         print("modified")
#         watch = self.watches.get(event.src_path)

#         if watch is not None: 
#             if watch['extensions'] is None or (not event.is_directory and any(event.src_path.endswith(ext) for ext in watch['extensions'])):
#                 print(f'{event.src_path} has been modified')
#                 watch['callback'](event.src_path)
            
#     def start(self):
#         self.observer.start()

#     def stop(self):
#         self.observer.stop()
#         self.observer.join()