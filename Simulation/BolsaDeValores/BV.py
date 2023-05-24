import time
import random
import socket
import threading
import logging
import sys
from collections import defaultdict

# Configura o logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class BolsaValores:
    def __init__(self, host='localhost', port=5000):
        self.relogio = time.time()
        self.acoes = defaultdict(lambda: {'quantidade': 100, 'valor': 50.0})
        self.host = host
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.port))
        self.servidor.listen(5)
        threading.Thread(target=self.escutar).start()

    def escutar(self):
        while True:
            cliente, endereco = self.servidor.accept()
            threading.Thread(target=self.handle_client,args=(cliente,)).start()

    def handle_client(self, cliente):
        pedido = cliente.recv(1024).decode('utf-8')
        if pedido:
            if pedido == "Sincronizar":
                cliente.send(str(self.relogio).encode('utf-8'))
            else:
                nome_acao, operacao, quantidade, tempo_pedido = pedido.split(',')
                quantidade = int(quantidade)
                tempo_pedido = float(tempo_pedido)
                if abs(tempo_pedido - self.relogio) > 1:
                    logging.info(f'Sincronizando relógio com HB: {cliente}')
                    cliente.send("Sincronizar".encode('utf-8'))
                else:
                    self.compra_venda_acao(nome_acao, operacao, quantidade)
                    cliente.send("Pedido realizado com sucesso".encode('utf-8'))
                    logging.info(f'Pedido de {operacao} de {quantidade} {nome_acao} aceito')

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def compra_venda_acao(self, nome_acao, operacao, quantidade):
        acao = self.acoes[nome_acao]
        if operacao == 'compra':
            acao['quantidade'] += quantidade
            acao['valor'] *= 1.01
        elif operacao == 'venda':
            acao['quantidade'] -= quantidade
            acao['valor'] *= 0.99

if __name__ == "__main__":
    bv = BolsaValores()
    while True:
        bv.atualizar_relogio()
        time.sleep(10)
