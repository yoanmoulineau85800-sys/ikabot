import shutil
from pathlib import Path
from PySide6.QtCore import Qt, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QMainWindow, QMenu, QMessageBox, QPushButton, QScrollArea, QStyle, QSystemTrayIcon,
    QTableView, QTextEdit, QVBoxLayout, QWidget, QHeaderView)
from desktop.catalog import ACTIONS, SECTIONS
from desktop.i18n import tr
from desktop.storage import Store
from desktop.supervisor import Supervisor

DARK = """
QWidget { background:#101722; color:#e6edf7; font-family:'Segoe UI'; font-size:14px; }
QMainWindow { background:#101722; }
QListWidget { background:#162130; border:0; padding:12px; min-width:240px; }
QListWidget::item { padding:13px 10px; border-radius:7px; }
QListWidget::item:selected { background:#24486c; color:#8fd3ff; }
QPushButton { background:#234e72; border:1px solid #37668e; padding:9px 14px; border-radius:6px; }
QPushButton:hover { background:#326b95; } QPushButton:disabled { color:#77899d; background:#1d2937; }
QLineEdit,QComboBox,QTextEdit { background:#1b2939; padding:9px; border:1px solid #35465c; border-radius:5px; }
QTableView { background:#162130; alternate-background-color:#1b2939; border:1px solid #35465c; gridline-color:#28394d; }
QHeaderView::section { background:#22344a; color:#bcd0e6; padding:9px; border:0; }
QLabel#heading { font-size:26px; font-weight:600; } QLabel#muted { color:#9eb2ca; }
QFrame#card { background:#19283a; border:1px solid #2c425d; border-radius:9px; padding:10px; }
QFrame#card QLabel { background:transparent; }
QToolTip { background:#234e72; color:white; }
"""
LIGHT = """
QWidget { background:#f4f7fb; color:#172b42; font-family:'Segoe UI'; font-size:14px; }
QListWidget { background:#e4edf7; border:0; padding:12px; min-width:240px; }
QListWidget::item { padding:13px 10px; border-radius:7px; }
QListWidget::item:selected { background:#c6dff4; }
QPushButton { background:#d5e8f8; border:1px solid #adc9e0; padding:9px 14px; border-radius:6px; }
QLineEdit,QComboBox,QTextEdit { background:white; padding:9px; border:1px solid #adc9e0; border-radius:5px; }
QHeaderView::section { background:#dce8f4; padding:9px; }
QLabel#heading { font-size:26px; font-weight:600; } QLabel#muted { color:#50657a; }
QFrame#card { background:white; border:1px solid #c9d9e8; border-radius:9px; padding:10px; }
QFrame#card QLabel { background:transparent; }
"""


def label(text, style=""):
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.PlainText)
    if style:
        widget.setObjectName(style)
    return widget


def button(text, slot, layout):
    widget = QPushButton(text)
    widget.clicked.connect(slot)
    layout.addWidget(widget)
    return widget


class DataTable(QWidget):
    def __init__(self, headers, rows, store=None):
        super().__init__()
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filtrer toutes les colonnes…")
        layout.addWidget(self.search)
        self.model = QStandardItemModel(0, len(headers), self)
        self.model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = []
            for value in row:
                item = QStandardItem()
                item.setData(value if isinstance(value, (int, float)) else str(value), Qt.DisplayRole)
                item.setEditable(False)
                if value in ("Hostile", "Échec"):
                    item.setForeground(QColor("#d95363"))
                elif value == "En construction":
                    item.setForeground(QColor("#d19b34"))
                items.append(item)
            self.model.appendRow(items)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.search.textChanged.connect(self.proxy.setFilterFixedString)
        self.view = QTableView()
        self.view.setModel(self.proxy)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.horizontalHeader().setSectionsMovable(True)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.horizontalHeader().customContextMenuRequested.connect(self.columns_menu)
        self.view.resizeColumnsToContents()
        self.store = store
        self.settings_key = "table:" + "|".join(headers)
        if store:
            from PySide6.QtCore import QByteArray
            saved = store.setting(self.settings_key)
            if saved:
                self.view.horizontalHeader().restoreState(QByteArray.fromHex(saved.encode()))
            self.view.horizontalHeader().sectionResized.connect(self.save_columns)
            self.view.horizontalHeader().sectionMoved.connect(self.save_columns)
        layout.addWidget(self.view)
        self.setMinimumHeight(220)

    def columns_menu(self, point):
        menu = QMenu(self)
        for column in range(self.model.columnCount()):
            action = menu.addAction(self.model.headerData(column, Qt.Horizontal))
            action.setCheckable(True)
            action.setChecked(not self.view.isColumnHidden(column))
            action.toggled.connect(lambda checked, c=column: self.view.setColumnHidden(c, not checked))
            action.toggled.connect(self.save_columns)
        menu.exec(self.view.horizontalHeader().mapToGlobal(point))

    def save_columns(self, *args):
        if self.store:
            self.store.set_setting(self.settings_key, bytes(self.view.horizontalHeader().saveState().toHex()).decode())


