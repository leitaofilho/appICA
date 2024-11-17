# audio_config.py

from dataclasses import dataclass


@dataclass
class AudioConfig:
    window_size: int = 2048
    sample_rate: int = 44100
    n_components: int = 2
    buffer_size: int = 4410
    update_interval: int = 50
    min_signal_threshold: float = 0.01
    queue_size: int = 100
    monitoring_interval: float = 1.0  # Intervalo de monitoramento em segundos
