import cv2
import threading
import numpy as np
import queue

import original
import bilateral
import resized
import difference

class Producer:
    def __init__(self, url, name, data_queue, desired_fps = None):
        self.cap = cv2.VideoCapture(url)
        self.name = name 
        self.running = True
        self.frame = None
        self.desired_fps = desired_fps
        self.actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.data_queue = data_queue
        self.prev_frame = None
        self.data = {}

    def update(self):
        while self.running:
            if self.desired_fps and self.actual_fps > float(self.desired_fps):
                self.cap.set(cv2.CAP_PROP_FPS, self.desired_fps)

            ret, frame = self.cap.read()
            self.prev_frame = frame

            if ret:
                self.frame = frame


    def main_writer_q(self):
        if self.running:
            if self.frame is not None:
                self.data["Prev_frame"] = self.prev_frame
                self.data["Original"] = self.frame
     
    def stop(self):
        self.running = False
        

class Thread_manager:
    def Main_manager(self):
        desired_fps = 30
        urls = [
            "rtsp://test:test@1234@192.168.1.246:554/cam/realmonitor?channel=2&subtype=0",
            "rtsp://test:test@1234@192.168.1.246:554/cam/realmonitor?channel=3&subtype=0",
            "rtsp://test:test@1234@192.168.1.246:554/cam/realmonitor?channel=7&subtype=0",
            "rtsp://test:test@1234@192.168.1.246:554/cam/realmonitor?channel=8&subtype=0"
        ]

        queues = [queue.Queue(maxsize=10) for _ in range(len(urls))]

        threads = []

        for i, (url, q) in enumerate(zip(urls, queues), start=1):
            camera_name = f"Camera_{i}"
        
            t = threading.Thread(
                target=Producer.main_writer_q, 
                daemon=True, 
                args=(url, camera_name, q, desired_fps)
            )
            t.start()
            threads.append(t)


        for thread in threads:
            thread.stop()

        for queue in queues:
            queue.join()



#########################################################################################################

def main():
    Thread_manager_1 = Thread_manager()
    Thread_manager_1.Main_manager()
    

######################################################################################################### 

if __name__ == "__main__":
    main()



