import sys
from PySide6.QtWidgets import QLabel,QGridLayout, QApplication,QMainWindow, QPushButton,QWidget
from PySide6.QtCore import QTime,QTimer
from PySide6.QtGui import QIcon



#Definição da janela 
app = QApplication(sys.argv)
JanelaCentral = QWidget()
layout = QGridLayout() #define o estilo de layout

JanelaCentral.setWindowTitle("Relogio") #Seta o nome da janela
caminho_icone = "//media//thales//LINUX_HD//Programacao//Relogio//file.png" # Define o icone
icon = QIcon(caminho_icone)
JanelaCentral.setWindowIcon(icon)

LabelDaHora = QLabel()
Labelsepara = QLabel()
LabelDaHora.setStyleSheet("Background-color: GREEN; padding:auto; font-size:100px")
Labelsepara.setStyleSheet("Background-color:black")

#Adiciona o a label criada LabelDaHora ao widget
layout.addWidget(LabelDaHora)
layout.addWidget(Labelsepara)

def AtualizaHora():
    Hora = QTime.currentTime().toString()
    LabelDaHora.setText(Hora)

#Cria uma variavel que vai atualizar o codigo a cada tempo desejado 
timer = QTimer()
timer.timeout.connect(AtualizaHora)
timer.start(1000)

AtualizaHora()
JanelaCentral.setLayout(layout)
JanelaCentral.show()
app.exec()
