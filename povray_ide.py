### FILE CREATED ON 05/29/2026 | 13:56:00 ###
### By Nolin Brashears ###
### Written in VIM ###
#
# The purpose of this program is to create a more efficient workspace for 
# POV-Ray creations by allowing the user to view their rendered image in 
# realtime, rather than having to save the file and run [povray file.pov] each
# time they'd like to view it. This may be the first of many attempts to 
# modernize POV-Ray's systems into a more useful format while still maintaining
# it's Y2K charm and character.
#
# I'm sure at some point if I want to dive deeper into GUI development it 
# probably would help to just learn a C language, but I don't wanna xP

import sys
import subprocess
import os

# I'll be using Qt to develop the GUI. In order to use Qt in Python, I will be
# using PySide6.

from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QHBoxLayout,
        QVBoxLayout,
        QPlainTextEdit,
        QLabel,
        QPushButton,
        QTextEdit
)

from PySide6.QtGui import (
        QPixmap,
        QFont,
        QTextOption,
        QTextCursor,
        QColor,
        QTextCharFormat,
        QSyntaxHighlighter
        )

from PySide6.QtCore import Qt, QRegularExpression

scene_file = "scene.pov" # Can change to user input later
render_file = "output.png"

class POVSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        ###
        # KEYWORDS
        ###

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#344b1b"))

        keywords = [
                "camera",
                "light_source",
                "sphere",
                "box",
                "cone",
                "cylinder",
                "plane",
                "texture",
                "pigment",
                "finish",
                "normal",
                "translate",
                "rotate",
                "scale",
                "union",
                "difference",
                "intersection",
                "sky_sphere",
                "gradient",
                "color",
                "rgb",
                "ambient",
                "bozo",
                "color_map",
                "diffuse",
                "radiosity",
                "pretrace_start",
                "pretrace_end",
                "count",
                "nearest_count",
                "error_bound",
                "recursion_limit",
                "background",
                "roughness",
                "emission",
                "reflection",
                "specular",
                "roughness"
                ]

        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, keyword_format))

        ###
        # COMMENTS
        ###

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#46423b"))

        self.rules.append((QRegularExpression(r"//[^\n]*"), comment_format))

        ###
        # NUMBERS
        ### 

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#aa261f"))

        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), number_format))

        ###
        # VECTORS
        ###

        vector_format = QTextCharFormat()
        vector_format.setForeground(QColor("#FF0000"))

        self.rules.append((QRegularExpression(r"<[^]+>"), vector_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            matches = pattern.globalMatch(text)

            while matches.hasNext():
                match = matches.next()

                self.setFormat(
                        match.capturedStart(),
                        match.capturedLength(),
                        fmt
                )

class POVRayIDE(QWidget):
    def __init__(self):
        super().__init__() # IDK what this does (yet)

        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                color: white;
            }
        """)

        self.setWindowTitle("Persistence of Vision Raytracer - Live Viewer")
        self.resize(1200, 700)
        
        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(11)

        ###
        # TEXT EDITOR
        ###

        self.editor = QPlainTextEdit()

        # Styling
        self.highlighter = POVSyntaxHighlighter(self.editor.document())
        self.editor.setFont(font)
        metrics = self.editor.fontMetrics()
        self.editor.setTabStopDistance(
                metrics.horizontalAdvance(' ') * 4 # Can make this a variable later
                )
        self.editor.setStyleSheet("""
        QPlainTextEdit {
            background-color: #141414;
            color: white;
            border: 1px solid #444;
            selection-background-color: #555;
        }
        """)

        # Default scene
        if os.path.exists(scene_file):
            with open(scene_file, "r") as f:
                self.editor.setPlainText(f.read())
        else:
            self.editor.setPlainText(
'''
#include "colors.inc"
#include "metals.inc"
#include "glass.inc"

background { color Cyan }

global_settings {
    radiosity {
        pretrace_start 0.08
        pretrace_end 0.01
        count 100
        nearest_count 5
        error_bound 0.5
        recursion_limit 1
    }
}

sky_sphere {
    pigment {
        gradient y

        color_map {
            [0.0 color rgb <1, 1, 1>]
            [0.3 color rgb <0.4, 0.6, 1.0>]
            [1.0 color rgb <0.0, 0.1, 0.5>]
        }
    }
}

camera {
    location <0, 2, -3.2>
    look_at <0, 1, 2>
}

plane {
    <0, 1, 0>, -1
    pigment {
        checker color Red, color Blue
    }
}

sphere {
    <0, 1, 1.5>, 2
    texture {
        pigment { color White }
    }

    finish {
        reflection 1
        ambient 0
        diffuse 0.1
        specular 1
        roughness 0.001
    }
}

light_source {
    <2, 4, -3> 
    color White
}
'''
        )

        ###
        # PREVIEW
        ###

        self.preview = QLabel("No render yet")
        self.preview.setAlignment(Qt.AlignCenter)

        ###
        # CONSOLE
        ###

        self.console = QTextEdit()

        # Styling
        self.console.setFont(font)
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        self.console.setStyleSheet("""
        QTextEdit {
            background-color: #141414;
            color: white;
            border: 1px solid #444;
            selection-background-color #555;
        }
        """)

        ###
        # RENDER BUTTON
        ###

        self.render_button = QPushButton("Render (Ctrl+S)")
        self.render_button.clicked.connect(self.render_scene)

        ###
        # LAYOUT
        ###

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.editor)
        left_layout.addWidget(self.render_button)
        left_layout.addWidget(self.console)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.preview, 1)

        self.setLayout(main_layout)

    def keyPressEvent(self, event):
        # Ctrl+S shortcut
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.render_scene()


    def render_scene(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            with open(scene_file, "w") as f:
                f.write(self.editor.toPlainText())

            command = [
                    "povray",
                    scene_file,
                    f"+O{render_file}",
                    "+W800",
                    "+H600",
                    "-D"
                    ]

            result = subprocess.run(
                    command,
                    capture_output = True,
                    text = True
                    )

            output = result.stdout + "\n" + result.stderr
            self.console.setPlainText(output)

            self.console.moveCursor(QTextCursor.End)

            if result.returncode == 0:
                pixmap = QPixmap(render_file)

                self.preview.setPixmap(
                        pixmap.scaled(
                            self.preview.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                            )
                        )
        finally:
            QApplication.restoreOverrideCursor()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = POVRayIDE()
    window.show()

    sys.exit(app.exec())
