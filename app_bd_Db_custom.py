from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time

from customtkinter import *
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
import sqlite3

import os
import os.path


set_appearance_mode("Systen")
set_default_color_theme("blue")


class Funcoes:
    def limpa_tela(self):
        """Este método limpa os campos de entrada na interface gráfica."""
        self.entrada_id.delete(0, END)
        self.entrada_nome.delete(0, END)
        self.entrada_email.delete(0, END)
        self.entrada_nasc.delete(0, END)
        self.entrada_cpf.delete(0, END)
        self.entrada_wpp.delete(0, END)
        self.entrada_data.delete(0, END)
        self.entrada_pedidos.delete(0, END)
        self.entrada_satis.delete(0, END)

    def imprime(self, texto='Teste'):
        # escreve uma mensagem no widget Text
        self.output2.insert('0.0', f"{texto}\n\n")

    def conecta_BD(self):
        """Este método conecta-se ao banco de dados SQLite."""
        baseBD = "clientes.db"
        self.imprime(f'{datetime.now()}\nConectando ao Banco de Dados {baseBD}')
        self.conexao = sqlite3.connect(baseBD)
        self.cursor = self.conexao.cursor()

    def desconecta_BD(self):
        """Este método desconecta-se ao banco de dados SQLite."""
        self.conexao.close()
        self.imprime('Banco de Dados desconectado')

    def montaTabelas(self):
        """Este método cria uma tabela chamada clientes no banco de dados, 
        se ela ainda não existir."""
        self.conecta_BD()
        # Cria tabela
        comandsql = """
                CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nome_cliente CHAR(200) not null,
                email CHAR(100),
                nascimento CHAR(20),
                cpf INT(11),
                telefone INT(20) not null,
                ultima_comp CHAR(15),
                pedidos INT(5),
                satisfacao INT(2)
                );
            """
        self.cursor.execute(comandsql)
        self.conexao.commit()
        self.desconecta_BD()

    def seleciona_saida(self, nome_coluna='id'):
        """Este método executa uma consulta SQL para selecionar informações 
        de clientes do banco de dados e exibi-las na interface gráfica."""
        self.saida.delete(*self.saida.get_children())
        self.conecta_BD()
        comandsql = f"""
            SELECT id, nome_cliente, email, nascimento, cpf, telefone, ultima_comp, pedidos, satisfacao FROM clientes
            ORDER BY {nome_coluna} ASC;
            """
        lista = self.cursor.execute(comandsql)

        for i in lista:
            self.saida.insert("", END, values=i)
        self.desconecta_BD()

    def buscar(self):
        """Ele executa uma consulta SQL para buscar informações de clientes com base 
        no nome inserido no campo de entrada entrada_nome na interface gráfica. 
        Os resultados da consulta são exibidos na interface gráfica."""
        self.conecta_BD()
        self.saida.delete(*self.saida.get_children())

        self.entrada_nome.insert(END, '%')
        nome = self.entrada_nome.get()
        self.cursor.execute("""
            SELECT id, nome_cliente, email, nascimento, cpf, telefone, ultima_comp, pedidos, satisfacao FROM clientes
            WHERE nome_cliente LIKE '%s' ORDER BY nome_cliente ASC
        """ % nome
                            )
        buscanome = self.cursor.fetchall()
        for i in buscanome:
            self.saida.insert("", END, values=i)

        self.limpa_tela()
        self.desconecta_BD()

    def ordena(self, event=None):
        coluna_id = event.widget.identify_column(event.x)
        linha_id = event.widget.identify_row(event.y)
        if not linha_id and coluna_id:
            # ID;Nome;E-mail;"Data de nascimento";CPF/CNPJ;Telefone;"Última compra";Pedidos;Satisfação
            if event.widget.heading(coluna_id, 'text') == 'Nome':
                nome_coluna = 'nome_cliente'
            elif event.widget.heading(coluna_id, 'text') == 'E-mail':
                nome_coluna = 'email'
            elif event.widget.heading(coluna_id, 'text') == 'Data de Nasc.':
                nome_coluna = 'nascimento'
            elif event.widget.heading(coluna_id, 'text') == 'CPF':
                nome_coluna = 'cpf'
            elif event.widget.heading(coluna_id, 'text') == 'Whatsapp':
                nome_coluna = 'telefone'
            elif event.widget.heading(coluna_id, 'text') == 'Última Compra':
                nome_coluna = 'ultima_comp'
            elif event.widget.heading(coluna_id, 'text') == 'Pedidos':
                nome_coluna = 'pedidos'
            elif event.widget.heading(coluna_id, 'text') == 'Satisfação':
                nome_coluna = 'satisfacao'
            else:
                nome_coluna = 'id'
            
            self.seleciona_saida(nome_coluna)

    def abre_lista(self):
        path = 'Saves/Enviados_'+str(f'{datetime.now().strftime("%d-%m")}')+'.csv'
        with open(path, 'r') as lista:
            for linha in lista:
                self.imprime(linha)


