import sys

import numpy
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import UI
# import WRF_SCM_FORCING_INITIALIZATION_MAKER as scm
import parse_xml
import datetime
import matplotlib.dates as mdates
from numpy import ma
from matplotlib import ticker
import numpy as np

class MyApp(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.ui = UI.Ui_MainWindow()
        self.ui.setupUi(self)
    def parse_xml(self):
        # 选择xml文件
        filename,_ = QFileDialog.getOpenFileName(self, '选择xml文件', '../data/', 'xml file (*.xml)')
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
            self.ui.log_textBrowser.append(self.str2Red(str(error_log)))
            return False
        # 生成input_sounding
        is_ok = self.px.make_input_sounding()
        if is_ok:
            self.ui.log_textBrowser.append('|>input_sounding 生成成功')
            self.plot_initialization()
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>input_sounding 生成失败')
            return False
        # 生成input_soil
        is_ok = self.px.make_input_soil()
        if is_ok:
            self.ui.log_textBrowser.append('|>input_soil 生成成功')
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>input_soil 生成失败')
            return False
        # 生成force.nc
        is_ok,error_log = self.px.make_forcing()
        if is_ok:
            self.ui.log_textBrowser.append('|>force.nc 生成成功')
            self.on_force_combobox('U')
        else:
            self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
            self.ui.log_textBrowser.append('|>force.nc 生成失败，错误提示：')
            self.ui.log_textBrowser.append(self.str2Red(error_log))
            return False
        self.ui.log_textBrowser.append('<<--SUCCEESS-->>')

    def plot_force(self, f_datetime, f_z, f_variable_2D, title, ylabel, xlabel, cbar_label, log_mk=False):
        force_datetime = [datetime.datetime.strptime(dt, '%Y-%m-%d_%H:%M:%S') for dt in f_datetime]
        f_variable_2D = list(map(list, zip(*f_variable_2D)))
        ax1 = self.ui.plot_force_widget.canvas.fig.add_subplot(111)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m%d'))
        ax1.set_ylim(top = 12)
        if log_mk:
            f_variable_2D = numpy.array(f_variable_2D)
            f_variable_2D = ma.masked_where(f_variable_2D <= 0, f_variable_2D)
            cs = ax1.contourf(force_datetime, f_z, f_variable_2D, locator=ticker.LogLocator(),cmap='RdBu_r')
        else:
            cs = ax1.contourf(force_datetime, f_z, f_variable_2D, cmap='RdBu_r')
        cbar = self.ui.plot_force_widget.canvas.fig.colorbar(cs, ax = ax1, label = cbar_label)
        ax1.set_title(title)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        self.ui.plot_force_widget.canvas.fig.autofmt_xdate()
        self.ui.plot_force_widget.canvas.fig.set_tight_layout(True)
        self.ui.plot_force_widget.canvas.draw()
        cbar.remove()
        ax1.remove()

    def on_force_combobox(self, force_variable):
        if force_variable == 'U':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       ,self.px.force_u, force_variable, 'Height(km)', 'DateTime', 'ms$^{-1}$')
        if force_variable == 'V':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_v, force_variable, 'Height(km)', 'DateTime', 'ms$^{-1}$')
        if force_variable == 'W':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_w, force_variable, 'Height(km)', 'Dat eTime', 'ms$^{-1}$')
        if force_variable == 'QVAPOR':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qvapor, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'QRAIN':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qrain, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'QCLOUD':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_qcloud, force_variable, 'Height(km)', 'DateTime', 'kgkg$^{-1}$', True)
        if force_variable == 'theta':
            self.plot_force(self.px.force_datetime, [x / 1000 for x in self.px.force_z]
                       , self.px.force_theta, force_variable, 'Height(km)', 'DateTime', 'K', True)

    def plot_initialization(self):
        sounding_z = [x / 1000 for x in self.px.souding_z]
        ax1 = self.ui.plot_initial_widget.canvas.fig.add_subplot(121)
        ax2 = self.ui.plot_initial_widget.canvas.fig.add_subplot(122, sharey=ax1)
        #
        sounding_qv = numpy.array(self.px.souding_qv)
        sounding_qv = ma.masked_where(sounding_qv <= 0, sounding_qv)
        ax1.set_xscale('log')
        ax1.set_ylim(top = 12)
        p1, = ax1.plot(self.px.souding_qv, sounding_z, 'b-', label = 'qv')
        ax1.set_xlabel('kgkg$^{-1}$')
        ax1.set_ylabel('Height(km)')
        ax1.xaxis.label.set_color(p1.get_color())
        ax11 = ax1.twiny()
        p11, = ax11.plot(self.px.souding_theta, sounding_z, 'g-', label = 'theta')
        ax11.set_xlabel('K')
        ax11.xaxis.label.set_color(p11.get_color())
        tkw = dict(size=4, width=1.5)
        ax1.tick_params(axis='x', colors=p1.get_color(), **tkw)
        ax11.tick_params(axis='x', colors=p11.get_color(), **tkw)
        ax1.legend(handles=[p1, p11])
        ax2.set_ylim(top = 12)
        ax2.barbs([0 for x in range(len(sounding_z))], sounding_z, self.px.souding_u, self.px.souding_v, length = 7)
        ax2.set_title('Wind')
        ax2.axes.get_xaxis().set_visible(False)
        self.ui.plot_initial_widget.canvas.fig.set_tight_layout(True)
        self.ui.plot_initial_widget.canvas.draw()
        ax1.remove()
        ax11.remove()
        ax2.remove()
    def str2Red(self, str):
        return "<span style=\" font-size:10pt; font-weight:500; color:#ff0000;\" >" + str + "</span>"