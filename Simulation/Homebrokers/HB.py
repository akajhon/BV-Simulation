import time
import sys
import logging
import random
import socket
import threading

# Configura o logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class HomeBroker:
    def __init__(self, bv_host='localhost', bv_port=5000, host='localhost', port=6000):
        self.relogio = time.time()
        self.bv_host = bv_host
        self.bv_port = bv_port
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
            nome_acao, operacao, quantidade = pedido.split(',')
            quantidade = int(quantidade)
            pedido_bv = f"{nome_acao},{operacao},{quantidade},{self.relogio}"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.bv_host, self.bv_port))
                s.send(pedido_bv.encode('utf-8'))
                resposta = s.recv(1024).decode('utf-8')
                if resposta == "Sincronizar":
                    logging.info('Iniciando sincronização com BV')
                    self.sincronizar_relogio(s)
                else:
                    logging.info(f'Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao BV com Sucesso!')
                    cliente.send(resposta.encode('utf-8'))

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def sincronizar_relogio(self, socket_bv):
        self.relogio = time.time()
        socket_bv.send(str(self.relogio).encode('utf-8'))
        tempo_coordenador = float(socket_bv.recv(1024).decode('utf-8'))
        self.relogio = (self.relogio + tempo_coordenador) / 2

if __name__ == "__main__":
    hb = HomeBroker()
    while True:
        hb.atualizar_relogio()
        time.sleep(10)
