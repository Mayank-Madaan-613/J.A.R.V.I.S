"""
Jarvis UI — PyQt6 Voice Assistant Interface
Install: pip install PyQt6
Run:     python jarvis_ui.py

Integration points are clearly marked with # <-- CONNECT YOUR CODE HERE
"""

import sys
import math
import time
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPointF,
    QPropertyAnimation, QEasingCurve, QRectF, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient,
    QLinearGradient, QPainterPath, QFont, QFontMetrics,
    QPalette, QConicalGradient
)


# ─────────────────────────────────────────────
#  CONSTANTS / DESIGN TOKENS
# ─────────────────────────────────────────────
BG          = QColor("#080B14")
BG2         = QColor("#0D1220")
BLUE        = QColor("#00A8FF")
BLUE_DIM    = QColor("#005580")
BLUE_GLOW   = QColor(0, 168, 255, 40)
WHITE       = QColor("#E8F4FF")
MUTED       = QColor("#3A4A6B")
MUTED2      = QColor("#1E2A45")
GREEN       = QColor("#00FF88")
RED         = QColor("#FF4466")
AMBER       = QColor("#FFB800")

FONT_MAIN   = "Segoe UI"        # Windows
# Falls back to San Francisco on Mac, Roboto on Linux automatically


# ─────────────────────────────────────────────
#  STATE ENUM
# ─────────────────────────────────────────────
class JarvisState:
    IDLE      = "idle"
    LISTENING = "listening"
    THINKING  = "thinking"
    SPEAKING  = "speaking"
    ERROR     = "error"


