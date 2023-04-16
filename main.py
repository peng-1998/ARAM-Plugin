import asyncio
import sys
from PySide6.QtGui import QGuiApplication,QIcon,QAction
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QTimer,QThread
from PySide6.QtWidgets import QSystemTrayIcon,QMenu,QApplication
from PySide6.QtNetwork import QSslCertificate,QSslConfiguration,QNetworkAccessManager,QNetworkRequest,QNetworkReply

from psutil import process_iter, Process
import json 
import pyautogui
from lcu_driver import Connector
from lcu_driver.connection import Connection
from RiotClientProcess import RiotClientProcess
from SystemTray import SystemTray
from Setting import language_pack, language

class Backend(QThread):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        connector.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pem = QSslCertificate.fromPath('data/riotgames.pem')
    config = QSslConfiguration.defaultConfiguration()
    config.addCaCertificate(pem[0])
    QSslConfiguration.setDefaultConfiguration(config)
    netmanager = QNetworkAccessManager()

    riotclient_process = RiotClientProcess()
    backend=Backend()

    # 定义英雄联盟连接器
    connector = Connector()
    sandlist = []
    # 定义连接开始事件
    @connector.ready
    async def init(connection:Connection):
        # 获取端口 和 token
        riotclient_process.setPort(connection._port)
        riotclient_process.setToken(connection._auth_key)

        # 获取当前游戏用户信息
        summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
        summoner = await summoner.json()
        # 设置summonerId
        riotclient_process._summonerId = summoner['summonerId']
        # 获取所有英雄信息
        Champions = await connection.request('get', f'/lol-champions/v1/inventories/{riotclient_process._summonerId}/champions')
        Champions = await Champions.json()
        allChampions = {}
        
        for champion in Champions:
            id = champion['id']
            if id==-1:
                continue
            name = champion['name']
            icon = champion['squarePortraitPath']
            # 保存英雄信息 id 名字 头像
            allChampions[str(id)] = {'name':name,'icon':f"https://riot:{riotclient_process.token}@127.0.0.1:{riotclient_process.port}{icon}"}
        
        window = pyautogui.getWindowsWithTitle("League of Legends")[0]
        riotclient_process.window = window
        
        
        riotclient_process.setAllChampions(allChampions)
        async def send_chat():
            while True:
                while len(sandlist)>0:
                    msg = sandlist.pop(0)
                    req = await connection.request('post',f'/lol-chat/v1/conversations/{riotclient_process.chatId}/messages', data={'body': msg, 'type': 'chat'})
                await asyncio.sleep(0.1)
        await send_chat()


    @connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
    async def gameflow_updated(connection, event):
        if event.data == 'InProgress':
            riotclient_process.setIs_aram_selecting(False)


    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def session_updated(connection, event):
        # 判断是在极地大乱斗选人界面
        riotclient_process.setIs_aram_selecting(event.data['benchEnabled'])

        if event.data['benchEnabled']:
            # 顶部可选英雄
            benchChampions = event.data['benchChampions']
            # 队伍当前选择的英雄
            myTeam = event.data['myTeam']
            benchChampions = [champion['championId'] for champion in benchChampions]
            teamChampions = [champion['championId'] for champion in myTeam]
            riotclient_process.setTeam_champ_select(teamChampions)
            riotclient_process.setBench_champ_select(benchChampions)
        chatId = event.data['chatDetails']['multiUserChatId']
        riotclient_process.setChatId(chatId)


    @connector.close
    async def disconnect(connection):
        # 当客户端断开连接时，重置所有数据
        riotclient_process.setAllChampions([])
        riotclient_process.setIs_aram_selecting(False)
        riotclient_process.window = None
        connector.start()

    
    def sendBuff(championId):
        buff = riotclient_process._buffs[championId]
        words = buff["name"]+":"+language_pack[language]["buff_name"]["dmg_dealt"]+\
            buff["dmg_dealt"]+" "+language_pack[language]["buff_name"]["dmg_taken"]+\
            buff["dmg_taken"]+" "+buff["other"]+"--"+language_pack[language]["from"]
        words = words.replace("\n","")
        sandlist.append(words)
        
    riotclient_process.sendBuff.connect(sendBuff)
    # 启动后台线程 即英雄联盟连接器
    backend.start()
    # 主要界面
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("riotclient_process", riotclient_process)
    engine.load(QUrl.fromLocalFile('main.qml'))

    def quit():
        backend.terminate()
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

