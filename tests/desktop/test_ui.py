from PySide6.QtCore import Qt
from desktop.ui import MainWindow, DataTable, EnginePrompt, ProfileDialog


def test_navigation_empty_dashboard_and_theme_persistence(qtbot, tmp_path):
    window = MainWindow(tmp_path)
    qtbot.addWidget(window)
    window.show()
    assert window.nav.count() == 13
    assert not window.snapshots
    assert not window.refresh_button.isEnabled()
    for index in range(13):
        window.nav.setCurrentRow(index)
        assert window.scroll.widget() is not None
    window.apply_theme("clair")
    assert window.store.setting("theme") == "clair"
    window.supervisor.shutdown()


def test_data_table_numeric_sort_and_filter(qtbot):
    table = DataTable(["Ville", "Bois"], [["Rome", 100], ["Athènes", 9]])
    qtbot.addWidget(table)
    table.view.sortByColumn(1, Qt.AscendingOrder)
    assert table.proxy.index(0, 1).data() == 9
    table.search.setText("Rome")
    assert table.proxy.rowCount() == 1
    assert table.proxy.index(0, 0).data() == "Rome"


def test_graphical_form_rejects_invalid_range_and_does_not_echo_password(qtbot):
    answers = []
    prompt = EnginePrompt(None, {"message": "Nombre", "secret": True,
        "constraints": {"digit": True, "min": 2, "max": 10}}, answers.append, lambda: None)
    qtbot.addWidget(prompt)
    prompt.input.setText("1")
    prompt.submit()
    assert answers == []
    prompt.input.setText("5")
    prompt.submit()
    assert answers == ["5"]
    assert prompt.input.text() == ""


def test_snapshot_changes_rendered_dashboard(qtbot, tmp_path):
    window = MainWindow(tmp_path)
    qtbot.addWidget(window)
    key = window.store.save_profile("Compte", "test@example.org", "")
    window.load_profiles(key)
    window.on_message(key, {"type": "snapshot", "data": {"server": "https://example.org", "cities": [
        {"name": "Ville réelle injectée par le test", "id": "1", "x": 2, "y": 3, "resources": [123, 0, 0, 0, 0],
         "buildings": [{"name": "townHall", "level": 8, "busy": True}]}]}})
    tables = window.scroll.widget().findChildren(DataTable)
    assert tables[0].model.item(0, 0).text() == "Ville réelle injectée par le test"
    assert tables[0].model.item(0, 2).data(Qt.DisplayRole) == 123
    assert tables[1].model.item(0, 1).text() == "Hôtel de ville"
    window.supervisor.shutdown()


def test_table_column_preferences_survive_recreation(qtbot, tmp_path):
    from desktop.storage import Store
    store = Store(tmp_path)
    table = DataTable(["Ville", "Bois"], [["Rome", 1]], store)
    qtbot.addWidget(table)
    table.view.setColumnHidden(1, True)
    table.save_columns()
    restored = DataTable(["Ville", "Bois"], [["Rome", 1]], store)
    qtbot.addWidget(restored)
    assert restored.view.isColumnHidden(1)
