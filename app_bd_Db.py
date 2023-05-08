from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sqlite3

import os
import os.path
import requests

root = Tk()


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
        self.output2.insert(END, f"{texto}\n")

    def conecta_BD(self):
        """Este método conecta-se ao banco de dados SQLite."""
        baseBD = "clientes.db"
        self.imprime(f'Conectando ao Banco de Dados {baseBD}')
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
        if coluna_id:
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
            self.imprime(f'Upload do arquivo: {self.caminho} ')

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

    def envio_imagem(self,imagem):
        # clicar no ícone de anexo
        self.driver.find_element_by_xpath("//div[@title='Anexar']").click()

        # selecionar a opção de enviar imagem
        enviar_imagem = self.driver.find_element_by_xpath("//input[@accept='image/*,video/*']")
        enviar_imagem.send_keys(imagem) # substitua pelo caminho da imagem que deseja enviar

        # esperar 5 segundos para que a imagem seja carregada
        time.sleep(5)

        # clicar no botão de enviar
        #self.driver.find_element_by_xpath("//span[@data-icon='send']").click()

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

            except Exception as e:
                self.campo_pesquisa.send_keys(Keys.ESCAPE)
                with open(f'Saves\Enviados_{datetime.now().strftime("%d-%m")}.csv', 'a') as enviados:
                    enviados.writelines(
                        f'Erro - {e}; {pessoa[1]}; {datetime.now().strftime("%H %M %S")}\n')

            time.sleep(10)

        self.finaliza()

    def finaliza(self):
        with open(f'Saves\Enviados_{datetime.now().strftime("%d-%m")}.csv', 'a') as enviados:
            enviados.writelines(
                f'Finalizado às {datetime.now().strftime("%H %M %S")}')
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
            self.imprime(f'Iniciando ... imagem {self.caminho} será carregada.')
            acesso.iniciar(self.msg, clientes, self.caminho)
        else:
            self.imprime('Iniciando... ')
            acesso.iniciar(self.msg, clientes)
        self.desconecta_BD()


