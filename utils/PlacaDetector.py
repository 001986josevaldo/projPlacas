from easyocr import Reader
import re
import pytesseract


class PlacaDetector:
    def __init__(self, idiomas, gpu=True, tesseract_cmd=None):
        """
        Inicializa o detector de placas.
        :param idiomas: Lista de idiomas para o Reader.
        :param gpu: Indica se o GPU deve ser usado.
        """
        # Padrão regex para placas (atributo da classe)
        self.padrao_placas = r'^[A-Z]{3}\d{4}$|^[A-Z]{3}\d[A-Z]\d{2}$'

        self.reader = Reader(idiomas, gpu=gpu)
        """ Inicializa a classe e define o caminho do Tesseract OCR (se necessário) """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Mapeamento de caracteres para correção
        self.letras_map = {
            "1": "I",
            "5": "S",
            "8": "B",
            "4": "A",
            "2": "Z",
            "0": "O"
        }
        self.numeros_map = {
            "/": "1",
            "\\": "1",
            "|": "1",
            "G": "6",
            "A": "0",
            "D": "0",
            "O": "0",
            "S": "5",
            "B": "8"
        }
    def limpar_texto(self, texto):
        """
        Remove caracteres especiais e converte o texto para maiúsculas.
        :param texto: Texto a ser limpo.
        :return: Texto limpo.
        """
        caracteres_especiais = ["(", ")", "*", "@", " ", '"', "[", "'", ";", "?"]
        for char in caracteres_especiais:
            texto = texto.replace(char, "")
        return texto.upper()
        
    def corrigir_caracteres(self, texto_limpo):
        """
        Corrige caracteres incorretos no texto da placa.
        :param texto_limpo: Texto limpo da placa.
        :return: Texto corrigido.
        """
        texto_limpo = list(texto_limpo)  # Converte para lista mutável

        # Corrigir posições 0, 1, 2 (sempre letras)
        for i in [0, 1, 2]:
            if texto_limpo[i] in self.letras_map:
                texto_limpo[i] = self.letras_map[texto_limpo[i]]

        # Corrigir posição 4 (pode ser número ou letra)
        if texto_limpo[4] in self.letras_map:
            texto_limpo[4] = self.letras_map[texto_limpo[4]]

        # Corrigir posições 3, 5, 6 (sempre números)
        for i in [3, 5, 6]:
            if texto_limpo[i] in self.numeros_map:
                texto_limpo[i] = self.numeros_map[texto_limpo[i]]

        return "".join(texto_limpo)  # Converte de volta para string

    def detectar_placa(self, imagem):
        """
        Detecta e limpa o texto de uma placa em uma imagem.
        :param imagem: A imagem binária contendo a placa.
        :return: Texto limpo da placa detectada ou uma mensagem de erro.
        """
        try:
            placas = self.reader.readtext(imagem)
            if not placas:
                return "Nenhuma placa detectada na imagem"

            # Extrai o texto da última detecção
            _, texto, _ = placas[-1]

            # Limpeza inicial do texto
            texto_limpo = self.limpar_texto(texto)

            # Aplica correções apenas se o texto tiver 7 caracteres
            if len(texto_limpo) == 7:
                texto_limpo = self.corrigir_caracteres(texto_limpo)

            return texto_limpo

        except Exception as e:
            return f"Erro ao processar a imagem: {e}"
    
    def detectar_placa2(self, imagem):

         # Configuração do Tesseract para detectar apenas letras e números
        config_tesseract = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        texto_ocr = pytesseract.image_to_string(imagem, config=config_tesseract)
        # Verifica se a string está vazia antes de continuar
                # Filtrar apenas letras e números (remoção de caracteres especiais)
        texto_limpo = re.sub(r'[^A-Z0-9]', '', texto_ocr)
        if not texto_limpo or len(texto_limpo) < 7:
            return ""  # Retorna se a string for vazia ou menor que 7
        texto_limpo = list(texto_limpo)  # Converte para lista mutável

          # Mapeamento para correção de caracteres para letras (posições fixas 0, 1, 2)
        letras_map = {
        "1": "I",
        "5": "S",
        "8": "B",
        "4": "A",
        "2": "Z",
        "0":"O"
        }
            # Corrigir posições (3, 5, 6) que sempre será número 
         # Mapeamento para correção de caracteres para números (posições 3, 5, 6)
        numeros_map = {
            "/": "1",
            "\\": "1",
            "|": "1",
            "G": "6",
            "A": "0",
            "D": "0",
            "O": "0",
            "S": "5",
            "B": "8"
        }

        # Corrigir posições 0, 1, 2 (sempre letras)
        for i in [0, 1, 2]:
            if i < len(texto_limpo) and texto_limpo[i] in letras_map:
                texto_limpo[i] = letras_map[texto_limpo[i]]

        '''            
        # Corrigir posição (4) que pode ser número ou letra 
        if texto_limpo[4] == "1":
            texto_limpo[4] = "I"
        elif texto_limpo[4] == "5":
            texto_limpo[4] = "S"
        elif texto_limpo[4] == "8":
            texto_limpo[4] = "B"
        elif texto_limpo[4] == "4":
            texto_limpo[4] = "A"
        elif texto_limpo[4] == "2":
            texto_limpo[4] = "Z"
        elif texto_limpo[4] in ["/", "\\", "|"]:
            texto_limpo[4] = "1"'''

        # Corrigir posição 4 (pode ser número ou letra)
        if 4 < len(texto_limpo) and texto_limpo[4] in letras_map:
            texto_limpo[4] = letras_map[texto_limpo[4]]

        # Corrigir posições 3, 5, 6 (sempre números)
        for i in [3, 5, 6]:
            if i < len(texto_limpo) and texto_limpo[i] in numeros_map:
                texto_limpo[i] = numeros_map[texto_limpo[i]]


        # Converte de volta para string
        texto_limpo = "".join(texto_limpo)
        return texto_limpo
    
    def validar_placa(self, placa):
        """
        Valida se a placa está no formato correto (XXX1234 ou XXX1X23).

        :param placa: String contendo a placa a ser validada.
        :return: True se a placa for válida, False caso contrário.
        """
        if re.match(self.padrao_placas, placa):
            return True
        else:
            return False

    







# Exemplo de uso:
'''# Importa a classe PlacaDetector do arquivo placaDetector.py
from placaDetector import PlacaDetector

# Configurações de exemplo
idiomas = ['pt', 'en']
gpu = True

# Instancia o detector
detector = PlacaDetector(idiomas, gpu)

# Chama o método de detecção
imagem = 'caminho/para/imagem.png'  # Substitua pelo caminho real da imagem ou pela imagem em uso
resultado = detector.detectar_placa(imagem)'''