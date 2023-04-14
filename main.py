import sys
from PySide6.QtGui import QGuiApplication,QIcon,QAction
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QTimer,QThread
from PySide6.QtWidgets import QSystemTrayIcon,QMenu,QApplication

from psutil import process_iter, Process
import json 

from lcu_driver import Connector
from RiotClientProcess import RiotClientProcess
from SystemTray import SystemTray

class Backend(QThread):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        connector.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    riotclient_process = RiotClientProcess()
    backend=Backend()
    # 定义英雄联盟连接器
    connector = Connector()
    # 定义连接开始事件
    @connector.ready
    async def init(connection):
        # 获取当前游戏用户信息
        summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
        summoner = await summoner.json()
        # 设置summonerId
        riotclient_process._summonerId = summoner['summonerId']
        # 获取所有英雄信息
        Champions = await connection.request('get', f'/lol-champions/v1/inventories/{riotclient_process._summonerId}/champions')
        Champions = await Champions.json()
        allChampions = {}
        prot = connection._port
        for champion in Champions:
            id = champion['id']
            if id==-1:
                continue
            name = champion['name']
            icon = champion['squarePortraitPath']
            # 保存英雄信息 id 名字 头像
            allChampions[str(id)] = {'name':name,'icon':f"https://127.0.0.1:{prot}{icon}"}
        riotclient_process.setAllChampions(allChampions)

    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def session_updated(connection, event):
        # 判断是在极地大乱斗选人界面
        riotclient_process.setIs_jddld_selecting(event.data['benchEnabled'])

        if event.data['benchEnabled']:
            # 顶部可选英雄
            benchChampions = event.data['benchChampions']
            # 队伍当前选择的英雄
            myTeam = event.data['myTeam']
            benchChampions = [champion['championId'] for champion in benchChampions]
            teamChampions = [champion['championId'] for champion in myTeam]
            riotclient_process.setTeam_champ_select(teamChampions)
            riotclient_process.setBench_champ_select(benchChampions)

    @connector.close
    async def disconnect(connection):
        # 当客户端断开连接时，重置所有数据
        riotclient_process.setAllChampions([])
        riotclient_process.setIs_jddld_selecting(False)

    # 启动后台线程 即英雄联盟连接器
    backend.start()
    # 主要界面
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("riotclient_process", riotclient_process)
    engine.load(QUrl.fromLocalFile('main.qml'))

    def quit():
        backend.quit()
        app.quit()
    # SystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print('I couldn\'t detect any system tray on this system.')
    else:
        trayIcon = SystemTray()
        trayIcon.quit_signal.connect(quit)
        
    if not engine.rootObjects():
        sys.exit(-1)
        
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)

