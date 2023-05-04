from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import os


"""
AutoBot
A classe AutoBot é responsável por automatizar o envio de mensagens no 
WhatsApp Web.

__init__()
    O método __init__() é o construtor da classe, que define as configurações do 
    Google Chrome e inicializa o driver.

acesso()
    O método acesso() acessa a página do WhatsApp Web e aguarda até que a página 
    esteja carregada.

pesquisa(nome)
    O método pesquisa(nome) pesquisa um contato no campo de pesquisa do WhatsApp 
    Web e seleciona o contato correspondente.

comenta(mensagem)
    O método comenta(mensagem) escreve uma mensagem para o contato selecionado e 
    envia a mensagem.

iniciar(textos,base_dados)
    O método iniciar(textos,base_dados) inicia o envio de mensagens para a lista 
    de contatos fornecida.

Parâmetros
    textos (string): Mensagem a ser enviada para os contatos
    base_dados (list): Lista de contatos a serem enviados
"""


class AutoBot:
    def __init__(self):
        # Configurações do google
        dir_path = os.getcwd()
        profile = os.path.join(dir_path, "profile", "bot")
        options = ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--mute-audio")
        options.add_argument(
            r"user-data-dir={}".format(profile))
        self.driver = webdriver.Chrome(options=options)
        # Contatos para envio de mensagem automatica

    def acesso(self):
        # Acessa a pagina desejada
        driver = self.driver
        driver.get("https://web.whatsapp.com/")
        driver.implicitly_wait(30)
        print('Acesso...')

    def pesquisa(self, nome):
        # Localiza o campo de pesquisa e
        # Escreve o texto desejado no campo de pesquisa
        print(f'Pesquisando... {nome}')
        campo_pesquisa = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='div[title="Caixa de texto de pesquisa"]'
        )
        campo_pesquisa.click()
        campo_pesquisa.clear()
        campo_pesquisa.send_keys(nome)
        time.sleep(1)
        campo_pesquisa.send_keys(Keys.RETURN)

    def comenta(self, mensagem):
        # Localiza o campo de comentarios e escreve uma resposta
        campo_comentario = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='div[title="Mensagem"]'
        )
        campo_comentario.click()
        campo_comentario.clear
        campo_comentario.send_keys(mensagem)
        time.sleep(2)
        self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='button[aria-label="Enviar"]'
        ).click()
        time.sleep(1)
        campo_comentario.send_keys(Keys.ESCAPE)

    def iniciar(self, textos, base_dados):
        print('Iniciando...', datetime.now().strftime('%H %M %S'))

        for pessoa in base_dados:
            time.sleep(5)
            self.pesquisa(pessoa[1])
            self.comenta(textos)
            print(pessoa[1], "-", datetime.now().strftime('%H %M %S'))
            time.sleep(20)

        self.finaliza()
    
    def finaliza(self):
        self.driver.close()
        print('Finalizado!!!')


if __name__ == "__main__":
    msg = "teste"
    pessoa = ["Lucas Patrick", "Entregas por fora"]
    OnlineBot = AutoBot()
    OnlineBot.acesso()
    OnlineBot.iniciar(msg, pessoa)
