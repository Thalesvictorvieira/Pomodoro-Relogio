import sys
from PySide6.QtWidgets import QLabel, QGridLayout, QApplication, QPushButton, QWidget
from PySide6.QtCore import QTime, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt



# Janela principal

app = QApplication(sys.argv)
JanelaCentral = QWidget()
layout = QGridLayout()

JanelaCentral.setWindowTitle("Relógio / Pomodoro")
JanelaCentral.setFixedSize(500, 300)  




# Labels

LabelDaHora = QLabel()
LabelDaHora.setStyleSheet(
    "background-color: gray; color: black; font-size: 80px;"
)
LabelDaHora.setAlignment(Qt.AlignCenter)


# Botões

botao25 = QPushButton("Pomodoro 25 min")
botao50 = QPushButton("Pomodoro 50 min")
botao5 = QPushButton("Descanso 5 min")


# Layout

layout.addWidget(LabelDaHora, 0, 0, 1, 3)
layout.addWidget(botao25, 1, 0)
layout.addWidget(botao50, 1, 1)
layout.addWidget(botao5, 1, 2)

JanelaCentral.setLayout(layout)


# Lógica de tempo

timer = QTimer()
tempo_restante = 0  # em segundos
modo_relogio = True

def atualizar_relogio():
    if modo_relogio:
        hora = QTime.currentTime().toString("HH:mm:ss")
        LabelDaHora.setText(hora)

def iniciar_contagem(segundos):
    global tempo_restante, modo_relogio
    modo_relogio = False
    tempo_restante = segundos
    atualizar_contagem()

def atualizar_contagem():
    global tempo_restante, modo_relogio

    if tempo_restante <= 0:
        modo_relogio = True
        return

    minutos = tempo_restante // 60
    segundos = tempo_restante % 60
    LabelDaHora.setText(f"{minutos:02d}:{segundos:02d}")
    tempo_restante -= 1


# Conexões

botao25.clicked.connect(lambda: iniciar_contagem(25 * 60))
botao50.clicked.connect(lambda: iniciar_contagem(50 * 60))
botao5.clicked.connect(lambda: iniciar_contagem(5 * 60))

timer.timeout.connect(lambda: atualizar_contagem() if not modo_relogio else atualizar_relogio())
timer.start(1000)

# Inicial
atualizar_relogio()

JanelaCentral.show()
app.exec()
