import requests
import os
import json
from typing import Dict, Any, Optional

# Importa configurações centralizadas
from config import WEBHOOK_URL, HTTP_TIMEOUT

class Webhook:
    """
    Classe responsável por enviar arquivos PDF para um webhook externo e processar as respostas.
    """
    
    def __init__(self, url: str):
        """
        Inicializa a classe com a URL do webhook.
        
        Args:
            url: URL do webhook para onde os arquivos serão enviados
        """
        self.url = url

    def enviar_pdf(self, caminho_pdf: str) -> Dict[str, Any]:
        """
        Envia um arquivo PDF para o webhook e retorna a resposta.
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF a ser enviado
            
        Returns:
            Dicionário com a resposta do webhook ou mensagem de erro
        """
        try:
            # Verifica se o arquivo existe antes de tentar abri-lo
            if not os.path.exists(caminho_pdf):
                return {"erro": f"Arquivo PDF não encontrado: {caminho_pdf}"}
                
            with open(caminho_pdf, 'rb') as f:
                # Prepara o arquivo para envio
                nome_arquivo = os.path.basename(caminho_pdf)
                files = {'file': (nome_arquivo, f, 'application/pdf')}
                
                # Envia o arquivo para o webhook
                print(f"Enviando arquivo {nome_arquivo} para {self.url}...")
                resposta = requests.post(self.url, files=files, timeout=HTTP_TIMEOUT)
                resposta.raise_for_status()  # Levanta exceção para códigos de erro HTTP
                
                # Processa a resposta
                dados_json = resposta.json()
                print(f"Resposta recebida com sucesso: {len(str(dados_json))} caracteres")
                return dados_json
                
        except FileNotFoundError:
            return {"erro": f"Arquivo PDF não encontrado: {caminho_pdf}"}
        except requests.exceptions.Timeout:
            return {"erro": "Tempo limite excedido ao conectar ao webhook."}
        except requests.exceptions.RequestException as e:
            return {"erro": f"Erro na requisição: {str(e)}"}
        except ValueError:
            return {"erro": "Resposta não é um JSON válido."}
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}

    def salvar_resposta(self, dados: Dict[str, Any], caminho_saida: str = 'resposta.json') -> bool:
        """
        Salva a resposta do webhook em um arquivo JSON.
        
        Args:
            dados: Dicionário com os dados a serem salvos
            caminho_saida: Caminho onde o arquivo JSON será salvo
            
        Returns:
            True se o arquivo foi salvo com sucesso, False caso contrário
        """
        try:
            # Cria o diretório de saída se não existir
            diretorio = os.path.dirname(caminho_saida)
            if diretorio and not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
                
            # Salva os dados no arquivo JSON
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
                
            print(f"[✔] Resposta salva com sucesso em: {os.path.abspath(caminho_saida)}")
            return True
            
        except PermissionError:
            print(f"[✘] Erro de permissão ao salvar o arquivo: {caminho_saida}")
            return False
        except Exception as e:
            print(f"[✘] Erro ao salvar o arquivo: {e}")
            return False