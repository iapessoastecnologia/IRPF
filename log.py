import os
import datetime
from typing import Dict, List, Any, Optional

class Logger:
    """
    Classe responsável por gerar e gerenciar logs das operações realizadas pelo sistema.
    Os logs são salvos em arquivos na pasta 'logs' com o nome do arquivo DBK processado.
    """
    
    def __init__(self, nome_dbk: str):
        """
        Inicializa o logger com o nome do arquivo DBK sendo processado.
        
        Args:
            nome_dbk: Nome do arquivo DBK sendo processado
        """
        self.nome_dbk = os.path.basename(nome_dbk)
        self.log_entries = []
        self.timestamp_inicio = datetime.datetime.now()
        
        # Criar pasta de logs se não existir
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Definir caminho do arquivo de log
        self.log_file = os.path.join(self.log_dir, f"{self.nome_dbk}.log")
        
        # Registrar início do processamento
        self.adicionar_entrada(f"Iniciando processamento do arquivo: {self.nome_dbk}")
        self.adicionar_entrada(f"Data/Hora: {self.timestamp_inicio.strftime('%d/%m/%Y %H:%M:%S')}")
        self.adicionar_entrada("="*80)
    
    def adicionar_entrada(self, mensagem: str, nivel: str = "INFO") -> None:
        """
        Adiciona uma entrada ao log.
        
        Args:
            mensagem: Mensagem a ser registrada no log
            nivel: Nível do log (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{timestamp}] [{nivel}] {mensagem}"
        self.log_entries.append(entrada)
        print(f"LOG: {entrada}")
    
    def adicionar_secao(self, titulo: str) -> None:
        """
        Adiciona uma seção ao log para melhor organização.
        
        Args:
            titulo: Título da seção
        """
        self.adicionar_entrada("\n" + "-"*80)
        self.adicionar_entrada(f"SEÇÃO: {titulo}")
        self.adicionar_entrada("-"*80)
    
    def registrar_dependente(self, nome: str, codigo: str, sucesso: bool) -> None:
        """
        Registra informações sobre o processamento de um dependente.
        
        Args:
            nome: Nome do dependente
            codigo: Código do dependente
            sucesso: Indica se o processamento foi bem-sucedido
        """
        status = "✅ Sucesso" if sucesso else "❌ Falha"
        self.adicionar_entrada(f"Dependente: {nome} (Código: {codigo}) - {status}", 
                              "SUCCESS" if sucesso else "ERROR")
    
    def registrar_rendimento_pj(self, nome: str, dados: Dict[str, Any], sucesso: bool) -> None:
        """
        Registra informações sobre o processamento de rendimentos de pessoa jurídica.
        
        Args:
            nome: Nome da fonte pagadora
            dados: Dados dos rendimentos
            sucesso: Indica se o processamento foi bem-sucedido
        """
        status = "✅ Sucesso" if sucesso else "❌ Falha"
        self.adicionar_entrada(f"Rendimento PJ: {nome} - {status}", 
                              "SUCCESS" if sucesso else "ERROR")
        
        if sucesso:
            for chave, valor in dados.items():
                self.adicionar_entrada(f"  - {chave}: {valor}")
    
    def registrar_bem_direito(self, indice: int, descricao: str, valor: str, sucesso: bool) -> None:
        """
        Registra informações sobre o processamento de um bem ou direito.
        
        Args:
            indice: Índice da linha no arquivo DBK
            descricao: Descrição do bem ou direito
            valor: Valor do bem ou direito
            sucesso: Indica se o processamento foi bem-sucedido
        """
        status = "✅ Sucesso" if sucesso else "❌ Falha"
        self.adicionar_entrada(f"Bem/Direito (linha {indice}): {descricao[:50]}... - Valor: {valor} - {status}", 
                              "SUCCESS" if sucesso else "ERROR")
    
    def finalizar(self, caminho_saida: str, sucesso_geral: bool) -> None:
        """
        Finaliza o log, registrando informações de conclusão e salvando o arquivo.
        
        Args:
            caminho_saida: Caminho do arquivo DBK modificado
            sucesso_geral: Indica se todo o processamento foi bem-sucedido
        """
        timestamp_fim = datetime.datetime.now()
        duracao = timestamp_fim - self.timestamp_inicio
        
        self.adicionar_secao("Conclusão")
        status_geral = "✅ Sucesso" if sucesso_geral else "❌ Falha"
        self.adicionar_entrada(f"Status geral: {status_geral}", "SUCCESS" if sucesso_geral else "ERROR")
        self.adicionar_entrada(f"Arquivo de saída: {caminho_saida}")
        self.adicionar_entrada(f"Duração do processamento: {duracao.total_seconds():.2f} segundos")
        self.adicionar_entrada(f"Data/Hora de conclusão: {timestamp_fim.strftime('%d/%m/%Y %H:%M:%S')}")
        self.adicionar_entrada("="*80)
        
        # Salvar o log em arquivo
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                for entrada in self.log_entries:
                    f.write(f"{entrada}\n")
            print(f"Log salvo em: {self.log_file}")
        except Exception as e:
            print(f"Erro ao salvar o log: {e}")
