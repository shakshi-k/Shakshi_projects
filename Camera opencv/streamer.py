from __future__ import annotations
import cv2
import traceback
from queue import Queue

class Streamer:
    def __init__(self,url):
        self.url = url
        self.frame_count = 0
        self.cap = cv2.VideoCapture(url)
        self.running = True
        self.writer_queue = Queue(maxsize=1)
    def start(self):
        while self.running:
            ret,frame = self.cap.read()

            if ret:
                
                data = dict()
                self.frame_count+=1
                data['frame'] = frame
                data['frame_count'] = self.frame_count

                if self.writer_queue.empty():
                    self.writer_queue.put(data)

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()
        self.running=False
        