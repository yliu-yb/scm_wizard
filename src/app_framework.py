import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
import UI
import parse_xml
from namelist import Namelist
from wrfout import Wrfoutdata
import os
from woker import Worker
from mplwidget import MplCanvas
from draw import draw_wrfout, draw_force, draw_initialization
import threading

def fmt(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    b = int(b)
    return r'$10^{{{}}}$'.format(b)

class MyApp(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = UI.Ui_MainWindow()
        self.ui.setupUi(self)

        # window size change
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.updateView)

        self.ui.tabWidget.currentChanged.connect(self.tab_changed)

        # Setting
        self.setting = QtCore.QSettings("v1", "wrf_scm_wizard")

        #TAB "INPUT" SET
        self.tab_input_set()
        #TAB "NAMELIST" SET
        self.tab_namelist_set()
        #TAB "RUN" SET
        self.tab_run_set()

        self.tab_result_set()

    def tab_result_set(self):
        try:
            self.wrfoutdata = Wrfoutdata(self.wrf_base_dir)
            for item in self.wrfoutdata.vars:
                self.ui.comboBox_N1.addItem(item)
                self.ui.comboBox_N2.addItem(item)
                self.ui.comboBox_N3.addItem(item)
                self.ui.comboBox_N4.addItem(item)
            self.ui.comboBox_N1.setCurrentIndex(0)
            self.ui.comboBox_N2.setCurrentIndex(1)
            self.ui.comboBox_N3.setCurrentIndex(2)
            self.ui.comboBox_N4.setCurrentIndex(3)
        except:
            pass
        self.ui.comboBox_N1.currentTextChanged['QString'].connect(lambda x: self.draw_wrfout(x, self.ui.widget_N1.canvas))
        self.ui.comboBox_N2.currentTextChanged['QString'].connect(lambda x: self.draw_wrfout(x, self.ui.widget_N2.canvas))
        self.ui.comboBox_N3.currentTextChanged['QString'].connect(lambda x: self.draw_wrfout(x, self.ui.widget_N3.canvas))
        self.ui.comboBox_N4.currentTextChanged['QString'].connect(lambda x: self.draw_wrfout(x, self.ui.widget_N4.canvas))

    def draw_wrfout(self, var, canvas : MplCanvas) -> None:
        if var not in self.wrfoutdata.vars:
            print('no var:', var)
            return 0
        xlabel = 'DateTime'
        ylabel = 'Height'
        title = getattr(self.wrfoutdata.df.variables[var], 'description')
        barlabel = getattr(self.wrfoutdata.df.variables[var], 'units')

        draw_wrfout(canvas, self.wrfoutdata.datetime, self.wrfoutdata.height, self.wrfoutdata.df.variables[var][:,:,0,0], xlabel, ylabel, title, barlabel)

    def tab_changed(self, index):
        if index == 2:
            namelist_input_path = self.namelist.Save()
            self.ui.lineEdit_namelist_input_folder.setText(namelist_input_path)
        elif index == 3:
            try:
                threading.Thread(target=self.result_draw_thread).start()
            except:
                pass

    def result_draw_thread(self):
        self.draw_wrfout(self.ui.comboBox_N1.currentText(), self.ui.widget_N1.canvas)
        self.draw_wrfout(self.ui.comboBox_N2.currentText(), self.ui.widget_N2.canvas)
        self.draw_wrfout(self.ui.comboBox_N3.currentText(), self.ui.widget_N3.canvas)
        self.draw_wrfout(self.ui.comboBox_N4.currentText(), self.ui.widget_N4.canvas)

    def closeEvent(self, event):
        self.setting.setValue('wrf_folder', self.ui.lineEdit_wrf_folder.text())
        self.setting.setValue('ideal_folder', self.ui.lineEdit_ideal_folder.text())
        self.setting.setValue('input_soil_folder', self.ui.lineEdit_input_soil_folder.text())
        self.setting.setValue('input_sounding_folder', self.ui.lineEdit_input_sounding_folder.text())
        self.setting.setValue('force_ideal_folder', self.ui.lineEdit_force_ideal_folder.text())
        self.setting.setValue('namelist_folder', self.ui.lineEdit_namelist_input_folder.text())
        self.setting.setValue('wrf_out_folder', self.ui.lineEdit_wrf_out_folder.text())
        self.setting.setValue('wrf_base_dir', self.wrf_base_dir)
        print(self.setting.fileName())

    def tab_run_set(self):
        self.ui.pushButton_wrf_folder.clicked.connect(lambda x: self.choose_folder('Choose WRF Executable Program',
                                                                                   '|>WRF Executable Program Path: ',
                                                                                   self.ui.lineEdit_wrf_folder,
                                                                                   self.ui.log_textBrowser))

        self.ui.pushButton_ideal_folder.clicked.connect(lambda x: self.choose_folder('Choose IDEAL Executable Program',
                                                                                   '|>IDEAL Executable Program Path: ',
                                                                                   self.ui.lineEdit_ideal_folder,
                                                                                   self.ui.log_textBrowser))

        self.ui.pushButton_input_soil_folder.clicked.connect(lambda x: self.choose_folder('Choose Input_soil File',
                                                                                   '|>IDEAL Input_soil File: ',
                                                                                   self.ui.lineEdit_input_soil_folder,
                                                                                   self.ui.log_textBrowser))

        self.ui.pushButton_input_sounding_folder.clicked.connect(lambda x: self.choose_folder('Choose Input_sounding File',
                                                                                   '|>IDEAL Input_sounding File: ',
                                                                                   self.ui.lineEdit_input_sounding_folder,
                                                                                   self.ui.log_textBrowser))

        self.ui.pushButton_force_ideal_folder.clicked.connect(lambda x: self.choose_folder('Choose Force_ideal File',
                                                                                   '|>IDEAL Force_ideal File: ',
                                                                                   self.ui.lineEdit_force_ideal_folder,
                                                                                   self.ui.log_textBrowser))

        self.ui.pushButton_namelist_input_folder.clicked.connect(lambda x: self.choose_folder('Choose Namelist_input File',
                                                                                     '|>IDEAL Namelist_input File: ',
                                                                                     self.ui.lineEdit_namelist_input_folder,
                                                                                     self.ui.log_textBrowser))

        self.ui.pushButton_wrf_out_folder.clicked.connect(lambda x: self.select_directory('Choose WRF Output Folder',
                                                                                     '|>IDEAL WRF Output Folder: ',
                                                                                     self.ui.lineEdit_wrf_out_folder,
                                                                                     self.ui.log_textBrowser))

        self.ui.pushButton_run_scm_wrf.clicked.connect(self.run_wrf_scm)
        self.ui.pushButton_wrf_run_log_clear.clicked.connect(self.clear_wrf_run_log)
        self.wrf_base_dir = ''

        if self.setting.contains('wrf_folder'):
            self.ui.lineEdit_wrf_folder.setText(self.setting.value('wrf_folder'))
        if self.setting.contains('ideal_folder'):
            self.ui.lineEdit_ideal_folder.setText(self.setting.value('ideal_folder'))
        if self.setting.contains('input_soil_folder'):
            self.ui.lineEdit_input_soil_folder.setText(self.setting.value('input_soil_folder'))
        if self.setting.contains('input_sounding_folder'):
            self.ui.lineEdit_input_sounding_folder.setText(self.setting.value('input_sounding_folder'))
        if self.setting.contains('force_ideal_folder'):
            self.ui.lineEdit_force_ideal_folder.setText(self.setting.value('force_ideal_folder'))
        if self.setting.contains('namelist_folder'):
            self.ui.lineEdit_namelist_input_folder.setText(self.setting.value('namelist_folder'))
        if self.setting.contains('wrf_out_folder'):
            self.ui.lineEdit_wrf_out_folder.setText(self.setting.value('wrf_out_folder'))
        if self.setting.contains('wrf_base_dir'):
            self.wrf_base_dir = self.setting.value('wrf_base_dir')
        self.worker = Worker()
        self.worker.outSignal.connect(self.logging)

    def logging(self, string):
        if string == 'yanliu':
            try:
                self.ui.comboBox_N1.clear()
                self.ui.comboBox_N2.clear()
                self.ui.comboBox_N3.clear()
                self.ui.comboBox_N4.clear()
                self.wrfoutdata = Wrfoutdata(self.wrf_base_dir)
                for item in self.wrfoutdata.vars:
                    self.ui.comboBox_N1.addItem(item)
                    self.ui.comboBox_N2.addItem(item)
                    self.ui.comboBox_N3.addItem(item)
                    self.ui.comboBox_N4.addItem(item)

                self.ui.comboBox_N1.setCurrentIndex(0)
                self.ui.comboBox_N2.setCurrentIndex(1)
                self.ui.comboBox_N3.setCurrentIndex(2)
                self.ui.comboBox_N4.setCurrentIndex(3)
                self.ui.log_textBrowser.append('|>run WRF successed')
            except:
                pass
        else:
            self.ui.textBrowser_wrf_out.append(string.strip())
    def clear_wrf_run_log(self):
        self.ui.textBrowser_wrf_out.clear()

    def run_wrf_scm(self):
        wrf_base_dir_list = self.ui.lineEdit_wrf_folder.text().split('/')
        self.wrf_base_dir = ""
        for d in wrf_base_dir_list[:len(wrf_base_dir_list)-1]:
            self.wrf_base_dir += d + "/"

        self.run_wrf_scm_fileName = "run_wrf_scm.sh"

        # clear wrf folder
        file_1 = open('clear_wrf_folder.sh', 'w')
        file_1.write("cd " + self.wrf_base_dir)
        file_1.write("\n")
        file_1.write("rm -rf input_soil")
        file_1.write("\n")
        file_1.write("rm -rf input_sounding")
        file_1.write("\n")
        file_1.write("rm -rf force_ideal.nc")
        file_1.write("\n")
        file_1.write("rm -rf namelist.input")
        file_1.write("\n")
        file_1.write("rm -rf wrfinput_*")
        file_1.write("\n")
        file_1.write("rm -rf wrfout_*")

        file_1.close()
        os.system("chmod +x clear_wrf_folder.sh")
        os.system("./clear_wrf_folder.sh")
        os.system("rm -rf clear_wrf_folder.sh")

        # link input data to wrf folder
        os.system("ln " + self.ui.lineEdit_input_soil_folder.text() + " " + self.wrf_base_dir)
        os.system("ln " + self.ui.lineEdit_input_sounding_folder.text() + " " + self.wrf_base_dir)
        os.system("ln " + self.ui.lineEdit_force_ideal_folder.text() + " " + self.wrf_base_dir)
        os.system("ln " + self.ui.lineEdit_namelist_input_folder.text() + " " + self.wrf_base_dir)

        self.make_run_wrf_scm_sh()
        os.system("chmod +x " + self.run_wrf_scm_fileName)
        command = "./" + self.run_wrf_scm_fileName

        self.worker.run_command(command, cwd = './')

    def make_run_wrf_scm_sh(self):
        file = open("./" + self.run_wrf_scm_fileName, 'w')
        file.write("cd " + self.wrf_base_dir)
        file.write("\n")
        file.write("ulimit -s unlimited")
        file.write("\n")
        file.write(self.ui.lineEdit_ideal_folder.text())
        file.write("\n")
        file.write(self.ui.lineEdit_wrf_folder.text())
        file.close()

    def choose_folder(self, hint_1, hint_2, lineEdit, log_browser):
        filename,_ = QFileDialog.getOpenFileName(self, hint_1, '', 'ALL FILES(*)')
        if filename == "":
            return 0
        lineEdit.setText(filename)
        log_browser.append(hint_2 + filename)
    def select_directory(self, hint_1, hint_2, lineEdit, log_browser):
        directory = QFileDialog.getExistingDirectory(self, hint_1)
        if directory == "":
            return 0
        lineEdit.setText(directory)
        log_browser.append(hint_2 + directory)
    def tab_namelist_set(self):
        self.domainNum = 1
        self.namelist_table_header = ["Parameter", "Master Domain"]
        # namelist load from user set file or form default file
        # namelist domain
        self.set_maxDomain_nums()
        self.set_namelist_table_content()
        self.add_data_to_namelist_table()

        # namelist content
        self.ui.tableWidget_namelist.itemPressed.connect(self.hint_namelist_description)
        self.ui.tableWidget_namelist.cellChanged.connect(self.namelist_cell_changed)
        self.ui.pushButton_Reset.clicked.connect(self.namelist_domain_reset)
        self.ui.pushButton_validate.clicked.connect(self.namelist.Save)

    def tab_input_set(self):
        self.data_mk = False
        self.show_force_variable = ''
        self.set_singnal_slot()

    def save_namelist(self):
        self.namelist.Save()

    def namelist_domain_reset(self):
        columnCount = self.ui.tableWidget_namelist.columnCount()
        for i in range(1, columnCount):
            for j in range(0, len(self.namelist.parameter)):
                self.ui.tableWidget_namelist.setItem(j, i, QTableWidgetItem(''))

    def namelist_cell_changed(self, row, column):
        cell_text = self.ui.tableWidget_namelist.item(row, column).text()
        if column == 0:
            self.namelist.parameter[row] = cell_text
        elif column == 1:
            self.namelist.mainDomain[row] = cell_text
        else:
            self.namelist.nest[column-2][row] = cell_text
        if row > 0 and row < 17:
            if cell_text != '':
                cell_text = cell_text.zfill(2)
            self.ui.tableWidget_namelist.cellChanged.disconnect(self.namelist_cell_changed)
            self.ui.tableWidget_namelist.setItem(row, column, QTableWidgetItem(cell_text))
            self.ui.tableWidget_namelist.cellChanged.connect(self.namelist_cell_changed)

        return 0
    def hint_namelist_description(self):
        row = self.ui.tableWidget_namelist.currentRow()
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(self.namelist.description[row])

    def add_data_to_namelist_table(self):
        self.namelist = Namelist(0)
        for p, d in zip(self.namelist.parameter, self.namelist.defaultValue):
            rowcount = self.ui.tableWidget_namelist.rowCount()
            if rowcount > 0 and rowcount < 17:
                d = str(d).zfill(2)
            self.ui.tableWidget_namelist.insertRow(rowcount)
            self.ui.tableWidget_namelist.setItem(rowcount, 0, QTableWidgetItem(p))
            self.ui.tableWidget_namelist.setItem(rowcount, 1, QTableWidgetItem(d))

    def set_namelist_table_content(self):
        self.ui.tableWidget_namelist.setColumnCount(int(self.ui.comboBox_maxDoms.currentText()) + 1)
        self.domainNum = int(self.ui.comboBox_maxDoms.currentText())
        self.ui.tableWidget_namelist.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_namelist.verticalHeader().hide()
        self.ui.tableWidget_namelist.setHorizontalHeaderLabels(self.namelist_table_header)
        self.ui.tableWidget_namelist.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

    def domain_num_changed(self, strNums):
        nums = int(strNums)
        num_diff = nums - self.domainNum
        if num_diff > 0:
            for i in range(0, num_diff):
                self.namelist_table_header.append("Nest " + str(self.ui.tableWidget_namelist.columnCount()))
                self.ui.tableWidget_namelist.insertColumn(self.ui.tableWidget_namelist.columnCount())
                self.ui.tableWidget_namelist.setHorizontalHeaderLabels(self.namelist_table_header)
                self.namelist.nest.append([])
                for j in range(0, len(self.namelist.parameter)):
                    self.namelist.nest[len(self.namelist.nest)-1].append('')
                print('nest num:',len(self.namelist.nest))
            self.domainNum = nums
        if num_diff < 0:
            for i in range(0, abs(num_diff)):
                self.ui.tableWidget_namelist.removeColumn(self.ui.tableWidget_namelist.columnCount()-1)
                self.namelist_table_header.pop()
                del self.namelist.nest[len(self.namelist.nest) - 1]
                print('nest num:',len(self.namelist.nest))
            self.domainNum = nums


    def set_maxDomain_nums(self):
        '''
        set "max domain" combobox content as domain nums (1-16)
        '''
        for i in range(1, 16):
            self.ui.comboBox_maxDoms.addItem(str(i))

    def set_singnal_slot(self):
        # "input" model parse_xml and force var change
        self.ui.pushButton.clicked.connect(self.parse_xml)
        self.ui.comboBox.currentTextChanged['QString'].connect(self.on_force_combobox)
        self.ui.comboBox_maxDoms.currentTextChanged['QString'].connect(self.domain_num_changed)

    def resizeEvent(self, event):
        # if self.data_mk:
        self.timer.stop()
        self.timer.start()
        return super(QMainWindow, self).resizeEvent(event)
    def updateView(self):
        try:
            self.draw_wrfout(self.ui.comboBox_N1.currentText(), self.ui.widget_N1.canvas)
            self.draw_wrfout(self.ui.comboBox_N2.currentText(), self.ui.widget_N2.canvas)
            self.draw_wrfout(self.ui.comboBox_N3.currentText(), self.ui.widget_N3.canvas)
            self.draw_wrfout(self.ui.comboBox_N4.currentText(), self.ui.widget_N4.canvas)
        except:
            pass

        if self.data_mk == False:
            return
        draw_initialization(self.ui.plot_initial_widget.canvas, self.px.souding_z, self.px.souding_qv,
                            self.px.souding_theta, self.px.souding_u, self.px.souding_v)

        self.on_force_combobox(self.show_force_variable)
        print('window resize and redraw data')

    def parse_xml(self):
        # 选择xml文件
        filename,_ = QFileDialog.getOpenFileName(self, '选择xml文件', '../../scm_wizard_data/data/', 'xml file (*.xml)')
        if filename == "":
            return 0
        self.ui.log_textBrowser.append('|>xml文件路径：'+filename)
        # 解析xml文件
        # self.px = parse_xml.Parse_xml(filename)
        try:
            self.px = parse_xml.Parse_xml(filename)
        except:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>xml 解析失败，错误提示：')
            self.ui.log_textBrowser.append(self.str2Red(str(sys.exc_info())))
            return
        else:
            self.ui.log_textBrowser.append('|>xml 解析成功')
        # 验证xml文件
        is_validate,error_log = self.px.validate()
        if is_validate:
            self.ui.log_textBrowser.append('|>xml 验证通过')
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>xml 验证失败，错误提示：')
            # print(error_log[0])
            for err in error_log:
                self.ui.log_textBrowser.append(self.str2Red(str(err)))
            return False
        # 生成input_sounding
        is_ok,input_souding_path = self.px.make_input_sounding()
        if is_ok:
            self.ui.log_textBrowser.append('|>input_sounding 生成成功')
            self.ui.lineEdit_input_sounding_folder.setText(input_souding_path)
            draw_initialization(self.ui.plot_initial_widget.canvas, self.px.souding_z, self.px.souding_qv, self.px.souding_theta, self.px.souding_u, self.px.souding_v)
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>input_sounding 生成失败')
            return False
        # 生成input_soil
        is_ok,input_soil_path = self.px.make_input_soil()
        if is_ok:
            self.ui.log_textBrowser.append('|>input_soil 生成成功')
            self.ui.lineEdit_input_soil_folder.setText(input_soil_path)
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>input_soil 生成失败')
            return False
        # 生成force.nc
        is_ok,error_log,force_ideal_path = self.px.make_forcing()
        if is_ok:
            self.ui.log_textBrowser.append('|>force.nc 生成成功')
            self.on_force_combobox('U')
            self.ui.lineEdit_force_ideal_folder.setText(force_ideal_path)
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>force.nc 生成失败，错误提示：')
            self.ui.log_textBrowser.append(self.str2Red(error_log))
            return False
        self.data_mk = True
        self.ui.log_textBrowser.append('<<--SUCCEESS-->>')

    def on_force_combobox(self, force_variable):
        self.show_force_variable = force_variable
        if force_variable == 'U':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       ,self.px.force_u, force_variable, 'Height(km)', 'DateTime', 'ms$^{-1}$')
        if force_variable == 'V':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_v, force_variable, 'Height(km)', 'DateTime', 'ms$^{-1}$')
        if force_variable == 'W':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_w, force_variable, 'Height(km)', 'Dat eTime', 'ms$^{-1}$')
        if force_variable == 'QVAPOR':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qvapor, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'QRAIN':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qrain, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'QCLOUD':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qcloud, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'theta':
            draw_force(self.ui.plot_force_widget.canvas, self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_theta, force_variable, 'Height(km)', 'DateTime', 'K', True)


    def str2Red(self, str):
        return "<span style=\" font-size:10pt; font-weight:500; color:#ff0000;\" >" + str + "</span>"