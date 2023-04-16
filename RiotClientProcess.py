from PySide6.QtCore import QObject, Signal, Slot, Property
import json
from Setting import language_pack, language
from PySide6.QtCore import QPoint

class RiotClientProcess(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_aram_selecting = False
        self._allChampions = "{}"
        self._summonerId = 0
        self._team_champ_select = ["1","1","1","1","1"]
        self._bench_champ_select = []
        self._buffs = {}
        self.getBuffData()
        self._port = 0
        self._token = ""
        self.chatId = 0
        self.window = None

    is_aram_selecting_changed = Signal()
    team_champ_select_changed = Signal()
    bench_champ_select_changed = Signal()
    buffs_changed = Signal()
    port_changed = Signal()
    token_changed = Signal()
    sendBuff = Signal(str)

    @Property(bool, notify=is_aram_selecting_changed)
    def is_aram_selecting(self):
        return self._is_aram_selecting

    def setIs_aram_selecting(self, is_aram_selecting):
        if self._is_aram_selecting != is_aram_selecting:
            self._is_aram_selecting = is_aram_selecting
            self.is_aram_selecting_changed.emit()
        if not is_aram_selecting:
            self.setTeam_champ_select([])
            self.setBench_champ_select([])

    def setAllChampions(self, allChampions):
        buffs = self._buffs
        for k,v in buffs.items():
            champ = allChampions[k]
            v['icon'] = champ['icon']
            v['name'] = champ['name']
        self.buffs_changed.emit()
        

    @Property(str, notify=team_champ_select_changed)
    def team_champ_select(self):
        return json.dumps(self._team_champ_select)

    def setTeam_champ_select(self, team_champ_select):
        team_champ_select = [str(i) for i in team_champ_select]
        if self._team_champ_select != team_champ_select:
            self._team_champ_select = team_champ_select
            self.team_champ_select_changed.emit()

    @Property(str, notify=bench_champ_select_changed)
    def bench_champ_select(self):
        return json.dumps(self._bench_champ_select)

    def setBench_champ_select(self, bench_champ_select):
        bench_champ_select = [str(i) for i in bench_champ_select]
        if self._bench_champ_select != bench_champ_select:
            self._bench_champ_select = bench_champ_select
            self.bench_champ_select_changed.emit()

    @Property(int, notify=port_changed)
    def port(self):
        return self._port

    def setPort(self, port):
        if self._port != port:
            self._port = port
            self.port_changed.emit()

    @Property(str, notify=token_changed)
    def token(self):
        return self._token

    def setToken(self, token):
        if self._token != token:
            self._token = token
            self.token_changed.emit()

    @Property(str,notify=buffs_changed)
    def buffs(self):
        return json.dumps(self._buffs)
    def setBuffs(self,buffs):
        if self._buffs != buffs:
            self._buffs = buffs
            self.buffs_changed.emit()

    def setChatId(self, chatId):
        if self.chatId != chatId:
            self.chatId = chatId
            print("chatId:", chatId)

    def format_buff_value(value, decimal_places=0):
        parsed_value = float(value)
        if parsed_value == 1:
            return "100%"
        sign = "-" if parsed_value < 1 else "+"
        abs_diff = abs(parsed_value - 1) * 100
        return f"{sign}{abs_diff:.{decimal_places}f}%"

    def getBuffData(self):
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
        # buffs= {k:v for k,v in buffs.items() if k.isdigit()}
        new_buffs = {}
        for k, v in buffs.items():
            if not k.isdigit():
                continue
            buff = {'icon':"", 'name':"", 'dmg_dealt':"", 'dmg_taken':"", 'other':""}
            buff['dmg_dealt'] = RiotClientProcess.format_buff_value(v['dmg_dealt']) if 'dmg_dealt' in v else "100%"
            buff['dmg_taken'] = RiotClientProcess.format_buff_value(v['dmg_taken']) if 'dmg_taken' in v else "100%"
            other_buffs = []
            for buff_type in ['tenacity', 'energy_regen', 'healing', 'shielding']:
                if buff_type in v:
                    other_buffs.append(f"{language_pack[language]['buff_name'][buff_type]} {RiotClientProcess.format_buff_value(v[buff_type])}")
            if 'ability_haste' in v:
                other_buffs.append(f"{language_pack[language]['buff_name']['ability_haste']} {v['ability_haste']}")
            if 'attack_speed' in v:
                other_buffs.append(f"{language_pack[language]['buff_name']['attack_speed']} {RiotClientProcess.format_buff_value(v['attack_speed'],1)}")
            buff['other'] = '\n'.join(other_buffs)
            new_buffs[k] = buff
        self.setBuffs(new_buffs)

    @Property(QPoint)
    def windowsPosition(self):
        if self.window:
            return QPoint(*self.window.topleft)
        return QPoint(0,0)
        

        