class ProfileDialog(QDialog):
    def __init__(self, parent, profile=None):
        super().__init__(parent)
        self.setWindowTitle("Profil Ikabot")
        self.setMinimumWidth(540)
        self.fields = {}
        layout = QFormLayout(self)
        for key, title, placeholder in [
            ("name", "Nom du profil", "Mon compte"),
            ("email", "Adresse e-mail", "Adresse du compte Gameforge"),
            ("server", "Serveur attendu (facultatif)", "s1-fr.ikariam.gameforge.com"),
            ("proxy", "Proxy strict (facultatif)", "http://127.0.0.1:8080 ou socks5h://hôte:port")]:
            edit = QLineEdit((profile or {}).get(key, ""))
            edit.setPlaceholderText(placeholder)
            self.fields[key] = edit
            layout.addRow(title, edit)
        layout.addRow(label("Sans proxy choisi, la connexion utilise le réseau de l'environnement. "
                            "Avec un proxy, une panne bloque les requêtes du processus. "
                            "Les proxies authentifiés ne sont pas encore pris en charge.", "muted"))
        self.error = label("")
        layout.addRow(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate(self):
        from desktop.network import validate_proxy
        try:
            values = self.values()
            if not values["name"].strip() or "@" not in values["email"]:
                raise ValueError("Renseignez un nom et une adresse e-mail valide.")
            if values["server"] and ("/" in values["server"] or " " in values["server"]):
                raise ValueError("Le serveur doit être un nom d'hôte sans https:// ni chemin.")
            validate_proxy(values["proxy"])
        except ValueError as exc:
            self.error.setText(str(exc))
            return
        self.accept()

    def values(self):
        return {key: edit.text().strip() for key, edit in self.fields.items()}


class EnginePrompt(QDialog):
    def __init__(self, parent, message, answer, cancel):
        super().__init__(parent)
        self.setWindowTitle("Assistant Ikabot — étape du moteur")
        self.resize(650, 500)
        self.constraints = message.get("constraints", {})
        self.answer_callback = answer
        self.cancel_callback = cancel
        self.sent = False
        layout = QVBoxLayout(self)
        layout.addWidget(label("Configuration de l'opération", "heading"))
        layout.addWidget(label("Les étapes proviennent du moteur existant. Certains textes du moteur "
                               "restent en anglais dans cette première version.", "muted"))
        context = QTextEdit()
        context.setReadOnly(True)
        context.setPlainText(tr(message.get("context", "")))
        layout.addWidget(context)
        title = tr(message.get("message", "")).strip() or "Votre choix :"
        if title == ">":
            title = "Votre choix :"
        layout.addWidget(label(title))
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password if message.get("secret") else QLineEdit.Normal)
        if self.constraints.get("default") is not None:
            self.input.setPlaceholderText("Par défaut : " + str(self.constraints["default"]))
        layout.addWidget(self.input)
        self.error = label("")
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Valider")
        buttons.button(QDialogButtonBox.Cancel).setText("Annuler l'opération")
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.input.returnPressed.connect(self.submit)

    def submit(self):
        value = self.input.text()
        constraints = self.constraints
        if value not in constraints.get("additionalValues", []) and not (
            value == "" and (constraints.get("empty") or constraints.get("default") is not None)):
            numeric = constraints.get("digit") or constraints.get("min") is not None or constraints.get("max") is not None
            if numeric:
                if not value.isdecimal():
                    self.error.setText("Saisissez un nombre entier positif.")
                    return
                number = int(value)
                if constraints.get("min") is not None and number < constraints["min"] or constraints.get("max") is not None and number > constraints["max"]:
                    self.error.setText("La valeur est hors des limites indiquées.")
                    return
            compared = int(value) if numeric else value
            if constraints.get("values") is not None and compared not in constraints["values"]:
                self.error.setText("Choisissez l'une des valeurs indiquées par le moteur.")
                return
        self.sent = True
        self.answer_callback(value)
        self.input.clear()
        self.accept()

    def reject(self):
        if not self.sent:
            self.sent = True
            self.cancel_callback()
        super().reject()


