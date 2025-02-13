from ultralytics import YOLO
import os
import cv2
import numpy as np
from utils.sort import *
from datetime import datetime
from utils.PlacaDetector import PlacaDetector

lista_idiomas = "en,pt"
idiomas = lista_idiomas.split(",")
gpu = True #@param {type:"boolean"}
# Carrega o modelo YOLO
model = YOLO("E:/ProjetoPlacas/modelos/best.pt")
tracker = Sort(max_age=30)  # Rastreador
# Instancia o detector
tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
detector = PlacaDetector(idiomas, gpu,tesseract_cmd)

# Caminho do vídeo
caminho_video = 'videos2/03.mp4'
# Verifica se o arquivo existe
if not os.path.exists(caminho_video):
    raise FileNotFoundError(f"Arquivo '{caminho_video}' não encontrado.")
# Abre o vídeo
video = cv2.VideoCapture(caminho_video)
if not video.isOpened():
    raise ValueError(f"Não foi possível abrir o vídeo: {caminho_video}")

# Nome das pastas onde os arquivos serão salvos
folder_name = "deteccoes"
folder_name2 = "x"

# Certifique-se de que as pastas existem
os.makedirs(folder_name, exist_ok=True)
os.makedirs(folder_name2, exist_ok=True)

# Configurações do vídeo de saída 1
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = os.path.join(folder_name, "output_video.mp4")
fps = 30
output_width = 840
output_height = 480
out = cv2.VideoWriter(output_path, fourcc, fps, (output_width, output_height))

# Configurações do vídeo de saída 2 (placas recortadas)
output_path2 = os.path.join(folder_name2, "output_video2.mp4")
output_width2 = 228 #200
output_height2 = 60 #output_width2 //2
video_writer2 = cv2.VideoWriter(output_path2, fourcc, fps, (output_width2, output_height2))

# Classes de veículos
classNames = ["placa"]

# Redimensiona o frame para uma largura fixa (ex: 840px), mantendo a proporção
def redimensionar_frame(frame, largura, altura):
    """
    Redimensiona o frame para o tamanho especificado.
    """
    return cv2.resize(frame, (largura, altura))

while True:
    _, img = video.read()
    if img is None:
        break

    # Redimensiona o frame
    img = redimensionar_frame(img,output_width, output_height )

     # Processar a detecção e extração de placas
    results = model(img, stream=True)
    detections = np.empty((0,5))

    # itera sopbre todos os objetos detectados
    for obj in results:
        dados = obj.boxes
        for x in dados:
            #conf
            conf = int(x.conf[0]*100)
            cls = int(x.cls[0])
            nomeClass = classNames[cls]

            if conf >= 50:

                    # Coordenadas do bounding box
                x1, y1, x2, y2 = x.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                # Calcula o centro do bounding box
                cx, cy = x1 + w // 2, y1 + h // 2  
                #classe
                cv2.putText(img, nomeClass, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)

                

                crArray = np.array([x1,y1,x2,y2,conf])
                detections = np.vstack((detections,crArray))

    # Rastrear os objetos

    resultTracker = tracker.update(detections)

    for result in resultTracker:
        # Coordenadas do objeto detectado
        x1,y1,x2,y2,id = result
        x1, y1, x2, y2 = (int(x1)), int(y1), (int(x2)-5), int(y2)
        w, h = x2 - x1, y2 - y1 # Largura e altura do objeto
        cx,cy = x1+w//2, y1+h//2 # Centro do objeto
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 1)# desenha o retangulo nos objettos
        #cvzone.putTextRect(img,str(int(id)),(x1,y1-10),scale=1,thickness=1)

        # Realiza o recorte do objeto usando as coordenadas ajustadas
        cropped_car = img[y1:y2, x1:x2]
        
        texto_limpo = ""  # Variável para armazenar o texto da placa atual
        #print(x2, y1)
         #  processamento do objeto recortado
        if cropped_car.size > 0:  # Garante que o recorte não está vazio
            
# ------------------- TÉCNICAS DE PRÉ-PROCESSAMENTO DE IMAGEM ---------------------------------------           

            cropped_car = cv2.resize(cropped_car,(output_width2, output_height2), interpolation=cv2.INTER_CUBIC)
            #cropped_car = cv2.resize(cropped_car, None,fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            cropped_car = cv2.cvtColor(cropped_car, cv2.COLOR_BGR2GRAY)
            value, binary = cv2.threshold(cropped_car, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # otsu)
            # Aqui você pode salvar ou processar o recorte como quiser
            '''
            gray = cv2.cvtColor(cropped_car, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # otsu
            binary = cv2.dilate(binary, np.ones((5,5), np.uint8))
            binary = cv2.erode(binary, np.ones((3,3), np.uint8))
            '''
            
            #val, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            # binary = 255 - thresh # inverte o preto/branco

            # Aplica suavização antes da binarização (opcional)
            #gray = cv2.GaussianBlur(gray_cropped, (3, 3), 0)

            # Converte para uma imagem binaria
            #_, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY) # simples

            #binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 9) # adaptativa
            #binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 9)
            #binary = cv2.resize(binary,(output_width2,output_height2))
            #binary = cv2.erode(binary, np.ones((5, 5), np.uint8)) # diminui
            

            # Salva o recorte com a placa detectada
            #video_writer2.write(cropped_car)
            cv2.imshow("Recorte de Placa", binary)
            # Exibe o recorte
            #faz leitura de caracteres
# -------------------------------------------------------------------------------------------------------------------------------------------------

            if (( x2 > 180) and (x2 < 280)) and y1 > 200:

                # Chama o método de detecção e retorna os caracteres encontrados
                texto_limpo = detector.detectar_placa(binary)
                placa = detector.detectar_placa2(binary)
                # Valida a placa usando o método da instância `detector`
                valida = detector.validar_placa(placa)
                valida2 = detector.validar_placa(texto_limpo)
                # adicionar classificadore yolo
                print(texto_limpo, valida2)
                print(placa, valida)
                '''if valida2:
                    # Exibe a placa detectada no vídeo
                    print("Placa detectada:", texto_limpo if texto_limpo else "Nenhuma placa reconhecida.")
                #print(texto_limpo)
'''
    if cv2.waitKey(1) == 27:
        break

    # Coordenadas da linha2
    ponto_inicial2 = (280, 270)
    ponto_final2 = (280, 400)
    # coordernads da linha1
    ponto_inicial1 = (180, 270)
    ponto_final1 = (180, 400)

    # Desenhar a linha
    cv2.line(img, ponto_inicial1, ponto_final1, (255, 0, 0), 1)
    cv2.line(img, ponto_inicial2, ponto_final2, (255, 0, 0), 1)
    
    # escreve a placa
    if (len(texto_limpo) == 7):

        if valida2:
            cv2.putText(img, f"Placa: {texto_limpo}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        if valida:
            cv2.putText(img, f"Placa: {placa}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # Chama a função para registrar a placa
        #registrar_placa_unica(texto_limpo)

    # Grava o frame no vídeo de saída
    #out.write(img)
    cv2.imshow('Detector de Placas',img)
    
# Fechar o vídeo e arquivo de texto
#out.release()
#video_writer2.release()
cv2.destroyAllWindows()
