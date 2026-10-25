"""
🍅 Pomodoro Relógio - Versão Moderna
Aplicativo em formato de tomate com interface intuitiva, temporizador Pomodoro e relógio digital.
Desenvolvido com PySide6 (Qt para Python).
"""

import sys
import os
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, 
    QHBoxLayout, QVBoxLayout, QMenu
)
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QLinearGradient, 
    QRadialGradient, QPen, QBrush, QPixmap, QIcon, QAction
)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, QTime

# Suporte a som no Windows sem travar a interface
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Identificador exclusivo de aplicativo no Windows para exibir ícone correto na barra de tarefas
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('pomodoro.tomato.relogio.app')
    except Exception:
        pass


# Configurações dos Modos
MODES = {
    '25m': {
        'title': 'FOCO (25 MIN)',
        'seconds': 25 * 60,
        'badge': '🍅 FOCO',
        'is_break': False,
        'label': '🍅 25m'
    },
    '50m': {
        'title': 'FOCO LONGO (50 MIN)',
        'seconds': 50 * 60,
        'badge': '⚡ FOCO +',
        'is_break': False,
        'label': '⚡ 50m'
    },
    '5m': {
        'title': 'PAUSA CURTA (5 MIN)',
        'seconds': 5 * 60,
        'badge': '☕ PAUSA',
        'is_break': True,
        'label': '☕ 5m'
    },
    '15m': {
        'title': 'PAUSA LONGA (15 MIN)',
        'seconds': 15 * 60,
        'badge': '🌴 DESCANSO',
        'is_break': True,
        'label': '🌴 15m'
    },
    'clock': {
        'title': 'RELÓGIO DIGITAL',
        'seconds': 0,
        'badge': '🕒 HORÁRIO',
        'is_break': False,
        'label': '🕒 Hora'
    }
}


