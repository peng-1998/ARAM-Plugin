from PySide6.QtCore import QObject, Signal, Slot, Property
import json

class RiotClientProcess(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_jddld_selecting = False
        self._allChampions =""
        self._summonerId = 0
        self._team_champ_select = []
        self._bench_champ_select = []
        self._buffs = {}
        self.getBuffData()

    is_jddld_selecting_changed = Signal()
    allChampions_changed = Signal()
    team_champ_select_changed = Signal()
    bench_champ_select_changed = Signal()

    @Property(bool, notify=is_jddld_selecting_changed)
    def is_jddld_selecting(self):
        return self._is_jddld_selecting
    def setIs_jddld_selecting(self,is_jddld_selecting):
        if self._is_jddld_selecting != is_jddld_selecting:
            self._is_jddld_selecting = is_jddld_selecting
            self.is_jddld_selecting_changed.emit()
        if not is_jddld_selecting:
            self.setTeam_champ_select([])
            self.setBench_champ_select([])
    
    @Property(str, notify=allChampions_changed)
    def allChampions(self):
        return self._allChampions
    def setAllChampions(self,allChampions):
        allChampions = json.dumps(allChampions)
        if self._allChampions != allChampions:
            self._allChampions = allChampions
            self.allChampions_changed.emit()

    @Property(list, notify=team_champ_select_changed)
    def team_champ_select(self):
        return self._team_champ_select
    def setTeam_champ_select(self,team_champ_select):
        if self._team_champ_select != team_champ_select:
            self._team_champ_select = team_champ_select
            self.team_champ_select_changed.emit()
    
    @Property(list, notify=bench_champ_select_changed)
    def bench_champ_select(self):
        return self._bench_champ_select
    def setBench_champ_select(self,bench_champ_select):
        if self._bench_champ_select != bench_champ_select:
            self._bench_champ_select = bench_champ_select
            self.bench_champ_select_changed.emit()

    @Property(str)
    def buffs(self):
        return self._buffs

    def getBuffData(self):
        buffs = {}
        with open('data/data.lua', 'r', encoding='utf-8') as f:
            while f.readable():
                line = f.readline()
                if len(line) <3:
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
                            line = line[:-1].replace(' ','').split('=')
                            buffs[id][line[0].replace('"','').replace('[','').replace(']','')] = line[1].replace(',','')
        buffs= {k:v for k,v in buffs.items() if k.isdigit()}
        self._buffs = json.dumps(buffs)

