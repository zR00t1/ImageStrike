#!/usr/bin/python
# -*- coding: utf-8 -*-

# import pyexiv2
import os
import subprocess
import  sys
import exifread
import pyzbar.pyzbar as pyzbar
import webbrowser
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

class MainEvents(QtWidgets.QMainWindow,Ui_ImageStrike):
    def __init__(self,parent=None):
        super(MainEvents, self).__init__(parent)

        mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True
        mkdirlambda('./imgs')                                   # 创建imgs目录

        self.Ui = Ui_ImageStrike()
        self.Ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())           # 禁止拉伸窗口大小和最大化按钮
        self.Ui.img1_text.textChanged.connect(self.change_text)  # 文本发生改变
        self.Ui.img2_text.textChanged.connect(self.change_text)
        self.Ui.model_Box.currentIndexChanged.connect(self.my_combobox)     # 选项发生改变
        self.Ui.pwnButton.clicked.connect(self.pwn)         # 点击pwn按钮
        self.Ui.resetButton.clicked.connect(self.reset)     # 点击reset按钮

        # 菜单栏按钮
        self.Ui.action_about_2.triggered.connect(self.about)
        self.Ui.action_author_2.triggered.connect(self.author)
        self.Ui.action_update_2.triggered.connect(self.update)

        self.Ui.imglabel.setStyleSheet("border: 2px solid blue")    #图片label自适应
        self.Ui.imglabel.setScaledContents(True)

        # 声明在groupBox创建右键菜单
        self.Ui.imglabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Ui.imglabel.customContextMenuRequested.connect(self.create_rightmenu)  # 连接到菜单显示函数
        self.Ui.imglabel.contextMenu = QMenu(self)
        self.Ui.imglabel.OP = self.Ui.imglabel.contextMenu.addAction('打开图片')
        self.Ui.imglabel.QR = self.Ui.imglabel.contextMenu.addAction('扫描二维码')
        # 事件绑定
        self.Ui.imglabel.OP.triggered.connect(self.showimg)
        self.Ui.imglabel.QR.triggered.connect(lambda:self.qrcode(self.Ui.infolabel.text()))

    def about(self):
        box = QMessageBox()
        box.about(self, "关于", '\nImageStrike 是一款用于CTF中图片隐写的综合利用工具\n\n')
    def author(self):
        box = QMessageBox()
        box.about(self, "作者", 'zR00t1\n\nGithub:  https://github.com/zR00t1\nMail:  zR00t1@qq.com\n')
    def update(self):
        webbrowser.open("https://github.com/zR00t1/ImageStrike/releases")

    def closeEvent(self, event):
        '''关闭按钮事件'''
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if (os.path.exists('./tools/output.txt')) == True:
                print('[debug] /tools/output.txt文件存在，先删除再退出')
                dlt_file = subprocess.run('del .\\tools\\output.txt',shell=True)
            else:
                print('[debug] /tools/output.txt文件不存在，直接退出')

            if (os.path.exists('./tools/strings.txt')) == True:
                print('[debug] /tools/output.txt文件存在，先删除再退出')
                dlt_file = subprocess.run('del .\\tools\\strings.txt',shell=True)
            else:
                print('[debug] /tools/strings.txt文件不存在，直接退出')
            if (os.path.exists('./imgs/gif/')) == True:
                dlt_dir = subprocess.run('rd /s /q .\\imgs\\gif\\',shell=True)
            else:
                print('[debug] /imgs/gif/目录不存在，直接退出')
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
        if current_index == 2 or current_index == 3 or current_index == 5 or current_index == 7 or current_index == 8 or current_index == 10:
            self.Ui.info_text.append(text)
        elif current_index == 1:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入原图片的路径\n[*] 请在Img2中填入被加密图片的路径\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 4:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n[*] 数据格式为每行三组数以空格作为分割，例：\n[*] 255 255 255\n[*] 255 255 255\n[*] 128 128 128\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 6:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] PNG IDAT功能暂未实现\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))
        elif current_index == 9:
            self.Ui.info_text.append('[*] 当前选择的隐写方式为：{}\n[*] 请在Img1中填入文件路径\n[*] 如不是默认密码，请在Img2中填入密码\n- - - - - - - - - - - - - - - - - - - - - - - -'.format(self.Ui.model_Box.currentText()))

    def pwn(self):
        print('[debug] pwn函数执行')
        img1_text_null = '[*] Img1 文件路径为空'
        img2_text_null = '[*] Img2 文件路径为空'
        info_text_line = '- - - - - - - - - - - - - - - - - - - - - - - -'
        current_index = self.Ui.model_Box.currentIndex()

        if current_index == 1:
            '''盲水印'''
            if self.Ui.img1_text.toPlainText() != '' or self.Ui.img2_text.toPlainText() != '':
                if self.blind_watermark(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] 盲水印 - 执行成功，图片保存在 /imgs/result1.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result1.png'))
                    self.Ui.infolabel.setText('./imgs/result1.png')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append('[*] Img1 或 Img2 文件路径为空')
        elif current_index == 2:
            '''二维码扫描'''
            if self.Ui.img1_text.toPlainText() != '':
                self.qrcode(self.Ui.img1_text.toPlainText())
            else:
                self.Ui.info_text.append('[*] Img1 或 Img2 文件路径为空')
        elif current_index == 3:
            '''图片反相'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.inversion(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] 图片反相 - 执行成功，图片保存在 /imgs/result3.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result3.png'))
                    self.Ui.infolabel.setText('./imgs/result3.png')
                else:
                    self.Ui.info_text.append('[*] 图片反相 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 4:
            '''RGB转图片'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.rgb2img() == True:
                    self.Ui.info_text.append('[*] RGB转图片 - 执行成功，图片保存在 /imgs/result4.jpg')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result4.jpg'))
                    self.Ui.infolabel.setText('./imgs/result4.jpg')
                else:
                    self.Ui.info_text.append('[*] RGB转图片 - 转储失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 5:
            '''PNG改宽高'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.png_crc32(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] PNG改宽高 - 执行成功，图片保存在 /imgs/result5.png')
                    self.Ui.imglabel.setPixmap(QPixmap('./imgs/result5.png'))
                    self.Ui.infolabel.setText('./imgs/result5.png')
                else:
                    self.Ui.info_text.append('[*] PNG改宽高 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 6:
            if self.Ui.img1_text.toPlainText() != '':
                pass
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 7:
            '''图片元数据(EXIF、IPTC、XMP)'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.metadata(self.Ui.img1_text.toPlainText()) ==True:
                    self.Ui.info_text.append('[*] 图片元数据 - 数据获取成功')
                else:
                    self.Ui.info_text.append('[*] 图片元数据 - 数据获取失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 8:
            '''GIF帧分离'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.splitGIF(self.Ui.img1_text.toPlainText()) == True:
                    self.Ui.info_text.append('[*] GIF帧分离 - 图片分离成功，请查看 /imgs/gif/ 目录')
                else:
                    self.Ui.info_text.append('[*] GIF帧分离 - 图片分离失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 9:
            '''F5隐写'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.f5(self.Ui.img1_text.toPlainText(),self.Ui.img2_text.toPlainText()) == True:
                    if  (os.path.exists('./tools/output.txt')) == True:
                        self.Ui.info_text.append('[*] F5隐写 - 执行成功,得到以下数据：')
                        with open('./tools/output.txt','r') as f:
                            file = f.read()
                            self.Ui.info_text.append(file)
                        self.Ui.info_text.append(info_text_line)
                    else:
                        self.Ui.info_text.append('[*] 执行失败，该图片可能不是F5隐写\n' + info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)
        elif current_index == 10:
            '''strings可打印字符'''
            if self.Ui.img1_text.toPlainText() != '':
                if self.strings(self.Ui.img1_text.toPlainText()) == True:
                    with open('./tools/strings.txt','r') as f:
                        self.Ui.info_text.append(f.read())
                    self.Ui.info_text.append('[*] Strings可打印字符 - 执行成功')
                else:
                    self.Ui.info_text.append('[*] Strings可打印字符 - 执行失败')
                self.Ui.info_text.append(info_text_line)
            else:
                self.Ui.info_text.append(img1_text_null)

    def reset(self):
        self.Ui.img1_text.setText('')
        self.Ui.img2_text.setText('')

    def blind_watermark(self,file1,file2):
        print('[debug] blind_watermark函数执行')
        program_dir = '.\\tools\\bwm.exe'
        try:
            subprocess.run('{} decode {} {} ./imgs/result1.png'.format(program_dir,file1,file2),shell=True)
            return True
        except:
            print('[debug] Wrong cmd')
            self.Ui.info_text.append('[*] 执行失败，该图片可能不是盲水印隐写')

    def lsb(self):
        pass

    def inversion(self,file):
        '''图片反相'''
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
        out_img.save("./imgs/result3.png", "PNG")
        return True

    def rgb2img(self):
        '''RGB转图片'''
        print('[debug] rgb2img函数执行')
        filepath = self.Ui.img1_text.toPlainText()
        with open(filepath) as f:  # 打开rbg值的文件
            lines_num = len(open(filepath, 'r').readlines())
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
                im.save('./imgs/result4.jpg')
                return True
            else:
                return False

    def png_crc32(self,file):
        '''根据crc值暴力破解宽度和高度'''
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
                        with open('./imgs/result5.png', 'wb') as f1:
                            f1.write(all_b[0:16] + width + height + all_b[24:])
                            return True

    def metadata(self,file):
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
        '''Gif帧分离'''
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
        '''F5隐写'''
        print('[debug] f5函数执行')
        if pwd != '':
            pwd = pwd
        else:
            pwd = 'abc123'
        try:
            subprocess.run('cd .\\tools\\ && java Extract -e {} -p {}'.format(file,pwd),shell=True)
            return True
        except:
            print('[debug] 报错了，可能是命令错误')
            self.Ui.info_text.append('[*] 执行失败，请排查问题')

    def strings(self,file):
        '''Strings可打印字符'''
        print('[debug] strings函数执行')
        program_dir = '.\\tools\\strings.exe'
        try:
            subprocess.run('{} -a {} > ./tools/strings.txt'.format(program_dir, file), shell=True)
            return True
        except:
            self.Ui.info_text.append('[*] 执行失败，请排查问题')

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

    def qrcode(self,file):
        '''二维码识别'''
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainEvents()       # 加载窗口
    ui.show()               # 显示窗口
    sys.exit(app.exec_())