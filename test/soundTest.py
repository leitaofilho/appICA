import sounddevice as sd
import numpy as np
import time


def test_audio_routing():
    """Testa se o BlackHole está recebendo áudio"""
    # Encontrar BlackHole
    devices = sd.query_devices()
    blackhole_idx = None
    for i, device in enumerate(devices):
        if 'BlackHole' in device['name']:
            blackhole_idx = i
            break

    if blackhole_idx is None:
        print("BlackHole não encontrado!")
        return

    print(f"\nTestando entrada de áudio no BlackHole (índice {blackhole_idx})")
    print("Reproduza algum áudio no seu sistema...")

    try:
        # Configurar stream de teste
        with sd.InputStream(device=blackhole_idx,
                            channels=2,
                            samplerate=44100,
                            blocksize=4410) as stream:

            # Testar por 10 segundos
            for i in range(10):
                data, _ = stream.read(4410)
                max_level = np.max(np.abs(data))
                print(f"Nível de áudio: {max_level:.4f}", end='\r')

                if max_level > 0.01:
                    print(f"\nÁudio detectado! Nível: {max_level:.4f}")
                    return True

                time.sleep(1)

            print("\nNenhum áudio detectado após 10 segundos")
            return False

    except Exception as e:
        print(f"\nErro ao testar áudio: {e}")
        return False


if __name__ == "__main__":
    print("Teste de Roteamento de Áudio")
    print("-" * 50)
    print("\nVerificando configuração do sistema...")

    # Mostrar dispositivos
    print("\nDispositivos de áudio disponíveis:")
    print(sd.query_devices())

    # Testar roteamento
    success = test_audio_routing()

    if success:
        print("\nConfigurações de áudio OK!")
        print("Pode executar o programa ICA agora")
    else:
        print("\nProblemas na configuração de áudio!")
        print("Por favor, verifique:")
        print("1. BlackHole 2ch está selecionado como saída do sistema?")
        print("2. Multi-Output Device está configurado corretamente?")
        print("3. Há áudio sendo reproduzido no sistema?")