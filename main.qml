import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: window
    width: 300
    height: 800
    visible: true
    title: "Hello World"
    flags: Qt.FramelessWindowHint
    Rectangle {
        id:bgRect
        width:parent.width
        height:parent.height
        color:"black"
        Item {
            id:topBar
            width:parent.width
            height:30
            x:0
            y:0

            Item {
                anchors.fill: parent
                width: parent.width-30
                height: parent.height
                DragHandler {
                    grabPermissions: TapHandler.CanTakeOverFromAnything
                    onActiveChanged: if (active) { window.startSystemMove(); }
                }
            }


            MouseArea {
                id:closeBtn
                width:parent.height
                height:parent.height
                anchors.right:parent.right
                anchors.top:parent.top
                hoverEnabled:true
                onClicked: {
                    window.hide()
                }
                onEntered: {
                    closeBtnRect.color="#444444"
                }
                onExited: {
                    closeBtnRect.color=bgRect.color
                }

                Rectangle {
                    id:closeBtnRect
                    width:parent.width
                    height:parent.height
                    color:bgRect.color
                    Text {
                        id:closeBtnText
                        anchors.centerIn:parent
                        text:"X"
                        color:"white"
                        font.pixelSize:parent.height-10
                    }
                }
            }
        }
        Item{
            id:buffViewer
            width:parent.width
            Component {
                id: buffItem
                Item {
                    width:parent.width
                    height:60
                    Item{
                        id:buffIcon
                        width:80
                        height:parent.height
                        Image{
                            width:parent.height - 10
                            height:parent.height - 10
                            anchors.centerIn:parent
                            source:img_source
                        }
                    }
                    Text{
                        id:dmg_dealt_tex
                        width:60
                        height:parent.height/2
                        anchors.left:buffIcon.right
                        anchors.top:parent.top
                        font.pixelSize:20
                        color:"white"
                        text:dmg_dealt
                    }
                    Text{
                        id:dmg_taken_tex
                        width:60
                        height:parent.height/2
                        anchors.left:buffIcon.right
                        anchors.top:dmg_dealt_tex.bottom
                        font.pixelSize:20
                        color:"white"
                        text:dmg_taken
                    }
                    Text{
                        id:other_tex
                        width:parent.width - 60 - parent.height - 10
                        height:parent.height
                        anchors.left:dmg_dealt_tex.right
                        anchors.top:parent.top
                        font.pixelSize:20
                        color:"white"
                        text:other
                        wrapMode: Text.WordWrap
                    }
                }
            }
            Item{
                id:buffHeader
                width:parent.width
                height:30
                Text{
                    id:buffHeader1
                    width:80
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:parent.left
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize:20
                    color:"white"
                    text:"英雄"
                }
                Text{
                    id:buffHeader2
                    width:80
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:buffHeader1.right
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize:20
                    color:"white"
                    text:"伤害/承伤"
                }

                Text{
                    width:parent.width - buffHeader2.width - buffHeader1.width
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:buffHeader2.right
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    color:"white"
                    text:"其他"
                    font.pixelSize:20
                }
            }

            ListView{
                id:teamViewer
                width:parent.width
                height:500
                delegate:buffItem
                anchors.top:buffHeader.bottom
                model:ListModel{
                    id:teamModel
                    ListElement{
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                    }
                    ListElement{
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                    }
                    ListElement{
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                    }
                    ListElement{
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                    }
                    ListElement{
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                    }
                }
            }
            ListView{
                id:benchViewer
            }
        }
    }
    Connections {
        target: riotclient_process
        function onAllChampions_changed(){
            var champions=riotclient_process.allChampions
            champions = JSON.parse(champions)
            for(var i = 0; i < teamModel.count; i++){
                var em = teamModel.get(i)
                em.img_source = champions[teamModel.get(i).championId].icon
                console.log(em.img_source)
            }
        }
    }
    Component.onCompleted: {
        var buffs = riotclient_process.buffs
        buffs = JSON.parse(buffs)
        var teamChampions = [1,2,22,4,5]
        for(var i = 0; i < teamChampions.length; i++){
            var em = teamModel.get(i)
            em.championId = teamChampions[i]
            if(! teamChampions[i].toString() in buffs){
                em.dmg_dealt="100%"
                em.dmg_taken="100%"
                em.other=""
            }
            var champion = buffs[teamChampions[i].toString()]
            if("dmg_dealt" in champion){
                var dmg_dealt=parseFloat(champion.dmg_dealt)
                if(dmg_dealt != 1){
                    dmg_dealt = (dmg_dealt < 1 ? "-" : "+") + (Math.abs(dmg_dealt - 1) * 100).toFixed(0) + "%";
                }else{
                    dmg_dealt = "100%"
                }
                em.dmg_dealt=dmg_dealt
            }else{
                em.dmg_dealt=dmg_dealt
            }
            if("dmg_taken" in champion){
                var dmg_taken=parseFloat(champion.dmg_taken)
                if(dmg_taken != 1){
                    dmg_taken = (dmg_taken < 1 ? "-" : "+") + (Math.abs(dmg_taken - 1) * 100).toFixed(0) + "%";
                }else{
                    dmg_taken = "100%"
                }
                em.dmg_taken=dmg_taken
            }else{
                em.dmg_taken=dmg_taken
            }
            var other = ""
            if("tenacity" in champion){
                var tenacity=parseFloat(champion.tenacity)
                if(tenacity != 1){
                    tenacity = (tenacity < 1 ? "-" : "+") + (Math.abs(tenacity - 1) * 100).toFixed(0) + "%";
                }else{
                    tenacity = "100%"
                }
                other += "韧性:" + tenacity+" "
            }
            if("energy_regen" in champion){
                var energy_regen=parseFloat(champion.energy_regen)
                if(energy_regen != 1){
                    energy_regen = (energy_regen < 1 ? "-" : "+") + (Math.abs(energy_regen - 1) * 100).toFixed(0) + "%";
                }else{
                    energy_regen = "100%"
                }
                other += "能量回复:" + energy_regen+" "
            }
            if("healing" in champion){
                var healing=parseFloat(champion.healing)
                if(healing != 1){
                    healing = (healing < 1 ? "-" : "+") + (Math.abs(healing - 1) * 100).toFixed(0) + "%";
                }else{
                    healing = "100%"
                }
                other += "治疗效果:" + healing+" "
            }
            if("shielding" in champion){
                var shielding=parseFloat(champion.shielding)
                if(shielding != 1){
                    shielding = (shielding < 1 ? "-" : "+") + (Math.abs(shielding - 1) * 100).toFixed(0) + "%";
                }else{
                    shielding = "100%"
                }
                other += "护盾效果:" + shielding+" "
            }
            if("attack_speed" in champion){
                var attack_speed=parseFloat(champion.attack_speed)
                if(attack_speed != 1){
                    attack_speed = (attack_speed < 1 ? "-" : "+") + (Math.abs(attack_speed - 1) * 100).toFixed(0) + "%";
                }else{
                    attack_speed = "100%"
                }
                other += "攻速成长:" + attack_speed+" "
            }
            if("ability_haste" in champion){
                other += "技能冷却:" + champion.ability_haste+" "
            }

            em.other=other
        }
    }

}