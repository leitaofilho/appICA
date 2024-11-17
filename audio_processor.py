import logging
import queue
import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QTimer, QDateTime
from signal_analysis import SignalAnalysis


class AudioProcessor:
    def __init__(self, config, device_manager, signal_processor, visualizer):
        self.config = config
        self.device_manager = device_manager
        self.signal_processor = signal_processor
        self.visualizer = visualizer
        self.audio_queue = queue.Queue(maxsize=self.config.queue_size)
        self.frame_count = 0
        self.running = True
        self.stream = None
        self.all_mixed_data = []
        self.all_separated_data = []

    def start(self):
        """Inicia o processamento de áudio"""
        try:
            logging.info("Configurando o dispositivo de áudio...")
            self.device_manager.setup_device()
            logging.info("Dispositivo configurado. Iniciando stream de áudio.")

            # Inicia o stream de áudio
            self.stream = sd.InputStream(
                device=sd.default.device[0],
                channels=2,
                callback=self.audio_callback,
                samplerate=self.config.sample_rate,
                blocksize=self.config.buffer_size
            )
            self.stream.start()
            logging.info("Stream de áudio iniciado com sucesso.")

        except Exception as e:
            logging.error(f"Erro durante a execução do processador de áudio: {e}", exc_info=True)
            self._cleanup()

    def start_update_loop(self):
        """Inicia o loop de atualização de gráficos via QTimer (na thread principal)"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # Atualiza a cada 50ms (20 FPS)
        logging.info("Loop de atualização de gráficos iniciado com QTimer na thread principal.")

    def audio_callback(self, indata, frames, time_info, status):
        """Callback do stream de áudio"""
        if status:
            logging.warning(f"Status do áudio: {status}")
        if indata is not None and np.any(indata):
            signal_level = np.max(np.abs(indata))
            logging.info(f"Sinal capturado com nível: {signal_level:.6f}")

            if signal_level > 0:
                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(indata.copy())
                    self.frame_count += 1
                    if self.frame_count % 100 == 0:
                        logging.debug(f"Processados {self.frame_count} frames")
                else:
                    logging.warning("Fila de áudio está cheia")

    def update_plot(self):
        """Atualiza a visualização dos sinais"""
        try:
            if not self.audio_queue.empty():
                data = self.audio_queue.get_nowait()

                if data is not None:
                    logging.info("Dados capturados, processando...")
                    data = data[:self.config.window_size]

                    # Normalizar os dados
                    data = np.nan_to_num(data)
                    data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

                    # Aplicar o ICA
                    separated_data = self.signal_processor.process(data)

                    if separated_data is not None:
                        # Calcular métricas de análise entre sinais
                        distances = {
                            "Euclidean": SignalAnalysis.euclidean_distance(separated_data[:, 0], separated_data[:, 1]),
                            "Cross Correlation": SignalAnalysis.cross_correlation(separated_data[:, 0],
                                                                                  separated_data[:, 1]),
                            "Pearson": SignalAnalysis.pearson_distance(separated_data[:, 0], separated_data[:, 1]),
                            "MSE": SignalAnalysis.mean_squared_error(separated_data[:, 0], separated_data[:, 1]),
                            "Cosine": SignalAnalysis.cosine_distance(separated_data[:, 0], separated_data[:, 1]),
                            "Cross Entropy": SignalAnalysis.cross_entropy(separated_data[:, 0], separated_data[:, 1])
                        }

                        logging.info(f"Distâncias entre sinais separados: {distances}")

                        # Atualizar o gráfico com os dados processados e métricas
                        self.visualizer.update_plot(data, separated_data, distances)

                        # Armazenar os dados misturados e separados
                        self.all_mixed_data.append(data)
                        self.all_separated_data.append(separated_data)
                    else:
                        logging.warning("Nenhum dado separado foi retornado.")
            else:
                logging.warning("Fila de dados de áudio está vazia!")
        except Exception as e:
            logging.error(f"Erro na atualização do gráfico: {e}", exc_info=True)

    def stop_stream(self):
        """Para o stream de áudio de forma segura"""
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                logging.info("Stream de áudio parado com sucesso.")
                self.stream = None
        except Exception as e:
            logging.error(f"Erro ao parar o stream: {e}", exc_info=True)

    def _cleanup(self):
        """Limpeza robusta de recursos e salvamento de dados"""
        self.running = False
        logging.info("Limpando recursos e salvando dados...")

        # Parar o stream de áudio
        self.stop_stream()

        # Parar o timer de atualização (se estiver rodando)
        if hasattr(self, 'timer'):
            self.timer.stop()

        # Verificar e salvar os dados misturados e separados
        if self.all_mixed_data and self.all_separated_data:
            logging.info("Salvando resultados do processamento...")
            self.save_results()
        else:
            logging.warning("Nenhum dado capturado para salvar.")

        logging.info("Sistema finalizado com sucesso.")

    def save_results(self):
        """Salva os dados de áudio misturados e separados"""
        try:
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss")
            filename = self.visualizer.graphs_dir / f"ica_recording_{timestamp}.png"

            # Processar e concatenar os dados
            mixed_data = np.array(self.all_mixed_data).reshape(-1, 2)
            separated_data = np.array(self.all_separated_data).reshape(-1, 2)

            # Plotar e salvar os gráficos
            self.visualizer.save_graphs(mixed_data, separated_data, filename)

            logging.info(f"Resultados salvos em: {filename}")
        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {e}", exc_info=True)
