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
		x: 510
		y: 481
		text: qsTr("Hallo Max!")
		font.pointSize: 39
	}
}
