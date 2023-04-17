import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: window

    ListModel{
        id:uiConfig
        property int current:setting.ui_size
        ListElement{
            type: "big"
            width0: 370
            lineHeight:30
            fontSize1:20
            fontSize2:14
            iconsize:50
            width1: 80
            width2: 80
            width3: 150
            width4: 60
        }
        ListElement{
            type: "middle"
            width0: 290
            lineHeight:25
            fontSize1:18
            fontSize2:11
            iconsize:40
            width1: 60
            width2: 70
            width3: 110
            width4: 50
        }
        ListElement{
            type: "small"
            width0: 235
            lineHeight:20
            fontSize1:15
            fontSize2:8
            iconsize:30
            width1: 45
            width2: 60
            width3: 90
            width4: 40
        }
    }

    property var uiWords:{
        "champion":"英雄",
        "damage_dealt":"伤害",
        "damage_taken":"承伤",
        "other":"其他",
        "send":"发送",
        "otherchampion":"可替换英雄"
    }
    property string sendText:"发送"
    width: uiConfig.get(uiConfig.current).width0
    height: {
        var lineHeight = uiConfig.get(uiConfig.current).lineHeight
        return lineHeight*13+6+(lineHeight*2+1)*benchModel.count
    }

    
    
    flags: Qt.FramelessWindowHint
    property var buffs:JSON.parse(riotclient_process.buffs)
    property var team_champ_select:JSON.parse(riotclient_process.team_champ_select)
    property var bench_champ_select:JSON.parse(riotclient_process.bench_champ_select)
    property bool is_aram_selecting:riotclient_process.is_aram_selecting
    property bool closed : false
    visible: is_aram_selecting && !closed
    // visible: true

    onIs_aram_selectingChanged: {
        if (is_aram_selecting)
        {
           closed = false
           updateBanchView()
           updateTeamView()
           var xy = riotclient_process.windowsPosition

            x = xy.x-window.width
            if(x<0)
                x = 0
            window.x = x
            window.y = xy.y
        }
    }
    
    Rectangle {
        id:bgRect
        anchors.fill:parent
        color:"black"
        Item {
            id:topBar
            width:parent.width
            height:uiConfig.get(uiConfig.current).lineHeight
            anchors.top:parent.top
            anchors.left:parent.left

            //用于拖动窗口
            Item { 
                anchors.fill: parent
                width: parent.width-parent.height
                height: parent.height
                DragHandler {
                    grabPermissions: TapHandler.CanTakeOverFromAnything
                    onActiveChanged: if (active) { window.startSystemMove(); }
                }
            }

            //关闭按钮
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
                        font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
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
                    property int linewidth: 1
                    width:buffViewer.width
                    height:uiConfig.get(uiConfig.current).lineHeight*2+linewidth
                    
                    Item {
                        id:buffIcon
                        width:uiConfig.get(uiConfig.current).width1
                        height:parent.height-parent.linewidth
                        Image {
                            width:uiConfig.get(uiConfig.current).iconsize
                            height:width
                            anchors.centerIn:parent
                            source:img_source
                        }
                    }
                    Text {
                        id:dmg_dealt_tex
                        width:uiConfig.get(uiConfig.current).width2
                        height: uiConfig.get(uiConfig.current).lineHeight
                        anchors.left:buffIcon.right
                        anchors.top:parent.top
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
                        color: {if(dmg_dealt == "100%"){return "white"}else {if(dmg_dealt[0] == "-"){return "red"}else {return "green"}}}
                        text:dmg_dealt
                    }
                    Text {
                        id:dmg_taken_tex
                        width:uiConfig.get(uiConfig.current).width2
                        height: uiConfig.get(uiConfig.current).lineHeight
                        anchors.left:buffIcon.right
                        anchors.top:dmg_dealt_tex.bottom
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
                        color: {if(dmg_taken == "100%"){return "white"}else {if(dmg_taken[0] == "-"){return "green"}else {return "red"}}}
                        text:dmg_taken
                    }
                    Text {
                        id:other_tex
                        width:uiConfig.get(uiConfig.current).width3
                        height: parent.height-parent.linewidth
                        anchors.left:dmg_dealt_tex.right
                        anchors.top:parent.top
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: {
                            var count = (other.match(/\n/g) || []).length + 1;
                            if (count >2)
                            {
                                return parseInt(uiConfig.get(uiConfig.current).fontSize1*0.6)
                            }
                            return uiConfig.get(uiConfig.current).fontSize1
                        }
                        color:"white"
                        text:other
                        wrapMode: Text.WordWrap
                    }
                    MouseArea {
                        id:sendBtn
                        width:uiConfig.get(uiConfig.current).width4
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
                            text:window.sendText
                            color:"white"
                            font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
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
                height:uiConfig.get(uiConfig.current).lineHeight
                Text {
                    id:buffHeader1
                    width:uiConfig.get(uiConfig.current).width1
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:parent.left
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
                    color:"white"
                    text:uiWords.champion
                }
                Text {
                    id:buffHeader2
                    width:uiConfig.get(uiConfig.current).width2
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:buffHeader1.right
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
                    color:"white"
                    text:uiWords.damage_dealt+"/"+uiWords.damage_taken
                }

                Text {
                    id:buffHeader3
                    width:parent.width - buffHeader2.width - buffHeader1.width
                    height:parent.height
                    anchors.top:parent.top
                    anchors.left:buffHeader2.right
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    color:"white"
                    text:uiWords.other
                    font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
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
                height:(uiConfig.get(uiConfig.current).lineHeight*2+1)*5
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
                height:uiConfig.get(uiConfig.current).lineHeight
                anchors.top:teamViewer.bottom
                verticalAlignment: Text.AlignVCenter
                font.pixelSize:uiConfig.get(uiConfig.current).fontSize1
                color:"white"
                text:uiWords.otherchampion
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
                height: (uiConfig.get(uiConfig.current).lineHeight*2+1)*benchModel.count
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
        var view_length = benchModel.count
        if(window.bench_champ_select.length==0){
            benchModel.clear()
            return
        }
        if(window.bench_champ_select.length>view_length){
            for(var i = view_length; i < window.bench_champ_select.length; i++)
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
        else if(window.bench_champ_select.length==view_length){
            for(var i = 0; i < view_length; i++)
            {
                var em = benchModel.get(i)
                em.dmg_dealt = window.buffs[window.bench_champ_select[i]].dmg_dealt
                em.dmg_taken = window.buffs[window.bench_champ_select[i]].dmg_taken
                em.other = window.buffs[window.bench_champ_select[i]].other
                em.img_source = window.buffs[window.bench_champ_select[i]].icon
                em.championId = window.bench_champ_select[i]
                em.name = window.buffs[window.bench_champ_select[i]].name
            }
        }
        // benchModel.clear()
        // for(var i = 0; i < window.bench_champ_select.length; i++)
        // {
        //     benchModel.append({
        //                           dmg_dealt:window.buffs[window.bench_champ_select[i]].dmg_dealt,
        //                           dmg_taken:window.buffs[window.bench_champ_select[i]].dmg_taken,
        //                           other:window.buffs[window.bench_champ_select[i]].other,
        //                           img_source:window.buffs[window.bench_champ_select[i]].icon,
        //                           championId:window.bench_champ_select[i],
        //                           name:window.buffs[window.bench_champ_select[i]].name
        //                       })
        // }
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
    function setUiWords(){
        var _uiWords = JSON.parse(setting.ui_words)
        for(var k in window.uiWords){
            window.uiWords[k] = _uiWords[k]
        }
        sendText = uiWords.send
        buffHeader1.text = uiWords.champion
        buffHeader2.text = uiWords.damage_dealt+"/"+uiWords.damage_taken
        buffHeader3.text = uiWords.other
        benchHeader.text = uiWords.otherchampion
    }
    Connections{
        target:setting 
        function onLanguage_changed(){
            setUiWords()
        }
    }

    Component.onCompleted: {
        window.buffs = JSON.parse(riotclient_process.buffs)
        window.team_champ_select = JSON.parse(riotclient_process.team_champ_select)
        window.bench_champ_select = JSON.parse(riotclient_process.bench_champ_select)
        updateTeamView()
        updateBanchView()
        setUiWords()
    }
}
