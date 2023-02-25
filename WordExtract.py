'''

@author: YuYuXiang

@fucntion: 批量提取pdf中所有单词

@time: 2023-01-17

'''

import sys
import re
import os
import string
import io
from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog
from PyQt5 import QtCore, uic
import pandas
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator, TextConverter
import xlrd

class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("WordProcess.ui")
        self.word_list = {}
        # print(self.ui.__dict__)  # 查看ui文件中有哪些控件

        # 用来显示系统消息
        # self.ui.msg.setWordWrap(True)  # 自动换行
        # self.ui.msg.setAlignment(Qt.AlignTop)  # 靠上
        # 创建垂直布局器，用来添加自动滚动条
        # v_layout = QVBoxLayout()
        # v_layout.addWidget(QScrollArea)
        # try:
        #     print("111")
        #     self.ui.scrollArea.setWidget(self.ui.msg)
        # except Exception as e:
        #     print(e)


        self.ui.file_adress_bidui.setText("D:\Program\Python\EnglishArticleProcess\800sentence.txt")
        self.ui.file_adress_kaogang.setText("D:\Program\Python\EnglishArticleProcess\考研英语词汇.txt")
        self.ui.file_save_path.setText("D:\桌面")

        # 绑定槽函数--------------

        # 选择文件路径
        self.ui.select_file_bidui.clicked.connect(lambda: self.click_find_file_path(1))
        self.ui.select_file_kaogang.clicked.connect(lambda: self.click_find_file_path(2))
        # 选择保存路径
        self.ui.select_save_path.clicked.connect(self.click_set_save_path)
        # 解析
        self.ui.jiexi.clicked.connect(self.click_jiexi)
        # 保存
        self.ui.save.clicked.connect(self.click_save)
        # 调整消息框的scrollbar的槽函数
        self.ui.scrollArea.verticalScrollBar().rangeChanged.connect(self.set_scroll_bar)
        # # 选择保存
        # self.ui.select_type.clicked.connect(lambda: self.click_find_file_path(self.ui.select_type))



    # 更新系统消息的函数
    def updatemsg(self, news):
        self.ui.msg.resize(361, self.ui.msg.frameSize().height() + 20)
        # self.ui.scrollArea.setMinimumHeight(self.ui.msg.frameSize().height() + 60)
        self.ui.msg.setText(self.ui.msg.text() + "<br>" + news)
        self.ui.msg.repaint()  # 更新内容，如果不更新可能没有显示新内容

    # 调整消息框的scrollbar的槽函数
    def set_scroll_bar (self):
        self.ui.scrollArea.verticalScrollBar().setValue(self.ui.scrollArea.verticalScrollBar().maximum())

    # 选择保存路径的槽函数
    def click_set_save_path(self):
        m = QFileDialog.getExistingDirectory(None, "选取文件夹", "./")  # 起始路径
        if m != "" :
            self.ui.file_save_path.setText(m)

    # 选择文件的槽函数
    def click_find_file_path(self, flag):
        # 设置文件扩展名过滤，同一个类型的不同格式如xlsx和xls 用空格隔开
        filename, filetype = QFileDialog.getOpenFileName(self, "选择文件", "C:/Users", "*.xls *.xlsx *.pdf *.txt")
        if filename =="" :
            return
        if flag == 1 :
            self.ui.file_adress_bidui.setText(filename)
        elif flag == 2 :
            self.ui.file_adress_kaogang.setText(filename)

    # 解析文件的槽函数
    def click_jiexi(self):
        self.updatemsg("开始解析比对文件")
        biduifile = self.ui.file_adress_bidui.text()
        self.word_list["比对文件的单词"] = get_word(biduifile)
        self.updatemsg("开始解析考纲文件")
        kaogangfile = self.ui.file_adress_kaogang.text()
        self.word_list["考纲文件的单词"] = get_word(kaogangfile)

        self.updatemsg("开始比较")
        # self.ui.msg.text + "解析完成"
        hanyou = []
        queshi = []
        for word in self.word_list["考纲文件的单词"] :
            if word in self.word_list["比对文件的单词"] :
                hanyou.append(word)
            else:
                queshi.append(word)
        self.word_list["比对文件中含有的考纲词"] = hanyou
        self.word_list["比对文件中缺失的考纲词"] = queshi
        # a-b
        self.updatemsg("比较结束")
        self.updatemsg(u"比对文件中共有" + str(len(self.word_list["比对文件的单词"])) + u"个单词")
        self.updatemsg(u"比对文件中含有" + str(len(hanyou)) + u"个考纲词")
        self.updatemsg(u"比对文件中缺失" + str(len(queshi)) + u"个考纲词")


    # 保存文件的槽函数
    def click_save(self):
        path = self.ui.file_save_path.text()
        type = self.ui.select_file_type.currentText()
        if(path == "") :
            self.updatemsg(U"请输入保存路径")
            return
        else :
            self.updatemsg(u"保存路径为：" + path)
        if (type == "保存格式"):
            self.updatemsg(U"请选择要保存的格式")
            return
        else:
            self.updatemsg(u"保存格式为：" + type)
        self.updatemsg("开始保存文件")

        flag = self.ui.select_type.currentText()
        self.updatemsg(u"您的选择是：" + flag)

        if flag == "选择要保存的单词" :
            self.updatemsg(U"请选择要保存的文件！")
            return
        elif flag == "保存对比文件中的所有单词" :
            try :
                save_file(self.word_list["比对文件的单词"], path, "比对文件的单词", type)
            except Exception as e :
                self.updatemsg(e)
                self.updatemsg("出错了！可能是保存路径错误！")
                return
        elif flag == "保存对比文件中缺失的考纲词" :
            try :
                save_file(self.word_list["比对文件中缺失的考纲词"], path, "比对文件缺失的考纲词", type)
            except Exception as e :
                self.updatemsg(e)
                self.updatemsg("出错了！可能是保存路径错误！")
                return
        elif flag == "保存对比文件中的考纲词" :
            try :
                save_file(self.word_list["比对文件中含有的考纲词"], path, "比对文件含有的考纲词", type)
            except Exception as e :
                self.updatemsg(e)
                self.updatemsg("出错了！可能是保存路径错误！！")
                return
        else :
            self.updatemsg(U"请选择要保存的文件！")
            return

        self.updatemsg(u"保存成功")

