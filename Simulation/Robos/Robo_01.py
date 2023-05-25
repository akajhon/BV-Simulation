import pika
import time
import random
import logging
import sys

# Cores
VERDE = '\033[92m'
VERMELHO = '\033[91m'
AMARELO = '\033[93m'
RESET = '\033[0m'

# Configura o logging para o 'pika'
pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# # Configura o logging para o 'HOMEBROKER'
# RB_logger = logging.getLogger('ROBO_01')
# RB_logger.setLevel(logging.INFO)

# # Cria um manipulador de log que escreve para stdout
# handler = logging.StreamHandler(sys.stdout)

# # Cria um formatador de log
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# # Adiciona o formatador ao manipulador
# handler.setFormatter(formatter)

# # Adiciona o manipulador ao logger
# RB_logger.addHandler(handler)

class Robo:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hb')

    def realizar_operacao(self):
        try:
            nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
            operacao = random.choice(['compra', 'venda'])
            quantidade = random.randint(1, 10)
            pedido = f"{nome_acao},{operacao},{quantidade},{self.relogio}"
            self.channel.basic_publish(exchange='', routing_key='hb', body=pedido.encode('utf-8'))
            resposta = self.channel.basic_get('hb')[2].decode('utf-8')
            if resposta == "Sincronizar":
                logging.info(AMARELO + 'Aguardando sincronização' + RESET)
                time.sleep(2)  # Aguarda a sincronização
            else:
                logging.info(VERDE + f"Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!" + RESET)
        except Exception as e:
            logging.info(VERMELHO + f'[!] ERRO NO ROBO: {e} [!]' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

if __name__ == "__main__":
    robo = Robo()
    while True:
        robo.realizar_operacao()
        robo.atualizar_relogio()
        time.sleep(10)