def ensure_icon_files():
    """Gera os arquivos de ícone se ainda não existirem."""
    os.makedirs('assets', exist_ok=True)
    ico_path = os.path.join('assets', 'tomato.ico')
    png_path = os.path.join('assets', 'tomato.png')

    if os.path.exists(ico_path) and os.path.exists(png_path):
        return

    pix = QPixmap(256, 256)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    cx, cy = 128, 145
    W, H = 225, 200
    top, bottom = cy - H // 2, cy + H // 2

    path = QPainterPath()
    path.moveTo(cx, top + 13)
    path.cubicTo(cx + W * 0.22, top - 1, cx + W * 0.5, top + H * 0.15, cx + W * 0.5, top + H * 0.48)
    path.cubicTo(cx + W * 0.5, top + H * 0.78, cx + W * 0.32, bottom, cx, bottom - 3)
    path.cubicTo(cx - W * 0.32, bottom, cx - W * 0.5, top + H * 0.78, cx - W * 0.5, top + H * 0.48)
    path.cubicTo(cx - W * 0.5, top + H * 0.15, cx - W * 0.22, top - 1, cx, top + 13)
    path.closeSubpath()

    grad = QRadialGradient(cx - 32, cy - 38, W * 0.7)
    grad.setColorAt(0.0, QColor('#FF4D4D'))
    grad.setColorAt(0.35, QColor('#E52B2B'))
    grad.setColorAt(0.75, QColor('#C41C1C'))
    grad.setColorAt(1.0, QColor('#880A0A'))

    painter.setBrush(QBrush(grad))
    painter.setPen(QPen(QColor('#6D0707'), 2))
    painter.drawPath(path)

    # Highlight
    hl_path = QPainterPath()
    hl_path.moveTo(cx - W * 0.35, top + H * 0.22)
    hl_path.cubicTo(cx - W * 0.4, top + H * 0.36, cx - W * 0.3, top + H * 0.52, cx - W * 0.22, top + H * 0.46)
    hl_path.cubicTo(cx - W * 0.27, top + H * 0.36, cx - W * 0.3, top + H * 0.25, cx - W * 0.35, top + H * 0.22)
    hl_grad = QLinearGradient(cx - W * 0.35, top + H * 0.22, cx - W * 0.22, top + H * 0.46)
    hl_grad.setColorAt(0.0, QColor(255, 255, 255, 100))
    hl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.setBrush(QBrush(hl_grad))
    painter.setPen(Qt.NoPen)
    painter.drawPath(hl_path)

    # Stem
    stem = QPainterPath()
    stem.moveTo(cx - 4, top + 8)
    stem.cubicTo(cx - 6, top - 10, cx - 14, top - 26, cx - 6, top - 32)
    stem.cubicTo(cx + 2, top - 32, cx - 1, top - 10, cx + 4, top + 8)
    stem.closeSubpath()

    stem_grad = QLinearGradient(cx - 13, top - 32, cx + 3, top + 8)
    stem_grad.setColorAt(0.0, QColor('#43A047'))
    stem_grad.setColorAt(1.0, QColor('#1B5E20'))
    painter.setBrush(QBrush(stem_grad))
    painter.setPen(QPen(QColor('#1B5E20'), 1))
    painter.drawPath(stem)

    # Leaves
    def draw_leaf(p_tip, p_left, p_right, color):
        lp = QPainterPath()
        lp.moveTo(cx, top + 11)
        lp.cubicTo(p_left.x(), p_left.y(), p_tip.x() - 2, p_tip.y(), p_tip.x(), p_tip.y())
        lp.cubicTo(p_tip.x() + 2, p_tip.y(), p_right.x(), p_right.y(), cx, top + 11)
        lp.closeSubpath()
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor('#1B5E20'), 1))
        painter.drawPath(lp)

    draw_leaf(QPointF(cx - 44, top + 3), QPointF(cx - 28, top - 4), QPointF(cx - 22, top + 15), QColor('#4CAF50'))
    draw_leaf(QPointF(cx - 24, top + 24), QPointF(cx - 24, top + 12), QPointF(cx - 8, top + 21), QColor('#43A047'))
    draw_leaf(QPointF(cx, top + 28), QPointF(cx - 9, top + 19), QPointF(cx + 9, top + 19), QColor('#388E3C'))
    draw_leaf(QPointF(cx + 24, top + 24), QPointF(cx + 8, top + 21), QPointF(cx + 24, top + 12), QColor('#43A047'))
    draw_leaf(QPointF(cx + 44, top + 3), QPointF(cx + 22, top + 15), QPointF(cx + 28, top - 4), QColor('#4CAF50'))

    painter.end()
    pix.save(png_path, 'PNG')
    pix.save(ico_path, 'ICO')