# 保存文件的函数
def save_file(lst, path, name, type) :
    # print("list is :")
    # print(lst)
    if path[len(path)-1] != '/' :
        path = path + '/'
    if type == ".txt" :
        file = open(path + name + type, 'w')
        mid = str(lst).replace('[', '').replace(']', '')
        # 删除单引号并用字符空格代替逗号
        mid = mid.replace("'", '').replace(',', '')
        file.write(mid)
        file.close()
    elif type == ".xlsx" :
        mid = pandas.DataFrame(lst)
        mid.to_excel(path + name + type, header=False, index=False)
    elif type == ".csv" :
        mid = pandas.DataFrame(lst)
        mid.to_csv(path + name + type, header=False, index=False)
    else :
        self.updatemsg("Save Error!")

# 获取文件中的单词列表的函数
def get_word(file):
    # self.updatemsg("function get_word start work")
    word_list = []

    if file.endswith("txt") :
        f = open(file, 'r', encoding='utf-8')
        for line in f.readlines():
            # 去掉非字母的符号
            line = re.sub(r'[^a-z]+', ' ', line.lower())
            text = line.split()
            for word in text:
                if (word not in word_list) and (len(word) > 2):
                    word_list.append(word)
        f.close()
    elif file.endswith("xls") or file.endswith("xlsx") :
        f = xlrd.open_workbook(file)  # 打开excel表所在路径
        for sheet in f.sheets():
            for r in range(sheet.nrows):  # 将表中数据按行逐步添加到列表中，最后转换为list结构
                for c in range(sheet.ncols):
                    word = sheet.cell_value(r, c)
                    word = re.sub(r'[^a-z]+', '', str(word).lower())
                    if (word not in word_list) and (len(word) > 2):
                        word_list.append(word)
    elif file.endswith("pdf") :
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        with open(file, 'rb') as fh:
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
        converter.close()
        fake_file_handle.close()
        text = re.sub(r'[^a-z]+', ' ', text.lower())
        text = text.split()
        for word in text:
            if (word not in word_list) and (len(word) > 2):
                word_list.append(word)

    # else:
        # self.updatemsg("Error, invalid file type")
    # self.updatemsg("function get_word end work")
    return word_list


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MyWindow()
    # 展示窗口
    w.ui.show()

    app.exec()