# ─────────────────────────────────────────────
#  ORB WIDGET  — the animated core visual
# ─────────────────────────────────────────────
class OrbWidget(QWidget):
    """
    Draws the animated orb:
    - IDLE:      slow breathing pulse, dim blue
    - LISTENING: arc wave spins + waveform bars react
    - THINKING:  rotating dashed orbit rings
    - SPEAKING:  radiating concentric rings
    - ERROR:     red flash
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 280)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._state      = JarvisState.IDLE
        self._phase      = 0.0          # animation phase accumulator
        self._amp        = 0.0          # waveform amplitude 0-1
        self._target_amp = 0.0
        self._error_flash = 0.0         # 0-1 for error flash

        # Wave bars (for LISTENING visualizer)
        self._bars = [random.uniform(0.1, 0.3) for _ in range(32)]

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)           # ~60 fps

    # ── public API ─────────────────────────────
    def set_state(self, state: str):
        self._state = state
        if state == JarvisState.ERROR:
            self._error_flash = 1.0
        self.update()

    def set_amplitude(self, amp: float):
        """Feed real mic amplitude here (0.0 – 1.0)"""
        self._target_amp = max(0.0, min(1.0, amp))

    # ── internal tick ───────────────────────────
    def _tick(self):
        self._phase += 0.03

        # Smooth amplitude
        self._amp += (self._target_amp - self._amp) * 0.15

        # Error flash decay
        if self._error_flash > 0:
            self._error_flash = max(0.0, self._error_flash - 0.04)

        # Animate bars
        if self._state == JarvisState.LISTENING:
            for i in range(len(self._bars)):
                target = self._amp * random.uniform(0.3, 1.0)
                self._bars[i] += (target - self._bars[i]) * 0.25
        else:
            for i in range(len(self._bars)):
                self._bars[i] += (0.05 - self._bars[i]) * 0.1

        self.update()

    # ── paint ───────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        t = self._phase

        # ── 1. Background glow halo ──
        state_color = self._state_color()
        glow = QRadialGradient(cx, cy, 130)
        glow.setColorAt(0,   QColor(state_color.red(), state_color.green(), state_color.blue(), 22))
        glow.setColorAt(0.6, QColor(state_color.red(), state_color.green(), state_color.blue(), 8))
        glow.setColorAt(1,   QColor(0, 0, 0, 0))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx-130, cy-130, 260, 260))

        # ── 2. State-specific outer effect ──
        if self._state == JarvisState.IDLE:
            self._draw_idle(p, cx, cy, t)
        elif self._state == JarvisState.LISTENING:
            self._draw_listening(p, cx, cy, t)
        elif self._state == JarvisState.THINKING:
            self._draw_thinking(p, cx, cy, t)
        elif self._state == JarvisState.SPEAKING:
            self._draw_speaking(p, cx, cy, t)

        # ── 3. Core orb ──
        self._draw_core(p, cx, cy, t, state_color)

        # ── 4. Error overlay ──
        if self._error_flash > 0:
            err_col = QColor(255, 50, 80, int(self._error_flash * 120))
            p.setBrush(QBrush(err_col))
            p.drawEllipse(QRectF(cx-55, cy-55, 110, 110))

        p.end()

    def _state_color(self):
        if self._state == JarvisState.ERROR:     return RED
        if self._state == JarvisState.LISTENING: return BLUE
        if self._state == JarvisState.THINKING:  return AMBER
        if self._state == JarvisState.SPEAKING:  return GREEN
        return BLUE  # IDLE

    def _draw_core(self, p, cx, cy, t, color):
        """The central glowing sphere"""
        # Breathe scale
        if self._state == JarvisState.IDLE:
            scale = 1.0 + 0.06 * math.sin(t * 0.8)
        elif self._state == JarvisState.SPEAKING:
            scale = 1.0 + 0.12 * math.sin(t * 3.0) + 0.05 * self._amp
        else:
            scale = 1.0
        r = 52 * scale

        # Outer ring
        pen = QPen(QColor(color.red(), color.green(), color.blue(), 60), 1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx-r-6, cy-r-6, (r+6)*2, (r+6)*2))

        # Core gradient
        grad = QRadialGradient(cx - r*0.25, cy - r*0.25, r * 1.2)
        grad.setColorAt(0,   QColor(min(255, color.red()+80),
                                    min(255, color.green()+80),
                                    min(255, color.blue()+80), 255))
        grad.setColorAt(0.4, color)
        grad.setColorAt(1,   QColor(color.red()//3, color.green()//3, color.blue()//3, 200))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))

        # Specular highlight
        hi = QRadialGradient(cx - r*0.3, cy - r*0.35, r * 0.55)
        hi.setColorAt(0, QColor(255, 255, 255, 90))
        hi.setColorAt(1, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(hi))
        p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))

    def _draw_idle(self, p, cx, cy, t):
        """Slow concentric breathing rings"""
        for i in range(3):
            phase = t * 0.5 + i * 1.2
            alpha = int(40 * (0.5 + 0.5 * math.sin(phase)))
            radius = 72 + i * 18 + 8 * math.sin(phase * 0.7)
            pen = QPen(QColor(0, 168, 255, alpha), 1)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx-radius, cy-radius, radius*2, radius*2))

    def _draw_listening(self, p, cx, cy, t):
        """Waveform arc around the orb"""
        n = len(self._bars)
        radius = 80
        bar_width = (2 * math.pi * radius) / (n * 1.4)

        for i, amp in enumerate(self._bars):
            angle = (2 * math.pi * i / n) - math.pi / 2
            bar_h = 10 + amp * 38
            # inner and outer points
            inner = radius - 4
            outer = radius + bar_h
            x1 = cx + inner * math.cos(angle)
            y1 = cy + inner * math.sin(angle)
            x2 = cx + outer * math.cos(angle)
            y2 = cy + outer * math.sin(angle)

            alpha = int(120 + 135 * amp)
            col = QColor(0, 168, 255, alpha)
            pen = QPen(col, max(1.5, bar_width * 0.6))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Spinning arc overlay
        p.setPen(QPen(QColor(0, 168, 255, 80), 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        rect = QRectF(cx-78, cy-78, 156, 156)
        p.drawArc(rect, int(-t * 360 * 16 / (2*math.pi)) % (360*16), 100*16)
        p.drawArc(rect, int(-t * 360 * 16 / (2*math.pi) + 180*16) % (360*16), 60*16)

    def _draw_thinking(self, p, cx, cy, t):
        """Rotating dashed orbit rings"""
        for ring in range(3):
            r = 70 + ring * 14
            speed = [1.0, -0.7, 0.5][ring]
            angle_offset = t * speed
            dash_len = [80, 50, 110][ring]
            gap_len  = [30, 60, 40][ring]

            pen = QPen(QColor(255, 184, 0, 70 - ring * 15), 1.2)
            pen.setStyle(Qt.PenStyle.CustomDashLine)
            pen.setDashPattern([dash_len / 10, gap_len / 10])
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.save()
            p.translate(cx, cy)
            p.rotate(math.degrees(angle_offset))
            p.drawEllipse(QRectF(-r, -r, r*2, r*2))
            p.restore()

        # Dots orbiting
        for d in range(4):
            ang = t * 1.5 + d * (math.pi / 2)
            dx = cx + 68 * math.cos(ang)
            dy = cy + 68 * math.sin(ang)
            alpha = int(150 + 105 * math.sin(ang * 2))
            p.setBrush(QBrush(QColor(255, 184, 0, alpha)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(dx-3, dy-3, 6, 6))

    def _draw_speaking(self, p, cx, cy, t):
        """Radiating concentric rings, speed tied to amplitude"""
        speed = 0.8 + self._amp * 2.0
        for i in range(4):
            prog = ((t * speed * 0.4 + i * 0.25) % 1.0)
            r    = 58 + prog * 80
            alpha = int(160 * (1.0 - prog))
            w    = 2.5 * (1.0 - prog * 0.7)
            pen = QPen(QColor(0, 255, 136, alpha), w)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))


# ─────────────────────────────────────────────
#  TRANSCRIPT BUBBLE
# ─────────────────────────────────────────────
class BubbleWidget(QWidget):
    def __init__(self, text: str, role: str, parent=None):
        super().__init__(parent)
        self.role = role  # "user" or "jarvis"
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setMaximumWidth(480)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        if role == "user":
            label.setStyleSheet(f"""
                QLabel {{
                    background: #1A2540;
                    color: #C8DCFF;
                    border: 1px solid #2A3F6A;
                    border-radius: 16px;
                    border-bottom-right-radius: 4px;
                    padding: 10px 14px;
                    font-size: 13px;
                    font-family: '{FONT_MAIN}';
                    line-height: 1.5;
                }}
            """)
            layout.addStretch()
            layout.addWidget(label)
        else:
            label.setStyleSheet(f"""
                QLabel {{
                    background: #0D1829;
                    color: #E8F4FF;
                    border: 1px solid #00A8FF33;
                    border-radius: 16px;
                    border-bottom-left-radius: 4px;
                    padding: 10px 14px;
                    font-size: 13px;
                    font-family: '{FONT_MAIN}';
                    line-height: 1.5;
                }}
            """)
            # Jarvis label
            tag = QLabel("J")
            tag.setFixedSize(28, 28)
            tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tag.setStyleSheet("""
                QLabel {
                    background: #00A8FF22;
                    color: #00A8FF;
                    border: 1px solid #00A8FF55;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            layout.addWidget(tag, alignment=Qt.AlignmentFlag.AlignBottom)
            layout.addWidget(label)
            layout.addStretch()


# ─────────────────────────────────────────────
#  STATUS BAR WIDGET
# ─────────────────────────────────────────────
class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(8)

        self._dot = QLabel("●")
        self._dot.setFixedWidth(14)

        self._label = QLabel("Idle — say 'Hey Jarvis' to begin")
        self._label.setStyleSheet(f"""
            color: #3A4A6B;
            font-family: '{FONT_MAIN}';
            font-size: 12px;
        """)

        self._right = QLabel("")
        self._right.setStyleSheet(f"""
            color: #1E2A45;
            font-family: 'Courier New';
            font-size: 11px;
        """)

        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        layout.addStretch()
        layout.addWidget(self._right)

        # Clock timer
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._update_clock)
        self._clock.start(1000)
        self._update_clock()

        self.set_state(JarvisState.IDLE)

    def _update_clock(self):
        self._right.setText(time.strftime("%H:%M:%S"))

    def set_state(self, state: str):
        messages = {
            JarvisState.IDLE:      ("●", "#3A4A6B", "Idle  ·  Say 'Hey Jarvis' to begin"),
            JarvisState.LISTENING: ("●", "#00A8FF", "Listening..."),
            JarvisState.THINKING:  ("●", "#FFB800", "Processing..."),
            JarvisState.SPEAKING:  ("●", "#00FF88", "Speaking"),
            JarvisState.ERROR:     ("●", "#FF4466", "Error — try again"),
        }
        dot, color, text = messages.get(state, ("●", "#3A4A6B", ""))
        self._dot.setText(dot)
        self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        self._label.setText(text)
        self._label.setStyleSheet(f"""
            color: {color};
            font-family: '{FONT_MAIN}';
            font-size: 12px;
        """)


