import logging
import threading
from audio_config import AudioConfig
from audio_device_manager import AudioDeviceManager
from signal_processor import SignalProcessor
from signal_visualizer import SignalVisualizer
from audio_processor import AudioProcessor
from PyQt5.QtWidgets import QApplication

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ica_debug.log', mode='w')  # Logando em arquivo para debug
    ]
)


def main():
    try:
        # Inicializando a configuração do sistema de áudio
        config = AudioConfig()

        # Inicializando o gerenciador de dispositivos de áudio
        device_manager = AudioDeviceManager(config)

        # Inicializando o processador de sinais (ex: FastICA)
        signal_processor = SignalProcessor(config)

        # Inicializando o visualizador de sinais com PyQtGraph
        app = QApplication([])  # QApplication precisa estar na thread principal
        visualizer = SignalVisualizer(config)

        # Inicializando o processador geral que conecta tudo
        audio_processor = AudioProcessor(config, device_manager, signal_processor, visualizer)

        logging.info("Iniciando processamento de áudio...")

        # Iniciando a thread de processamento de áudio
        audio_processor_thread = threading.Thread(target=audio_processor.start)
        audio_processor_thread.start()

        # Iniciando a interface PyQtGraph e o loop de atualização de gráficos na thread principal
        visualizer.start_update_loop(audio_processor.update_plot)  # Corrigido

        # Executando a interface gráfica (PyQt) na thread principal
        app.exec_()

    except KeyboardInterrupt:
        logging.info("Programa interrompido pelo usuário.")
    except Exception as e:
        logging.error(f"Erro fatal: {e}", exc_info=True)
    finally:
        logging.info("Programa finalizado.")


if __name__ == "__main__":
    main()
