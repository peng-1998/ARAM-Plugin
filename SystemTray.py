from PySide6.QtWidgets import QSystemTrayIcon,QMenu,QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal


class SystemTray(QSystemTrayIcon):

    quit_signal = Signal()
    setting_signal = Signal()

    def __init__(self, parent=None):
        super(SystemTray, self).__init__(parent)
        self.setIcon(QIcon('images\icon.png'))
        self.setToolTip('极地大乱斗选人助手')
        self.menu = QMenu()
        self.menu.addAction('设置', self.setting_signal.emit)
        self.menu.addAction('退出', self.quit_signal.emit)
        self.setContextMenu(self.menu)
        self.show()


