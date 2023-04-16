import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: window
    width: 400
    height: 30+30+1+5*61+61*benchModel.count+31
    x: 0
    y: 0
    
    title: "Hello World"
    flags: Qt.FramelessWindowHint
    property var buffs:JSON.parse(riotclient_process.buffs)
    property var team_champ_select:JSON.parse(riotclient_process.team_champ_select)
    property var bench_champ_select:JSON.parse(riotclient_process.bench_champ_select)
    property bool is_aram_selecting:riotclient_process.is_aram_selecting
    visible: is_aram_selecting
    Rectangle {
        id:bgRect
        anchors.fill:parent
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
        Item {
            id:buffViewer
            width:parent.width
            anchors.top:topBar.bottom
            Component {
                id: buffItem
                Item {
                    width:buffViewer.width
                    height:61
                    property int linewidth: 1
                    Item {
                        id:buffIcon
                        width:80
                        height:parent.height-parent.linewidth
                        Image {
                            width:parent.height - 10
                            height:parent.height - 10
                            anchors.centerIn:parent
                            source:img_source
                        }
                    }
                    Text {
                        id:dmg_dealt_tex
                        width:60
                        height: (parent.height-parent.linewidth)/2
                        anchors.left:buffIcon.right
                        anchors.top:parent.top
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize:20
                        color: {if(dmg_dealt == "100%"){return "white"}else {if(dmg_dealt[0] == "-"){return "red"}else {return "green"}}}
                        text:dmg_dealt
                    }
                    Text {
                        id:dmg_taken_tex
                        width:60
                        height: (parent.height-parent.linewidth)/2
                        anchors.left:buffIcon.right
                        anchors.top:dmg_dealt_tex.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize:20
                        color: {if(dmg_taken == "100%"){return "white"}else {if(dmg_taken[0] == "-"){return "green"}else {return "red"}}}
                        text:dmg_taken
                    }
                    Text {
                        id:other_tex
                        width:parent.width - 60 - parent.height - 10 - 60
                        height:parent.height - parent.linewidth
                        anchors.left:dmg_dealt_tex.right
                        anchors.top:parent.top
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: {
                            var count = (other.match(/\n/g) || []).length + 1;
                            if (count >2)
                            {
                                return parseInt(20*0.6)
                            }
                            return 20
                        }
                        color:"white"
                        text:other
                        wrapMode: Text.WordWrap
                    }
                    MouseArea {
                        id:sendBtn
                        width:60
                        height:parent.height-parent.linewidth
                        anchors.right:parent.right
                        anchors.top:parent.top
                        hoverEnabled:true
                        Rectangle {
                            id:sendBtnRect
                            anchors.fill:parent 
                            color:"transparent"
                        }
                        
                        Text {
                            id:sendBtnText
                            anchors.centerIn:parent
                            text:"发送"
                            color:"white"
                            font.pixelSize:20
                        }
                        onClicked: {
                            riotclient_process.sendBuff(championId)
                        }
                        onEntered: {
                            sendBtnRect.color="#444444"
                        }
                        onExited: {
                            sendBtnRect.color="transparent"
                        }
                    }
                    Rectangle {
                        width:parent.width*0.9
                        height:parent.linewidth
                        anchors.bottom:parent.bottom
                        anchors.horizontalCenter:parent.horizontalCenter
                        color:"gray"
                    }
                }
            }
            Item {
                id:buffHeader
                width:parent.width
                height:30
                Text {
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
                Text {
                    id:buffHeader2
                    width:60
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:buffHeader1.right
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize:13
                    color:"white"
                    text:"伤害\n承伤"
                }

                Text {
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
            Rectangle {
                id:firstLine
                width:parent.width
                height:1
                anchors.top:buffHeader.bottom
                color:"gray"
            }

            ListView {
                id:teamViewer
                width:parent.width
                height:61*5
                delegate:buffItem
                anchors.top:firstLine.bottom
                flickableDirection: Flickable.AutoFlickIfNeeded

                model:ListModel {
                    id:teamModel
                    ListElement {
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                        name:""
                    }
                    ListElement {
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                        name:""
                    }
                    ListElement {
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                        name:""
                    }
                    ListElement {
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                        name:""
                    }
                    ListElement {
                        dmg_dealt:"100%"
                        dmg_taken:"100%"
                        other:""
                        img_source:""
                        championId:"1"
                        name:""
                    }
                }
            }
            Text{
                id:benchHeader
                width:parent.width
                height:30
                anchors.top:teamViewer.bottom
                verticalAlignment: Text.AlignVCenter
                font.pixelSize:20
                color:"white"
                text:"可替换英雄"
            }
            Rectangle {
                id:secondLine
                width:parent.width
                height:1
                anchors.top:benchHeader.bottom
                color:"gray"
            }
            ListView {
                id:benchViewer
                width:parent.width
                delegate:buffItem
                anchors.top:secondLine.bottom
                flickableDirection: Flickable.AutoFlickIfNeeded
                model:ListModel {
                    id:benchModel
                }
                height: 61*benchModel.count
            }
        }
    }
    function updateTeamView(){
        if(!window.is_aram_selecting){
            return
        }
        for(var i = 0; i < 5; i++)
        {
            var em = teamModel.get(i)
            em.dmg_dealt = window.buffs[window.team_champ_select[i]].dmg_dealt
            em.dmg_taken = window.buffs[window.team_champ_select[i]].dmg_taken
            em.other = window.buffs[window.team_champ_select[i]].other
            em.img_source = window.buffs[window.team_champ_select[i]].icon
            em.championId = window.team_champ_select[i]
            em.name = window.buffs[window.team_champ_select[i]].name
        }
    }
    function updateBanchView() {
        if(!window.is_aram_selecting){
            return
        }
        // var view_length = benchModel.count
        // if(window.bench_champ_select.length==0){
        //     benchModel.clear()
        //     return
        // }
        // if(window.bench_champ_select.length>view_length){
        //     for(var i = view_length; i < window.bench_champ_select.length; i++)
        //     {
        //         benchModel.append({
        //                               dmg_dealt:window.buffs[window.bench_champ_select[i]].dmg_dealt,
        //                               dmg_taken:window.buffs[window.bench_champ_select[i]].dmg_taken,
        //                               other:window.buffs[window.bench_champ_select[i]].other,
        //                               img_source:window.buffs[window.bench_champ_select[i]].icon,
        //                               championId:window.bench_champ_select[i],
        //                               name:window.buffs[window.bench_champ_select[i]].name
        //                           })
        //     }
        // }
        // else if(window.bench_champ_select.length==view_length){
        //     for(var i = 0; i < view_length; i++)
        //     {
        //         var em = benchModel.get(i)
        //         em.dmg_dealt = window.buffs[window.bench_champ_select[i]].dmg_dealt
        //         em.dmg_taken = window.buffs[window.bench_champ_select[i]].dmg_taken
        //         em.other = window.buffs[window.bench_champ_select[i]].other
        //         em.img_source = window.buffs[window.bench_champ_select[i]].icon
        //         em.championId = window.bench_champ_select[i]
        //         em.name = window.buffs[window.bench_champ_select[i]].name
        //     }
        // }
        benchModel.clear()
        for(var i = 0; i < window.bench_champ_select.length; i++)
        {
            benchModel.append({
                                  dmg_dealt:window.buffs[window.bench_champ_select[i]].dmg_dealt,
                                  dmg_taken:window.buffs[window.bench_champ_select[i]].dmg_taken,
                                  other:window.buffs[window.bench_champ_select[i]].other,
                                  img_source:window.buffs[window.bench_champ_select[i]].icon,
                                  championId:window.bench_champ_select[i],
                                  name:window.buffs[window.bench_champ_select[i]].name
                              })
        }
    }
    
    
    Connections{
        target:riotclient_process
        function onBuffs_changed(){
            window.buffs = JSON.parse(riotclient_process.buffs)
            updateTeamView()
            updateBanchView()
        }
        function onTeam_champ_select_changed(){
            window.team_champ_select = JSON.parse(riotclient_process.team_champ_select)
            updateTeamView()
        }
        function onBench_champ_select_changed(){
            window.bench_champ_select = JSON.parse(riotclient_process.bench_champ_select)
            updateBanchView()
        }
    }
    Component.onCompleted: {
        window.buffs = JSON.parse(riotclient_process.buffs)
        window.team_champ_select = JSON.parse(riotclient_process.team_champ_select)
        window.bench_champ_select = JSON.parse(riotclient_process.bench_champ_select)
        updateTeamView()
        updateBanchView()
    }
}