class Up_Down(Funcoes):
    def abrir(self):
        """ Este método usa o módulo filedialog do Tkinter para abrir uma caixa de diálogo
          e permitir que o usuário selecione um arquivo.

        """
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                               title="Selecione um arquivo", filetypes=(
            ('all files', '*.*'),
            ('db files', '*.db'),
            ('csv files', '*.csv'),
            ('jpg files', '*.jpg')))
        if file_path:
            self.caminho = file_path
            self.imprime(f'{datetime.now()}\nUpload do arquivo: {self.caminho} ')

    def verifica(self, nome):
        """Este método verifica se um nome específico já existe no banco de dados."""
        lista = self.cursor.execute("""
        SELECT nome_cliente FROM clientes
        ORDER BY nome_cliente asc;
        """)
        for row in lista.fetchall():
            if nome == row[0]:
                self.imprime(f"{nome} já existe no banco de dados!!!")
                return False
        else:
            return True

    def Upload(self):
        """
        Este método carrega dados de clientes de um arquivo e os adiciona ao banco de dados.
        """
        self.abrir()
        self.conecta_BD()
        with open(self.caminho, encoding='utf-8') as lista_clientes:
            clientes = lista_clientes.readlines()
            for cliente in clientes:
                if cliente == clientes[0]:
                    pass
                else:
                    cliente = cliente.split(";")
                    if self.verifica(cliente[0]):
                        self.cursor.execute("""
                            INSERT INTO clientes (nome_cliente, email, nascimento, cpf, telefone, ultima_comp, pedidos, satisfacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (cliente[0], cliente[1], cliente[2], cliente[3], cliente[4], cliente[5], cliente[6], cliente[7])
                        )
                    else:
                        self.cursor.execute("""
                            UPDATE clientes SET email = ?, nascimento = ?, cpf = ?, telefone = ?, ultima_comp = ?, pedidos = ?, satisfacao = ?
                            WHERE nome_cliente = ?
                        """, (cliente[1], cliente[2], cliente[3], cliente[4], cliente[5], cliente[6], cliente[7], cliente[0])
                        )

        self.caminho = None
        self.conexao.commit()
        self.desconecta_BD()
        self.seleciona_saida()


class AutoBot(Up_Down):
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
        # Cria diretorio para salvar informaçoes de envio
        if not os.path.exists('Saves'):
            os.makedirs('Saves')

    def acesso(self):
        """O método acesso() acessa a página do WhatsApp Web e aguarda até que a página 
        esteja carregada."""
        driver = self.driver
        driver.get("https://web.whatsapp.com/")
        driver.implicitly_wait(30)

    def pesquisa(self, nome):
        """O método pesquisa(nome) pesquisa um contato no campo de pesquisa do WhatsApp 
        Web e seleciona o contato correspondente."""
        self.campo_pesquisa = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='div[title="Caixa de texto de pesquisa"]'
        )
        self.campo_pesquisa.click()
        self.campo_pesquisa.clear()
        self.campo_pesquisa.send_keys(nome)
        time.sleep(1)
        self.campo_pesquisa.send_keys(Keys.RETURN)

    def comenta(self, mensagem):
        """O método comenta(mensagem) escreve uma mensagem para o contato selecionado e 
        envia a mensagem."""
        campo_comentario = self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='div[title="Mensagem"]'
        )
        campo_comentario.click()
        campo_comentario.clear()
        campo_comentario.send_keys(mensagem)
        time.sleep(2)
        self.driver.find_element(
            by=By.CSS_SELECTOR,
            value='button[aria-label="Enviar"]'
        ).click()
        time.sleep(1)
        campo_comentario.send_keys(Keys.ESCAPE)

    def envio_imagem(self, imagem):
        # clicar no ícone de anexo
        self.driver.find_element_by_xpath("//div[@title='Anexar']").click()

        # selecionar a opção de enviar imagem
        enviar_imagem = self.driver.find_element_by_xpath(
            "//input[@accept='image/*,video/*']")
        # substitua pelo caminho da imagem que deseja enviar
        enviar_imagem.send_keys(imagem)

        # esperar 5 segundos para que a imagem seja carregada
        time.sleep(5)

        # clicar no botão de enviar
        # self.driver.find_element_by_xpath("//span[@data-icon='send']").click()

    def iniciar(self, textos, base_dados, image=None):
        """O método iniciar(textos,base_dados) inicia o envio de mensagens para a lista 
        de contatos fornecida."""

        for pessoa in base_dados:
            time.sleep(5)
            self.pesquisa(pessoa[1])
            try:
                if image != "":
                    self.envio_imagem(image)
                self.comenta(textos)
                with open(f'Saves\Enviados_{datetime.now().strftime("%d-%m")}.csv', 'a') as enviados:
                    enviados.writelines(
                        f'; {pessoa[1]}; {datetime.now().strftime("%H %M %S")}\n')
                time.sleep(2)

            except Exception as e:
                self.campo_pesquisa.send_keys(Keys.ESCAPE)
                with open(f'Saves\Enviados_{datetime.now().strftime("%d-%m")}.csv', 'a') as enviados:
                    enviados.writelines(
                        f'Erro - {e}; {pessoa[1]}; {datetime.now().strftime("%H %M %S")}\n')

            time.sleep(5)

        self.finaliza()

    def finaliza(self):
        with open(f'Saves\Enviados_{datetime.now().strftime("%d-%m")}.csv', 'a') as enviados:
            enviados.writelines(
                f'Finalizado às {datetime.now().strftime("%H %M %S")}\n\n')
        self.driver.close()


class funcoesClientes(Up_Down):
    def variaveis_clientes(self):
        """Atribui os valores inseridos nos campos de entrada a variáveis correspondentes."""
        self.id = self.entrada_id.get()
        self.nome = self.entrada_nome.get()
        self.email = self.entrada_email.get()
        self.nasc = self.entrada_nasc.get()
        self.cpf = self.entrada_cpf.get()
        self.wpp = self.entrada_wpp.get()
        self.data = self.entrada_data.get()
        self.pedidos = self.entrada_pedidos.get()
        self.satis = self.entrada_satis.get()

    def add_cliente(self):
        """Insere um novo cliente na tabela "clientes" do banco de dados, caso o nome e o telefone não estejam vazios."""
        self.variaveis_clientes()
        self.conecta_BD()
        if self.nome != '' and self.telefone != '':
            self.cursor.execute("""
                INSERT INTO clientes (nome_cliente, email, nascimento, cpf, telefone, ultima_comp, pedidos, satisfacao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, self.nome, self.email, self.nasc, self.cpf, self.wpp, self.data, self.pedidos, self.satis
                                )
            self.conexao.commit()
            self.desconecta_BD()
            self.seleciona_saida()
            self.limpa_tela()

        else:
            pass

    def abre_cliente(self, event):
        self.limpa_tela()
        self.saida.selection()

        for i in self.saida.selection():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = self.saida.item(
                i, 'values')
            self.entrada_id.insert(END, col1)
            self.entrada_nome.insert(END, col2)
            self.entrada_email.insert(END, col3)
            self.entrada_nasc.insert(END, col4)
            self.entrada_cpf.insert(END, col5)
            self.entrada_wpp.insert(END, col6)
            self.entrada_data.insert(END, col7)
            self.entrada_pedidos.insert(END, col8)
            self.entrada_satis.insert(END, col9)

    def deleta_cliente(self):
        """Exclui um cliente da tabela "clientes" do banco de dados, com base em seu ID"""
        self.variaveis_clientes()
        self.conecta_BD()

        self.cursor.execute("""
            DELETE FROM clientes WHERE id = ?
        """, (self.id)
        )
        self.conexao.commit()

        self.desconecta_BD()
        self.limpa_tela()
        self.seleciona_saida()

    def editar_cliente(self):
        """Atualiza as informações de um cliente na tabela "clientes" do banco de dados, com base em seu ID."""
        self.variaveis_clientes()
        self.conecta_BD()
        self.cursor.execute("""
            UPDATE clientes SET nome_cliente = ?, email = ?, nascimento = ?, cpf = ?, telefone = ?, ultima_comp = ?, pedidos = ?, satisfacao = ?
            WHERE id = ?
        """, (self.nome, self.email, self.nasc, self.cpf, self.wpp, self.data, self.pedidos, self.satis, self.id)
        )
        self.conexao.commit()
        self.desconecta_BD()
        self.seleciona_saida()
        self.limpa_tela()
    
    def envia_msg(self):
        """Envia uma mensagem para todos os clientes na tabela "clientes" do banco de dados, usando a classe "autoMsg"."""
        self.msg = self.entrada_mensagem.get()
        self.conecta_BD()
        clientes = self.cursor.execute("""
            SELECT id, nome_cliente, email, nascimento, cpf, telefone, ultima_comp, pedidos, satisfacao FROM clientes
            ORDER BY nome_cliente ASC;
            """)
        acesso = AutoBot()
        acesso.acesso()
        if self.caminho != None:
            self.imprime(
                f'{datetime.now()}\nIniciando ... imagem {self.caminho} será carregada.')
            acesso.iniciar(self.msg, clientes, self.caminho)
        else:
            self.imprime(f'{datetime.now()}\nIniciando...')
            acesso.iniciar(self.msg, clientes)
        self.abre_lista()
        self.desconecta_BD()


class Application(CTk, funcoesClientes):
    def __init__(self):
        super().__init__()
        self.tela()
        self.personalizacao()
        self.menus()
        self.frames_tela()
        self.paginas()
        self.frame_1_pag_1()
        self.frame_1_pag_2()
        self.frame_2_banco()
        self.frame_2_retorno()
        self.montaTabelas()
        self.seleciona_saida()
        self.caminho = None

    def tela(self):
        self.title('Envio de Promocoes')
        self.geometry(None)
        self.minsize(width=800, height=600)

    def personalizacao(self,
                       tamanho_texto=11, fonte_botao='arial black',
                       fonte_texto='verdana', tipo='bold'):
        self.fonte_botao = fonte_botao
        self.fonte_texto = fonte_texto
        self.tamanho = tamanho_texto

        self.tipo = tipo

    def frames_tela(self):
        # Cria os frames da tela
        self.frame_1 = CTkFrame(self)
        self.frame_1.place(relx=0.02, rely=0.02, relheight=0.46, relwidth=0.96)

        self.frame_2 = CTkFrame(self)
        self.frame_2.place(relx=0.02, rely=0.52, relheight=0.46, relwidth=0.96)

    def paginas(self):
        # criar as abas do frame_1
        self.abas = CTkTabview(self.frame_1)

        # configura as abas do frame_1
        self.abas.add('Cadastro')
        self.abas.add('Envio')

        self.aba_cadastro = self.abas.tab('Cadastro')
        self.aba_envio = self.abas.tab('Envio')

        # criar as abas do frame_2
        self.abas_2 = CTkTabview(self.frame_2)

        # configura as abas do frame_2
        self.abas_2.add('Banco de Dados')
        self.abas_2.add('Retorno')

        self.aba_banco = self.abas_2.tab('Banco de Dados')
        self.aba_retorno = self.abas_2.tab('Retorno')

        # Posiciona as abas na tela
        self.abas.place(x=0, y=0, relheight=1, relwidth=1)
        self.abas_2.place(x=0, y=0, relheight=1, relwidth=1)

    def botoes(self, aba):
        # limpar
        self.bt_limpar = CTkButton(aba, text='Limpar', fg_color='#ad8a0c',
                                   command=self.limpa_tela,
                                   font=('arial black', 11, 'bold'))
        self.bt_limpar.place(relx=0.2, rely=0.1, relheight=0.1, relwidth=0.1)

        # buscar
        self.bt_buscar = CTkButton(aba, text='Buscar', fg_color='#ad8a0c',
                                   command=self.buscar,
                                   font=('arial black', 11, 'bold'))
        self.bt_buscar.place(relx=0.32, rely=0.1, relheight=0.1, relwidth=0.1)

        # adicionar
        self.bt_add = CTkButton(aba, text='Adicionar', fg_color='#007382',
                                command=self.add_cliente,
                                font=('arial black', 11, 'bold'))
        self.bt_add.place(relx=0.52, rely=0.1, relheight=0.1, relwidth=0.1)

        # editar
        self.bt_editar = CTkButton(aba, text='Editar', fg_color='#ad8a0c',
                                   command=self.editar_cliente,
                                   font=('arial black', 11, 'bold'))
        self.bt_editar.place(relx=0.72, rely=0.1, relheight=0.1, relwidth=0.1)

        # deletar
        self.bt_apagar = CTkButton(aba, text='Apagar', fg_color='#ad8a0c',
                                   command=self.deleta_cliente,
                                   font=('arial black', 11, 'bold'))
        self.bt_apagar.place(relx=0.84, rely=0.1, relheight=0.1, relwidth=0.1)

    def frame_1_pag_1(self):
        # cira os widgets da aba cadastro
        self.botoes(self.aba_cadastro)

        # Entradas e labels
        # ID
        self.lb_id = CTkLabel(self.aba_cadastro, text='ID',
                              font=(self.fonte_texto, 8))
        self.lb_id.place(relx=0.01, rely=0.02)
        self.entrada_id = CTkEntry(self.aba_cadastro)
        self.entrada_id.place(relx=0.01, rely=0.1,
                              relheight=0.1, relwidth=0.15)

        # Nome
        self.lb_nome = CTkLabel(self.aba_cadastro, text='Nome',
                                font=(self.fonte_texto, 8))
        self.lb_nome.place(relx=0.01, rely=0.22)
        self.entrada_nome = CTkEntry(self.aba_cadastro)
        self.entrada_nome.place(relx=0.01, rely=0.3,
                                relheight=0.1, relwidth=0.73)

        # E-mail
        self.lb_email = CTkLabel(self.aba_cadastro, text='E-mail',
                                 font=(self.fonte_texto, 8))
        self.lb_email.place(relx=0.01, rely=0.42)
        self.entrada_email = CTkEntry(self.aba_cadastro)
        self.entrada_email.place(
            relx=0.01, rely=0.5, relheight=0.1, relwidth=0.73)

        # Data de Nascimento
        self.lb_nasc = CTkLabel(self.aba_cadastro, text='Data de Nascimento',
                                font=(self.fonte_texto, 8))
        self.lb_nasc.place(relx=0.01, rely=0.62)
        self.entrada_nasc = CTkEntry(self.aba_cadastro)
        self.entrada_nasc.place(relx=0.01, rely=0.7,
                                relheight=0.1, relwidth=0.2)

        # CPF
        self.lb_cpf = CTkLabel(self.aba_cadastro, text='CPF',
                               font=(self.fonte_texto, 8))
        self.lb_cpf.place(relx=0.25, rely=0.62)
        self.entrada_cpf = CTkEntry(self.aba_cadastro)
        self.entrada_cpf.place(relx=0.25, rely=0.7,
                               relheight=0.1, relwidth=0.2)

        # Whatsapp
        self.lb_wpp = CTkLabel(self.aba_cadastro, text='Contato WhatsApp',
                               font=(self.fonte_texto, 8))
        self.lb_wpp.place(relx=0.5, rely=0.62)
        self.entrada_wpp = CTkEntry(self.aba_cadastro)
        self.entrada_wpp.place(relx=0.5, rely=0.7, relheight=0.1, relwidth=0.2)

        # Data da Ultima Compra
        self.lb_data = CTkLabel(self.aba_cadastro, text='Última Compra',
                                font=(self.fonte_texto, 8))
        self.lb_data.place(relx=0.01, rely=0.82)
        self.entrada_data = CTkEntry(self.aba_cadastro)
        self.entrada_data.place(relx=0.01, rely=0.9,
                                relheight=0.1, relwidth=0.2)

        # Pedidos
        self.lb_pedidos = CTkLabel(self.aba_cadastro, text='Pedidos',
                                   font=(self.fonte_texto, 8))
        self.lb_pedidos.place(relx=0.25, rely=0.82)
        self.entrada_pedidos = CTkEntry(self.aba_cadastro)
        self.entrada_pedidos.place(
            relx=0.25, rely=0.9, relheight=0.1, relwidth=0.2)

        # Satisfacao
        self.lb_satis = CTkLabel(self.aba_cadastro, text='Satisfação',
                                 font=(self.fonte_texto, 8))
        self.lb_satis.place(relx=0.5, rely=0.82)
        self.entrada_satis = CTkEntry(self.aba_cadastro)
        self.entrada_satis.place(
            relx=0.5, rely=0.9, relheight=0.1, relwidth=0.2)

    def botoes_2(self):
        # botao upload de imagem/video
        self.bt_upload = CTkButton(self.aba_envio, command=self.abrir,
                                   text='Enviar Imagem', fg_color='#ad8a0c',
                                   font=('arial black', 11, 'bold'))
        self.bt_upload.place(relx=0.7, rely=0.025, relheight=0.1, relwidth=0.1)

        # botao limpar
        self.bt_limpar = CTkButton(self.aba_envio, command=self.limpa_tela,
                                   text='Limpar', fg_color='#ad8a0c',
                                   font=('arial black', 11, 'bold'))
        self.bt_limpar.place(relx=0.9, rely=0.9, relheight=0.1, relwidth=0.1)

        # botao enviar
        self.bt_enviar = CTkButton(self.aba_envio, command=self.envia_msg,
                                   text='Enviar', fg_color='#ad8a0c',
                                   font=('arial black', 11, 'bold'))
        self.bt_enviar.place(relx=0.7, rely=0.9, relheight=0.1, relwidth=0.1)

        # botao filtar

        # botao parar

    def frame_1_pag_2(self):
        self.botoes_2()
        # Cria os widgets da aba de envio de mensagens
        # entrada da mensagem a ser enviada
        self.lb_msg = CTkLabel(self.aba_envio, text='Digite a mensagem a ser enviada: ',
                               font=(self.fonte_texto, 8))
        self.lb_msg.place(relx=0.01, rely=0.05)
        self.entrada_mensagem = CTkEntry(self.aba_envio)
        self.entrada_mensagem.place(
            relx=0.01, rely=0.15, relheight=0.7, relwidth=0.93)

    def frame_2_banco(self):
        # retorno do banco de dados
        # ID;Nome;E-mail;"Data de nascimento";CPF/CNPJ;Telefone;"Última compra";Pedidos;Satisfação
        self.saida = ttk.Treeview(self.aba_banco, height=1, columns=(
            'col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9'))
        self.saida.heading('#0', text='')
        self.saida.heading('#1', text='Id')
        self.saida.heading('#2', text='Nome')
        self.saida.heading('#3', text='E-mail')
        self.saida.heading('#4', text='Data de Nasc.')
        self.saida.heading('#5', text='CPF')
        self.saida.heading('#6', text='Whatsapp')
        self.saida.heading('#7', text='Última Compra')
        self.saida.heading('#8', text='Pedidos')
        self.saida.heading('#9', text='Satisfação')

        self.saida.column('#0', width=0)
        self.saida.column('#1', width=5)
        self.saida.column('#2', width=200)
        self.saida.column('#3', width=250)
        self.saida.column('#4', width=50)
        self.saida.column('#5', width=50)
        self.saida.column('#6', width=50)
        self.saida.column('#7', width=50)
        self.saida.column('#8', width=10)
        self.saida.column('#9', width=10)

        self.saida.place(rely=0.1, relx=0.01, relheight=0.85, relwidth=0.95)

        self.scroolLista = Scrollbar(self.aba_banco, orient='vertical')
        self.saida.configure(yscroll=self.scroolLista.set)
        self.scroolLista.place(rely=0.1, relx=0.96,
                               relheight=0.85, relwidth=0.04)

        self.saida.bind("<Delete>", self.abre_cliente)
        self.saida.bind("<Double-1>", self.abre_cliente)
        self.saida.bind("<Return>", self.abre_cliente)
        self.saida.bind("<Button-1>", self.ordena)

    def frame_2_retorno(self):
        # Cria a área de texto
        self.output2 = CTkTextbox(self.aba_retorno)
        self.output2.place(rely=0.1, relx=0.01,
                            relheight=0.85, relwidth=0.95)

    def menus(self):
        barraMenu = Menu(self)
        self.config(menu=barraMenu)
        abamenu = Menu(barraMenu)
        abamenu2 = Menu(barraMenu)

        def Quit(): self.root.destroy()

        barraMenu.add_cascade(label='Opções', menu=abamenu)
        barraMenu.add_cascade(label='Ajuda', menu=abamenu2)

        abamenu.add_command(label='Upload', command=self.Upload)
        abamenu.add_command(label='Donwload')
        abamenu.add_command(label='Sair', command=Quit)
        abamenu2.add_command(label='Modo de Usar')

if __name__ == '__main__':
    root = Application()
    root.mainloop()
