from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
QVBoxLayout, QWidget, QFrame, QLabel, QPushButton                          
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
import cv2
import os
import pyzbar
from PIL import ImageGrab 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface pra Gabriela se localizar")
        self.setMouseTracking(True)


        # Widget principal
        self.widget_principal = QWidget()
        self.layout_principal = QHBoxLayout()
        self.widget_principal.setLayout(self.layout_principal)
        self.setCentralWidget(self.widget_principal)

        # Frame para mostrar imagem da câmera do notebook

        self.frame_camera = QFrame()
        self.frame_camera.setFrameShape(QFrame.Box)
        self.layout_frame_camera = QVBoxLayout()
        self.frame_camera.setLayout(self.layout_frame_camera)

        self.layout_principal.addWidget(self.frame_camera)

        # Label para exibir imagens propriamente ditas

        self.label_camera = QLabel()
        self.layout_frame_camera.addWidget(self.label_camera)

        # Label para foto tirada

        self.label_foto = QLabel()
        self.layout_frame_camera.addWidget(self.label_foto)

        # Botao captura

        self.btn_captura = QPushButton("Capturar")
        self.layout_frame_camera.addWidget(self.btn_captura)
        self.btn_captura.clicked.connect(self.capture_screen)


        # Tirar fotos da câmera
        self.cap = cv2.VideoCapture(0)  # Abrir a câmera (0 para câmera padrão)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # A cada 10 milissegundos atualiza o frame da câmera



    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converter de BGR para RGB
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_Qt_format)
            pixmap = pixmap.scaled(640, 480)  # Ajustar o tamanho do frame para o QLabel
            self.label_camera.setPixmap(pixmap)

            # Chamada para atualizar o frame novamente (loop)
            self.label_camera.repaint()

    def capture_screen(self):
        # Obter as coordenadas do canto superior esquerdo e inferior direito do QLabel
        label_geometry = self.label_camera.geometry()
        x, y = self.label_camera.mapToGlobal(label_geometry.topLeft()).x(), self.label_camera.mapToGlobal(label_geometry.topLeft()).y()
        w, h = label_geometry.width(), label_geometry.height()

        # Capturar a tela na área do QLabel usando o método ImageGrab
        screen = ImageGrab.grab(bbox=(x, y, x + w, y + h))  # Captura da tela na área do QLabel

        # Converter a captura da tela para um formato QImage
        img = screen.toqpixmap()

        # Exibir a captura da tela no QLabel label_foto
        self.label_foto.setPixmap(img)
        

        def closeEvent(self, event):
            self.cap.release()  # Liberar a câmera ao fechar o aplicativo
            event.accept()

''' 
    # Função para identificar e decodificar o código de barras em uma imagem
    def decode_barcode(image):
        # Converter a imagem para tons de cinza
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Usar a função decode() da pyzbar para encontrar e decodificar o código de barras na imagem
        barcodes = decode(gray_image)

        # Iterar sobre os códigos de barras encontrados na imagem
        for barcode in barcodes:
        # Extrair as informações do código de barras
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type

        # Exibir as informações do código de barras
        print(f'Tipo: {barcode_type}, Dados: {barcode_data}')

        # Desenhar um retângulo ao redor do código de barras na imagem
        x, y, w, h = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Exibir o texto do código de barras na imagem
        cv2.putText(image, f'{barcode_data} ({barcode_type})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return image

        # Ler a imagem que contém o código de barras (substitua 'caminho_para_sua_imagem' pelo caminho da sua imagem)
        image_path = 'caminho_para_sua_imagem'
        img = cv2.imread(image_path)

        # Chamar a função para identificar e decodificar o código de barras na imagem
        result_img = decode_barcode(img)

        # Exibir a imagem resultante com os códigos de barras identificados
        cv2.imshow('Result', result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
'''

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()