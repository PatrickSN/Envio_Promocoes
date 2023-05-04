from tkinter import *
from tkinter import ttk
from tkinter import tix
import sqlite3

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Image
import webbrowser

import autoMsg

root = Tk()


class Relatorios:
    def print_cliente(self):
        webbrowser.open('relatório.pdf')

    def geraRelatclient(self):
        self.canvasRel = canvas.Canvas('relatório.pdf')

        self.idRel = self.entrada_id.get()
        self.nomeRel = self.entrada_nome.get()
        self.wppRel = self.entrada_wpp.get()
        self.cidadeRel = self.entrada_cidade.get()
        self.enderecoRel = self.entrada_endereco.get()

        self.canvasRel.setFont('Helvetica-Bold', 24)
        self.canvasRel.drawString(200, 790, 'Ficha do Cliente')

        self.canvasRel.setFont('Helvetica-Bold', 18)
        self.canvasRel.drawString(50, 700, 'Id: ')
        self.canvasRel.drawString(50, 670, 'Nome: ')
        self.canvasRel.drawString(50, 640, 'Whatsapp: ')
        self.canvasRel.drawString(50, 610, 'Endereço: ')
        self.canvasRel.drawString(50, 580, 'Cidade: ')

        self.canvasRel.setFont('Helvetica', 18)
        self.canvasRel.drawString(150, 700, self.idRel)
        self.canvasRel.drawString(150, 670, self.nomeRel)
        self.canvasRel.drawString(150, 640, self.wppRel)
        self.canvasRel.drawString(150, 610, self.enderecoRel)
        self.canvasRel.drawString(150, 580, self.cidadeRel)

        self.canvasRel.showPage()
        self.canvasRel.save()
        self.print_cliente()


class Funcoes:
    def limpa_tela(self):
        self.entrada_id.delete(0, END)
        self.entrada_nome.delete(0, END)
        self.entrada_email.delete(0, END)
        self.entrada_data1.delete(0, END)
        self.entrada_cpf.delete(0, END)
        self.entrada_wpp.delete(0, END)
        self.entrada_mensagem.delete(0, END)

    def conecta_BD(self):
        baseBD = "clientes.db"
        print(f'Conectando ao Banco de Dados {baseBD}')
        self.conexao = sqlite3.connect(baseBD)
        self.cursor = self.conexao.cursor()

    def desconecta_BD(self):
        self.conexao.close()
        print('Banco de Dados desconectado')

    def montaTabelas(self):
        self.conecta_BD()
        # Cria tabela
        comandsql = """
                CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nome_cliente CHAR(200) not null,
                email CHAR(100),
                primeira_comp CHAR(15),
                telefone INT(20) not null,
                cpf INT(11)
            );
            """
        self.cursor.execute(comandsql)
        self.conexao.commit()
        self.desconecta_BD()

    def seleciona_saida(self, comandsql=None):
        self.saida.delete(*self.saida.get_children())
        self.conecta_BD()
        comandsql = """
        SELECT id, nome_cliente, email, primeira_comp, cpf, telefone FROM clientes
        ORDER BY nome_cliente ASC;
        """
        lista = self.cursor.execute(comandsql)

        for i in lista:
            self.saida.insert("", END, values=i)

        self.desconecta_BD()

    def buscar(self):
        self.conecta_BD()
        self.saida.delete(*self.saida.get_children())

        self.entrada_nome.insert(END, '%')
        nome = self.entrada_nome.get()
        self.cursor.execute("""
            SELECT id, nome_cliente, email, primeira_comp, cpf, telefone FROM clientes
            WHERE nome_cliente LIKE '%s' ORDER BY nome_cliente ASC
        """ % nome
                            )
        buscanome = self.cursor.fetchall()
        for i in buscanome:
            self.saida.insert("", END, values=i)

        self.limpa_tela()
        self.desconecta_BD()

    