class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()
        self.setWindowTitle("Ikabot Desktop")
        self.resize(1320, 860)
        self.setMinimumSize(940, 620)
        self.store = Store(root)
        self.supervisor = Supervisor(Path(root) / "profiles")
        self.supervisor.message.connect(self.on_message)
        self.snapshots, self.states, self.operations, self.prompts = {}, {}, {}, {}
        self.quitting = False
        self.build_ui()
        self.build_tray()
        self.apply_theme(self.store.setting("theme", "sombre"))
        self.load_profiles()
        self.nav.setCurrentRow(0)

    def build_ui(self):
        body = QWidget()
        self.setCentralWidget(body)
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        self.nav = QListWidget()
        self.nav.setMaximumWidth(285)
        self.nav.addItems(SECTIONS)
        icons = [QStyle.SP_DesktopIcon, QStyle.SP_DirHomeIcon, QStyle.SP_DirIcon, QStyle.SP_DriveHDIcon,
                 QStyle.SP_FileDialogNewFolder, QStyle.SP_FileDialogDetailedView, QStyle.SP_ArrowRight,
                 QStyle.SP_ComputerIcon, QStyle.SP_MediaPlay, QStyle.SP_MessageBoxInformation,
                 QStyle.SP_FileDialogContentsView, QStyle.SP_DriveNetIcon, QStyle.SP_FileDialogListView]
        for index, icon in enumerate(icons):
            self.nav.item(index).setIcon(self.style().standardIcon(icon))
        self.nav.currentRowChanged.connect(self.render)
        layout.addWidget(self.nav)
        right = QVBoxLayout()
        right.setContentsMargins(24, 20, 24, 20)
        layout.addLayout(right, 1)
        top = QHBoxLayout()
        top.addWidget(label("IKABOT  /  DESKTOP", "muted"))
        top.addStretch()
        self.profiles = QComboBox()
        self.profiles.setMinimumWidth(200)
        self.profiles.setPlaceholderText("Choisir un profil")
        self.profiles.currentIndexChanged.connect(self.profile_changed)
        top.addWidget(self.profiles)
        self.connect_button = button("Se connecter", self.connect_profile, top)
        self.refresh_button = button("Actualiser", lambda: self.command("refresh"), top)
        self.stop_button = button("Arrêter le profil", self.stop_profile, top)
        right.addLayout(top)
        self.state_label = label("Aucun profil connecté", "muted")
        right.addWidget(self.state_label)
        self.notice = label("Ajoutez un profil pour vous connecter. Aucune donnée de démonstration n'est utilisée.", "muted")
        right.addWidget(self.notice)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        right.addWidget(self.scroll, 1)
        self.progress = QTextEdit()
        self.progress.setReadOnly(True)
        self.progress.setPlaceholderText("Suivi du moteur en temps réel — traduction partielle ; contenu non enregistré")
        self.progress.setMaximumHeight(155)
        self.progress.document().setMaximumBlockCount(200)
        right.addWidget(self.progress)
        self.statusBar().showMessage("Version 0.1 — intégration progressive du moteur Ikabot")

    def build_tray(self):
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Ikabot Desktop")
        menu = QMenu(self)
        menu.addAction("Ouvrir Ikabot Desktop", self.restore)
        menu.addAction("Arrêter toutes les tâches", self.stop_all)
        menu.addSeparator()
        menu.addAction("Quitter complètement", self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.restore() if reason == QSystemTrayIcon.DoubleClick else None)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def restore(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def key(self):
        return self.profiles.currentData()

    def profile(self):
        return next((p for p in self.store.profiles() if p["id"] == self.key()), None)

    def load_profiles(self, selected=None):
        selected = selected or self.key() or self.store.setting("profile")
        self.profiles.blockSignals(True)
        self.profiles.clear()
        for profile in self.store.profiles():
            self.profiles.addItem(profile["name"], profile["id"])
        index = self.profiles.findData(selected)
        if index >= 0:
            self.profiles.setCurrentIndex(index)
        self.profiles.blockSignals(False)
        self.profile_changed()

    def profile_changed(self, *args):
        self.store.set_setting("profile", self.key())
        self.update_status()
        if hasattr(self, "progress"):
            self.progress.clear()
        self.render()

    def update_status(self):
        key = self.key()
        worker = self.supervisor.workers.get(key)
        self.state_label.setText(self.states.get(key, "Déconnecté") + "  •  " +
                                 (self.profile() or {}).get("server", "Serveur choisi à la connexion"))
        self.connect_button.setEnabled(bool(key) and not worker)
        self.refresh_button.setEnabled(bool(worker and worker["idle"]))
        self.stop_button.setEnabled(bool(worker))
        self.state_label.setStyleSheet("color:" + ("#50b9a0" if worker and worker["idle"] else "#d19b34" if worker else "#97a9bd"))

    def table(self, headers, rows):
        return DataTable(headers, rows, self.store)

    def render(self, *args):
        if not hasattr(self, "scroll"):
            return
        page = QWidget()
        self.page_layout = QVBoxLayout(page)
        section = SECTIONS[max(0, self.nav.currentRow())]
        self.page_layout.addWidget(label(section, "heading"))
        self.page_layout.addWidget(label("Moteur Ikabot conservé • profils isolés • données réelles uniquement", "muted"))
        if section == SECTIONS[1]:
            self.render_profiles()
        elif section == SECTIONS[10]:
            self.page_layout.addWidget(label("Seuls les états et erreurs structurés sont conservés. Les sorties brutes et les réponses aux formulaires ne sont pas enregistrées.", "muted"))
            self.page_layout.addWidget(self.table(["Date UTC", "Profil", "Événement"], self.store.events()))
        elif section == SECTIONS[11]:
            self.render_network()
        elif section == SECTIONS[12]:
            self.render_settings()
        elif section == SECTIONS[9]:
            row = QHBoxLayout()
            for channel, name in (("telegram", "Telegram"), ("discord", "Discord")):
                configure = button("Configurer " + name, lambda checked=False, c=channel: self.configure_notification(c), row)
                configure.setEnabled(bool(self.supervisor.workers.get(self.key(), {}).get("idle")))
            self.page_layout.addLayout(row)
            self.page_layout.addWidget(label("L'enregistrement n'envoie aucun message. Utilisez ensuite le test du canal souhaité. Les jetons sont protégés avec la session Windows ; sous Linux, ils restent en mémoire.", "muted"))
        if section in (SECTIONS[0], SECTIONS[2], SECTIONS[3], SECTIONS[4]):
            self.render_data(section)
        if section in (SECTIONS[0], SECTIONS[6], SECTIONS[7]):
            self.render_movements()
        if section in (SECTIONS[0], SECTIONS[8]):
            rows = [[self.profile_name(key), self.states.get(key, ""), self.operations.get(key, "Connexion / attente")]
                    for key in self.supervisor.workers]
            self.page_layout.addWidget(label("Sessions et opérations"))
            self.page_layout.addWidget(self.table(["Profil", "État", "Opération"], rows))
        for action in ACTIONS.values():
            if action.section != section:
                continue
            card = QFrame()
            card.setObjectName("card")
            row = QHBoxLayout(card)
            row.addWidget(label(action.label), 1)
            if action.reason:
                row.addWidget(label(action.reason, "muted"), 2)
            else:
                launch = button("Configurer…", lambda checked=False, a=action: self.launch(a), row)
                launch.setEnabled(bool(self.supervisor.workers.get(self.key(), {}).get("idle")))
            self.page_layout.addWidget(card)
        self.page_layout.addStretch()
        old = self.scroll.takeWidget()
        self.scroll.setWidget(page)
        if old:
            old.deleteLater()

    def render_profiles(self):
        row = QHBoxLayout()
        button("Ajouter un profil", lambda: self.edit_profile(False), row)
        button("Modifier le profil sélectionné", lambda: self.edit_profile(True), row)
        button("Supprimer le profil sélectionné", self.delete_profile, row)
        self.page_layout.addLayout(row)
        self.page_layout.addWidget(self.table(["Nom", "E-mail", "Serveur attendu", "Connexion"],
            [[p["name"], p["email"], p["server"] or "Au choix à la connexion", p["proxy"] or "Réseau de l'environnement"] for p in self.store.profiles()]))
        self.page_layout.addWidget(label("Le mot de passe est demandé dans un formulaire masqué. Sous Windows, les sessions sont chiffrées avec DPAPI et liées à l'utilisateur Windows. Sous Linux, elles restent uniquement en mémoire. Aucun mot de passe n'est conservé par Desktop.", "muted"))

    def render_data(self, section):
        data = self.snapshots.get(self.key())
        if not data:
            self.page_layout.addWidget(label("Aucune donnée chargée. Connectez un profil puis cliquez sur Actualiser.", "muted"))
            return
        self.page_layout.addWidget(label("Dernière lecture : " + data["read_at"] + " — " + data.get("server", ""), "muted"))
        cities = data["cities"]
        if section == SECTIONS[0]:
            card = QFrame()
            card.setObjectName("card")
            row = QHBoxLayout(card)
            row.addWidget(label(str(len(cities)) + " villes"))
            row.addWidget(label(str(sum(1 for c in cities for b in c["buildings"] if b["busy"])) + " constructions en cours"))
            row.addWidget(label("Profil : " + self.profiles.currentText()))
            self.page_layout.addWidget(card)
        if section in (SECTIONS[0], SECTIONS[2], SECTIONS[3]):
            self.page_layout.addWidget(self.table(["Ville", "Coordonnées", "Bois", "Vin", "Marbre", "Cristal", "Soufre"],
                [[c["name"], f'{c["x"]}:{c["y"]}', *c["resources"]] for c in cities]))
        if section in (SECTIONS[0], SECTIONS[4]):
            self.page_layout.addWidget(self.table(["Ville", "Bâtiment", "Niveau", "État"],
                [[c["name"], tr(b["name"]), b["level"], "En construction" if b["busy"] else "Disponible"]
                 for c in cities for b in c["buildings"]]))

    def render_movements(self):
        data = self.snapshots.get(self.key(), {})
        if data.get("movements") is None:
            if data.get("movements_error"):
                self.page_layout.addWidget(label("Lecture des mouvements échouée : " + data["movements_error"] + ". Les données des villes restent disponibles.", "muted"))
            return
        from datetime import datetime
        rows = [[m["origin"], m["target"], m["mission"], "Retour" if m["returning"] else "Aller",
                 datetime.fromtimestamp(m["arrival"]).astimezone().strftime("%d/%m %H:%M:%S"),
                 "Hostile" if m["hostile"] else "Autre mouvement"] for m in data["movements"]]
        self.page_layout.addWidget(label("Transports et mouvements militaires — dernière lecture du serveur"))
        self.page_layout.addWidget(self.table(["Départ", "Destination", "Mission", "Sens", "Arrivée locale", "État"], rows))
        if not rows:
            self.page_layout.addWidget(label("Aucun mouvement renvoyé par le serveur.", "muted"))

    def configure_notification(self, channel):
        from desktop.notifications import notification_data
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurer " + channel.capitalize())
        dialog.setMinimumWidth(550)
        layout = QFormLayout(dialog)
        fields = {}
        for key, title in ([("token", "Jeton du bot"), ("chat", "Identifiant de conversation")]
                           if channel == "telegram" else [("webhook", "URL du webhook")]):
            edit = QLineEdit()
            edit.setEchoMode(QLineEdit.Password)
            fields[key] = edit
            layout.addRow(title, edit)
        error = label("")
        layout.addRow(error)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Enregistrer sans envoyer")
        buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        def submit():
            values = {key: edit.text() for key, edit in fields.items()}
            try:
                notification_data(channel, values)
            except ValueError as exc:
                error.setText(str(exc))
                return
            self.command("notification", channel=channel, values=values)
            for edit in fields.values():
                edit.clear()
            dialog.accept()
        buttons.accepted.connect(submit)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        dialog.exec()

    def render_network(self):
        profile = self.profile()
        self.page_layout.addWidget(label("Connexion : " + ((profile or {}).get("proxy") or "Réseau de l'environnement")))
        self.page_layout.addWidget(label("Le proxy du profil est imposé avant l'authentification et pour les requêtes du moteur. Une panne n'active pas de connexion directe. Le contrôle s'applique au processus Python, pas à tout Windows. Les modules personnalisés sont exclus. La validation sur un véritable poste Windows reste nécessaire.", "muted"))
        row = QHBoxLayout()
        ip = button("Vérifier l'adresse IP publique", lambda: self.command("ip"), row)
        ip.setEnabled(bool(self.supervisor.workers.get(self.key(), {}).get("idle")))
        self.page_layout.addLayout(row)

    def render_settings(self):
        row = QHBoxLayout()
        button("Thème sombre", lambda: self.apply_theme("sombre"), row)
        button("Thème clair", lambda: self.apply_theme("clair"), row)
        self.page_layout.addLayout(row)
        self.page_layout.addWidget(label("Données locales : " + str(self.store.root), "muted"))
        self.page_layout.addWidget(label("Fermer la fenêtre la masque dans la zone de notification si celle-ci est disponible. Quitter complètement arrête les opérations. Les tâches interrompues ne sont jamais relancées automatiquement, afin d'éviter les doublons.", "muted"))
        self.page_layout.addWidget(label("État de cette version : interface native en français ; traduction des assistants du moteur partielle ; une opération à la fois par profil. Les modules exclus et les limites sont détaillés dans docs/AUDIT.md et docs/GUIDE_FR.md.", "muted"))

    def apply_theme(self, theme):
        QApplication.instance().setStyleSheet(LIGHT if theme == "clair" else DARK)
        self.store.set_setting("theme", theme)

    def profile_name(self, key):
        return next((p["name"] for p in self.store.profiles() if p["id"] == key), key)

    def edit_profile(self, edit):
        profile = self.profile() if edit else None
        if edit and (not profile or profile["id"] in self.supervisor.workers):
            self.notice.setText("Sélectionnez un profil déconnecté pour le modifier.")
            return
        dialog = ProfileDialog(self, profile)
        if dialog.exec() == QDialog.Accepted:
            key = self.store.save_profile(**dialog.values(), profile_id=profile["id"] if profile else None)
            self.load_profiles(key)

    def delete_profile(self):
        profile = self.profile()
        if not profile:
            return
        if profile["id"] in self.supervisor.workers:
            self.notice.setText("Arrêtez ce profil avant de le supprimer.")
            return
        if QMessageBox.question(self, "Supprimer le profil", "Supprimer ce profil et ses sessions locales ?") == QMessageBox.Yes:
            key = profile["id"]
            shutil.rmtree(self.store.root / "profiles" / key, ignore_errors=False) if (self.store.root / "profiles" / key).exists() else None
            self.store.delete_profile(key)
            self.snapshots.pop(key, None)
            self.load_profiles()

    def connect_profile(self):
        profile = self.profile()
        if not profile:
            self.nav.setCurrentRow(1)
            return
        try:
            self.supervisor.start(profile)
            self.states[profile["id"]] = "Connexion en cours"
            self.record(profile["id"], "Connexion demandée")
        except (ValueError, OSError) as exc:
            self.notice.setText(str(exc))
        self.update_status()
        self.render()

    def command(self, name, **fields):
        try:
            self.supervisor.send(self.key(), name, **fields)
            self.operations[self.key()] = "Actualisation" if name == "refresh" else "Vérification réseau" if name == "ip" else self.operations.get(self.key(), "Opération")
            self.update_status()
            self.render()
        except (ValueError, OSError) as exc:
            self.notice.setText(str(exc))

    def launch(self, action):
        self.operations[self.key()] = action.label
        self.record(self.key(), "Lancement : " + action.label)
        self.command("action", action=action.function)

    def stop_profile(self):
        key = self.key()
        if key:
            self.supervisor.stop(key)

    def stop_all(self):
        for key in list(self.supervisor.workers):
            self.supervisor.stop(key)

    def record(self, key, message):
        self.store.event(self.profile_name(key), message)
        self.notice.setText(message)

    def on_message(self, key, message):
        kind = message["type"]
        if kind == "state":
            self.states[key] = message["state"]
            self.record(key, message["state"])
        elif kind == "prompt":
            dialog = EnginePrompt(self, message,
                lambda value, k=key: self.answer(k, value),
                lambda k=key: self.cancel(k))
            dialog.setWindowTitle(self.profile_name(key) + " — assistant Ikabot")
            self.prompts[key] = dialog
            dialog.finished.connect(lambda result, k=key: self.prompts.pop(k, None))
            dialog.show()
            if self.tray.isVisible() and not self.isVisible():
                self.tray.showMessage("Ikabot Desktop", "Une opération attend votre réponse.")
        elif kind == "snapshot":
            from datetime import datetime
            data = message["data"]
            data["read_at"] = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S %Z")
            self.snapshots[key] = data
            self.record(key, "Données des villes actualisées")
        elif kind == "ip":
            self.record(key, "Adresse IP publique : " + message["address"])
        elif kind == "configured":
            self.record(key, "Configuration " + message["channel"].capitalize() + " enregistrée ; aucun message envoyé")
        elif kind == "error":
            self.record(key, "Échec de l'opération — " + message["code"] + ". Vérifiez la connexion et les paramètres ; aucune réussite n'est supposée.")
            self.operations[key] = "Échec : " + message["code"]
            if self.tray.isVisible():
                self.tray.showMessage("Ikabot Desktop", "Une opération a échoué. Consultez l'historique.")
        elif kind == "engine_log":
            self.record(key, "Signalement du moteur : " + message["level"] + " — " + message["component"] + ". Le contenu réseau brut est masqué pour protéger les secrets.")
        elif kind == "progress":
            if key == self.key():
                self.progress.setPlainText(tr(message["text"]))
        elif kind == "complete":
            self.record(key, "Le moteur a rendu la main ; vérifiez le résultat de l'action." if message.get("operation") == "action" else "Opération terminée")
            self.operations[key] = "Aucune opération"
        elif kind == "idle":
            self.states[key] = "Connecté — disponible"
        elif kind == "stopped":
            self.states[key] = "Déconnecté"
            self.operations.pop(key, None)
            self.snapshots.pop(key, None)
            dialog = self.prompts.pop(key, None)
            if dialog:
                dialog.sent = True
                dialog.close()
            self.record(key, "Session arrêtée ; aucune relance automatique. Une requête déjà envoyée peut avoir été exécutée côté jeu.")
        elif kind == "output":
            dialog = QDialog(self)
            dialog.setWindowTitle("Résultat du moteur — " + self.profile_name(key))
            dialog.resize(750, 520)
            layout = QVBoxLayout(dialog)
            layout.addWidget(label("Résultat réel du moteur ; traduction partielle. Ce texte n'est pas conservé dans l'historique.", "muted"))
            text = QTextEdit()
            text.setReadOnly(True)
            text.setPlainText(tr(message["text"]))
            layout.addWidget(text)
            close = QDialogButtonBox(QDialogButtonBox.Close)
            close.button(QDialogButtonBox.Close).setText("Fermer")
            close.rejected.connect(dialog.reject)
            layout.addWidget(close)
            dialog.setAttribute(Qt.WA_DeleteOnClose)
            dialog.show()
        self.update_status()
        if kind not in ("prompt", "progress"):
            self.render()

    def answer(self, key, value):
        try:
            self.supervisor.send(key, "answer", value=value)
        except (ValueError, OSError):
            self.notice.setText("La session n'attend plus de réponse.")

    def cancel(self, key):
        try:
            self.supervisor.send(key, "cancel")
        except (ValueError, OSError):
            pass

    def closeEvent(self, event):
        if not self.quitting and self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self.supervisor.shutdown()
            self.tray.hide()
            event.accept()

    def quit_app(self):
        self.quitting = True
        self.supervisor.shutdown()
        self.tray.hide()
        QApplication.instance().quit()
