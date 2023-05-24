import pika
import time
import random
import logging

# Configura o logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Robo:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hb')

    def realizar_operacao(self):
        nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
        operacao = random.choice(['compra', 'venda'])
        quantidade = random.randint(1, 10)
        pedido = f"{nome_acao},{operacao},{quantidade},{self.relogio}"
        self.channel.basic_publish(exchange='', routing_key='hb', body=pedido.encode('utf-8'))
        resposta = self.channel.basic_get('hb')[2].decode('utf-8')
        if resposta == "Sincronizar":
            logging.info('Aguardando sincronização')
            time.sleep(2)  # Aguarda a sincronização
        else:
            print(f"Pedido de {operacao} de {quantidade} {nome_acao} realizado com sucesso")
            logging.info(f"Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!")

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

if __name__ == "__main__":
    robo = Robo()
    while True:
        robo.realizar_operacao()
        robo.atualizar_relogio()
        time.sleep(10)
