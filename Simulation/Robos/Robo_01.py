import time
import random
import socket
import logging
import sys

# Configura o logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Robo:
    def __init__(self, hb_host='localhost', hb_port=6000):
        self.hb_host = hb_host
        self.hb_port = hb_port

    def realizar_operacao(self):
        nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
        operacao = random.choice(['compra', 'venda'])
        quantidade = random.randint(1, 10)
        pedido = f"{nome_acao},{operacao},{quantidade}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.hb_host, self.hb_port))
            s.send(pedido.encode('utf-8'))
            resposta = s.recv(1024).decode('utf-8')
            if resposta == "Sincronizar":
                logging.info('Aguardando sincronização')
                time.sleep(2)  # Aguarda a sincronização
            else:
                print(f"Pedido de {operacao} de {quantidade} {nome_acao} realizado com sucesso")
                logging.info(f"Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!")

if __name__ == "__main__":
    robo = Robo()
    while True:
        robo.realizar_operacao()
        time.sleep(10)
