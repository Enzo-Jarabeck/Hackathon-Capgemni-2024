import flet as ft
import cv2
import numpy as np
import os
from deepface import DeepFace
from cryptography.fernet import Fernet 

# Variáveis para contar piscadas e calcular o movimento dos olhos
eye_movement = 0
blink_count = 0
prev_eye_center = None
status = ""
usuario = ""
arq = ""

# Função para gerar uma chave de criptografia 
def gerar_chave(): 
    return Fernet.generate_key()
# Função para criptografar uma pasta 
def criptografar_pasta(caminho_pasta, chave): 
    fernet = Fernet(chave) 
    for root, _, files in os.walk(caminho_pasta): 
        for file in files: 
            caminho_arquivo = os.path.join(root, file) 
            with open(caminho_arquivo, 'rb') as f: 
                dados = f.read() 
            dados_criptografados = fernet.encrypt(dados) 
            with open(caminho_arquivo + '.encrypted', 'wb') as f: 
                f.write(dados_criptografados) 
            os.remove(caminho_arquivo) 
# Função para descriptografar uma pasta 
def descriptografar_pasta(caminho_pasta, chave): 
    fernet = Fernet(chave) 
    for root, _, files in os.walk(caminho_pasta): 
        for file in files: 
            if file.endswith('.encrypted'): 
                caminho_arquivo = os.path.join(root, file) 
                with open(caminho_arquivo, 'rb') as f: 
                    dados_criptografados = f.read() 
                dados_descriptografados = fernet.decrypt(dados_criptografados) 
                with open(caminho_arquivo[:-10], 'wb') as f: 
                    f.write(dados_descriptografados) 
                os.remove(caminho_arquivo)  
if __name__ == "__main__": 
    # Defina o caminho para a pasta que deseja criptografar/descriptografar 
    caminho_pasta = "C:\Base_dados" 
    # Gere uma chave de criptografia 
    chave = gerar_chave() 
    print("chave:", chave)
    # Criptografar a pasta 
    criptografar_pasta(caminho_pasta, chave) 
    # Descriptografar a pasta 
    descriptografar_pasta(caminho_pasta, chave) 

# Acessar à pasta com fotos (banco de dados)
# Define o caminho para a pasta de imagens
folder_path = "C:\\Base_dados"
# Lista todos os arquivos na pasta
image_files = os.listdir(folder_path)
# Exibe os nomes dos arquivos
for file in image_files:
    print(file)

