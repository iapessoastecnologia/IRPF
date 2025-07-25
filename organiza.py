import os
import shutil

# Caminho da pasta com os arquivos
pasta_origem = 'dados'  # substitua aqui

# Lista todos os arquivos na pasta
for arquivo in os.listdir(pasta_origem):
    caminho_arquivo = os.path.join(pasta_origem, arquivo)

    # Verifica se é arquivo
    if os.path.isfile(caminho_arquivo):
        # Pega prefixo antes do primeiro hífen
        prefixo = arquivo.split('-')[0]

        # Cria a pasta de destino
        pasta_destino = os.path.join(pasta_origem, prefixo)
        os.makedirs(pasta_destino, exist_ok=True)

        # Move o arquivo
        shutil.move(caminho_arquivo, os.path.join(pasta_destino, arquivo))

print("Arquivos organizados com sucesso!")
