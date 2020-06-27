import os
import sys
import shutil
import subprocess
import socket
from pathlib import Path
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide2.QtGui import QIcon

script_path = Path(os.path.abspath(os.path.dirname(__file__)))


# TrayWidgetクラスは、QSystemTrayIconを継承して作成
class TrayWidget(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self, parent)

        # タスクトレイアイコン クリックメニュー登録
        menu = QMenu(parent)
        qt_action = menu.addAction("Status")
        qt_action.triggered.connect(self.Message)
        menu.addSeparator()
        quit_action = menu.addAction("&Quit")
        quit_action.triggered.connect(self.Quit)

        # タスクトレイアイコン クリックメニュー設定
        self.setContextMenu(menu)

        # 初期アイコン設定
        self.setIcon(QIcon(str(Path(script_path / 'icon.jpg').resolve())))

        # run competitive companion server
        if not shutil.which('node'):
            QMessageBox.critical(None, "error", "node not found", QMessageBox.Ok)
            sys.exit()
        # elif socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('127.0.0.1', 8080)) != 0:
        #     QMessageBox.critical(None, "error", "port:8080 is alreday in use", QMessageBox.Ok)
        #     sys.exit()
        else:
            self.proc = subprocess.Popen(['node', str(Path(script_path / 'index.js').resolve())])

    # "Qtちゃん"メニューでメッセージ表示
    def Message(self):
        self.showMessage("pcm-cc", "waiting for request on port:8080", QIcon('QtChan.png'), 5000 );

    # "Quit"にて、タスクトレイアイコンアプリを閉じる
    def Quit(self):
        self.proc.kill()
        QApplication.quit()


def main():
    app = QApplication([])
    tray = TrayWidget()
    # タスクトレイに表示
    tray.show()

    ret = app.exec_()
    sys.exit(ret)


if __name__ == '__main__':
    main()
