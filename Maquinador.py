import hashlib
import os

from GerenciaDBK import GerenciaDBK
from pdf_2024_dados import PDF2024Dados
from config import NEW_FILE_PREFIX, WEBHOOK_URL

class Maquinador:
    """
    Classe responsável por coordenar a extração de dados de PDFs e a atualização de arquivos DBK.
    Funciona como um orquestrador entre as classes PDF2024Dados e GerenciaDBK.
    """

    def __init__(self):
        """
        Inicializa a classe Maquinador.
        """
        self.dbkObjeto = None
        self.pdfObjeto = None
    
    def calcular_sha256(self, caminho_arquivo: str) -> str:
        """
        Calcula o hash SHA-256 de um arquivo.
        
        Args:
            caminho_arquivo: Caminho para o arquivo a ser calculado o hash
            
        Returns:
            String contendo o hash SHA-256 ou mensagem de erro
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(caminho_arquivo, "rb") as f:
                for bloco in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(bloco)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return "Arquivo não encontrado."
        except Exception as e:
            return f"Erro ao calcular o hash: {e}"
    

    def vincular(self, arquivo: str) -> bool:
        """
        Vincula um arquivo DBK ao Maquinador, criando uma instância de GerenciaDBK.
        
        Args:
            arquivo: Caminho para o arquivo DBK
            
        Returns:
            True se o vínculo foi bem-sucedido, False caso contrário
        """
        try:
            self.dbkObjeto = GerenciaDBK(arquivo)
            return True
        except Exception as e:
            print(f"Erro ao vincular arquivo DBK: {e}")
            return False

    def vincularPDF(self, arquivo: str) -> bool:
        """
        Vincula um arquivo PDF ao Maquinador, criando uma instância de PDF2024Dados.
        
        Args:
            arquivo: Caminho para o arquivo PDF
            
        Returns:
            True se o vínculo foi bem-sucedido, False caso contrário
        """
        try:
            self.pdfObjeto = PDF2024Dados(arquivo)
            return True if self.pdfObjeto.dados else False
        except Exception as e:
            print(f"Erro ao vincular arquivo PDF: {e}")
            return False

    def salvarBKP(self, diretorio_saida: str = None) -> str:
        """
        Salva o arquivo DBK modificado com um novo nome.
        
        Args:
            diretorio_saida: Diretório onde o arquivo será salvo. Se None, usa o diretório atual.
            
        Returns:
            Caminho completo do arquivo salvo
        
        Raises:
            ValueError: Se não houver um objeto DBK vinculado
            Exception: Para erros durante a escrita do arquivo
        """
        if not self.dbkObjeto:
            raise ValueError("Nenhum arquivo DBK vinculado. Use vincular() primeiro.")
            
        try:
            nome_arquivo = self.dbkObjeto.nomeArquivo
            novo_nome = nome_arquivo.replace("2024-2023", "2025-2024").replace(".DEC", ".DBK")
            
            
            caminho_saida = f"{NEW_FILE_PREFIX}{novo_nome}"
            if diretorio_saida:
                os.makedirs(diretorio_saida, exist_ok=True)
                caminho_saida = os.path.join(diretorio_saida, f"{NEW_FILE_PREFIX}{novo_nome}")
                
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(self.dbkObjeto.dados)
                
            print(f"Arquivo DBK salvo com sucesso em: {caminho_saida}")
            return caminho_saida
        except Exception as e:
            print(f"Erro ao salvar arquivo DBK: {e}")
            raise