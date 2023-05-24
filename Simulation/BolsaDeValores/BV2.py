import pika
import time
import logging
import random
import threading

# Configura o logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class BolsaValores:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='bv')
        self.channel.queue_declare(queue='hb')
        self.channel.basic_consume(queue='bv', on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        print('BV waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def handle_message(self, ch, method, properties, body):
        pedido = body.decode('utf-8')
        if pedido:
            nome_acao, operacao, quantidade, relogio_hb = pedido.split(',')
            quantidade = int(quantidade)
            relogio_hb = float(relogio_hb)
            if relogio_hb > self.relogio + 2 or relogio_hb < self.relogio - 2:
                self.channel.basic_publish(exchange='', routing_key='hb', body="Sincronizar".encode('utf-8'))
            else:
                self.processar_pedido(nome_acao, operacao, quantidade)
                self.channel.basic_publish(exchange='', routing_key='hb', body=f"{nome_acao},{operacao},{quantidade}".encode('utf-8'))

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def processar_pedido(self, nome_acao, operacao, quantidade):
        # Implemente a lógica para processar o pedido aqui
        logging.info(f'Pedido de {operacao} de {quantidade} {nome_acao} processado com sucesso!')

if __name__ == "__main__":
    bv = BolsaValores()
    while True:
        bv.atualizar_relogio()
        time.sleep(10)
