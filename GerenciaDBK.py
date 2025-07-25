import json
import os
import shutil
from typing import Dict, List, Any, Optional, Tuple
import unicodedata

# Importa configurações centralizadas
from config import DBK_ID_MAPPING, DBK_INTERVALOS, BACKUP_EXTENSION


class GerenciaDBK:
    """
    Classe responsável por gerenciar o arquivo DBK (backup de 2025 referente ao calendário 2024).
    Implementa métodos para manipulação segura do arquivo DBK, permitindo busca e edição
    de informações específicas no arquivo.
    """
    
    def __init__(self, caminho_dbk: str):
        """
        Inicializa a classe com o caminho do arquivo DBK.
        
        Args:
            caminho_dbk: Caminho para o arquivo DBK que será modificado
        """
        self.caminho_dbk = caminho_dbk
        self.backup_path = f"{caminho_dbk}{BACKUP_EXTENSION}"
        self.nomeArquivo = os.path.basename(self.caminho_dbk)
        self.dados = None
        self.carregar_dados()

    def remover_espacos(self,texto):
        """
        Remove todos os espaços em branco (inclusive tabs e quebras de linha).
        """
        if not isinstance(texto, str):
            return texto
        return ''.join(texto.split())

        
    def normalizar(self,texto):
        """
        Remove todos os espaços e acentos para comparação robusta.
        """
        if not isinstance(texto, str):
            return texto

        # Remove espaços
        texto = ''.join(texto.split())

        # Remove acentos/cedilhas
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

        # Torna case-insensitive (opcional)
        return texto

    def carregar_dados(self) -> None:
        """
        Carrega os dados do arquivo DBK para a memória.
        
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            Exception: Para outros erros de leitura
        """
        try:
            with open(self.caminho_dbk, 'r', encoding='utf-8') as arquivo:
                self.dados = arquivo.read()  # Lê o conteúdo como texto puro
            print(f"Dados do DBK carregados com sucesso: {self.caminho_dbk}")
        except FileNotFoundError:
            print(f"Erro: Arquivo DBK não encontrado: {self.caminho_dbk}")
            raise
        except Exception as e:
            print(f"Erro ao carregar dados do DBK: {e}")
            raise


    def _fazer_backup(self) -> None:
        """
        Cria uma cópia de segurança do arquivo DBK antes de qualquer modificação.
        
        Raises:
            FileNotFoundError: Se o arquivo original não for encontrado
            PermissionError: Se não houver permissão para criar o backup
            Exception: Para outros erros durante a cópia
        """
        try:
            shutil.copy2(self.caminho_dbk, self.backup_path)
            print(f"Backup do arquivo DBK criado em: {self.backup_path}")
        except FileNotFoundError:
            print(f"Erro: Arquivo DBK original não encontrado: {self.caminho_dbk}")
            raise
        except PermissionError:
            print(f"Erro: Sem permissão para criar backup em: {self.backup_path}")
            raise
        except Exception as e:
            print(f"Erro ao criar backup do arquivo DBK: {e}")
            raise

    def procurarID(self, id: str, name: str) -> Dict[str, Any]:
        # Utiliza o mapeamento de IDs da configuração
       
        tipo_dado = id
        print(f"Procurando por {tipo_dado} com nome '{name}'...")

        
        linhas = self.dados.splitlines()
        for i, linha in enumerate(linhas):
            # Verifica se os dois primeiros caracteres da linha correspondem ao ID
            if len(linha) >= 2 and linha[0:2] == id:
                # Procura pelo nome nas próximas 7 linhas (incluindo a atual)
                for j in range(i, min(i + 7, len(linhas))):


                    if self.normalizar(self.remover_espacos(name)) in self.remover_espacos(linhas[j]):
                        print(f"O nome '{name}' foi encontrado na linha {j}")
                        # Utiliza os intervalos definidos na configuração
                        if id in DBK_INTERVALOS:
                            intervalos_nomeados = DBK_INTERVALOS[id]
                        else:
                            intervalos_nomeados = {}
                            print(f"Aviso: Não há intervalos definidos para o ID {id}")
                        return {
                            "indice_linha": j,
                            "posicoes": intervalos_nomeados
                        }
                    

        # Retorna valores padrão se não encontrar
        return {
            "indice_linha": None,
            "posicoes": {},
            "conteudo_linha": []
        }
        
    def procuraBensDBK(self) -> List[Dict[str, Any]]:
        """
        Percorre todas as linhas do arquivo DBK e encontra todas as linhas com ID '27' (Bens e Direitos).
        
        Returns:
            Lista de dicionários, cada um contendo o índice da linha e os intervalos definidos para o ID '27'
        """
        print("Procurando por todas as linhas de Bens e Direitos (ID 27)...")
        
        resultado = []
        linhas = self.dados.splitlines()
        
        # Obter os intervalos definidos para o ID '27'
        if "27" in DBK_INTERVALOS:
            intervalos_nomeados = DBK_INTERVALOS["27"]
        else:
            intervalos_nomeados = {}
            print("Aviso: Não há intervalos definidos para o ID 27")
        
        # Percorrer todas as linhas do arquivo
        for i, linha in enumerate(linhas):
            # Verificar se a linha começa com '27'
            if len(linha) >= 2 and linha[0:2] == "27":
                print(f"Encontrada linha com ID 27 no índice {i}: {linha[:30]}...")
                
                # Adicionar índice e intervalos ao resultado
                resultado.append({
                    "indice": i,
                    "intervalos": intervalos_nomeados,
                    "linha": linha
                })
        
        print(f"Total de {len(resultado)} linhas com ID 27 encontradas")
        return resultado
                     
    
    def editarID(self, indice_linha: int, substituicoes: Dict[str, str], intervalos_nomeados: Dict[str, Tuple[int, int]]) -> str:
        try:
            linhas = self.dados.splitlines()
            
            if indice_linha is None or indice_linha >= len(linhas):
                raise IndexError(f"Índice de linha inválido: {indice_linha}")
                
            linha_original = linhas[indice_linha]
            linha_lista = list(linha_original)
            
            print("LINHA:", linha_original)
            print("SUBSTITUIÇÕES:", substituicoes)

            for categoria, novo_valor in substituicoes.items():
                if categoria in intervalos_nomeados:
                    inicio, fim = intervalos_nomeados[categoria]

                    # Verifica se o valor novo tem o tamanho certo
                    tamanho_intervalo = fim - inicio
                    if len(novo_valor) != tamanho_intervalo:
                        print(f"⚠️ Valor para '{categoria}' deve ter {tamanho_intervalo} caracteres. Ajustando com zeros à esquerda.")
                        novo_valor = novo_valor.zfill(tamanho_intervalo)

                    if fim <= len(linha_lista):
                        linha_lista[inicio:fim] = list(novo_valor)
                    else:
                        print(f"❌ Índices {inicio}-{fim} fora dos limites da linha {indice_linha}")
                else:
                    print(f"❌ Categoria '{categoria}' não está nos intervalos nomeados.")

            linhas[indice_linha] = ''.join(linha_lista)
            self.dados = '\n'.join(linhas)
            return self.dados
            
        except Exception as e:
            print(f"Erro ao editar linha {indice_linha}: {e}")
            raise




        
       

    def dependentesSubs(self, name: str, dados: Dict[str, str]) -> bool:
        """
        Modifica a seção de dependentes no arquivo DBK.
        
        Args:
            name: Nome do dependente a ser modificado
            dados: Dicionário com os dados a serem substituídos
            
        Returns:
            True se a modificação foi bem-sucedida, False caso contrário
        """
        id = '25'  # ID para dependentes (definido em DBK_ID_MAPPING)
        try:
            print(f"Preparando para modificar seção de dependentes no DBK")
            response = self.procurarID(id, name)
            
            if response["indice_linha"] is None:
                print(f"⚠️ Dependente '{name}' não encontrado no arquivo DBK")
                return False
                
            self.editarID(response["indice_linha"], dados, response['posicoes'])
            return True
        except Exception as e:
            print(f"Erro ao modificar seção de dependentes: {e}")
            return False

    def rendimentosPJ(self, name: str, dados: Dict[str, str]) -> bool:
        """
        Modifica a seção de rendimentos PJ no arquivo DBK.
        
        Args:
            name: Nome da fonte pagadora a ser modificada
            dados: Dicionário com os dados a serem substituídos
            
        Returns:
            True se a modificação foi bem-sucedida, False caso contrário
        """
        id = '21'  # ID para rendimentos PJ (definido em DBK_ID_MAPPING)
        try:
            print(f"Preparando para modificar seção de rendimentos PJ no DBK")
            resposta = self.procurarID(id, name)
           
            indice = resposta["indice_linha"]
            intervalos = resposta["posicoes"]

            if indice is not None:
                self.editarID(indice, dados, intervalos)
                return True
            else:
                print(f"⚠️ Fonte pagadora '{name}' não encontrada no arquivo DBK")
                return False
        except Exception as e:
            print(f"Erro ao modificar seção de rendimentos PJ: {e}")
            return False

    
    def rendimentosPF(self, name: str, dados: Dict[str, str]) -> bool:
        """
        Modifica a seção de rendimentos PF no arquivo DBK.
        
        Args:
            name: Nome da fonte pagadora a ser modificada
            dados: Dicionário com os dados a serem substituídos
            
        Returns:
            True se a modificação foi bem-sucedida, False caso contrário
        """
        id = '26'  # ID para rendimentos PF (definido em DBK_ID_MAPPING)
        try:
            print(f"Preparando para modificar seção de rendimentos PF no DBK")
            resposta = self.procurarID(id, name)
            
            indice = resposta["indice_linha"]
            intervalos = resposta["posicoes"]
            
            if indice is not None:
                self.editarID(indice, dados, intervalos)
                return True
            else:
                print(f"⚠️ Fonte pagadora '{name}' não encontrada no arquivo DBK")
                return False
        except Exception as e:
            print(f"Erro ao modificar seção de rendimentos PF: {e}")
            return False

    def rendimentosIsentos(self, name: str, dados: Dict[str, str]) -> bool:
        
        """
        Modifica a seção de rendimentos isentos no arquivo DBK.
        
        Args:
            name: Nome do rendimento a ser modificado
            dados: Dicionário com os dados a serem substituídos
            
        Returns:
            True se a modificação foi bem-sucedida, False caso contrário
        """
        id = '84'  # ID para rendimentos isentos (definido em DBK_ID_MAPPING)
        try:
            print(f"Preparando para modificar seção de Rendimentos Isentos no DBK")
            response = self.procurarID(id, name)
            
            if response["indice_linha"] is None:
                # Tenta com o ID alternativo
                id = '86'  # ID alternativo para rendimentos isentos
                response = self.procurarID(id, name)
            
            if response["indice_linha"] is not None:
                self.editarID(response["indice_linha"], dados, response['posicoes'])
                return True
            else:
                print(f"⚠️ Rendimento isento '{name}' não encontrado no arquivo DBK")
                return False
        except Exception as e:
            print(f"Erro ao modificar seção de rendimentos isentos: {e}")
            return False


    def bensDireitos(self, nome: str, dados: Dict[str, str]) -> bool:
        id = '27'  # ID para bens e direitos (definido em DBK_ID_MAPPING)
        try:
            print(f"Preparando para modificar seção de Bens e Direitos no DBK")
            response = self.procurarID(id, nome)
            
            if response["indice_linha"] is None:
                print(f"⚠️ Bens e direitos '{nome}' não encontrado no arquivo DBK")
                return False
            
            # Obter a linha específica do DBK
            linhas = self.dados.splitlines()
            linha_atual = linhas[response["indice_linha"]]
            
            # Extrair o valor da posição específica (531-544)
            if len(linha_atual) >= 544:
                valor_a_copiar = linha_atual[531:544]
                print(f"Valor encontrado para copiar: {valor_a_copiar}")
                
                # Criar dicionário com o valor a ser atualizado
                dados_atualizacao = {
                    "valor": valor_a_copiar
                }
                
                # Atualizar a linha com o valor copiado
                self.editarID(response["indice_linha"], dados_atualizacao, response['posicoes'])
                return True
            else:
                print(f"⚠️ Linha muito curta para extrair o valor: {len(linha_atual)} caracteres")
                return False
        except Exception as e:
            print(f"Erro ao modificar seção de bens e direitos: {e}")
            return False