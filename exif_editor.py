# 上書き保存できるのは以下の項目
# ・撮影日時
# ・メーカー名
# ・モデル名
# ・レンズ名
# ・焦点距離
# ・f値
# ・シャッタースピード
# ・ISO

import tkinter
from tkinter import ttk, filedialog
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import piexif
from PIL.ExifTags import Base,IFD,TAGS
import ctypes
import copy
import datetime

PICTURE_SIZE = 720


class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.geometry("1280x720+"+str(int((self.master.winfo_screenwidth()-1280)/2))+"+"+str(int((self.master.winfo_screenheight()-720)/2)))  # centering
        self.master.title("Exif Editor")
        self.master.grid_columnconfigure(1,weight=1)
        self.master.grid_rowconfigure((0,1,2),weight=1)
        
        self.master.update_idletasks()
        print("ウィンドウのサイズと座標:", self.master.winfo_geometry())
        
        # output_frame
        self.canvas = tkinter.Canvas(self.master, width=720, height=720)
        self.canvas.grid(row=0,column=0, rowspan=3, sticky="we")
        
        self.input_frame = tkinter.Frame(self.master, width=560, height=80, bg='white', ) 
        self.edit_frame = tkinter.Frame(self.master, width=560, height=240, bg='white')
        self.save_frame = tkinter.Frame(self.master, width=560, height=400, bg='white')
        self.save_frame.grid(row=2, column=1, sticky=tkinter.NSEW)
        self.edit_frame.grid(row=1, column=1, sticky=tkinter.NSEW)
        self.input_frame.grid(row=0,column=1, sticky=tkinter.NSEW)
        
        # input_frame
        self.file_edit = ttk.Entry(self.input_frame, width=40)
        self.file_edit.configure(state='readonly')
        self.path_btn = ttk.Button(self.input_frame, text='Open',command=self.select_img)
        self.file_edit.grid(column=0, row=0, sticky=tkinter.EW, padx=5)
        self.path_btn.grid(column=1, row=0, pady=10, padx=5)
        
        # edit_frame
        self.date_label = tkinter.Label(self.edit_frame, text="撮影日時：")
        self.make_label = tkinter.Label(self.edit_frame, text="メーカー名：")
        self.model_label = tkinter.Label(self.edit_frame, text="カメラ名：")
        self.lens_label = tkinter.Label(self.edit_frame, text="レンズ名：")
        self.focal_label = tkinter.Label(self.edit_frame, text="焦点距離(mm)：")
        self.fnum_label = tkinter.Label(self.edit_frame, text="f値：")
        self.speed_label = tkinter.Label(self.edit_frame, text="露光時間(1/,s)：")
        self.iso_label = tkinter.Label(self.edit_frame, text="ISO：")
        self.date_label.grid(column=0,row=0)
        self.make_label.grid(column=0,row=1)
        self.model_label.grid(column=0,row=2)
        self.lens_label.grid(column=0,row=3)
        self.focal_label.grid(column=0,row=4)
        self.fnum_label.grid(column=0,row=5)
        self.speed_label.grid(column=0,row=6)
        self.iso_label.grid(column=0,row=7)
        
        # self.date_edit = [ttk.Entry(self.edit_frame, width=6)] * 6 # 撮影日時
        # print(len(self.date_edit))
        self.date_edit = []
        for i in range(6):
            self.date_edit.append(ttk.Entry(self.edit_frame, width=5))
        self.make_edit  = ttk.Entry(self.edit_frame, width=40) # メーカー名
        self.model_edit = ttk.Entry(self.edit_frame, width=40) # モデル名
        self.lens_edit  = ttk.Entry(self.edit_frame, width=40) # レンズ名
        self.focal_edit = ttk.Entry(self.edit_frame, width=40) # 焦点距離 (mm)
        self.fnum_edit  = ttk.Entry(self.edit_frame, width=40) # f値
        self.speed_edit = ttk.Entry(self.edit_frame, width=40) # シャッタースピード (s)
        self.iso_edit   = ttk.Entry(self.edit_frame, width=40) # ISO
        n=1
        for e in self.date_edit:
            e.grid(column=n, row=0,  pady=10, padx=5)
            n += 1
        self.make_edit.grid(column=1, row=1, columnspan=6, pady=10, padx=5)
        self.model_edit.grid(column=1, row=2, columnspan=6,  pady=10, padx=5)
        self.lens_edit.grid(column=1, row=3, columnspan=6, pady=10, padx=5)
        self.focal_edit.grid(column=1, row=4, columnspan=6, pady=10, padx=5)
        self.fnum_edit.grid(column=1, row=5, columnspan=6, pady=10, padx=5)
        self.speed_edit.grid(column=1, row=6, columnspan=6, pady=10, padx=5)
        self.iso_edit.grid(column=1, row=7, columnspan=6,  pady=10, padx=5)
        
        # btn_frame
        self.readme_btn = ttk.Button(self.save_frame, text='README',command=self.read_me)
        self.reset_btn = ttk.Button(self.save_frame, text='Reset',command=self.reset_exif, state=tkinter.DISABLED)
        self.save_btn = ttk.Button(self.save_frame, text='Save',command=self.save_new_exif, state=tkinter.DISABLED)
        self.readme_btn.grid(column=0, row=0, pady=10, padx=5)
        self.reset_btn.grid(column=1, row=0, pady=10, padx=5)
        self.save_btn.grid(column=2, row=0, pady=10, padx=5)
        
        self.env_flag = True
    
    
    
    # 720*720内に画像を収める 
    def resize_image(self, file_name, orientation):
        img = Image.open(file_name)
        try:
            if(orientation == 8):
                img = img.rotate(90, expand=True)
            elif(orientation == 6):
                img = img.rotate(270, expand=True)
        except KeyError:
            pass
        img_width, img_height = img.size
        reducation_size =  img_width if img_width >= img_height else img_height
        return img.resize(( int( img_width * (PICTURE_SIZE/reducation_size)), int(img_height * (PICTURE_SIZE/reducation_size)) ))

    
    def set_img_exif(self, exif):
        if (exif != None):
            self.make_edit.delete(0, tkinter.END)
            self.model_edit.delete(0, tkinter.END)
            self.lens_edit.delete(0, tkinter.END)
            self.focal_edit.delete(0, tkinter.END)
            self.fnum_edit.delete(0, tkinter.END)
            self.speed_edit.delete(0, tkinter.END)
            self.iso_edit.delete(0, tkinter.END)
            
            try:
                pre_list = ((exif['Exif'][piexif.ExifIFD.DateTimeDigitized]).decode('utf-8')).split(' ')
                date_list = pre_list[0].split(':') + pre_list[1].split(':')
                for (e, d) in zip(self.date_edit, date_list):
                    e.delete(0, tkinter.END)
                    e.insert(0, d)
            except KeyError:
                pass
                
            try: 
                self.make_edit.insert(0, exif['0th'][piexif.ImageIFD.Make])
            except KeyError:
                pass
            try: 
                self.model_edit.insert(0, exif['0th'][piexif.ImageIFD.Model])
            except KeyError:
                pass
            try: 
                self.lens_edit.insert(0, exif['Exif'][piexif.ExifIFD.LensModel])
            except KeyError:
                pass
            try:
                self.focal_edit.insert(0, (exif['Exif'][piexif.ExifIFD.FocalLength][0] / exif['Exif'][piexif.ExifIFD.FocalLength][1]))
            except KeyError:
                pass
            try:
                self.fnum_edit.insert(0, (exif['Exif'][piexif.ExifIFD.FNumber][0] / exif['Exif'][piexif.ExifIFD.FNumber][1]))
            except KeyError:
                pass
            try:
                self.speed_edit.insert(0, exif['Exif'][piexif.ExifIFD.ExposureTime][1])
            except KeyError:
                pass
            try:
                self.iso_edit.insert(0, exif['Exif'][piexif.ExifIFD.ISOSpeedRatings])
            except KeyError:
                pass
            
            self.save_btn.configure(state=tkinter.NORMAL)
            self.reset_btn.configure(state=tkinter.NORMAL)
        
        
    
    def select_img(self):
        ret = True
        path = os.getcwd()
        if (self.file_edit.get() != ""):
            self.bell()
            path = os.path.dirname(self.file_edit.get())
            ret = messagebox.askyesno('確認', '現在編集中のデータは保存されません。よろしいですか？')
        if(ret):        
            filetype = [("Image file(.jpg .tiff)", ".jpg .tif .tiff")] # jpgファイルのみ対応
            
            filepath = ""
            filepath = filedialog.askopenfilename(filetype = filetype, initialdir = path)
            
            if (filepath != ""):
                self.file_edit.configure(state='normal')
                self.file_edit.delete(0, tkinter.END)
                self.file_edit.insert(0, filepath)
                self.file_edit.configure(state='readonly')
                
                self.img = Image.open(filepath)
                self.exif_load = piexif.load(filepath).copy()
                self.set_img_exif(self.exif_load)
            
                self.canvas.delete('all')
                try:
                    orientation = self.exif_load['0th'][piexif.ImageIFD.Orientation]
                except KeyError:
                    orientation = 1
                img = self.resize_image(filepath, orientation)
                self.photo = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(360,360, image=self.photo, anchor='center')
                
                
    
    def reset_exif(self):
        self.bell()
        ret = messagebox.askyesno('確認', '元のExif情報に戻しますか？')
        if ret == True:
            self.set_img_exif(self.exif_load)
    
    def save_new_exif(self):
        exif = copy.deepcopy(self.exif_load)
        
        # Vesion is 0232 if image doesn't have it
        try :
            version = exif['Exif'][piexif.ExifIFD.ExifVersion]
            print(version)
        except KeyError:
            version = "0232"
            exif['Exif'][piexif.ExifIFD.ExifVersion] = version.encode()
        
        now = datetime.datetime.now()
        date = now.strftime('%Y:%m:%d %H:%M:%S')
        exif['0th'][piexif.ImageIFD.DateTime] = date.encode()
        try :
            date_list = []
            for e in self.date_edit:
                date_list.append(int(e.get()))
            #date = str(date_list[0]) +":"+ str(date_list[1]) +":"+ str(date_list[2]) +" "+ str(date_list[3]) +":"+ str(date_list[4]) +":"+ str(date_list[5])
            date = self.date_edit[0].get() +":"+ self.date_edit[1].get() +":"+ self.date_edit[2].get() +" "+ self.date_edit[3].get() +":"+ self.date_edit[4].get() +":"+ self.date_edit[5].get()
            exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = date.encode()
            exif['Exif'][piexif.ExifIFD.DateTimeDigitized] = date.encode()
        except ValueError:
            print("ValueError: could not save date time")
            messagebox.showerror(title="Value Error", message="不正な値が入力されたため、撮影日時の情報は保存されません。")
        exif['0th'][piexif.ImageIFD.Make] = self.make_edit.get().encode()
        exif['0th'][piexif.ImageIFD.Model] = self.model_edit.get().encode()
        exif['Exif'][piexif.ExifIFD.LensModel] = self.lens_edit.get().encode()
        error = [False, False, False, False]
        try :
            focal = float(self.focal_edit.get())
            exif['Exif'][piexif.ExifIFD.FocalLength] = (int(focal*10), 10)
        except ValueError:
            error[0] = True
            if (self.env_flag): exif['Exif'][piexif.ExifIFD.FocalLength] = (0, 10)
            #print("ValueError: could not save focal length")
        try:
            fnum = float(self.fnum_edit.get())
            exif['Exif'][piexif.ExifIFD.FNumber]= (int(fnum*10), 10)
        except ValueError:
            error[1] = True
            if (self.env_flag): exif['Exif'][piexif.ExifIFD.FNumber] = (0, 10)
            #print("ValueError: could not save f number")
        try:
            exif['Exif'][piexif.ExifIFD.ExposureTime] = (1, int(self.speed_edit.get()))
        except ValueError:
            error[2] = True
            if (self.env_flag): exif['Exif'][piexif.ExifIFD.ExposureTime] = (0, 60)
            #print("ValueError: could not save Exprosure Time")
        try:
            exif['Exif'][piexif.ExifIFD.ISOSpeedRatings] = int(self.iso_edit.get())
        except ValueError:
            error[3] = True
            if (self.env_flag): exif['Exif'][piexif.ExifIFD.ISOSpeedRatings] = 0
            #print("ValueError: could not save ISO speed Ratings")
        
        if (error[0] or error[1] or error[2] or error[3]):
            error_text = str([index+1 for index, e in enumerate(error) if e])
            if (self.env_flag):
                error_text += "：不正な値が入力されたため「0.0」を保存します。\n"
            else:
                error_text += "：不正な値が入力されたため入力値を保存しません。\n"
            error_text += "[1:焦点距離，2:絞り値，3:露光時間，4:ISO]\n"
            messagebox.showerror(title="エラー", message=error_text)
        
        try:
            filepath = filedialog.asksaveasfilename(filetypes = [("JPEG(.JPG)", ".JPG"), ("JPEG(.jpg)", ".jpg"),
                                                                 ("JPEG(.jpeg)", ".jpeg"), ("PNG(.png)", ".png"),
                                                                 ("JFIF(.jfif)", ".jfif"), ("TIFF(.tif)", ".tif") ], defaultextension="JPEG(.JPG)")
            exif_bytes = piexif.dump(exif)
            self.img.save(filepath, exif=exif_bytes)
            print("save successfully!")
        except ValueError:
            print("Cancel: haven't select file path")
            
        
    def read_me(self):
        info = "Exif Editorは画像ファイルに付属するカメラ設定のメタデータを読み書きできるアプリケーションです。\n"
        info += "JPGファイルかTIFFファイルの画像ファイルが対象です。\n"
        info += "撮影日時、使用したカメラのメーカー名、モデル名、レンズ名、焦点距離、絞り値、露光時間、ISOの情報を上書きして、画像を保存する事が出来ます。\n"
        info += "撮影日時の入力欄は左から、年、月、日、時、分、秒となっています。\n"
        info += "焦点距離、絞り値には正しい数値を入力してください。（ダメな例：4.2.0 ← 小数点を複数含む）焦点距離と絞り値は、小数点第一位までの値が保存されます。\n"
        info += "露光時間、ISOに入力された数値は整数として保存されます。\n"
        info += "露光時間の入力欄には、分母の値を整数で入力してください。(例：1/3200 →「3200」)\n"
        info += "数値の入力には半角数字、文字の入力には半角英数字を使用してください。\n"
        messagebox.showinfo("READ ME" , message=info)

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass

    root = tkinter.Tk()
    app = Application(master = root)
    app.mainloop()