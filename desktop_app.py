"""Point d'entrée compatible avec multiprocessing et PyInstaller Windows."""
import multiprocessing
import sys


def main():
    from pathlib import Path
    from PySide6.QtCore import QLockFile, QStandardPaths, QTranslator, QLibraryInfo, QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox
    from desktop.ui import MainWindow
    app = QApplication(sys.argv)
    app.setApplicationName("Ikabot Desktop")
    app.setOrganizationName("IkabotDesktop")
    app.setStyle("Fusion")
    translator = QTranslator(app)
    translator.load("qtbase_fr", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    temporary = None
    if "--smoke-test" in sys.argv or "--worker-smoke-test" in sys.argv:
        import tempfile
        temporary = tempfile.TemporaryDirectory(prefix="ikabot-desktop-smoke-")
        root = Path(temporary.name)
    else:
        root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    root.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(root / "desktop.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        QMessageBox.information(None, "Ikabot Desktop", "L'application est déjà ouverte pour cet utilisateur.")
        return 1
    window = MainWindow(root)
    app.aboutToQuit.connect(window.supervisor.shutdown)
    window.show()
    if "--worker-smoke-test" in sys.argv:
        observed = {"prompt": False}
        def observe(key, message):
            if message["type"] == "prompt":
                observed["prompt"] = message.get("secret", False)
                window.supervisor.send(key, "cancel")
            if message["type"] == "stopped":
                app.exit(0 if observed["prompt"] else 2)
        window.supervisor.message.connect(observe)
        window.supervisor.start({"id": "smoke", "name": "Test de démarrage",
                                 "email": "smoke@example.invalid", "server": "", "proxy": ""})
        QTimer.singleShot(20000, lambda: app.exit(3))
    elif temporary:
        for index in range(window.nav.count()):
            window.nav.setCurrentRow(index)
        QTimer.singleShot(300, window.quit_app)
    return app.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
