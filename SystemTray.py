from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from Setting import language_pack, languages, setting, ui_sizes


# 创建系统托盘类
class SystemTray(QSystemTrayIcon):

    # 创建系统托盘类
    quit_signal = Signal()
    update_signal = Signal()

    def __init__(self, parent=None) -> None:
        super(SystemTray, self).__init__(parent)
        # 设置托盘图标和提示文字
        self.setIcon(QIcon('images\icon.png'))
        self.setToolTip(language_pack[setting.language]['title'])
        # 创建菜单
        self.menu = QMenu()
        # 获取当前语言下的UI文字
        ui_words = language_pack[setting.language]['ui_words']
        # 创建语言菜单
        lan_menu: QMenu = QMenu()
        lan_menu.setTitle(ui_words["language"])
        # 加入每种语言的选项
        for lan in languages:
            lan_menu.addAction(language_pack[lan]['show'], partial(self.setLanguage, lan))
            lan_menu.actions()[-1].setCheckable(True)
            lan_menu.actions()[-1].setChecked(lan == setting.language)
        self.menu.addMenu(lan_menu)
        # 创建UI尺寸菜单
        size_menu: QMenu = QMenu()
        size_menu.setTitle(ui_words["ui_size"])
        # 加入每个尺寸的选项
        for size in ui_sizes:
            size_menu.addAction(ui_words['ui_size_' + size], partial(self.setUiSize, size))
            size_menu.actions()[-1].setCheckable(True)
        size_menu.actions()[setting.ui_size].setChecked(True)
        self.menu.addMenu(size_menu)
        # 加入更新数据选项
        self.menu.addAction(ui_words["update"], self.update_signal.emit)
        # 加入退出选项
        self.menu.addAction(ui_words["quit"], self.quit_signal.emit)
        # 设置菜单
        self.setContextMenu(self.menu)
        self.show()

    # 设置语言 更新托盘显示的文字
    def setLanguage(self, language) -> None:
        setting.setLanguage(language)
        self.setToolTip(language_pack[setting.language]['from'])
        ui_words: dict = language_pack[setting.language]['ui_words']
        # 更新菜单文字
        self.menu.actions()[3].setText(ui_words["quit"])
        self.menu.actions()[0].setText(ui_words["language"])
        self.menu.actions()[1].setText(ui_words["ui_size"])
        self.menu.actions()[2].setText(ui_words["update"])
        # 更新语言选项的勾选状态
        for act in self.menu.actions()[0].menu().actions():
            act.setChecked(False)
        self.menu.actions()[0].menu().actions()[languages.index(setting.language)].setChecked(True)

    # 设置UI尺寸
    def setUiSize(self, ui_size) -> None:
        if setting.ui_size == ui_sizes.index(ui_size):
            return
        setting.setUiSize(ui_size)
        # 更新UI尺寸选项的勾选状态
        for act in self.menu.actions()[1].menu().actions():
            act.setChecked(False)
        self.menu.actions()[1].menu().actions()[setting.ui_size].setChecked(True)