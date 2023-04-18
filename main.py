import asyncio
import sys
from ast import List

from lcu_driver import Connector
from lcu_driver.connection import Connection
from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtNetwork import QSslCertificate, QSslConfiguration
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox

from RiotClientProcess import RiotClientProcess
from Setting import language_pack, setting
from SystemTray import SystemTray


class Backend(QThread):

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        connector.start()


# 发送Buff信息
def sendBuff(championId):
    buff: str = riotclient_process._buffs[championId]
    words: str = f"{buff['name']}:{language_pack[setting.language]['buff_name']['dmg_dealt']}{buff['dmg_dealt']} {language_pack[setting.language]['buff_name']['dmg_taken']}{buff['dmg_taken']} {buff['other']}--{language_pack[setting.language]['from']}"
    words: str = words.replace("\n", " ")
    sandlist.append(words)


# 退出程序
def quit():
    backend.terminate()
    app.quit()


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

    pem: List = QSslCertificate.fromPath('data/riotgames.pem')
    config: QSslConfiguration = QSslConfiguration.defaultConfiguration()
    config.addCaCertificate(pem[0])
    QSslConfiguration.setDefaultConfiguration(config)

    riotclient_process: RiotClientProcess = RiotClientProcess()
    backend: Backend = Backend()

    # 定义英雄联盟连接器
    connector: Connector = Connector()
    sandlist = []
    # 定义连接开始事件
    @connector.ready
    async def init(connection: Connection):
        # 获取端口 和 token
        riotclient_process.setPort(connection._port)
        riotclient_process.setToken(connection._auth_key)

        # 获取当前游戏用户信息
        summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
        summoner: dict = await summoner.json()
        # 设置summonerId
        riotclient_process._summonerId: int = summoner['summonerId']
        # 获取所有英雄信息
        Champions = await connection.request('get', f'/lol-champions/v1/inventories/{riotclient_process._summonerId}/champions')
        Champions: List = await Champions.json()
        allChampions = {str(champion['id']): {'name': champion['name'], 'icon': f"https://riot:{riotclient_process.token}@127.0.0.1:{riotclient_process.port}{champion['squarePortraitPath']}"} for champion in Champions if champion['id'] != -1}

        riotclient_process.setAllChampions(allChampions)

        async def send_chat():
            while True:
                while len(sandlist) > 0:
                    msg = sandlist.pop(0)
                    req = await connection.request('post', f'/lol-chat/v1/conversations/{riotclient_process.chatId}/messages', data={'body': msg, 'type': 'chat'})
                await asyncio.sleep(0.1)

        asyncio.create_task(send_chat())

    @connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE', 'CREATE'))
    async def gameflow_updated(connection, event):
        if event.data == 'InProgress':
            riotclient_process.setIs_aram_selecting(False)

    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE', 'CREATE'))
    async def session_updated(connection, event):
        # 判断是在极地大乱斗选人界面
        riotclient_process.setIs_aram_selecting(event.data.get('benchEnabled', False))

        if event.data.get('benchEnabled', False):
            # 顶部可选英雄
            benchChampions: list = event.data['benchChampions']
            # 队伍当前选择的英雄
            myTeam: list = event.data['myTeam']
            benchChampions: list = [champion['championId'] for champion in benchChampions]
            teamChampions: list = [champion['championId'] for champion in myTeam]
            riotclient_process.setTeam_champ_select(teamChampions)
            riotclient_process.setBench_champ_select(benchChampions)
        chatId: str = event.data['chatDetails']['multiUserChatId']
        riotclient_process.setChatId(chatId)

    @connector.close
    async def disconnect(connection):
        # 当客户端断开连接时，重置所有数据
        riotclient_process.reset()

    riotclient_process.sendBuff.connect(sendBuff)
    # 启动后台线程 即英雄联盟连接器
    backend.start()
    # 主要界面
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("riotclient_process", riotclient_process)
    engine.rootContext().setContextProperty('setting', setting)
    engine.load(QUrl.fromLocalFile('main.qml'))

    # SystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("error")
        msgBox.setInformativeText("Couldn't detect any system tray on this system.")
        msgBox.setWindowTitle("error")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.setIcon(QMessageBox.Icon.Warning)
        msgBox.exec_()
        sys.exit(1)
    else:
        trayIcon = SystemTray()
        trayIcon.quit_signal.connect(quit)
        trayIcon.update_signal.connect(riotclient_process.update)

    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
