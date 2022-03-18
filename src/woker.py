import subprocess
import threading
from PyQt5 import QtCore
import os

class Worker(QtCore.QObject):
    outSignal = QtCore.pyqtSignal(str)

    def run_command(self, cmd, **kwargs):
        threading.Thread(target=self._execute_command, args=(cmd,), kwargs=kwargs,daemon=True).start()

    def _execute_command(self, cmd, **kwargs):
        proc = subprocess.Popen(cmd, shell=True, stdout= subprocess.PIPE, stderr= subprocess.STDOUT, encoding='utf-8', **kwargs)
        for line in proc.stdout:
            self.outSignal.emit(line)
        self.outSignal.emit('yanliu')
        os.system("rm -rf run_wrf_scm.sh")