class TomatoPomodoroWindow(QWidget):
    """Janela principal do relógio Pomodoro em formato de tomate."""

    def __init__(self):
        super().__init__()

        # Configurações de Janela Frameless e Translúcida
        self.setFixedSize(480, 520)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Estados da Aplicação
        self.current_mode = '25m'
        self.total_seconds = MODES['25m']['seconds']
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.completed_pomodoros = 0
        self.always_on_top = False
        self.sound_enabled = True

        # Controle de Arraste da Janela
        self._is_dragging = False
        self._drag_pos = None

        # Timer principal (1 segundo)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(1000)

        # Construção da Interface
        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Monta os componentes e o layout interno do tomate."""
        # Layout Principal com espaçamento adequado dentro do corpo do tomate
        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(50, 146, 50, 44)
        master_layout.setSpacing(6)

        # ========================================================
        # 1. Barra de Ferramentas Superior (Ombros do tomate)
        # ========================================================
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(40, 0, 40, 0)

        tool_btn_style = '''
            QPushButton {
                background-color: rgba(0, 0, 0, 0.35);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 13px;
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.32);
            }
        '''
        close_btn_style = tool_btn_style + '''
            QPushButton:hover {
                background-color: #FF1744;
                border-color: #FF1744;
            }
        '''

        self.btn_pin = QPushButton('📌', self)
        self.btn_pin.setToolTip('Fixar no Topo (Sempre visível)')
        self.btn_pin.setStyleSheet(tool_btn_style)
        self.btn_pin.clicked.connect(self.toggle_always_on_top)

        self.btn_sound = QPushButton('🔔', self)
        self.btn_sound.setToolTip('Ativar/Desativar Som de Alerta')
        self.btn_sound.setStyleSheet(tool_btn_style)
        self.btn_sound.clicked.connect(self.toggle_sound)

        self.btn_min = QPushButton('🗕', self)
        self.btn_min.setToolTip('Minimizar Janela')
        self.btn_min.setStyleSheet(tool_btn_style)
        self.btn_min.clicked.connect(self.showMinimized)

        self.btn_close = QPushButton('✕', self)
        self.btn_close.setToolTip('Fechar Aplicativo')
        self.btn_close.setStyleSheet(close_btn_style)
        self.btn_close.clicked.connect(self.close)

        top_layout.addWidget(self.btn_pin)
        top_layout.addWidget(self.btn_sound)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_min)
        top_layout.addWidget(self.btn_close)
        master_layout.addLayout(top_layout)

        # ========================================================
        # 2. Seletor de Modos (Cápsulas intuitivas)
        # ========================================================
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(15, 4, 15, 0)
        mode_layout.setSpacing(4)

        self.mode_buttons = {}
        for key in ['25m', '50m', '5m', '15m', 'clock']:
            btn = QPushButton(MODES[key]['label'], self)
            btn.setToolTip(f"Modo: {MODES[key]['title']}")
            btn.clicked.connect(lambda checked=False, m=key: self.set_mode(m))
            self.mode_buttons[key] = btn
            mode_layout.addWidget(btn)

        master_layout.addLayout(mode_layout)

        # ========================================================
        # 3. Display Central (Dentro do Anel de Progresso)
        # ========================================================
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 18, 0, 18)
        center_layout.setSpacing(2)
        center_layout.setAlignment(Qt.AlignCenter)

        self.lbl_badge = QLabel('FOCO', self)
        self.lbl_badge.setStyleSheet('''
            QLabel {
                background-color: rgba(0, 0, 0, 0.35);
                color: #FFE082;
                font-size: 11px;
                font-weight: 800;
                border-radius: 9px;
                padding: 2px 14px;
                letter-spacing: 1px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        ''')
        self.lbl_badge.setAlignment(Qt.AlignCenter)

        self.lbl_time = QLabel('25:00', self)
        self.lbl_time.setStyleSheet('''
            QLabel {
                color: #FFFFFF;
                font-size: 50px;
                font-weight: 800;
                letter-spacing: 2px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        ''')
        self.lbl_time.setAlignment(Qt.AlignCenter)

        self.lbl_sub = QLabel('🍅 ⚪ ⚪ ⚪  •  Sessão 1 de 4', self)
        self.lbl_sub.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        ''')
        self.lbl_sub.setAlignment(Qt.AlignCenter)

        center_layout.addWidget(self.lbl_badge)
        center_layout.addWidget(self.lbl_time)
        center_layout.addWidget(self.lbl_sub)
        master_layout.addLayout(center_layout)

        # ========================================================
        # 4. Botões de Ação Intuitivos (Parte Inferior)
        # ========================================================
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(15, 0, 15, 6)
        bottom_layout.setSpacing(10)
        bottom_layout.setAlignment(Qt.AlignCenter)

        style_secondary = '''
            QPushButton {
                background-color: rgba(0, 0, 0, 0.35);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 17px;
                min-height: 34px;
                max-height: 34px;
                padding: 0 8px;
                font-weight: 600;
                font-size: 11px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        '''
        self.style_primary = '''
            QPushButton {
                background-color: #FFFFFF;
                color: #C62828;
                border: 2px solid #FFFFFF;
                border-radius: 19px;
                min-height: 38px;
                max-height: 38px;
                padding: 0 10px;
                font-weight: 800;
                font-size: 12px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QPushButton:hover {
                background-color: #FFF9C4;
            }
        '''

        self.btn_reset = QPushButton('🔄 Reiniciar', self)
        self.btn_reset.setToolTip('Reiniciar a contagem atual')
        self.btn_reset.setFixedWidth(100)
        self.btn_reset.setStyleSheet(style_secondary)
        self.btn_reset.clicked.connect(self.reset_timer)

        self.btn_play = QPushButton('▶ INICIAR', self)
        self.btn_play.setToolTip('Iniciar ou Pausar o Pomodoro')
        self.btn_play.setFixedWidth(130)
        self.btn_play.setStyleSheet(self.style_primary)
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_skip = QPushButton('⏭ Pular', self)
        self.btn_skip.setToolTip('Pular para a próxima etapa (Foco/Pausa)')
        self.btn_skip.setFixedWidth(100)
        self.btn_skip.setStyleSheet(style_secondary)
        self.btn_skip.clicked.connect(self.skip_session)

        bottom_layout.addWidget(self.btn_reset)
        bottom_layout.addWidget(self.btn_play)
        bottom_layout.addWidget(self.btn_skip)
        master_layout.addLayout(bottom_layout)

        self.update_mode_buttons_style()

    def update_mode_buttons_style(self):
        """Atualiza a aparência das cápsulas de modo para destacar o modo ativo."""
        mode_inactive = '''
            QPushButton {
                background-color: rgba(0, 0, 0, 0.35);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 13px;
                min-height: 26px;
                max-height: 26px;
                padding: 0 6px;
                font-weight: 600;
                font-size: 10px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        '''
        mode_active = '''
            QPushButton {
                background-color: #FFFFFF;
                color: #C62828;
                border: 1px solid #FFFFFF;
                border-radius: 13px;
                min-height: 26px;
                max-height: 26px;
                padding: 0 6px;
                font-weight: 800;
                font-size: 10px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        '''
        for key, btn in self.mode_buttons.items():
            btn.setStyleSheet(mode_active if key == self.current_mode else mode_inactive)

    def set_mode(self, mode_key, auto_start=False):
        """Muda o modo de operação do temporizador/relógio."""
        self.current_mode = mode_key
        self.is_running = auto_start

        if mode_key == 'clock':
            self.total_seconds = 0
            self.remaining_seconds = 0
            self.btn_play.setVisible(False)
            self.btn_reset.setVisible(False)
            self.btn_skip.setVisible(False)
        else:
            self.total_seconds = MODES[mode_key]['seconds']
            self.remaining_seconds = self.total_seconds
            self.btn_play.setVisible(True)
            self.btn_reset.setVisible(True)
            self.btn_skip.setVisible(True)
            self.update_play_button_text()

        self.update_mode_buttons_style()
        self.update_display()
        self.update()  # Força repintura do progresso

    def toggle_play(self):
        """Inicia ou pausa o temporizador."""
        if self.current_mode == 'clock':
            return
        self.is_running = not self.is_running
        self.update_play_button_text()
        self.update_display()
        self.update()

    def update_play_button_text(self):
        """Atualiza o texto e estilo do botão de Play/Pause conforme o estado."""
        if self.is_running:
            self.btn_play.setText('⏸ PAUSAR')
        else:
            if self.remaining_seconds < self.total_seconds:
                self.btn_play.setText('▶ CONTINUAR')
            else:
                self.btn_play.setText('▶ INICIAR')

    def reset_timer(self):
        """Reinicia o temporizador para a duração original do modo ativo."""
        if self.current_mode == 'clock':
            return
        self.is_running = False
        self.remaining_seconds = self.total_seconds
        self.update_play_button_text()
        self.update_display()
        self.update()

    def skip_session(self):
        """Pula para a próxima fase do ciclo Pomodoro mantendo o estado de execução coerente."""
        # Se estava rodando, continua rodando; se estava parado/pausado, inicia no novo modo apenas se já estiver rodando
        should_run = self.is_running

        if self.current_mode in ['25m', '50m']:
            # Concluiu foco, próxima etapa é pausa
            self.completed_pomodoros = (self.completed_pomodoros + 1) % 4
            if self.completed_pomodoros == 0:
                self.set_mode('15m', auto_start=should_run)
            else:
                self.set_mode('5m', auto_start=should_run)
        elif self.current_mode in ['5m', '15m']:
            # Concluiu pausa, próxima etapa é foco
            self.set_mode('25m', auto_start=should_run)

    def on_timer_tick(self):
        """Chamado a cada 1 segundo pelo QTimer."""
        if self.current_mode == 'clock':
            self.update_display()
            self.update()
            return

        if self.is_running:
            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
                self.update_display()
                self.update()
            else:
                self.session_completed()

    def session_completed(self):
        """Acionado quando a contagem regressiva chega a zero."""
        self.is_running = False
        self.update_play_button_text()

        # Alerta sonoro
        if self.sound_enabled:
            self.play_chime()

        # Avanço de ciclo Pomodoro
        self.skip_session()

    def play_chime(self):
        """Executa um aviso sonoro agradável em uma thread separada."""
        if not HAS_WINSOUND:
            return

        def _sound_thread():
            try:
                # Sequência de 4 notas alegres: C5, E5, G5, C6
                notes = [(523, 140), (659, 140), (784, 160), (1046, 300)]
                for freq, dur in notes:
                    winsound.Beep(freq, dur)
            except Exception:
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass

        threading.Thread(target=_sound_thread, daemon=True).start()

    def update_display(self):
        """Atualiza os textos das etiquetas de tempo, modo e ciclo."""
        if self.current_mode == 'clock':
            self.lbl_badge.setText('🕒 HORÁRIO ATUAL')
            now_str = QTime.currentTime().toString('HH:mm:ss')
            self.lbl_time.setStyleSheet('''
                QLabel {
                    color: #FFFFFF;
                    font-size: 38px;
                    font-weight: 800;
                    letter-spacing: 1px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
            ''')
            self.lbl_time.setText(now_str)
            self.lbl_sub.setText('Modo Relógio Contínuo')
        else:
            mode_info = MODES[self.current_mode]
            self.lbl_badge.setText(mode_info['badge'])
            
            self.lbl_time.setStyleSheet('''
                QLabel {
                    color: #FFFFFF;
                    font-size: 50px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
            ''')
            mins = self.remaining_seconds // 60
            secs = self.remaining_seconds % 60
            self.lbl_time.setText(f"{mins:02d}:{secs:02d}")

            # Indicador de ciclo Pomodoro
            cycle_idx = (self.completed_pomodoros % 4) + 1
            dots = ""
            for i in range(4):
                if i < self.completed_pomodoros % 4:
                    dots += "🍅 "
                elif i == self.completed_pomodoros % 4 and not mode_info['is_break']:
                    dots += "🟡 "
                else:
                    dots += "⚪ "

            if mode_info['is_break']:
                self.lbl_sub.setText(f"{dots}  Pausa Merecida")
            else:
                self.lbl_sub.setText(f"{dots}  Sessão {cycle_idx} de 4")

    def toggle_always_on_top(self):
        """Alterna a janela sempre no topo."""
        self.always_on_top = not self.always_on_top
        flags = self.windowFlags()
        if self.always_on_top:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            self.btn_pin.setStyleSheet('''
                QPushButton {
                    background-color: #FFE082;
                    color: #B71C1C;
                    border: 1px solid #FFE082;
                    border-radius: 13px;
                    min-width: 26px; max-width: 26px;
                    min-height: 26px; max-height: 26px;
                    font-size: 11px;
                }
            ''')
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            self.btn_pin.setStyleSheet('''
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.35);
                    color: #FFFFFF;
                    border: 1px solid rgba(255, 255, 255, 0.22);
                    border-radius: 13px;
                    min-width: 26px; max-width: 26px;
                    min-height: 26px; max-height: 26px;
                    font-size: 11px;
                }
            ''')
        self.show()

    def toggle_sound(self):
        """Alterna o som de notificação."""
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.btn_sound.setText('🔔')
            self.btn_sound.setToolTip('Som de Alerta Ativado')
        else:
            self.btn_sound.setText('🔕')
            self.btn_sound.setToolTip('Som de Alerta Mudo')

    # ========================================================
    # Pintura Vetorial do Tomate e Anel de Progresso
    # ========================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = 240
        cy = 295
        W = 430
        H = 380
        top = cy - H // 2
        bottom = cy + H // 2

        # 1. Sombra suave ambiente
        for i in range(16, 0, -2):
            sp = QPainterPath()
            s_top = top + i * 0.6
            s_bottom = bottom + i
            s_w = W + i * 1.3
            sp.moveTo(cx, s_top + 24)
            sp.cubicTo(cx + s_w * 0.22, s_top - 2, cx + s_w * 0.5, s_top + H * 0.15, cx + s_w * 0.5, s_top + H * 0.48)
            sp.cubicTo(cx + s_w * 0.5, s_top + H * 0.78, cx + s_w * 0.32, s_bottom, cx, s_bottom - 6)
            sp.cubicTo(cx - s_w * 0.32, s_bottom, cx - s_w * 0.5, s_top + H * 0.78, cx - s_w * 0.5, s_top + H * 0.48)
            sp.cubicTo(cx - s_w * 0.5, s_top + H * 0.15, cx - s_w * 0.22, s_top - 2, cx, s_top + 24)
            sp.closeSubpath()
            painter.setBrush(QBrush(QColor(0, 0, 0, int(15 - i))))
            painter.setPen(Qt.NoPen)
            painter.drawPath(sp)

        # 2. Corpo do Tomate
        path = QPainterPath()
        path.moveTo(cx, top + 24)
        path.cubicTo(cx + W * 0.22, top - 2, cx + W * 0.5, top + H * 0.15, cx + W * 0.5, top + H * 0.48)
        path.cubicTo(cx + W * 0.5, top + H * 0.78, cx + W * 0.32, bottom, cx, bottom - 6)
        path.cubicTo(cx - W * 0.32, bottom, cx - W * 0.5, top + H * 0.78, cx - W * 0.5, top + H * 0.48)
        path.cubicTo(cx - W * 0.5, top + H * 0.15, cx - W * 0.22, top - 2, cx, top + 24)
        path.closeSubpath()

        # Gradiente 3D com iluminação
        grad = QRadialGradient(cx - 60, cy - 70, W * 0.70)
        grad.setColorAt(0.0, QColor('#FF4D4D'))
        grad.setColorAt(0.35, QColor('#E52B2B'))
        grad.setColorAt(0.75, QColor('#C41C1C'))
        grad.setColorAt(1.0, QColor('#880A0A'))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor('#6D0707'), 2.5))
        painter.drawPath(path)

        # Brilho especular curvado
        hl_path = QPainterPath()
        hl_path.moveTo(cx - W * 0.35, top + H * 0.22)
        hl_path.cubicTo(cx - W * 0.4, top + H * 0.36, cx - W * 0.3, top + H * 0.52, cx - W * 0.22, top + H * 0.46)
        hl_path.cubicTo(cx - W * 0.27, top + H * 0.36, cx - W * 0.3, top + H * 0.25, cx - W * 0.35, top + H * 0.22)
        hl_grad = QLinearGradient(cx - W * 0.35, top + H * 0.22, cx - W * 0.22, top + H * 0.46)
        hl_grad.setColorAt(0.0, QColor(255, 255, 255, 80))
        hl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(hl_grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(hl_path)

        # 3. Talo Verde
        stem = QPainterPath()
        stem.moveTo(cx - 7, top + 15)
        stem.cubicTo(cx - 11, top - 18, cx - 26, top - 46, cx - 11, top - 56)
        stem.cubicTo(cx + 3, top - 56, cx - 2, top - 18, cx + 7, top + 15)
        stem.closeSubpath()

        stem_grad = QLinearGradient(cx - 24, top - 56, cx + 5, top + 15)
        stem_grad.setColorAt(0.0, QColor('#43A047'))
        stem_grad.setColorAt(1.0, QColor('#1B5E20'))
        painter.setBrush(QBrush(stem_grad))
        painter.setPen(QPen(QColor('#1B5E20'), 1.5))
        painter.drawPath(stem)

        # 4. Folhas (Cálice)
        def draw_leaf(p_tip, p_left, p_right, color):
            lp = QPainterPath()
            lp.moveTo(cx, top + 20)
            lp.cubicTo(p_left.x(), p_left.y(), p_tip.x() - 4, p_tip.y(), p_tip.x(), p_tip.y())
            lp.cubicTo(p_tip.x() + 4, p_tip.y(), p_right.x(), p_right.y(), cx, top + 20)
            lp.closeSubpath()
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor('#1B5E20'), 1.5))
            painter.drawPath(lp)

        draw_leaf(QPointF(cx - 80, top + 6), QPointF(cx - 52, top - 8), QPointF(cx - 40, top + 28), QColor('#4CAF50'))
        draw_leaf(QPointF(cx - 44, top + 44), QPointF(cx - 44, top + 22), QPointF(cx - 15, top + 38), QColor('#43A047'))
        draw_leaf(QPointF(cx, top + 52), QPointF(cx - 17, top + 34), QPointF(cx + 17, top + 34), QColor('#388E3C'))
        draw_leaf(QPointF(cx + 44, top + 44), QPointF(cx + 15, top + 38), QPointF(cx + 44, top + 22), QColor('#43A047'))
        draw_leaf(QPointF(cx + 80, top + 6), QPointF(cx + 40, top + 28), QPointF(cx + 52, top - 8), QColor('#4CAF50'))

        # 5. Anel de Progresso Circular em torno do Display Central
        ring_rect = QRectF(cx - 96, 222, 192, 192)

        # Pista de fundo do anel
        track_pen = QPen(QColor(0, 0, 0, 45), 7)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(ring_rect, 0, 360 * 16)

        # Arco ativo de progresso
        progress_pct = 0.0
        if self.current_mode == 'clock':
            # No modo relógio, o anel acompanha os segundos atuais do minuto
            sec = QTime.currentTime().second()
            progress_pct = sec / 60.0
        else:
            if self.total_seconds > 0:
                progress_pct = self.remaining_seconds / self.total_seconds

        if progress_pct > 0:
            arc_color = QColor('#FFF176') if not MODES[self.current_mode]['is_break'] else QColor('#81C784')
            arc_pen = QPen(arc_color, 7)
            arc_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(arc_pen)
            start_angle = 90 * 16
            span_angle = -int(progress_pct * 360 * 16)
            painter.drawArc(ring_rect, start_angle, span_angle)

    # ========================================================
    # Arraste Fluido da Janela com o Mouse
    # ========================================================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

    # ========================================================
    # Menu de Contexto (Botão Direito)
    # ========================================================
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu {
                background-color: #2D0B0B;
                color: #FFFFFF;
                border: 1px solid #720808;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #D32F2F;
            }
        ''')

        act_25 = menu.addAction('🍅 Foco 25 min')
        act_50 = menu.addAction('⚡ Foco 50 min')
        act_5 = menu.addAction('☕ Pausa Curta (5 min)')
        act_15 = menu.addAction('🌴 Pausa Longa (15 min)')
        act_clk = menu.addAction('🕒 Modo Relógio')
        menu.addSeparator()

        act_pin = menu.addAction('📌 Sempre Visível' if not self.always_on_top else '📌 Desafixar do Topo')
        act_snd = menu.addAction('🔔 Desativar Som' if self.sound_enabled else '🔔 Ativar Som')
        menu.addSeparator()

        act_min = menu.addAction('🗕 Minimizar')
        act_exit = menu.addAction('✕ Fechar')

        action = menu.exec(event.globalPos())
        if action == act_25:
            self.set_mode('25m')
        elif action == act_50:
            self.set_mode('50m')
        elif action == act_5:
            self.set_mode('5m')
        elif action == act_15:
            self.set_mode('15m')
        elif action == act_clk:
            self.set_mode('clock')
        elif action == act_pin:
            self.toggle_always_on_top()
        elif action == act_snd:
            self.toggle_sound()
        elif action == act_min:
            self.showMinimized()
        elif action == act_exit:
            self.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Relógio")

    # Garante ícone oficial
    ensure_icon_files()
    icon_path = os.path.join('assets', 'tomato.ico')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    window = TomatoPomodoroWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
