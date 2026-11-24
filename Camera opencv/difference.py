import cv2
import threading
import queue
 
import bilateral

class Difference:
    def __init__(self):
        self.running = True
        self.q = bilateral.Bilateral.bilateral_reader_q
        self.data = {}
        self.difference_reader_q = queue.Queue(maxsize=10)
        self.difference_filter = None
        self.prev_gray = None
    
    def Consumer(self):
        while self.running:
            if self.q:
                prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                data = self.q.get()
                data_resize = data["Resized"]
                self.bilateral_filter = cv2.bilateralFilter(data_resize, 9, 75, 75)
                data["Bilateral"] = self.bilateral_filter

                
    
    def Producer(self):
        while self.running:
            self.data["Bilateral"] = self.bilateral_filter

            self.d_reader_q(self.data)


    def stop(self):
        self.running = False
        self.difference_reader_q.join()



class Thread_manager:
    def Main_manager(self):

        threads_c = []
        for i in range(0,4):
        
            t = threading.Thread(
                target=Difference.Consumer, 
                daemon=True
            )
            t.start()
            threads_c.append(t)


        for thread in threads_c:
            thread.stop()

        
        
        threads_p = []
        for i in range(0,4):
        
            t = threading.Thread(
                target=Difference.Producer, 
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


