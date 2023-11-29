from PySide6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
QGridLayout, QVBoxLayout, QWidget, QFrame, QLabel, QPushButton                          
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt
import cv2
from pyzbar.pyzbar import decode
from PIL import ImageGrab
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leitor de código de barras")
        self.setMouseTracking(True)

        # Widget principal
        self.widget_principal = QWidget()
        self.layout_principal = QGridLayout()
        self.widget_principal.setLayout(self.layout_principal)
        self.setCentralWidget(self.widget_principal)

        # Frame para alocar label com detalhes da codificação
        self.frame_codigo= QFrame()
        self.frame_codigo.setFixedHeight(80)
        self.layout_frame_codigo = QVBoxLayout()
        self.frame_codigo.setLayout(self.layout_frame_codigo)

        self.layout_principal.addWidget(self.frame_codigo, 0, 0)

        # Label para mostrar informações obtidas da câmera
        self.label_codigo = QLabel("Aqui seu código será exibido")
        self.layout_frame_codigo.addWidget(self.label_codigo)

        # Frame para mostrar imagem da câmera do notebook
        self.frame_camera = QFrame()
        self.frame_camera.setFrameShape(QFrame.Box)
        self.layout_frame_camera = QVBoxLayout()
        self.frame_camera.setLayout(self.layout_frame_camera)

        self.layout_principal.addWidget(self.frame_camera, 1, 0)

        # Frame para mostrar foto capturada pela câmera
        self.frame_foto = QFrame()
        self.frame_foto.setFrameShape(QFrame.Box)
        self.layout_frame_foto = QVBoxLayout()
        self.frame_foto.setLayout(self.layout_frame_foto)

        self.layout_principal.addWidget(self.frame_foto, 1, 1)

        # Label para exibir imagens propriamente ditas
        self.label_camera = QLabel()
        self.layout_frame_camera.addWidget(self.label_camera)
        self.layout_frame_camera.setAlignment(self.label_camera, Qt.AlignCenter)

        # Label para foto tirada
        self.label_foto = QLabel()
        self.layout_frame_foto.addWidget(self.label_foto)
        self.layout_frame_camera.setAlignment(self.label_foto, Qt.AlignCenter)

        # Botão captura
        self.btn_captura = QPushButton("Capturar")
        self.layout_principal.addWidget(self.btn_captura, 2, 0)
        self.btn_captura.clicked.connect(self.capture_screen)

        # Tirar fotos da câmera
        self.cap = cv2.VideoCapture(0)  # Abrir a câmera (0 para câmera padrão) ==> No lugar do zero se coloca o link rtsp
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # A cada 10 milissegundos atualiza o frame da câmera


        # Botão para decodificar código de barras
        self.btn_decode = QPushButton("Decodificar")
        self.layout_principal.addWidget(self.btn_decode, 2, 1)
        self.btn_decode.clicked.connect(self.decode_bar)



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
        image = screen.convert("RGB")  # Convertendo para o formato RGB
        data = image.tobytes("raw", "RGB")  # Obtendo os dados da imagem
        q_image = QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)  # Criando um QImage
        foto = QPixmap.fromImage(q_image)

        # Coloca a foto recém tirada na label correspondente
        self.label_foto.setPixmap(foto)
        self.layout_frame_camera.setAlignment(self.label_foto, Qt.AlignCenter)

        # Formatar a data e hora para criar um nome de arquivo único
        agora = datetime.datetime.now()
        nome_arquivo = agora.strftime("%Y-%m-%d_%H-%M-%S") + ".png"

        # Salva a captura de tela em um arquivo
        self.caminho_imagem = f'C:/Users/gabriela/Desktop/barcodeReader/fotos/{nome_arquivo}'
        screen.save(self.caminho_imagem)
        print(f'Captura de tela salva em {self.caminho_imagem}')


    def decode_bar(self):
        self.label_codigo.clear()
        try:
            # Carregar a imagem salva usando o OpenCV
            imagem = cv2.imread(self.caminho_imagem)

            # Converte a imagem para tons de cinza
            imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

            # Decodifica os códigos de barras na imagem em tons de cinza
            codigos_barras = decode(imagem_cinza)

            # Verifica se há códigos de barras encontrados na imagem
            if codigos_barras:
                # Itera sobre os códigos de barras encontrados na imagem
                for codigo in codigos_barras:
                    dados = codigo.data.decode('utf-8')  # Converte os dados decodificados para string
                    tipo_codigo = codigo.type
                    self.label_codigo.setText(f'Tipo de código de barras: {tipo_codigo}\nDados do código de barras: {dados}')
            else:
                self.label_codigo.setText("Nenhum código de barras foi encontrado na imagem.")
        
        except Exception as e:
            self.label_codigo.setText(f"Ocorreu um erro durante a decodificação dos códigos de barras: {str(e)}")
            

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    window.cap.release() 