from functools import partial
from PySide6.QtWidgets import QSystemTrayIcon,QMenu,QApplication
from PySide6.QtGui import QIcon,QAction
from PySide6.QtCore import Signal
from Setting import setting,languages,ui_sizes,language_pack


class SystemTray(QSystemTrayIcon):

    quit_signal = Signal()
    setting_signal = Signal()


    def __init__(self, parent=None):
        super(SystemTray, self).__init__(parent)
        self.setIcon(QIcon('images\icon.png'))
        self.setToolTip('极地大乱斗选人助手')
        self.menu = QMenu()
        ui_words = language_pack[setting.language]['ui_words']
        
        lan_menu = QMenu()
        lan_menu.setTitle(ui_words["language"])
        for lan in languages:
            lan_menu.addAction(language_pack[lan]['show'], partial(self.setLanguage, lan))
            lan_menu.actions()[-1].setCheckable(True)
        lan_menu.actions()[languages.index(setting.language)].setChecked(True)
        self.menu.addMenu(lan_menu)
        size_menu = QMenu()
        size_menu.setTitle(ui_words["ui_size"])
        for size in ui_sizes:
            size_menu.addAction(ui_words['ui_size_'+size], partial(self.setUiSize, size))
            size_menu.actions()[-1].setCheckable(True)
        size_menu.actions()[setting.ui_size].setChecked(True)
        self.menu.addMenu(size_menu)
        self.menu.addAction(ui_words["quit"], self.quit_signal.emit)
        self.setContextMenu(self.menu)
        self.show()

    def setLanguage(self, language):
        setting.setLanguage(language)
        ui_words = language_pack[setting.language]['ui_words']
        self.menu.actions()[2].setText(ui_words["quit"])
        self.menu.actions()[0].setText(ui_words["language"])
        self.menu.actions()[1].setText(ui_words["ui_size"])
        for act in self.menu.actions()[0].menu().actions():
            act.setChecked(False)
        self.menu.actions()[0].menu().actions()[languages.index(setting.language)].setChecked(True)
    
    def setUiSize(self, ui_size):
        setting.setUiSize(ui_size)
        for act in self.menu.actions()[1].menu().actions():
            act.setChecked(False)
        self.menu.actions()[1].menu().actions()[setting.ui_size].setChecked(True)