# ─────────────────────────────────────────────
#  MIC BUTTON
# ─────────────────────────────────────────────
class MicButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False
        self._hover  = False
        self._phase  = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        if self._active:
            self._phase += 0.06
            self.update()

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def enterEvent(self, e):
        self._hover = True
        self.update()

    def leaveEvent(self, e):
        self._hover = False
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()/2, self.height()/2
        r = 28

        # Outer ring pulse when active
        if self._active:
            pulse_r = r + 6 + 4 * math.sin(self._phase)
            pen = QPen(QColor(0, 168, 255, 80), 1.5)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx-pulse_r, cy-pulse_r, pulse_r*2, pulse_r*2))

        # Background circle
        if self._active:
            bg = QColor("#00A8FF")
        elif self._hover:
            bg = QColor("#1A2A44")
        else:
            bg = QColor("#101828")

        pen = QPen(QColor("#00A8FF" if (self._active or self._hover) else "#1E2A45"), 1.5)
        p.setPen(pen)
        p.setBrush(QBrush(bg))
        p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))

        # Mic icon (drawn with lines)
        icon_color = QColor("#E8F4FF" if self._active else "#00A8FF")
        pen2 = QPen(icon_color, 2)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # Mic body (rounded rect)
        body = QPainterPath()
        body.addRoundedRect(QRectF(cx-6, cy-14, 12, 18), 6, 6)
        p.drawPath(body)

        # Stand arc
        arc_rect = QRectF(cx-10, cy-2, 20, 16)
        p.drawArc(arc_rect, 0, -180*16)

        # Stem
        p.drawLine(QPointF(cx, cy+14), QPointF(cx, cy+18))
        p.drawLine(QPointF(cx-5, cy+18), QPointF(cx+5, cy+18))

        p.end()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class JarvisWindow(QMainWindow):
    # Signals for thread-safe UI updates
    sig_set_state   = pyqtSignal(str)
    sig_add_message = pyqtSignal(str, str)   # text, role
    sig_set_amp     = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis")
        self.setMinimumSize(640, 780)
        self.resize(680, 860)
        self._current_state = JarvisState.IDLE
        self._build_ui()
        self._connect_signals()
        self._apply_global_style()

    # ── UI construction ──────────────────────────
    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Top bar ──
        top_bar = self._make_top_bar()
        main_layout.addWidget(top_bar)

        # ── Orb area ──
        orb_container = QWidget()
        orb_container.setFixedHeight(320)
        orb_container.setObjectName("orb_container")
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orb_layout.setContentsMargins(0, 24, 0, 16)

        self.orb = OrbWidget()
        orb_layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignCenter)

        # State label under orb
        self.state_label = QLabel("IDLE")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setObjectName("state_label")
        orb_layout.addWidget(self.state_label)

        main_layout.addWidget(orb_container)

        # ── Divider ──
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setFixedHeight(1)
        div.setStyleSheet("background: #1E2A45; border: none;")
        main_layout.addWidget(div)

        # ── Transcript ──
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("transcript")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.transcript_widget = QWidget()
        self.transcript_layout = QVBoxLayout(self.transcript_widget)
        self.transcript_layout.setContentsMargins(0, 16, 0, 16)
        self.transcript_layout.setSpacing(8)
        self.transcript_layout.addStretch()

        self.scroll_area.setWidget(self.transcript_widget)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # ── Bottom controls ──
        bottom = self._make_bottom_bar()
        main_layout.addWidget(bottom)

        # ── Status bar ──
        self.status_bar_widget = StatusBar()
        main_layout.addWidget(self.status_bar_widget)

    def _make_top_bar(self):
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setObjectName("top_bar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("⬡  JARVIS")
        logo.setObjectName("logo")

        version = QLabel("v2.0")
        version.setObjectName("version_tag")

        layout.addWidget(logo)
        layout.addWidget(version)
        layout.addStretch()

        # Minimal window actions (visual only)
        for color in ["#FF5F57", "#FFBD2E", "#28C840"]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 10px;")
            layout.addWidget(dot)
            layout.addSpacing(2)

        return bar

    def _make_bottom_bar(self):
        bar = QWidget()
        bar.setFixedHeight(96)
        bar.setObjectName("bottom_bar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Clear button
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("btn_secondary")
        self.btn_clear.setFixedSize(80, 40)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_transcript)

        # Mic button (center)
        self.mic_btn = MicButton()
        self.mic_btn.clicked.connect(self._toggle_listen)

        # Mute button
        self.btn_mute = QPushButton("Mute")
        self.btn_mute.setObjectName("btn_secondary")
        self.btn_mute.setFixedSize(80, 40)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.btn_clear)
        layout.addStretch()
        layout.addWidget(self.mic_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.btn_mute)

        return bar

    # ── Signal wiring ────────────────────────────
    def _connect_signals(self):
        self.sig_set_state.connect(self._on_set_state)
        self.sig_add_message.connect(self._on_add_message)
        self.sig_set_amp.connect(self.orb.set_amplitude)

    # ── Slots ────────────────────────────────────
    def _on_set_state(self, state: str):
        self._current_state = state
        self.orb.set_state(state)
        self.status_bar_widget.set_state(state)
        self.mic_btn.set_active(state == JarvisState.LISTENING)
        self.state_label.setText(state.upper())
        label_colors = {
            JarvisState.IDLE:      "#3A4A6B",
            JarvisState.LISTENING: "#00A8FF",
            JarvisState.THINKING:  "#FFB800",
            JarvisState.SPEAKING:  "#00FF88",
            JarvisState.ERROR:     "#FF4466",
        }
        self.state_label.setStyleSheet(
            f"color: {label_colors.get(state, '#3A4A6B')};"
            f"font-family: 'Courier New'; font-size: 11px; letter-spacing: 3px;"
        )

    def _on_add_message(self, text: str, role: str):
        bubble = BubbleWidget(text, role)
        # Insert before the trailing stretch
        count = self.transcript_layout.count()
        self.transcript_layout.insertWidget(count - 1, bubble)
        # Auto-scroll to bottom
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def _toggle_listen(self):
        if self._current_state == JarvisState.LISTENING:
            self.sig_set_state.emit(JarvisState.IDLE)
        else:
            self.sig_set_state.emit(JarvisState.LISTENING)

        # <-- CONNECT YOUR CODE HERE
        res=voice()
        # call your voice recognition start/stop here

    def _clear_transcript(self):
        while self.transcript_layout.count() > 1:
            item = self.transcript_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Global stylesheet ────────────────────────
    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow, #root {{
                background: #080B14;
            }}
            #top_bar {{
                background: #0A0E1A;
                border-bottom: 1px solid #1E2A45;
            }}
            #logo {{
                color: #00A8FF;
                font-family: '{FONT_MAIN}';
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 3px;
            }}
            #version_tag {{
                color: #1E2A45;
                font-family: 'Courier New';
                font-size: 11px;
                margin-left: 6px;
                margin-top: 3px;
            }}
            #orb_container {{
                background: #080B14;
            }}
            #state_label {{
                color: #3A4A6B;
                font-family: 'Courier New';
                font-size: 11px;
                letter-spacing: 3px;
            }}
            #transcript {{
                background: #080B14;
                border: none;
            }}
            QScrollBar:vertical {{
                background: #080B14;
                width: 4px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #1E2A45;
                border-radius: 2px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            #bottom_bar {{
                background: #0A0E1A;
                border-top: 1px solid #1E2A45;
            }}
            #btn_secondary {{
                background: transparent;
                color: #3A4A6B;
                border: 1px solid #1E2A45;
                border-radius: 20px;
                font-family: '{FONT_MAIN}';
                font-size: 12px;
                font-weight: 500;
            }}
            #btn_secondary:hover {{
                color: #E8F4FF;
                border-color: #3A4A6B;
                background: #0D1220;
            }}
            #btn_secondary:pressed {{
                background: #1A2540;
            }}
        """)


# ─────────────────────────────────────────────
#  PUBLIC API — call these from your Jarvis code
# ─────────────────────────────────────────────
#
#  window.sig_set_state.emit(JarvisState.LISTENING)
#  window.sig_set_state.emit(JarvisState.THINKING)
#  window.sig_set_state.emit(JarvisState.SPEAKING)
#  window.sig_set_state.emit(JarvisState.IDLE)
#  window.sig_set_state.emit(JarvisState.ERROR)
#
#  window.sig_add_message.emit("what's the weather", "user")
#  window.sig_add_message.emit("It's 28°C and sunny.", "jarvis")
#
#  window.sig_set_amp.emit(0.75)   # feed mic amplitude 0.0-1.0 each frame


# ─────────────────────────────────────────────
#  DEMO — simulates the full state loop
# ─────────────────────────────────────────────
class DemoThread(QThread):
    def __init__(self, window):
        super().__init__()
        self.w = window

    def run(self):
        time.sleep(1.2)

        # Simulate: user speaks
        self.w.sig_set_state.emit(JarvisState.LISTENING)
        for i in range(60):
            amp = 0.3 + 0.7 * abs(math.sin(i * 0.3))
            self.w.sig_set_amp.emit(amp)
            time.sleep(0.05)
        self.w.sig_add_message.emit("Hey Jarvis, what's the weather in Delhi?", "user")
        self.w.sig_set_amp.emit(0.0)

        # Simulate: thinking
        self.w.sig_set_state.emit(JarvisState.THINKING)
        time.sleep(1.8)

        # Simulate: Jarvis responds
        self.w.sig_set_state.emit(JarvisState.SPEAKING)
        self.w.sig_add_message.emit(
            "Right now in Delhi it's 34°C, hazy with a UV index of 8. "
            "You'll want sunscreen if you're heading out.",
            "jarvis"
        )
        for i in range(80):
            amp = 0.4 + 0.6 * abs(math.sin(i * 0.25 + 1.0))
            self.w.sig_set_amp.emit(amp)
            time.sleep(0.04)

        self.w.sig_set_amp.emit(0.0)
        self.w.sig_set_state.emit(JarvisState.IDLE)

        time.sleep(2.0)

        # Second exchange
        self.w.sig_set_state.emit(JarvisState.LISTENING)
        for i in range(40):
            amp = 0.5 + 0.5 * abs(math.sin(i * 0.4))
            self.w.sig_set_amp.emit(amp)
            time.sleep(0.05)
        self.w.sig_add_message.emit("Open Spotify and play lo-fi.", "user")
        self.w.sig_set_amp.emit(0.0)

        self.w.sig_set_state.emit(JarvisState.THINKING)
        time.sleep(1.0)

        self.w.sig_set_state.emit(JarvisState.SPEAKING)
        self.w.sig_add_message.emit("Opening Spotify. Playing Lo-Fi Beats playlist.", "jarvis")
        time.sleep(2.0)
        self.w.sig_set_amp.emit(0.0)
        self.w.sig_set_state.emit(JarvisState.IDLE)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis")

    # HiDPI
    # HiDPI is automatic in Qt6, no attribute needed

    window = JarvisWindow()
    window.show()

    # Run demo loop to preview all states
    # demo = DemoThread(window)
    # demo.start()

    sys.exit(app.exec())
