import sounddevice as sd
import logging
import numpy as np
import time


class AudioDeviceManager:
    def __init__(self, config):
        self.config = config
        self.device_info = None
        self.device_idx = None
        self.buffer = np.zeros((self.config.window_size, 2))

    def setup_device(self):
        """Configura o dispositivo de áudio"""
        devices = sd.query_devices()
        logging.info(f"Dispositivos disponíveis:\n{devices}")

        for i, device in enumerate(devices):
            if 'BlackHole' in device['name']:
                self.device_idx = i
                self.device_info = device
                logging.info(f"BlackHole encontrado no índice {i}")
                break

        if self.device_idx is None:
            raise RuntimeError("BlackHole não encontrado")

        sd.default.device = self.device_idx
        if not self._verify_audio_input():
            raise RuntimeError("Falha ao verificar entrada de áudio")

    def _verify_audio_input(self):
        """Verifica entrada de áudio de forma robusta"""
        try:
            with sd.InputStream(
                    device=self.device_idx,
                    channels=2,
                    blocksize=self.config.buffer_size,
                    samplerate=self.config.sample_rate
            ) as test_stream:
                for _ in range(3):  # Tenta várias leituras
                    data, _ = test_stream.read(self.config.buffer_size)
                    signal_level = np.max(np.abs(data))
                    logging.info(f"Teste de sinal: {signal_level:.6f}")
                    if signal_level >= self.config.min_signal_threshold:
                        return True
                    time.sleep(0.1)

            logging.warning("Sinal de áudio não detectado no teste inicial")
            return False
        except Exception as e:
            logging.error(f"Erro ao verificar entrada: {e}")
            return False
