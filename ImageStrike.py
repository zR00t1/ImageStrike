#!/usr/bin/python
# -*- coding: utf-8 -*-

# import pyexiv2
import binascii
import os
import random
import cv2.cv2 as cv2
import numpy as np
import subprocess
import sys
import exifread
import pefile
import pyzbar.pyzbar as pyzbar
from zlib import crc32
from gmpy2 import iroot
from struct import pack
# from pyexiv2 import Image
from PIL import Image,ImageSequence
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMessageBox,QMenu
from PyQt5.QtGui import QPixmap,QCursor
from PyQt5.QtCore import Qt
from mainUi import Ui_ImageStrike


banner = r'''
        ____                          _____ __       _ __      
       /  _/___ ___  ____ _____ ____ / ___// /______(_) /_____ 
       / // __ `__ \/ __ `/ __ `/ _ \\__ \/ __/ ___/ / //_/ _ \
     _/ // / / / / / /_/ / /_/ /  __/__/ / /_/ /  / / ,< /  __/
    /___/_/ /_/ /_/\__,_/\__, /\___/____/\__/_/  /_/_/|_|\___/ 
                        /____/      
                                                   
                [+] Version: V0.1                                   
                [+] Author: zR00t1
                [+] Github: https://github.com/zR00t1/ImageStrike
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
'''