class Application(funcoesClientes, Up_Down):
    def __init__(self):
        """Construtor da classe que inicializa a aplicação, definindo os métodos
        de personalização da tela, criação de widgets e seleção de saída. 
        Por fim, inicia o loop principal da aplicação."""
        self.root = root
        self.personalisacao()
        self.tela()
        self.menus()
        self.frames_tela_cadastro()
        self.paginas()
        self.widgets_pag_1()
        self.widgets_pag_2()
        self.output_frame2_banco()
        self.output_frame2_retorno()
        self.montaTabelas()
        self.seleciona_saida()
        root.mainloop()

    def personalisacao(self, fundo_tela='#353578', fundo='#cecef5',
                       fundo_botao='#4545ff', borda='#6262d9', cor_texto_botao='#ffffff',
                       tamanho_texto=8, fonte_botao='arial black', fonte_texto='verdana', tipo='bold'):
        # Método que personaliza a aparência da tela da aplicação
        self.fundo_tela = fundo_tela
        self.fundo = fundo

        self.borda = borda
        self.fundo_botao = fundo_botao
        self.texto_botao = cor_texto_botao

        self.fonte_botao = fonte_botao
        self.fonte_texto = fonte_texto
        self.tamanho = tamanho_texto
        self.tipo = tipo

    def tela(self):
        # Define as características básicas da janela da aplicação
        self.root.title('Envio de Promoções')
        self.root.configure(background=self.fundo_tela)
        self.root.geometry('1280x1024')
        self.root.minsize(width=800, height=600)

    def frames_tela_cadastro(self):
        # Cria os frames que irao aparecer na tela
        self.frame_1 = Frame(self.root, bd=4, bg=self.fundo,
                             highlightbackground=self.borda, highlightthickness=3)
        self.frame_1.place(rely=0.02, relx=0.02, relheight=0.46, relwidth=0.96)

        self.frame_2 = Frame(self.root, bd=4, bg='#ffffff',
                             highlightbackground=self.borda, highlightthickness=3)
        self.frame_2.place(rely=0.5, relx=0.02, relheight=0.46, relwidth=0.96)

    def paginas(self):
        # cria as abas da aplicaçao
        self.abas = ttk.Notebook(self.frame_1)
        self.abas2 = ttk.Notebook(self.frame_2)

        # abas do frame_1 e suas configuraçoes
        self.aba_cadastro = Frame(self.abas)
        self.aba_envio = Frame(self.abas)

        self.aba_cadastro.configure(background=self.fundo)
        self.aba_envio.configure(background=self.fundo)

        self.abas.add(self.aba_cadastro, text='Cadastro')
        self.abas.add(self.aba_envio, text='Envio')

        # abas do frame_2 e suas configuraçoes
        self.aba_banco = Frame(self.abas2)
        self.aba_retorno_back = Frame(self.abas2)

        self.aba_banco.configure(background=self.fundo)
        self.aba_retorno_back.configure(background=self.fundo)

        self.abas2.add(self.aba_banco, text='Base de dados')
        self.abas2.add(self.aba_retorno_back, text='Retorno')

        self.abas.place(rely=0, relx=0, relheight=0.98, relwidth=1)
        self.abas2.place(rely=0, relx=0, relheight=0.98, relwidth=1)

    def botoes(self, aba):
        # botao limpar
        self.bt_limpar = Button(aba, text='Limpar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.limpa_tela)
        self.bt_limpar.place(rely=0.1, relx=0.2, relheight=0.1, relwidth=0.1)

        # botao buscar
        self.bt_buscar = Button(aba, text='Buscar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.buscar)
        self.bt_buscar.place(rely=0.1, relx=0.32, relheight=0.1, relwidth=0.1)

        # botao adicionar
        self.bt_add = Button(aba, text='Adicionar', bd=2, bg=self.fundo_botao,
                             fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.add_cliente)
        self.bt_add.place(rely=0.1, relx=0.52, relheight=0.1, relwidth=0.1)

        # botao editar
        self.bt_editar = Button(aba, text='Editar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.editar_cliente)
        self.bt_editar.place(rely=0.1, relx=0.72, relheight=0.1, relwidth=0.1)

        # botao apagar
        self.bt_apagar = Button(aba, text='Apagar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.deleta_cliente)
        self.bt_apagar.place(rely=0.1, relx=0.84, relheight=0.1, relwidth=0.1)

    def widgets_pag_1(self):
        # Cria os widgets da aba de cadastro
        self.botoes(self.aba_cadastro)
        # ____Entradas e labels do frame_1
        # ID
        self.lb_id = Label(self.aba_cadastro, text='ID',
                           bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_id.place(rely=0.025, relx=0.01)
        self.entrada_id = Entry(self.aba_cadastro)
        self.entrada_id.place(rely=0.1, relx=0.01,
                              relheight=0.1, relwidth=0.15)
        # Nome
        self.lb_nome = Label(self.aba_cadastro, text='Nome',
                             bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_nome.place(rely=0.225, relx=0.01)
        self.entrada_nome = Entry(self.aba_cadastro)
        self.entrada_nome.place(rely=0.3, relx=0.01,
                                relheight=0.1, relwidth=0.73)

        # E-mail
        self.lb_email = Label(
            self.aba_cadastro, text='E-mail', bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_email.place(rely=0.425, relx=0.01)
        self.entrada_email = Entry(self.aba_cadastro)
        self.entrada_email.place(
            rely=0.5, relx=0.01, relheight=0.1, relwidth=0.73)

        # Data Nascimento
        self.lb_nasc = Label(self.aba_cadastro, text='Data de Nascimento',
                             bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_nasc.place(rely=0.625, relx=0.01)
        self.entrada_nasc = Entry(self.aba_cadastro)
        self.entrada_nasc.place(
            rely=0.7, relx=0.01, relheight=0.1, relwidth=0.2)

        # CPF
        self.lb_cpf = Label(self.aba_cadastro, text='CPF',
                            bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_cpf.place(rely=0.625, relx=0.25)
        self.entrada_cpf = Entry(self.aba_cadastro)
        self.entrada_cpf.place(
            rely=0.7, relx=0.25, relheight=0.1, relwidth=0.2)

        # Whatsapp
        self.lb_wpp = Label(
            self.aba_cadastro, text='Contato WhatsApp', bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_wpp.place(rely=0.625, relx=0.5)
        self.entrada_wpp = Entry(self.aba_cadastro)
        self.entrada_wpp.place(
            rely=0.7, relx=0.5, relheight=0.1, relwidth=0.2)

        # Data da Ultima Compra
        self.lb_data = Label(self.aba_cadastro, text='Última Compra',
                             bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_data.place(rely=0.825, relx=0.01)
        self.entrada_data = Entry(self.aba_cadastro)
        self.entrada_data.place(
            rely=0.875, relx=0.01, relheight=0.1, relwidth=0.2)

        # Pedidos
        self.lb_pedidos = Label(self.aba_cadastro, text='Nº de Pedidos',
                                bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_pedidos.place(rely=0.825, relx=0.25)
        self.entrada_pedidos = Entry(self.aba_cadastro)
        self.entrada_pedidos.place(
            rely=0.875, relx=0.25, relheight=0.1, relwidth=0.2)

        # Satisfaçao
        self.lb_satis = Label(self.aba_cadastro, text='Satisfação',
                              bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_satis.place(rely=0.825, relx=0.5)
        self.entrada_satis = Entry(self.aba_cadastro)
        self.entrada_satis.place(
            rely=0.875, relx=0.5, relheight=0.1, relwidth=0.2)

    def widgets_pag_2(self):
        # Cria os widgets da aba de envio de mensagens
        # botao upload de imagem/video
        self.bt_upload = Button(self.aba_envio, text='Enviar Imagem', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.abrir)
        self.bt_upload.place(rely=0.05, relx=0.7, relheight=0.1, relwidth=0.1)

        # botao limpar
        self.bt_limpar = Button(self.aba_envio, text='Limpar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.limpa_tela)
        self.bt_limpar.place(rely=0.9, relx=0.9, relheight=0.1, relwidth=0.1)

        # botao enviar
        self.bt_enviar = Button(self.aba_envio, text='Enviar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.envia_msg)
        self.bt_enviar.place(rely=0.9, relx=0.7, relheight=0.1, relwidth=0.1)

        # botao filtar
        
        # botao parar

        # entrada da mensagem a ser enviada
        self.lb_msg = Label(self.aba_envio, text='Digite a mensagem a ser enviada: ',
                            bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_msg.place(rely=0.05, relx=0.01)
        self.entrada_mensagem = Entry(self.aba_envio)
        self.entrada_mensagem.place(
            rely=0.15, relx=0.01, relheight=0.7, relwidth=0.93)

    def output_frame2_banco(self):
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

        self.scroolLista = Scrollbar(self.frame_2, orient='vertical')
        self.saida.configure(yscroll=self.scroolLista.set)
        self.scroolLista.place(rely=0.1, relx=0.96,
                               relheight=0.85, relwidth=0.04)

        self.saida.bind("<Delete>", self.abre_cliente)
        self.saida.bind("<Double-1>", self.abre_cliente)
        self.saida.bind("<Return>", self.abre_cliente)
        self.saida.bind("<Button-1>", self.ordena)

    def output_frame2_retorno(self):
        # Cria a área de texto
        self.output2 = Text(self.aba_retorno_back, bg=self.fundo, wrap=WORD, font=(self.fonte_texto, self.tamanho),
                            yscrollcommand=self.scroolLista.set, spacing1=5)
        self.output2.place(rely=0.1, relx=0.01, relheight=0.85, relwidth=0.95)
        self.output2.configure(yscroll=self.scroolLista.set)

    def menus(self):
        barraMenu = Menu(self.root)
        self.root.config(menu=barraMenu)
        abamenu = Menu(barraMenu)
        abamenu2 = Menu(barraMenu)

        def Quit(): self.root.destroy()

        barraMenu.add_cascade(label='Opções', menu=abamenu)
        barraMenu.add_cascade(label='Ajuda', menu=abamenu2)

        abamenu.add_command(label='Upload', command=self.Upload)
        abamenu.add_command(label='Donwload')
        abamenu.add_command(label='Sair', command=Quit)
        abamenu2.add_command(label='Modo de Usar', command=Quit)


Application()
