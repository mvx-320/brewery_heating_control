import QtQuick
import QtQuick.Window
import QtQuick.Controls

Window {
	id: mainWindow
	width: 1280
	height: 1024
	minimumWidth: 10
	minimumHeight: 10
	visible:true
	color: "#3d3846"
	title: qsTr("Dorfbrauerei Pfofeld")

	Label {
		id: label
		y: 481
		text: qsTr("Hallo Max!")
		anchors.horizontalCenter: parent.horizontalCenter
		font.pointSize: 39
	}

	Button {
		id: button
		x: 564
		y: 612
		text: qsTr("Button")
		font.pointSize: 25
		onClicked: {
			backend.function(label.text)
		}
	}

	Connections {
		target: backend

		function onSetText(text) {
			label.text = text
		}
	}
}
