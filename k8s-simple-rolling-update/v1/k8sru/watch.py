from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, filepath, callback):
        self.filepath = filepath
        self.callback = callback

    def on_any_event(self, event):
        if event.src_path == self.filepath:
            self.callback(filepath=self.filepath)


def filepath(filepath, callback):
    event_handler = MyEventHandler(filepath, callback)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    return observer
