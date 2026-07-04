import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal

from configuration import save_cfg


class EditorPreferencesTab(QtWidgets.QWidget):
    pending_changed = pyqtSignal(bool)

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self._controls = {}
        self._pending_values = {}

        self._setup_ui()
        self._populate_from_config()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        info_label = QtWidgets.QLabel(
            "Editor preferences are loaded from [editor] in editor_config.ini."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.restart_notice = QtWidgets.QLabel(
            "Restart required: Changes only take effect after restarting the editor."
        )
        self.restart_notice.setWordWrap(True)
        restart_font = self.restart_notice.font()
        restart_font.setBold(True)
        base_size = restart_font.pointSizeF()
        if base_size <= 0:
            base_size = self.font().pointSizeF()
        if base_size <= 0:
            base_size = 9.0
        restart_font.setPointSizeF(base_size + 1.0)
        self.restart_notice.setFont(restart_font)
        self.restart_notice.setStyleSheet("color: #b06000;")
        self.restart_notice.setVisible(True)
        layout.addWidget(self.restart_notice)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget(self.scroll_area)
        self.form_layout = QtWidgets.QFormLayout(self.scroll_content)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        layout.addStretch()

    def _populate_from_config(self):
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        self._controls = {}
        editor_cfg = self.editor.configuration["editor"]

        for key, value in editor_cfg.items():
            label = QtWidgets.QLabel(key)
            widget = self._build_control_for_value(key, value)
            self._controls[key] = widget
            self.form_layout.addRow(label, widget)

    def _build_control_for_value(self, key, value):
        if key.lower() == "3d_background":
            return self._build_rgb_control(key, value)

        lower_value = value.strip().lower()

        if lower_value in ("true", "false"):
            checkbox = QtWidgets.QCheckBox(self)
            checkbox.setChecked(lower_value == "true")
            checkbox.stateChanged.connect(
                lambda _state, k=key, cb=checkbox: self._queue_value(k, "True" if cb.isChecked() else "False")
            )
            return checkbox

        if self._is_integer(value):
            spinbox = QtWidgets.QSpinBox(self)
            spinbox.setRange(-1000000, 1000000)
            spinbox.setValue(int(value))
            spinbox.valueChanged.connect(
                lambda new_value, k=key: self._queue_value(k, str(new_value))
            )
            return spinbox

        line_edit = QtWidgets.QLineEdit(value, self)
        line_edit.editingFinished.connect(
            lambda k=key, le=line_edit: self._queue_value(k, le.text())
        )
        return line_edit

    def _build_rgb_control(self, key, value):
        container = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        r, g, b = self._parse_rgb(value)
        sliders = []
        spinboxes = []

        channels_widget = QtWidgets.QWidget(container)
        channels_layout = QtWidgets.QGridLayout(channels_widget)
        channels_layout.setContentsMargins(0, 0, 0, 0)
        channels_layout.setHorizontalSpacing(8)
        channels_layout.setVerticalSpacing(4)

        for row, (label_text, channel_value) in enumerate((("R", r), ("G", g), ("B", b))):
            channel_label = QtWidgets.QLabel(label_text, channels_widget)
            channel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            channel_label.setFixedWidth(16)
            channels_layout.addWidget(channel_label, row, 0)

            slider = QtWidgets.QSlider(Qt.Orientation.Horizontal, channels_widget)
            slider.setRange(0, 255)
            slider.setValue(channel_value)
            slider.setSingleStep(1)
            slider.setPageStep(10)
            channels_layout.addWidget(slider, row, 1)

            spinbox = QtWidgets.QSpinBox(channels_widget)
            spinbox.setRange(0, 255)
            spinbox.setValue(channel_value)
            spinbox.setFixedWidth(64)
            channels_layout.addWidget(spinbox, row, 2)

            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)

            sliders.append(slider)
            spinboxes.append(spinbox)

        layout.addWidget(channels_widget, 1)

        preview = QtWidgets.QLabel(container)
        preview.setFixedSize(68, 68)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setToolTip("Preview of 3d_background")
        layout.addWidget(preview)

        def update_rgb_value(_value=None):
            curr_r = spinboxes[0].value()
            curr_g = spinboxes[1].value()
            curr_b = spinboxes[2].value()
            rgb_text = f"{curr_r} {curr_g} {curr_b}"
            self._queue_value(key, rgb_text)
            self._update_rgb_preview(preview, curr_r, curr_g, curr_b)

        for spinbox in spinboxes:
            spinbox.valueChanged.connect(update_rgb_value)

        self._update_rgb_preview(preview, r, g, b)
        return container

    def _update_rgb_preview(self, preview, r, g, b):
        preview.setText("")
        preview.setStyleSheet(
            "border: 1px solid #3a3a3a;"
            "border-radius: 4px;"
            f"background-color: rgb({r}, {g}, {b});"
        )

    @staticmethod
    def _parse_rgb(value):
        raw_values = value.strip().replace(",", " ").split()
        if len(raw_values) >= 3:
            parsed = []
            for raw in raw_values[:3]:
                try:
                    parsed.append(max(0, min(255, int(raw))))
                except ValueError:
                    parsed.append(255)
            return tuple(parsed)

        return 255, 255, 255

    def _queue_value(self, key, new_value):
        editor_cfg = self.editor.configuration["editor"]
        old_value = editor_cfg.get(key, fallback="")
        if old_value == new_value:
            if key in self._pending_values:
                del self._pending_values[key]
        else:
            self._pending_values[key] = new_value

        has_pending_changes = len(self._pending_values) > 0
        self.pending_changed.emit(has_pending_changes)

    def apply_changes(self):
        if not self._pending_values:
            return False

        editor_cfg = self.editor.configuration["editor"]
        for key, new_value in self._pending_values.items():
            editor_cfg[key] = new_value

        save_cfg(self.editor.configuration)
        self._pending_values.clear()
        self.pending_changed.emit(False)
        return True

    @staticmethod
    def _is_integer(value):
        value = value.strip()
        if not value:
            return False

        if value[0] in ("-", "+"):
            return value[1:].isdigit()
        return value.isdigit()


class EditorPreferencesDialog(QtWidgets.QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor Preferences")
        self.resize(560, 520)

        layout = QtWidgets.QVBoxLayout(self)
        self.preferences_tab = EditorPreferencesTab(editor, self)
        layout.addWidget(self.preferences_tab)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Apply | QtWidgets.QDialogButtonBox.StandardButton.Close,
            self
        )
        self.apply_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Apply)
        self.apply_button.setEnabled(False)

        button_box.clicked.connect(self._on_button_clicked)
        self.preferences_tab.pending_changed.connect(self.apply_button.setEnabled)

        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.close)
        layout.addWidget(button_box)

    def _on_button_clicked(self, button):
        role = self.sender().buttonRole(button)
        if role == QtWidgets.QDialogButtonBox.ButtonRole.ApplyRole:
            self.preferences_tab.apply_changes()
