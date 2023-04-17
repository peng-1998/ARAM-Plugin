# 语言
languages = [
    'zh_CN',
    'en_US',
    'zh_TW'
]
ui_sizes = [
    'large',
    'middle',
    'small'
]

# 语言包
language_pack = {
    'zh_CN': {
        'buff_name':{
            'attack_speed': '攻速成长',
            'dmg_dealt': '伤害',
            'dmg_taken': '承伤',
            'tenacity': '韧性',
            'energy_regen': '能量回复',
            'healing': '治疗效果',
            'shielding': '护盾效果',
            'ability_haste': '技能急速',
        },
        'ui_words':{
                "champion":"英雄",
                "damage_dealt":"伤害",
                "damage_taken":"承伤",
                "other":"其他",
                "send":"发送",
                "otherchampion":"可替换英雄",
                "settings":"设置",
                "language":"语言",
                "quit":"退出",
                "ui_size":"界面大小",
                "ui_size_small":"小",
                "ui_size_middle":"中",
                "ui_size_large":"大",
        },
        'from':"来自极地大乱斗助手",
        'show':"简体中文"
    },
    'en_US': {
        'buff_name':{
            'attack_speed': 'Attack Speed',
            'dmg_dealt': 'Damage',
            'dmg_taken': 'Damage Taken',
            'tenacity': 'Tenacity',
            'energy_regen': 'Energy Regen',
            'healing': 'Healing',
            'shielding': 'Shielding',
            'ability_haste': 'Ability Haste',
        },
        'ui_words':{
                "champion":"Champ",
                "damage_dealt":"DD",
                "damage_taken":"DT",
                "other":"Other",
                "send":"Send",
                "otherchampion":"Other Champions",
                "settings":"Settings",
                "language":"Language",
                "quit":"Quit",
                "ui_size":"UI Size",
                "ui_size_small":"Small",
                "ui_size_middle":"Middle",
                "ui_size_large":"Large",
        },
        'from':"From ARAM Helper",
        'show':"English"
    },
    'zh_TW': {
        'buff_name':{
            'attack_speed': '攻速成長',
            'dmg_dealt': '傷害',
            'dmg_taken': '承傷',
            'tenacity': '韌性',
            'energy_regen': '能量回復',
            'healing': '治療效果',
            'shielding': '護盾效果',
            'ability_haste': '技能急速',
        },
        'ui_words':{
                "champion":"英雄",
                "damage_dealt":"傷害",
                "damage_taken":"承傷",
                "other":"其他",
                "send":"發送",
                "otherchampion":"可替換英雄",
                "settings":"設置",
                "language":"語言",
                "quit":"退出",
                "ui_size":"界面大小",
                "ui_size_small":"小",
                "ui_size_middle":"中",
                "ui_size_large":"大",
        },
        'from':"來自隨機單中助手",
        'show':"繁體中文"
    }
}


from PySide6.QtCore import QObject, Signal, Property
import json
class Setting(QObject):
    def __init__(self):
        super().__init__()
        self._language = "zh_CN"
        self._ui_size = "middle"
        self.file = "setting.json"
        self.load()
    

    language_changed = Signal()
    @Property(str, notify=language_changed)
    def language(self):
        return self._language
    def setLanguage(self, language):
        if self._language != language:
            self._language = language
            self.language_changed.emit()
            self.save()
    
    ui_size_changed = Signal()
    @Property(int, notify=ui_size_changed)
    def ui_size(self):
        return ui_sizes.index(self._ui_size)
    def setUiSize(self, ui_size):
        if self._ui_size != ui_size:
            self._ui_size = ui_size
            self.ui_size_changed.emit()
            self.save()
    
    @Property(str)
    def ui_words(self):
        return json.dumps(language_pack[self._language]['ui_words'])
    
    def load(self):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
                self.setLanguage(data['language'])
                self.setUiSize(data['ui_size'])
        except:
            with open(self.file, 'w') as f:
                json.dump({
                    'language': self._language,
                    'ui_size': self._ui_size
                }, f)

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'language': self._language,
                'ui_size': self._ui_size
            }, f)

    

setting = Setting()