# Criar app
def inicio(main: ft.Page):
    main.title = "Reconhecimento facial"
    bem_vindo = ft.Text("Bem-vindo!", size=30, text_align=ft.alignment.center, weight=ft.FontWeight.BOLD)
    mensagem = ft.Text("Para iniciar o processo de RECONHECIMENTO FACIAL, clique no botão abaixo:", text_align=ft.TextAlign.CENTER)
    # Função para fechar popup e abrir a página do reconhecimento (câmera)
    def ok_popup(evento):
        global eye_movement, blink_count, prev_eye_center, verificacao, usuario, rosto, arq, botoes
        # Fechar popup
        popup.open = False
        # Limpar página inicial
        if bem_vindo in main.controls:
            main.remove(bem_vindo, mensagem, botao_inicio)
        if mensagem_encerrar in main.controls:
            txt_ident.visible = False
            txt_foto.visible = False
            txt_Nident.visible = False
            if eye_movement > 88 and blink_count > 0:
                if verificacao:
                    main.remove(usuario, rosto, arq)
            main.remove(mensagem_encerrar)
            main.remove(botoes)
        # Inicializa a captura de vídeo da webcam
        cap = cv2.VideoCapture(0)
        # Inicializa o detector de olhos
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        # Variáveis para contar piscadas e calcular o movimento dos olhos
        eye_movement = 0
        blink_count = 0
        prev_eye_center = None
        while True:
            # Captura um frame da webcam
            ret, frame = cap.read()
            if not ret:
                break
            # Converte o frame para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detecta olhos no frame
            eyes = eye_cascade.detectMultiScale(gray)
            # Desenha retângulos ao redor dos olhos detectados
            for (x, y, w, h) in eyes:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Calcula o centro do olho
                eye_center = (x + w // 2, y + h // 2)
                # Calcula o movimento dos olhos comparando com o frame anterior
                if prev_eye_center is not None:
                    eye_movement = np.sqrt((eye_center[0] - prev_eye_center[0])**2 + (eye_center[1] - prev_eye_center[1])**2)
                    cv2.putText(frame, f'Eye movement: {eye_movement}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # Atualiza o centro do olho para o próximo frame
                prev_eye_center = eye_center
            # Exibe o frame com as detecções
            cv2.imshow('Frame', frame)
            # Verifica se houve uma piscada de olho
            if len(eyes) == 0:
                blink_count += 1
                print("PISCADA")
            # Verifica se houve movimento excessivo dos olhos
            if eye_movement > 85:  # Valor de movimento arbitrário (escolhi esse valor - pode mudar conforme achar necessário)
                cv2.imwrite('temp_frame.jpg', frame)
            # Mandar o python esperar um pouquinho
            tecla = cv2.waitKey(2)
            # Mandar ele parar o código se clicar no ESC
            if tecla == 27:
                break
        # Libera a captura de vídeo e fecha todas as janelas
        cap.release()
        cv2.destroyAllWindows()
        
        # Autenticação:
        if eye_movement > 88 and blink_count > 0: #condições para ser considerado pessoa real (não foto)
            for file in image_files:
                # Define o caminho completo para o arquivo de imagem
                image_path = os.path.join(folder_path, file)
                # Lê a imagem
                image = cv2.imread(image_path)
                # Definir caminho para frame da webcam
                temp_frame_path = "temp_frame.jpg"
                # Reconhecimento = autenticação
                resultado = DeepFace.verify(image_path, temp_frame_path)
                verificacao = resultado["verified"]
                if verificacao:
                    break
            if verificacao:
                print("ROSTO IDENTIFICADO")
                rosto = ft.Image(src=image_path, width=200, height=200, fit=ft.ImageFit.CONTAIN)
                nome = str(file)
                nome_u = nome.strip(".jpg")
                print("Usuário:", nome_u)
                usuario = ft.Text("Usuário:")
                arq = file.strip(".jpg")
                arq = ft.Text(arq, size=20, weight=ft.FontWeight.BOLD)
                txt_ident.visible = True
                txt_foto.visible = False
                txt_Nident.visible = False
                main.add(txt_ident, usuario, rosto, arq)
            else:
                print("ROSTO NÃO IDENTIFICADO")
                txt_Nident.visible = True
                txt_foto.visible = False
                txt_ident.visible = False
                main.add(txt_Nident)
        else:
            print("NÃO É POSSÍVEL REALIZAR O RECONHECIMENTO - FOTO")
            txt_foto.visible = True
            txt_ident.visible = False
            txt_Nident.visible = False
            main.add(txt_foto)
        
        #Função do botão de encerrar
        def encerrar(evento):
            txt_ident.visible = False
            txt_foto.visible = False
            txt_Nident.visible = False
            if eye_movement > 88 and blink_count > 0:
                if verificacao:
                    main.remove(usuario, rosto, arq)
            main.remove(mensagem_encerrar)
            main.remove(botoes)
            encerramento = ft.Text('''Fim da sua sessão!
Obrigada por usar nosso sistema!''', weight=ft.FontWeight.BOLD)
            main.add(encerramento)
            main.update()
        
        #botões para encerrar ou iniciar outro reconhecimento
        botao_encerrar = ft.ElevatedButton("Encerrar sessão", color="pink600", on_click=encerrar, icon=ft.icons.PAUSE_CIRCLE_FILLED_ROUNDED, icon_color="pink600")
        botao_dnv = ft.ElevatedButton("Novo reconhecimento", color=ft.colors.TEAL_700, icon=ft.icons.PLAY_CIRCLE_FILL_OUTLINED, icon_color=ft.colors.TEAL_700, on_click=rec_fac)
        botoes = ft.Container(ft.Row([botao_encerrar, botao_dnv]))
        main.add(mensagem_encerrar, botoes)
        main.update()

    # Popup de mensagem para piscar
    popup = ft.AlertDialog(
        open=False,
        modal=True,
        title=ft.Text("ATENÇÃO!"),
        content=ft.Text("Após abrir a câmera, é necessário piscar para que o sistema diferencie seu rosto de uma foto! Após se posicionar na câmera e piscar, aperte 'ESC'."),
        actions=[ft.ElevatedButton("Ok", on_click=ok_popup)]
    )
    # Definir função para realizar reconhecimento
    def rec_fac(evento):
        main.dialog = popup
        popup.open = True
        main.update()
    
    # Mensagens que aparecem ao confirmar o reconhecimento
    txt_foto = ft.Container(ft.Text("NÃO É POSSÍVEL REALIZAR O RECONHECIMENTO - FOTO IDENTIFICADA"), visible=False, bgcolor=ft.colors.AMBER, alignment=ft.alignment.center, padding=10)
    txt_Nident = ft.Container(ft.Text("ROSTO NÃO IDENTIFICADO"), visible=False, bgcolor=ft.colors.RED, alignment=ft.alignment.center, padding=10)
    txt_ident = ft.Container(ft.Text("ROSTO IDENTIFICADO COM SUCESSO"), visible=False, bgcolor=ft.colors.GREEN, alignment=ft.alignment.center, padding=10)
    
    # Mensagem para encerrar
    mensagem_encerrar = ft.Text('''Deseja realizar outro reconhecimento facial?
Ou deseja encerrar essa sessão?''')
    
    # Botão de iniciar o reconhecimento
    botao_inicio = ft.ElevatedButton("INICIAR", on_click=rec_fac, icon=ft.icons.PLAY_CIRCLE_FILL_OUTLINED)
    main.add(bem_vindo, mensagem, botao_inicio)

# Criar app
ft.app(target=inicio)