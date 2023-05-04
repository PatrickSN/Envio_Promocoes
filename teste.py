arquivo = input("Digite o nome do arquivo para a extração: ")
with open(arquivo, encoding='utf-8') as lista_Clientes:
    clientes = lista_Clientes.readlines()
    for cliente in clientes:
        cliente = cliente.split(";")
        print(cliente[0])
