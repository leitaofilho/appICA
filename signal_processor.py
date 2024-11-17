import numpy as np
from sklearn.decomposition import FastICA
import logging


class SignalProcessor:
    def __init__(self, config):
        # Aumente o número de iterações e ajuste a tolerância
        self.config = config
        self.ica = FastICA(n_components=self.config.n_components,
                           random_state=42,
                           max_iter=200,  # Aumente o número de iterações
                           tol=0.01)  # Aumente a tolerância
        self.all_mixed_data = []
        self.all_separated_data = []

    def enqueue_audio_data(self, data):
        # Enfileira os frames de áudio capturados
        self.audio_buffer.put(data)

        # Se o buffer não tiver atingido o tamanho ideal, aguarda mais dados
        if self.audio_buffer.qsize() < self.buffer_size:
            return None
        else:
            # Processa os dados somente quando o buffer está cheio
            buffer_data = []
            while not self.audio_buffer.empty():
                buffer_data.append(self.audio_buffer.get())
            return np.concatenate(buffer_data, axis=0)

    def process(self, buffer):
        """Aplica o ICA no buffer e separa os sinais"""
        try:
            separated = self.ica.fit_transform(buffer)
            self.all_separated_data.append(separated)
            logging.info(f"Processamento ICA realizado com sucesso.")
            return separated
        except Exception as e:
            logging.error(f"Erro no processamento do sinal: {e}", exc_info=True)
            return None

