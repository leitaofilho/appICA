import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
import sys
import numpy as np


class SignalVisualizer:
    def __init__(self, config):
        """
        Inicializa o visualizador de sinais com base na configuração fornecida.

        :param config: Objeto de configuração contendo window_size, update_interval e n_components.
        """
        self.config = config
        self.window_size = self.config.window_size  # Acessa o valor de window_size do objeto config
        self.update_interval = self.config.update_interval  # Em milissegundos

        # Criação da interface PyQt
        self.app = QtWidgets.QApplication(sys.argv)

        # Criação da janela principal
        self.main_window = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(self.main_window)  # Layout principal vertical

        # Criação do widget de layout para gráficos
        self.graph_widget = pg.GraphicsLayoutWidget()
        self.main_layout.addWidget(self.graph_widget)  # Adiciona os gráficos ao layout principal

        self.main_window.setWindowTitle("Visualização de Sinais em Tempo Real")
        self.main_window.resize(1200, 800)

        # Inicializando gráfico único para o sinal misturado
        self.mixed_plot = self.graph_widget.addPlot(title="Sinal Misturado (Entrada)")
        self.mixed_plot.setYRange(-1, 1)
        self.mixed_plot.setXRange(0, self.window_size)
        self.mixed_curve = self.mixed_plot.plot(pen='g')  # Curva única para sinal misturado
        self.graph_widget.nextRow()

        # Inicializando gráficos separados para cada componente separado
        self.separated_plots = []
        self.separated_curves = []
        colors = ['c', 'm', 'y', 'r', 'b']  # Lista de cores para componentes separados
        for i in range(self.config.n_components):
            plot = self.graph_widget.addPlot(title=f"Sinal Separado {i + 1} (ICA)")
            plot.setYRange(-1, 1)
            plot.setXRange(0, self.window_size)
            color = colors[i % len(colors)]
            curve = plot.plot(pen=color)
            self.separated_plots.append(plot)
            self.separated_curves.append(curve)
            self.graph_widget.nextRow()

        # Área de exibição das métricas (com altura ajustada)
        self.metrics_text = QtWidgets.QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setFixedHeight(150)  # Define a altura fixa para a área de métricas
        self.main_layout.addWidget(self.metrics_text)  # Adiciona a área de texto ao layout principal

        self.main_window.show()  # Exibe a janela principal

    def update_plot(self, mixed_data: np.ndarray, separated_data: np.ndarray, metrics: dict):
        """
        Atualiza os gráficos com os dados mais recentes e exibe as métricas calculadas.

        :param mixed_data: Dados misturados (entrada).
        :param separated_data: Dados separados pelo ICA.
        :param metrics: Dicionário de métricas calculadas.
        """
        # Atualizar o gráfico do sinal misturado (uma única curva)
        if mixed_data is not None:
            self.mixed_curve.setData(mixed_data[:, 0])

        # Atualizar gráficos separados para cada componente do sinal separado
        if separated_data is not None:
            for i, curve in enumerate(self.separated_curves):
                if i < separated_data.shape[1]:  # Garante que não ultrapasse o número de componentes
                    curve.setData(separated_data[:, i])

        # Atualizar a exibição das métricas
        if metrics:
            metrics_text = "Métricas entre sinais separados:\n"
            for metric_name, value in metrics.items():
                metrics_text += f"{metric_name}: {value:.10f}\n"  # Aumenta a precisão para 10 casas decimais
            self.metrics_text.setText(metrics_text)

    def start_update_loop(self, update_callback):
        """Inicia o loop de atualização usando QTimer."""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(update_callback)
        self.timer.start(self.update_interval)  # Definido pelo valor de update_interval no config

        self.start()  # Inicia a aplicação

    def start(self):
        """Inicia a aplicação PyQt e gerencia a execução do loop de eventos."""
        sys.exit(self.app.exec_())
