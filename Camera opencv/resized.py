import cv2
import threading
from __future__ import annotations
import cv2
import traceback
from queue import Queue


import main_file

class Resize:
    def __init__(self):
        self.running = True
        self.q = main_file.Producer.main_writer_q
        self.data = {}
        self.resized_reader_q = Queue(maxsize=10)
        self.original_frame = None
        self.resize_filter = None
        self.prev_frame = None
    
    def Consumer(self):
        while self.running:
            if self.q:
                data_queue = self.q.get()
                self.original_frame = data_queue["Original"]
                self.prev_frame = data_queue["Prev"]
                h, w = self.shape[:2]
                self.resize_filter = cv2.resize(self.original_frame, ((int(w*0.5), int(h*0.5))))
                
    
    def Producer(self):
        while self.running:
            self.data["Original"] = self.original_frame
            self.data["Resized"] = self.resize_filter
            self.data["Prev_frame"] = self.prev_frame

            self.resized_reader_q.put(self.data)


    def stop(self):
        self.running = False
        self.q_reader.join()



class Thread_manager:
    def Main_manager(self):

        threads_c = []
        for i in range(0,4):
        
            t = threading.Thread(
                target=Resize.Consumer, 
                daemon=True
            )
            t.start()
            threads_c.append(t)


        for thread in threads_c:
            thread.stop()

        

        threads_p = []
        for i in range(0,4):
        
            t = threading.Thread(
                target=Resize.Producer, 
                daemon=True
            )
            t.start()
            threads_p.append(t)


        for thread in threads_p:
            thread.stop()




#########################################################################################################

def main():
    Thread_manager_1 = Thread_manager()
    Thread_manager_1.Main_manager()
    

######################################################################################################### 

if __name__ == "__main__":
    main()