class funcoesClientes(Funcoes):
    def variaveis_clientes(self):
        self.id = self.entrada_id.get()
        self.nome = self.entrada_nome.get()
        self.email = self.entrada_email.get()
        self.pri_comp = self.entrada_data1.get()
        self.cpf = self.entrada_cpf.get()
        self.telefone = self.entrada_wpp.get()

    def add_cliente(self):
        self.variaveis_clientes()
        self.conecta_BD()
        if self.nome != '' and self.telefone != '':
            self.cursor.execute("""
                INSERT INTO clientes (nome_cliente, email, primeira_comp, cpf, telefone)
                VALUES (?, ?, ?, ?, ?)
            """, (self.nome, self.email, self.pri_comp, self.cpf, self.telefone)
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
            col1, col2, col3, col4, col5, col6 = self.saida.item(i, 'values')
            self.entrada_id.insert(END, col1)
            self.entrada_nome.insert(END, col2)
            self.entrada_email.insert(END, col3)
            self.entrada_data1.insert(END, col4)
            self.entrada_cpf.insert(END, col5)
            self.entrada_wpp.insert(END, col6)

    def deleta_cliente(self):
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
        self.variaveis_clientes()
        self.conecta_BD()
        self.cursor.execute("""
            UPDATE clientes SET nome_cliente = ?, email = ?, primeira_comp = ?, cpf = ?, telefone = ?
            WHERE id = ?
        """, (self.nome, self.email, self.pri_comp, self.cpf, self.telefone, self.id)
        )
        self.conexao.commit()
        self.desconecta_BD()
        self.seleciona_saida()
        self.limpa_tela()

    def envia_msg(self):
        self.msg = self.entrada_mensagem.get()
        self.conecta_BD()
        """acesso = autoMsg.AutoBot()
        acesso.acesso()
        acesso.iniciar(self.msg)"""
        self.saida.selection()
        for cliente in self.saida.selection():
            print(f"{self.msg}-{cliente}")


class Application(funcoesClientes, Relatorios):
    def __init__(self):
        self.root = root
        self.personalisacao()
        self.tela()
        self.menus()
        self.frames_tela_cadastro()
        self.paginas()
        self.widgets_pag_1()
        self.widgets_pag_2()
        self.output_frame_2()
        self.montaTabelas()
        self.seleciona_saida()
        root.mainloop()

    def personalisacao(self, fundo_tela='#353578', fundo='#cecef5',
                       fundo_botao='#4545ff', borda='#6262d9', cor_texto_botao='#ffffff',
                       tamanho_texto=8, fonte_botao='arial black', fonte_texto='verdana', tipo='bold'):
        # configura as cores e personalisaçoes da tela
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
        self.root.title('Envio de Promoções')
        self.root.configure(background=self.fundo_tela)
        self.root.geometry('1128x550')
        self.root.minsize(width=700, height=500)

    def frames_tela_cadastro(self):
        self.frame_1 = Frame(self.root, bd=4, bg=self.fundo,
                             highlightbackground=self.borda, highlightthickness=3)
        self.frame_1.place(rely=0.02, relx=0.02, relheight=0.46, relwidth=0.96)

        self.frame_2 = Frame(self.root, bd=4, bg='#ffffff',
                             highlightbackground=self.borda, highlightthickness=3)
        self.frame_2.place(rely=0.5, relx=0.02, relheight=0.46, relwidth=0.96)

    def paginas(self):
        self.abas = ttk.Notebook(self.frame_1)
        self.aba_cadastro = Frame(self.abas)
        self.aba_envio = Frame(self.abas)

        self.aba_cadastro.configure(background=self.fundo)
        self.aba_envio.configure(background=self.fundo)

        self.abas.add(self.aba_cadastro, text='Cadastro')
        self.abas.add(self.aba_envio, text='Envio')

        self.abas.place(rely=0, relx=0, relheight=0.98, relwidth=1)

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
        # Aba Cadastro
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
                                relheight=0.1, relwidth=0.93)

        # Whatsapp
        self.lb_wpp = Label(
            self.aba_cadastro, text='Contato WhatsApp', bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_wpp.place(rely=0.425, relx=0.01)
        self.entrada_wpp = Entry(self.aba_cadastro)
        self.entrada_wpp.place(rely=0.5, relx=0.01,
                               relheight=0.1, relwidth=0.2)

        # CPF
        self.lb_cpf = Label(self.aba_cadastro, text='CPF',
                              bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_cpf.place(rely=0.425, relx=0.25)
        self.entrada_cpf = Entry(self.aba_cadastro)
        self.entrada_cpf.place(
            rely=0.5, relx=0.25, relheight=0.1, relwidth=0.2)

        # Data da 1 Compra
        self.lb_data1 = Label(self.aba_cadastro, text='1º Compra',
                              bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_data1.place(rely=0.425, relx=0.5)
        self.entrada_data1 = Entry(self.aba_cadastro)
        self.entrada_data1.place(
            rely=0.5, relx=0.5, relheight=0.1, relwidth=0.2)

        # E-mail
        self.lb_email = Label(
            self.aba_cadastro, text='E-mail', bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_email.place(rely=0.625, relx=0.01)
        self.entrada_email = Entry(self.aba_cadastro)
        self.entrada_email.place(
            rely=0.7, relx=0.01, relheight=0.1, relwidth=0.73)

    def widgets_pag_2(self):
        # botao limpar
        self.bt_limpar = Button(self.aba_envio, text='Limpar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.limpa_tela)
        self.bt_limpar.place(rely=0.9, relx=0.9, relheight=0.1, relwidth=0.1)

        # botao enviar
        self.bt_enviar = Button(self.aba_envio, text='Enviar', bd=2, bg=self.fundo_botao,
                                fg=self.texto_botao, font=(self.fonte_botao, self.tamanho, self.tipo), command=self.envia_msg)
        self.bt_enviar.place(rely=0.9, relx=0.7, relheight=0.1, relwidth=0.1)

        #botao parar


        #entrada da mensagem a ser enviada
        self.lb_msg = Label(self.aba_envio, text='Digite a mensagem a ser enviada: ',
                           bg=self.fundo, font=(self.fonte_texto, self.tamanho))
        self.lb_msg.place(rely=0.05, relx=0.01)
        self.entrada_mensagem = Entry(self.aba_envio)
        self.entrada_mensagem.place(rely=0.15, relx=0.01, relheight=0.7, relwidth=0.93)

    def output_frame_2(self):
        self.saida = ttk.Treeview(self.frame_2, height=1, columns=(
            'col1', 'col2', 'col3', 'col4', 'col5'))
        self.saida.heading('#0', text='')
        self.saida.heading('#1', text='Id')
        self.saida.heading('#2', text='Nome')
        self.saida.heading('#3', text='WhatsApp')
        self.saida.heading('#4', text='Cidade')
        self.saida.heading('#5', text='Endereço')

        self.saida.column('#0', width=0)
        self.saida.column('#1', width=5)
        self.saida.column('#2', width=200)
        self.saida.column('#3', width=50)
        self.saida.column('#4', width=50)
        self.saida.column('#5', width=250)

        self.saida.place(rely=0.1, relx=0.01, relheight=0.85, relwidth=0.95)

        self.scroolLista = Scrollbar(self.frame_2, orient='vertical')
        self.saida.configure(yscroll=self.scroolLista.set)
        self.scroolLista.place(rely=0.1, relx=0.96,
                               relheight=0.85, relwidth=0.04)

        self.saida.bind("<Delete>", self.abre_cliente)
        self.saida.bind("<Double-1>", self.abre_cliente)
        self.saida.bind("<Return>", self.abre_cliente)

    def menus(self):
        barraMenu = Menu(self.root)
        self.root.config(menu=barraMenu)
        abamenu = Menu(barraMenu)
        abamenu2 = Menu(barraMenu)
        abamenu3 = Menu(barraMenu)

        def Quit(): self.root.destroy()

        barraMenu.add_cascade(label='Opções', menu=abamenu)
        barraMenu.add_cascade(label='Relatórios', menu=abamenu2)
        barraMenu.add_cascade(label='Ajuda', menu=abamenu3)

        abamenu.add_command(label='Sair', command=Quit)
        abamenu2.add_command(label='Ficha do Cliente',
                             command=self.geraRelatclient)


Application()
