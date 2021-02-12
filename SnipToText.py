import tkinter as tk
import cv2 as cv
import pyautogui
import pyperclip
import pytesseract

img_path = "lastSnip.png"
snipBtnText = "✀ Snip"
resnipBtnText = "new ✀"
baseSize = "250x50"

'''
basic snipping functions copied from:
https://stackoverflow.com/questions/49901928/how-to-take-a-screenshot-with-python-using-a-click-and-drag-method-like-snipping '

Tesseract downloaded and installed from:
https://github.com/UB-Mannheim/tesseract/wiki

'''

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Application():
    def __init__(self, master):
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None

        root.geometry(baseSize)  # set new geometry
        root.title('Snip-text')
        root.bind("<Escape>", self.cancelButtonfunc)

        self.menu_frame = tk.Frame(master, bg="white")
        self.menu_frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.buttonBar = tk.Frame(self.menu_frame, bg="white")
        self.buttonBar.grid(column=0, row=0, columnspan=2)

        self.snipButton = tk.Button(self.buttonBar, width=6, command=self.createScreenCanvas, font="bold", bg="#0492c2", text=snipBtnText, fg="white")
        self.snipButton.grid(column=0, row=0, columnspan=1, padx=30)
        
        self.cancelButton = tk.Button(self.buttonBar, width=6, command=self.cancelButtonfunc, font="bold", bg="#0492c2", text="Cancel",fg="white")
        self.cancelButton.grid(column=2, row=0, columnspan=1)

        self.master_screen = tk.Toplevel(root)
        self.master_screen.bind("<Escape>", self.cancelButtonfunc)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")

        self.picture_frame = tk.Frame(self.master_screen, background = "blue")
        self.picture_frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.pictureFrame = tk.Label(root,text="my label")


    def takeBoundedScreenShot(self, x1, y1, x2, y2): # takes screenshot at chosen coordinates and saves the picture to img_path
        margin = 1
        xmin = min(int(x1),int(x2))+margin
        ymin = min(int(y1),int(y2))+margin
        width = max(int(x1),int(x2))-xmin-2*margin
        height = max(int(y1),int(y2))-ymin-2*margin
        im = pyautogui.screenshot(region=(xmin, ymin, width, height))
        im.save(img_path)
        
    
    def openPicture(self): # opens and displays picture from img_path
        imagetext =  self.getTextFromImage(img_path)
        load = cv.imread(img_path)
        self.img = tk.PhotoImage(file=img_path)
        self.removePreviousSnip()

        root.geometry(str(load.shape[1])+"x"+str((load.shape[0]+50)*2))
        
        self.pictureFrame = tk.Label(root,text="my label")
        self.pictureFrame.configure(image=self.img, bg="white")
        self.pictureFrame.pack()
        
        self.mytext = tk.Text(root, height=100, width= 200)
        self.mytext.insert(tk.END, imagetext)
        self.mytext.pack()
        self.snipButton['text'] = resnipBtnText


    def getTextFromImage(self,image_path): 
        img=cv.imread(image_path)
        '''
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        th1 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,9,2)
        th1Text =  pytesseract.image_to_string(th1).strip()
        print("th1 text " + th1Text)
        '''
        imgText =  pytesseract.image_to_string(img).strip()
        print("img text " + imgText)  
        return imgText


    def createScreenCanvas(self):
        self.master_screen.deiconify()
        root.withdraw()

        self.screenCanvas = tk.Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.screenCanvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.screenCanvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screenCanvas.bind("<B1-Motion>", self.on_move_press)
        self.screenCanvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .8)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)


    def on_button_release(self, event):
        self.takeBoundedScreenShot(self.start_x, self.start_y, self.curX, self.curY)
        self.exitScreenshotMode()
        self.openPicture()
        return event
   

    def exitScreenshotMode(self):
        #print("Screenshot mode exited")
        self.screenCanvas.destroy()
        self.master_screen.withdraw()
        root.deiconify()
        

    def exit_application(self):
        print("Application exit")
        root.quit()


    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.screenCanvas.canvasx(event.x)
        self.start_y = self.screenCanvas.canvasy(event.y)
        self.rect = self.screenCanvas.create_rectangle(self.x, self.y, 1, 1, width=1, fill="blue")


    def on_move_press(self, event):
        self.curX, self.curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.screenCanvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)


    def cancelButtonfunc(self, *args): # returns to basic view, closes the picture view if open, else it closes the application
        try: 
            if self.screenCanvas.winfo_exists():
                self.exitScreenshotMode()
            else:
                if self.pictureFrame.winfo_exists():
                    self.removePreviousSnip()
                else:
                    self.exit_application()
        except Exception as e:
            if isinstance(e, AttributeError):
                self.exit_application()  
            if isinstance(e, TypeError):
                self.exitScreenshotMode()
            print("caught some exception: ", e)


    def removePreviousSnip(self):
        try:
            root.geometry(baseSize) 
            self.pictureFrame.destroy()
            self.mytext.destroy()
            self.snipButton['text']=snipBtnText 
        except Exception as e:
            pass
            # print(e)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.after(1, lambda: root.focus_force())
    root.mainloop()