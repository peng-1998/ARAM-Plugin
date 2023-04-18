import ctypes  # 引入 ctypes 库，用于调用 Windows API
import json  # 引入 json 库，用于处理 JSON 格式的数据

import pyautogui  # 引入 pyautogui 库，用于获取英雄联盟客户端的窗口位置
from PySide6.QtCore import Property, QObject, QPoint, Signal  # 引入 PySide6 库，用于创建 GUI 应用

from Setting import language_pack, setting


# 定义 RiotClientProcess 类，继承自 QObject 类
class RiotClientProcess(QObject):

    # 定义构造函数
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_aram_selecting = False  # 是否正在选择随机英雄
        self._allChampions = "{}"  # 所有英雄的数据
        self._summonerId = 0  # 召唤师 ID
        self._team_champ_select = ["1", "1", "1", "1", "1"]  # 队伍选择的英雄
        self._bench_champ_select = []  # 板凳上的英雄
        self._buffs = {}  # 所有英雄的数据
        self.getBuffData()  # 获取英雄buff数据
        self._port = 0  # 端口号
        self._token = ""  # 令牌
        self.chatId = 0  # 聊天 ID
        self.dpi = ctypes.windll.user32.GetDpiForSystem()  # 获取系统 DPI

    is_aram_selecting_changed = Signal()  # 是否正在选择英雄发生变化的信号
    team_champ_select_changed = Signal()  # 队伍选择的英雄发生变化的信号
    bench_champ_select_changed = Signal()  # 预备选择的英雄发生变化的信号
    buffs_changed = Signal()  # 所有英雄的数据发生变化的信号
    port_changed = Signal()  # 端口号发生变化的信号
    token_changed = Signal()  # 令牌发生变化的信号
    sendBuff = Signal(str)  # 发送英雄数据的信号

    @Property(bool, notify=is_aram_selecting_changed)
    def is_aram_selecting(self) -> bool:
        return self._is_aram_selecting

    def setIs_aram_selecting(self, is_aram_selecting) -> None:
        if self._is_aram_selecting != is_aram_selecting:
            self._is_aram_selecting = is_aram_selecting
            self.is_aram_selecting_changed.emit()
        if not is_aram_selecting: # 如果不是正在ARAM选人, 则重置选择的英雄
            self.setTeam_champ_select(["1", "1", "1", "1", "1"])
            self.setBench_champ_select([])

    def setAllChampions(self, allChampions) -> None:
        buffs = self._buffs
        for k, v in buffs.items():
            champ = allChampions[k]
            v['icon'] = champ['icon']
            v['name'] = champ['name']
        self.buffs_changed.emit()

    @Property(str, notify=team_champ_select_changed)
    def team_champ_select(self) -> str:
        return json.dumps(self._team_champ_select)

    def setTeam_champ_select(self, team_champ_select) -> None:
        team_champ_select = [str(i) for i in team_champ_select]
        if self._team_champ_select != team_champ_select:
            self._team_champ_select = team_champ_select
            self.team_champ_select_changed.emit()

    @Property(str, notify=bench_champ_select_changed)
    def bench_champ_select(self) -> str:
        return json.dumps(self._bench_champ_select)

    def setBench_champ_select(self, bench_champ_select):
        bench_champ_select = [str(i) for i in bench_champ_select]
        if self._bench_champ_select != bench_champ_select:
            self._bench_champ_select = bench_champ_select
            self.bench_champ_select_changed.emit()

    @Property(int, notify=port_changed)
    def port(self) -> int:
        return self._port

    def setPort(self, port) -> None:
        if self._port != port:
            self._port = port
            self.port_changed.emit()

    @Property(str, notify=token_changed)
    def token(self) -> str:
        return self._token

    def setToken(self, token) -> None:
        if self._token != token:
            self._token = token
            self.token_changed.emit()

    @Property(str, notify=buffs_changed)
    def buffs(self) -> str:
        return json.dumps(self._buffs)

    def setBuffs(self, buffs) -> None:
        if self._buffs != buffs:
            self._buffs = buffs
            self.buffs_changed.emit()

    def setChatId(self, chatId) -> None:
        if self.chatId != chatId:
            self.chatId = chatId
            print("chatId:", chatId)

    def format_buff_value(value, decimal_places=0) -> str:
        parsed_value = float(value)
        if parsed_value == 1:
            return "100%"
        sign = "-" if parsed_value < 1 else "+"
        abs_diff = abs(parsed_value - 1) * 100
        return f"{sign}{abs_diff:.{decimal_places}f}%"

    def getBuffData(self) -> None:
        buffs = {}
        with open('data/data.lua', 'r', encoding='utf-8') as f:
            while f.readable():
                line = f.readline()
                if len(line) < 3:
                    break
                if '["id"]' in line:
                    id = line.split('=')[1][:-2].strip()
                    buffs[id] = {}
                if '["aram"]' in line:
                    in_aram = True
                    while in_aram:
                        line = f.readline()
                        if '},' in line:
                            in_aram = False
                        else:
                            line = line[:-1].replace(' ', '').split('=')
                            buffs[id][line[0].replace('"', '').replace('[', '').replace(']', '')] = line[1].replace(',', '')
        new_buffs = {k: v for k, v in buffs.items() if k.isdigit()}
        for buff in new_buffs.values(): # 格式化buff数据
            buff['dmg_dealt'] = RiotClientProcess.format_buff_value(buff['dmg_dealt']) if 'dmg_dealt' in buff else "100%"
            buff['dmg_taken'] = RiotClientProcess.format_buff_value(buff['dmg_taken']) if 'dmg_taken' in buff else "100%"
            other_buffs = []
            for buff_type in ['tenacity', 'energy_regen', 'healing', 'shielding']:
                if buff_type in buff:
                    other_buffs.append(f"{language_pack[setting.language]['buff_name'][buff_type]} {RiotClientProcess.format_buff_value(buff[buff_type])}")
            if 'ability_haste' in buff: # 特殊处理 技能急速 因为不是百分比
                other_buffs.append(f"{language_pack[setting.language]['buff_name']['ability_haste']} {buff['ability_haste']}")
            if 'attack_speed' in buff:  # 特殊处理 攻速 因为需要保留一位小数
                other_buffs.append(f"{language_pack[setting.language]['buff_name']['attack_speed']} {RiotClientProcess.format_buff_value(buff['attack_speed'],1)}")
            buff['other'] = '\n'.join(other_buffs)
        self.setBuffs(new_buffs)

    @Property(QPoint)
    def windowsPosition(self) -> QPoint:
        windows = pyautogui.getWindowsWithTitle("League of Legends") # 获取窗口
        if windows:
            left, top = windows[0].left, windows[0].top
            # 由于获取到的窗口位置是按照dpi缩放的, 所以需要转换成96dpi
            left = int(left * 96 / self.dpi)
            top = int(top * 96 / self.dpi)
            return QPoint(left, top)
        return QPoint(0, 0)
    
    def reset(self) -> None:
        self.setTeam_champ_select(["1", "1", "1", "1", "1"])
        self.setBench_champ_select([])
        self._is_aram_selecting = False
        
