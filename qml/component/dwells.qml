import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: dwellItem
    visible: true
    width: 400
    height: 500


    ScrollView {
        id: scrollView
        anchors.fill: parent
        anchors.rightMargin: 0

        Column {
            id: column
            x: 0
            y: 0
            width: scrollView.width
            height: 1000
            spacing: 5
            ListModel {
                id: testModel

                ListElement { name: "Boiler"; temp: "72°C"; time: "10:21"; alarm: false }
                ListElement { name: "Cooler"; temp: "12°C"; time: "10:22"; alarm: false }
                ListElement { name: "Pump"; temp: "68°C"; time: "10:23"; alarm: true }
                ListElement { name: "Valve"; temp: "65°C"; time: "10:25"; alarm: false }
                ListElement { name: "Valve"; temp: "65°C"; time: "10:25"; alarm: false }
                ListElement { name: "Valve"; temp: "65°C"; time: "10:25"; alarm: false }
                ListElement { name: "Valve"; temp: "65°C"; time: "10:25"; alarm: false }
                ListElement { name: "Valve"; temp: "65°C"; time: "10:25"; alarm: false }
            }
            // Repeater {
            //     width: scrollView.width
            //     height: 100
            // model:testModel

            //delegate:
            Rectangle {
                width: scrollView.width
                height: 100
                color: "#6655ff"
                radius: 10

                Row {
                    id: row
                    anchors.fill: parent


                    Column {
                        id: column1
                        anchors.left: parent.left
                        anchors.right: button.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.rightMargin: 10

                        Label {
                            id: label
                            text: qsTr("So und So Rast")
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.verticalCenter
                            anchors.bottomMargin: 0
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pointSize: 18
                        }

                        RowLayout {
                            id: row1
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.verticalCenter
                            anchors.bottom: parent.bottom
                            anchors.topMargin: 0
                            layer.enabled: false
                            spacing: 3


                            Label {
                                id: label1
                                width: 39
                                text: qsTr("Label")
                            }

                            TextField {
                                id: textField
                                width: 74
                                placeholderText: qsTr("Text Field")
                            }

                            Label {
                                id: label2
                                width: 37
                                text: qsTr("Label")
                            }

                            TextField {
                                id: textField1
                                width: 103
                                placeholderText: qsTr("Text Field")
                            }



                        }
                    }
                    Button {
                        id: button
                        height: 64
                        text: qsTr("Button")
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                        icon.height: 30
                        icon.width: 30
                        icon.color: "#00000000"
                        icon.source: "../assets/alarm0.png"
                        display: AbstractButton.IconOnly
                    }
                }

                // }
            }
        }

        Connections {
            target: backend
            function onColumnsAboutToBeInserted() { console.log("clicked") }
        }

    }
}
