from PyQt5 import QtWidgets
import sys

# Local Module Imports
import app_framework as af

app = QtWidgets.QApplication(sys.argv)
form = af.MyApp()
form.show()
app.exec_()

# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
# import UI
# # import WRF_SCM_FORCING_INITIALIZATION_MAKER as scm
# import parse_xml
#
# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super(QMainWindow, self).__init__(parent)
#         self.ui = UI.Ui_MainWindow()
#         self.ui.setupUi(self)
#     def parse_xml(self):
#         # 选择xml文件
#         filename,_ = QFileDialog.getOpenFileName(self, '选择xml文件')
#         self.ui.log_textBrowser.append('xml文件路径：'+filename)
#         # 解析xml文件
#         px = parse_xml.Parse_xml(filename)
#         # 验证xml文件
#         is_validate,error_log = px.validate()
#         if is_validate:
#             self.ui.log_textBrowser.append('xml 验证通过')
#         else:
#             self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
#             self.ui.log_textBrowser.append('xml 验证失败，错误提示：')
#             self.ui.log_textBrowser.append(str(error_log))
#             return False
#         # 生成input_sounding
#         is_ok = px.make_input_sounding()
#         if is_ok:
#             self.ui.log_textBrowser.append('input_sounding 生成成功')
#         else:
#             self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
#             self.ui.log_textBrowser.append('input_sounding 生成失败')
#             return False
#         # 生成input_soil
#         is_ok = px.make_input_soil()
#         if is_ok:
#             self.ui.log_textBrowser.append('input_soil 生成成功')
#         else:
#             self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
#             self.ui.log_textBrowser.append('input_soil 生成失败')
#             return False
#         # 生成force.nc
#         is_ok,error_log=px.make_forcing()
#         if is_ok:
#             self.ui.log_textBrowser.append('force.nc 生成成功')
#         else:
#             self.ui.log_textBrowser.append('<<--FATAL ERROR-->>')
#             self.ui.log_textBrowser.append('force.nc 生成失败，错误提示：')
#             self.ui.log_textBrowser.append(error_log)
#             return False
#         self.ui.log_textBrowser.append('<<--SUCCEESS-->>')
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     myWindow = MainWindow()
#     myWindow.show()
#     sys.exit(app.exec())
#
#
#