class MainEvents(QtWidgets.QMainWindow,Ui_ImageStrike):
    def __init__(self,parent=None):
        super(MainEvents, self).__init__(parent)

        mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True
        mkdirlambda('./imgs')                                   # 不存在就创建imgs目录

        self.Ui = Ui_ImageStrike()
        self.Ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())                      # 禁止拉伸窗口大小和最大化按钮
        self.Ui.img1_text.textChanged.connect(self.change_text)             # 文本发生改变
        self.Ui.img2_text.textChanged.connect(self.change_text)
        self.Ui.model_Box.currentIndexChanged.connect(self.my_combobox)     # 选项发生改变
        self.Ui.pwnButton.clicked.connect(self.pwn)                         # 点击pwn按钮
        self.Ui.resetButton.clicked.connect(self.reset)                     # 点击reset按钮
        self.Ui.info_text.append(banner)                                    # 打印banner
        # 图片label自适应
        self.Ui.imglabel.setStyleSheet("border: 2px solid blue")
        self.Ui.imglabel.setScaledContents(True)
        # 声明在groupBox创建右键菜单
        self.Ui.imglabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Ui.imglabel.customContextMenuRequested.connect(self.create_rightmenu)
        # 连接到菜单显示函数
        self.Ui.imglabel.contextMenu = QMenu(self)
        self.Ui.imglabel.OP = self.Ui.imglabel.contextMenu.addAction('打开图片')
        self.Ui.imglabel.OPD = self.Ui.imglabel.contextMenu.addAction('打开图片所在目录')
        self.Ui.imglabel.QR = self.Ui.imglabel.contextMenu.addAction('扫描二维码')
        self.Ui.imglabel.IV = self.Ui.imglabel.contextMenu.addAction('图片反相')
        self.Ui.imglabel.CL = self.Ui.imglabel.contextMenu.addAction('清空显示')
        # 事件绑定
        self.Ui.imglabel.OP.triggered.connect(self.showimg)
        self.Ui.imglabel.OPD.triggered.connect(self.showdir)
        self.Ui.imglabel.QR.triggered.connect(lambda:self.qrcode(self.Ui.infolabel.text()))
        self.Ui.imglabel.IV.triggered.connect(lambda:self.inversion(self.Ui.infolabel.text()))
        self.Ui.imglabel.CL.triggered.connect(self.resetimg)

    def closeEvent(self, event):
        '''关闭按钮事件'''
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def change_text(self):
        '''去除file头'''
        if 0 == self.Ui.img1_text.toPlainText().find('file:///'):
            self.Ui.img1_text.setText(self.Ui.img1_text.toPlainText().replace('file:///', ''))
        if 0 == self.Ui.img2_text.toPlainText().find('file:///'):
            self.Ui.img2_text.setText(self.Ui.img2_text.toPlainText().replace('file:///', ''))

    def my_combobox(self):
        '''判断当前选项'''
        current_index = self.Ui.model_Box.currentIndex()
        text = '[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText())
        if current_index == 3 or current_index == 4 or current_index == 6 or current_index == 8 or current_index == 9 or current_index == 11 or current_index == 12 or current_index == 13:
            self.Ui.info_text.append(text)
        elif current_index == 1 or current_index == 2:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入原图片的路径\n[*] 请在Img2中填入被加密图片的路径\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 5:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n[*] 数据格式为每行三组数以空格作为分割，例：\n[*] 255 255 255\n[*] 255 255 255\n[*] 128 128 128\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 7:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] PNG IDAT功能暂未实现\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 10 or current_index == 15:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n[*] 如果有密码，请在Img2中填入密码\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 14:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n[*] 确保txt中数据只有01，例：\n[*] 11111110001000011011111111\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))

    def pwn(self):
        print('[debug] pwn函数执行')
        img1_text_null = '[*] Img1 文件路径为空'
        info_text_line = '- - - - - - - - - - - - - - - - - - - - - - - -'
        current_index = self.Ui.model_Box.currentIndex()

        if current_index == 1:
            '''盲水印-python2'''
            if self.Ui.img1_text.toPlainText() != '' or self.Ui.img2_text.toPlainText() != '':
                if self.blind_watermark(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText(),'./imgs/result1.png',True) == True:
                    self.Ui.info_text.append('[*] 盲水印 - 执行成功，图片保存在 /imgs/result1.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result1.png'))
                    self.Ui.infolabel.setText('./imgs/result1.png')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append('[*] Img1 或 Img2 文件路径为空')
        elif current_index == 2:
            '''盲水印-python3'''
            if self.Ui.img1_text.toPlainText() != '' or self.Ui.img2_text.toPlainText() != '':
                if self.blind_watermark(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText(),'./imgs/result2.png',False) == True:
                    self.Ui.info_text.append('[*] 盲水印 - 执行成功，图片保存在 /imgs/result2.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result2.png'))
                    self.Ui.infolabel.setText('./imgs/result2.png')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append('[*] Img1 或 Img2 文件路径为空')
        elif current_index == 3:
            '''二维码扫描'''
            if self.Ui.img1_text.toPlainText() != '':
                self.qrcode(self.Ui.img1_text.toPlainText())
            else:
                self.Ui.info_text.append('[*] Img1 或 Img2 文件路径为空')
        elif current_index == 4:
            '''图片反相'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.inversion(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] 图片反相 - 执行成功，图片保存在 /imgs/result4.png')
                else:
                    self.Ui.info_text.append('[*] 图片反相 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 5:
            '''RGB转图片'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.rgb2img(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] RGB转图片 - 执行成功，图片保存在 /imgs/result5.jpg')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result5.jpg'))
                    self.Ui.infolabel.setText('./imgs/result5.jpg')
                else:
                    self.Ui.info_text.append('[*] RGB转图片 - 转储失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 6:
            '''PNG改宽高'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.png_crc32(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] PNG改宽高 - 执行成功，图片保存在 /imgs/result6.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result6.png'))
                    self.Ui.infolabel.setText('./imgs/result6.png')
                else:
                    self.Ui.info_text.append('[*] PNG改宽高 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 7:
            if self.Ui.img1_text.toPlainText() != '':
                pass
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 8:
            '''图片元数据(EXIF、IPTC、XMP)'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.metadata(self.Ui.img1_text.toPlainText()) ==True:
                    self.Ui.info_text.append('[*] 图片元数据 - 数据获取成功')
                else:
                    self.Ui.info_text.append('[*] 图片元数据 - 数据获取失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 9:
            '''GIF帧分离'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.splitGIF(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] GIF帧分离 - 图片分离成功，请查看 /imgs/gif/ 目录')
                else:
                    self.Ui.info_text.append('[*] GIF帧分离 - 图片分离失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 10:
            '''F5隐写'''
            if self.Ui.img1_text.toPlainText() != '':
                res = self.f5(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText())
                if res == 'Tru':
                    self.Ui.info_text.append('[*] F5隐写 - 执行成功\n'+ info_text_line)
                elif res == 'Fals':
                    self.Ui.info_text.append('[*] F5隐写 - 执行成功，文件保存在/tools/F5/output.txt\n' + info_text_line)
                elif res == 'Err':
                    self.Ui.info_text.append('[*] F5隐写 - 执行失败，该图片可能不是F5隐写，或密码错误\n' + info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 11:
            '''strings可打印字符'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.strings(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] Strings可打印字符 - 执行成功')
                else:
                    self.Ui.info_text.append('[*] Strings可打印字符 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 12:
            '''jpg改高度-height'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.jpg_size(self.Ui.img1_text.toPlainText(),'h') == True:
                    self.Ui.info_text.append('[*] JPG改高度 - 执行成功，图片保存在 ./imgs/result12.jpg')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result12.jpg'))
                    self.Ui.infolabel.setText('./imgs/result12.jpg')
                else:
                    self.Ui.info_text.append('[*] JPG改高度 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 13:
            '''jpg改宽度-width'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.jpg_size(self.Ui.img1_text.toPlainText(),'w') == True:
                    self.Ui.info_text.append('[*] JPG改宽度 - 执行成功，图片保存在 ./imgs/result12.jpg')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result12.jpg'))
                    self.Ui.infolabel.setText('./imgs/result12.jpg')
                else:
                    self.Ui.info_text.append('[*] JPG改宽度 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 14:
            '''01二进制转黑白图片'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.bin2img(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] 01二进制转黑白图片 - 执行成功，图片保存在 ./imgs/result14.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result14.png'))
                    self.Ui.infolabel.setText('./imgs/result14.png')
                else:
                    self.Ui.info_text.append('[*] 01二进制转黑白图片 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 15:
            if self.Ui.img1_text.toPlainText() != '':
                if self.stegpy(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] Stegpy - 执行成功')
                else:
                    self.Ui.info_text.append('[*] Stegpy - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
    def reset(self):
        self.Ui.img1_text.setText('')
        self.Ui.img2_text.setText('')

    def blind_watermark(self,fn1,fn2,fn3,oldseed):
        '''2-盲水印python3'''
        oldseed = oldseed
        seed = 20160930
        alpha = 3.0
        # img = cv2.imread(fn1)
        # img_wm = cv2.imread(fn2)
        ## 解决imread不能读取中文路径的问题,imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
        cv_img = cv2.imdecode(np.fromfile(fn1, dtype=np.uint8), -1)
        img = cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
        cv_img_wm = cv2.imdecode(np.fromfile(fn2, dtype=np.uint8), -1)
        img_wm = cv2.cvtColor(cv_img_wm, cv2.COLOR_RGB2BGR)

        if oldseed:
            random.seed(seed, version=1)
        else:
            random.seed(seed)
        m, n = list(range(int(img.shape[0] * 0.5))), list(range(img.shape[1]))
        if oldseed:
            random.shuffle(m, random=random.random)
            random.shuffle(n, random=random.random)
        else:
            random.shuffle(m)
            random.shuffle(n)

        f1 = np.fft.fft2(img)
        f2 = np.fft.fft2(img_wm)

        rwm = (f2 - f1) / alpha
        rwm = np.real(rwm)

        wm = np.zeros(rwm.shape)
        for i in range(int(rwm.shape[0] * 0.5)):
            for j in range(rwm.shape[1]):
                wm[m[i]][n[j]] = np.uint8(rwm[i][j])
        for i in range(int(rwm.shape[0] * 0.5)):
            for j in range(rwm.shape[1]):
                wm[rwm.shape[0] - i - 1][rwm.shape[1] - j - 1] = wm[i][j]
        assert cv2.imwrite(fn3, wm)
        return True

    def lsb(self):
        pass

    def inversion(self,file):
        '''4-图片反相'''
        print('[debug] inversion函数执行')
        img = Image.open(file)
        in_pixels = list(img.getdata())
        out_pixels = list()
        for i in range(len(in_pixels)):
            r = in_pixels[i][0]
            g = in_pixels[i][1]
            b = in_pixels[i][2]
            out_pixels.append((255 - r, 255 - g, 255 - b))
        out_img = Image.new(img.mode, img.size)
        out_img.putdata(out_pixels)
        out_img.save("./imgs/result4.png", "PNG")
        self.Ui.imglabel.setPixmap(QPixmap('./imgs/result4.png'))
        self.Ui.infolabel.setText('./imgs/result4.png')
        return True

    def rgb2img(self,file):
        '''5-RGB转图片'''
        print('[debug] rgb2img函数执行')
        with open(file) as f:  # 打开rbg值的文件
            lines_num = len(open(file, 'r').readlines())
            i_root = iroot(lines_num, 2)
            if  i_root[1] == True:
                count = int(i_root[0])
                im = Image.new("RGB", (count, count))  # 创建图片
                for i in range(0, count):
                    # 宽度
                    for j in range(0, count):
                        # 高度
                        line = f.readline().strip(' \n')  # 获取一行的rgb值
                        rgb = line.split(" ")  # 空格分离rgb
                        im.putpixel((i, j), (int(rgb[0]), int(rgb[1]), int(rgb[2])))  # 将rgb转化为像素
                im.save('./imgs/result5.jpg')
                return True
            else:
                return False

    def png_crc32(self,file):
        '''6-根据crc值暴力破解宽度和高度'''
        print('[debug] png_crc32函数执行')
        with open(file, 'rb') as f:
            all_b = f.read()
            data_ihdr_flag = all_b[12:16]
            data_length = int.from_bytes(all_b[8:12], 'big')
            data_color = all_b[24:24 + data_length - 8]
            crc32key = int.from_bytes(all_b[16 + data_length:20 + data_length], 'big')
            i = 0
            for w in range(1, 1000):
                for h in range(1, 1000):
                    width = pack('>i', w)
                    height = pack('>i', h)
                    data = data_ihdr_flag + width + height + data_color
                    i = i + 1
                    if (crc32(data) & 0xffffffff) == crc32key:
                        with open('./imgs/result6.png', 'wb') as f1:
                            f1.write(all_b[0:16] + width + height + all_b[24:])
                            return True

    def metadata(self,file):
        '''8-图片元数据'''
        print('[debug] metadata函数执行')
        with open(file, 'rb') as f:
            exif = exifread.process_file(f)
            for key, value in exif.items():
                self.Ui.info_text.append('{}:{}'.format(key, value))
            return True
        # img = pyexiv2.Image(file,encoding = 'GBK')
        # exif = img.read_exif()
        # self.Ui.info_text.append('[*] 图片元数据 - EXIF信息：')
        # for key, value in exif.items():
        #     print('{}:{}'.format(key, value))
        #     self.Ui.info_text.append('{}:{}'.format(key, value))
        # iptc = img.read_iptc()
        # self.Ui.info_text.append('[*] 图片元数据 - IPTC信息：')
        # for key, value in iptc.items():
        #     print('{}:{}'.format(key, value))
        #     self.Ui.info_text.append('{}:{}'.format(key, value))
        # xmp = img.read_xmp()
        # self.Ui.info_text.append('[*] 图片元数据 - XMP信息：')
        # for key, value in xmp.items():
        #     print('{}:{}'.format(key, value))
        #     self.Ui.info_text.append('{}:{}'.format(key, value))
        # img.close()

    def splitGIF(self,file):
        '''9-Gif帧分离'''
        print('[debug] splitGIF函数执行')
        im = Image.open(file)
        iter = ImageSequence.Iterator(im)
        index = 1
        pic_dir = "imgs/gif"
        mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True
        mkdirlambda(pic_dir)
        for frame in iter:
            frame.save("imgs/gif/frame%d.png" % (index))
            index += 1
        return True

    def f5(self,file,pwd):
        '''10-F5隐写'''
        print('[debug] f5函数执行')
        if pwd != '':
            pwd = pwd
        else:
            pwd = 'abc123'
        f555 = subprocess.run('cd .\\tools\\F5\\ && java Extract {} -p {}'.format(file,pwd),shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if 'Incomplete file' not in str(f555):
                try:
                    with open('./tools/F5/output.txt', 'r') as f:
                        file = f.read()
                        self.Ui.info_text.append(file)
                    return 'Tru'
                except:
                    return 'Fals'
        else:
            return 'Err'

    def strings(self,file):
        '''11-Strings可打印字符'''
        print('[debug] strings函数执行')
        subprocess.run('.\\tools\\strings.exe -a {} > ./cache.txt'.format(file),shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open('.\\cache.txt','r') as f:
            text = f.read()
            self.Ui.info_text.append(text)
        dlt_file = subprocess.run('del .\\cache.txt', shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True

    def jpg_size(self,file,style):
        '''12-JPG改宽高'''
        img = Image.open(file)
        width = img.size[0]
        height = img.size[1]
        # 图片-->HEX
        with open(file, 'rb') as f:
            content = f.read()
            with open('cache.txt', 'wb') as ff:
                ff.write(binascii.hexlify(content))
        # HEX-->图片
        with open('cache.txt', 'r') as fff:
            if style == 'h':
                data = fff.read().replace(self.hex2str(width, height), self.hex2str(width, height * 2))
            elif style == 'w':
                data = fff.read().replace(self.hex2str(width, height), self.hex2str(width*2, height))
            if (os.path.exists('./imgs/result12.jpg')) == True:
                dlt_file = subprocess.run('del .\\imgs\\result12.jpg', shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open('./imgs/result12.jpg', 'ab') as ffff:
                pic = binascii.a2b_hex(data.encode())
                ffff.write(pic)
        dlt_file = subprocess.run('del cache.txt', shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True

    def bin2img(self,file):
        '''14-01二进制转黑白图片'''
        print('[debug] bin2img函数执行')
        with open(file,'r') as f:  # 打开rbg值的文件
            data = f.read().replace('\n','').replace(' ','')
            i_root = iroot(len(data), 2)
            if i_root[1] == True:
                count = int(i_root[0])
                pic = Image.new("RGB", (count, count))  # 创建图片
                i = 0
                for y in range(0, count):
                    for x in range(0, count):
                        if (data[i] == '1'):
                            pic.putpixel([x, y], (0, 0, 0))
                        else:
                            pic.putpixel([x, y], (255, 255, 255))
                        i += 1
                        pic.save("./imgs/result14.png")
                return True
            else:
                return False

    def stegpy(self,file,pwd):
        '''stegpy隐写'''
        print('[debug] stegpy函数执行')
        if pwd != '':
            pwd = pwd
        else:
            subprocess.run('stegpy {} > cache.txt'.format(file),shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open('cache.txt', 'r') as f:
                text = f.read()
                self.Ui.info_text.append(text)
            dlt_file = subprocess.run('del .\\cache.txt', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return True

    def create_rightmenu(self,pos):
        print(pos)  #打印鼠标坐标
        self.Ui.imglabel.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示菜单

    def showimg(self):
        '''右键打开图片'''
        if self.Ui.infolabel.text() != '':
            filepath = self.Ui.infolabel.text().replace('/','\\')
            os.startfile(filepath)
        else:
            self.Ui.info_text.append('[*] 打开图片 - 当前没有图片' )

    def showdir(self):
        '''右键打开图片所在目录'''
        if self.Ui.infolabel.text() != '':
            os.startfile('.\\imgs\\')
        else:
            self.Ui.info_text.append('[*] 打开图片所在目录 - 当前没有图片' )

    def qrcode(self,file):
        '''右键二维码识别'''
        print('[debug] qrcode函数执行')
        if file != '':
            img = Image.open(file)
            barcodes = pyzbar.decode(img)
            try:
                for barcode in barcodes:
                    barcodeData = barcode.data.decode("utf-8")
                    self.Ui.info_text.append('[*] 二维码扫描 - 识别到以下内容：\n' + barcodeData + '\n- - - - - - - - - - - - - - - - - - - - - - - -')
            except:
                self.Ui.info_text.append('[*] 二维码扫描 - 未识别到有效信息\n- - - - - - - - - - - - - - - - - - - - - - - -')
        else:
            self.Ui.info_text.append('[*] 扫描二维码 - 当前没有图片')

    def resetimg(self):
        '''右键清空显示'''
        self.Ui.infolabel.setText('')
        self.Ui.imglabel.setPixmap(QPixmap())

    def hex2str(self, width, height):
        '''图形宽高-->HEX'''
        list_width = list(hex(width).replace('0x', ''))
        list_height = list(hex(height).replace('0x', ''))
        # 转成list进行insert
        while len(list_width) != 4:
            list_width.insert(0, '0')
        while len(list_height) != 4:
            list_height.insert(0, '0')
        str = "".join(list_height) + "".join(list_width)
        return str

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainEvents()       # 加载窗口
    ui.show()               # 显示窗口
    sys.exit(app.exec_())