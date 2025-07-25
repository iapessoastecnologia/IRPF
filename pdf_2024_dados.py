import json
import os
import datetime
from typing import Dict, List, Any, Optional

from Webhook import Webhook
from config import WEBHOOK_URL, VALOR_TAMANHO_PADRAO




class PDF2024Dados:
    """
    Classe responsável por extrair e fornecer os dados do arquivo PDF (em formato JSON)
    que contém informações da declaração de 2024 (calendário 2023)
    """
    
    def __init__(self, origem: Any):
        self.dados = None
       
        if isinstance(origem, str):
            self.caminho_pdf = origem
            self.carregar_dados()
        else:
            print("ERRO: Tipo de origem inválido. Esperado str ou dict.")
            self.dados = {}
    
    def salvar_json_em_arquivo(dados: dict, caminho: str) -> None:
        """
        Salva um dicionário (JSON) em um arquivo local.

        Args:
            dados: O conteúdo do JSON.
            caminho: Caminho do arquivo de saída (ex: 'saida.json')
        """
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            print(f"JSON salvo com sucesso em: {caminho}")
        except Exception as e:
            print(f"Erro ao salvar o JSON: {e}")





    def carregar_dados(self) -> None:
        try:
            webhook = Webhook("https://linomenezes54.app.n8n.cloud/webhook/pdf")
            response = webhook.enviar_pdf(self.caminho_pdf)   
            self.dados = response
            print(f"Dados do PDF carregados com sucesso: {self.caminho_pdf}")
        except FileNotFoundError:
            print(f"ERRO: Arquivo não encontrado: {self.caminho_pdf}")
            self.dados = {}
        except json.JSONDecodeError:
            print(f"ERRO: Formato JSON inválido no arquivo: {self.caminho_pdf}")
            self.dados = {}
        except Exception as e:
            print(f"ERRO ao carregar dados do PDF: {e}")
            self.dados = {}
    
    def obter_declarante(self) -> Dict[str, Any]:
        """
        Retorna os dados do declarante
        
        Returns:
            Dicionário com informações do declarante
        """
        if not self.dados or 'declarante' not in self.dados:
            return {}
        return self.dados['declarante']
    
    def obter_rendimentos_tributaveis(self) -> List[Dict[str, Any]]:
        """
        Retorna os dados de rendimentos tributáveis
        
        Returns:
            Lista de rendimentos tributáveis
        """
        if not self.dados or 'rendimentos_tributaveis' not in self.dados:
            return []
        return self.dados['rendimentos_tributaveis']
    
    
    def obter_valores_rendimentos_pj(self) -> List[Dict[str, Any]]:
        if not self.dados or 'rendimentos_tributaveis_pj' not in self.dados:
            return []
        
        print("DADOS OBTIDOS DO PDF")
        
        return self.dados['rendimentos_tributaveis_pj']

    def obter_rendimentos_isentos(self) -> List[Dict[str, Any]]:
        if not self.dados or 'rendimentos_isentos_nao_tributaveis' not in self.dados:
            return []
        return self.dados['rendimentos_isentos_nao_tributaveis']
    
    def obter_rendimentos_exclusivos(self) -> List[Dict[str, Any]]:
        """
        Retorna os dados de rendimentos exclusivos de fonte
        
        Returns:
            Lista de rendimentos exclusivos
        """
        if not self.dados or 'rendimentos_exclusivos_fonte' not in self.dados:
            return []
        return self.dados['rendimentos_exclusivos_fonte']
    
    
    def obter_dividas_onus(self) -> List[Dict[str, Any]]:
        """
        Retorna os dados de dívidas e ônus
        
        Returns:
            Lista de dívidas e ônus
        """
        if not self.dados or 'dividas_onus' not in self.dados:
            return []
        return self.dados['dividas_onus']
    
    def obter_dependentes(self) -> List[Dict[str, Any]]:
        """
        Retorna os dados de dependentes, contendo apenas código e nome.
        
        Returns:
            Lista de dependentes com código e nome
        """
        if not self.dados or 'dependentes' not in self.dados:
            return []

        dependentes = self.dados['dependentes']
        resultado = [{'codigo': item['codigo'], 'nome': item['nome']} for item in dependentes]
        return resultado
    
    def obter_contas_bancarias(self) -> List[Dict[str, Any]]:
        """
        Retorna os dados de contas bancárias
        
        Returns:
            Lista de contas bancárias
        """
        if not self.dados or 'contas_bancarias' not in self.dados:
            return []
        return self.dados['contas_bancarias']
    

    def obter_bens_direitos(self) -> List[Dict[str, Any]]:
        if not self.dados or 'declaracao_bens_direitos' not in self.dados:
            return []
        return self.dados['declaracao_bens_direitos']



    def imprimir_cabecalho(self) -> None:
        """
        Imprime o cabeçalho com informações do declarante
        """
        declarante = self.obter_declarante()
        if not declarante:
            print("Nenhum dado de declarante encontrado.")
            return
        
        print("\n" + "=" * 60)
        print("DECLARAÇÃO DE IMPOSTO DE RENDA - ANO BASE 2023")
        print("=" * 60)
        print(f"Nome: {declarante.get('nome', 'N/A')}")
        print(f"CPF: {declarante.get('cpf', 'N/A')}")
        print(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 60)
    
    def imprimir_rendimentos_tributaveis(self) -> None:
        """
        Imprime os rendimentos tributáveis de forma organizada
        """
        rendimentos = self.obter_rendimentos_tributaveis()
        
        print("\n" + "=" * 60)
        print("RENDIMENTOS TRIBUTÁVEIS RECEBIDOS DE PJ E PF")
        print("=" * 60)
        
        if not rendimentos:
            print("Nenhum rendimento tributável encontrado.")
            return
        
        total_rendimentos = 0
        total_previdencia = 0
        total_irrf = 0
        
        for i, r in enumerate(rendimentos, 1):
            fonte = r.get('fonte', 'Fonte não informada')
            cnpj = r.get('cnpj', 'N/A')
            valor = r.get('valor', 0)
            previdencia = r.get('contrib_previdencia_oficial', 0)
            irrf = r.get('imposto_retido_fonte', 0)
            
            total_rendimentos += valor
            total_previdencia += previdencia
            total_irrf += irrf
            
            print(f"\nFonte #{i}: {fonte}")
            if cnpj != 'N/A':
                print(f"CNPJ: {cnpj}")
            print(f"Valor: R$ {valor:.2f}")
            print(f"Contribuição Previdenciária: R$ {previdencia:.2f}")
            print(f"Imposto de Renda Retido na Fonte: R$ {irrf:.2f}")
            
            # Se tiver informações de 13º salário
            if 'decimo_terceiro' in r:
                decimo = r['decimo_terceiro']
                valor_13 = decimo.get('valor', 0)
                irrf_13 = decimo.get('irrf', 0)
                if valor_13 > 0:
                    print(f"13º Salário: R$ {valor_13:.2f}")
                    print(f"IRRF sobre 13º: R$ {irrf_13:.2f}")
            
            print("-" * 45)
        
        print("\nTOTAIS:")
        print(f"Total de Rendimentos Tributáveis: R$ {total_rendimentos:.2f}")
        print(f"Total de Contribuição Previdenciária: R$ {total_previdencia:.2f}")
        print(f"Total de IRRF: R$ {total_irrf:.2f}")
    
    def imprimir_rendimentos_isentos(self) -> None:
        """
        Imprime os rendimentos isentos e não tributáveis
        """
        rendimentos = self.obter_rendimentos_isentos()
        
        print("\n" + "=" * 60)
        print("RENDIMENTOS ISENTOS E NÃO TRIBUTÁVEIS")
        print("=" * 60)
        
        if not rendimentos:
            print("Nenhum rendimento isento encontrado.")
            return
        
        total_isentos = 0
        
        for i, r in enumerate(rendimentos, 1):
            fonte = r.get('fonte', 'Fonte não informada')
            cnpj = r.get('cnpj', 'N/A')
            valor = r.get('valor', 0)
            
            total_isentos += valor
            
            print(f"\nFonte #{i}: {fonte}")
            if cnpj != 'N/A':
                print(f"CNPJ: {cnpj}")
            print(f"Valor: R$ {valor:.2f}")
            print("-" * 45)
        
        print(f"\nTotal de Rendimentos Isentos: R$ {total_isentos:.2f}")
    
    def imprimir_rendimentos_exclusivos(self) -> None:
        """
        Imprime os rendimentos sujeitos à tributação exclusiva/definitiva
        """
        rendimentos = self.obter_rendimentos_exclusivos()
        
        print("\n" + "=" * 60)
        print("RENDIMENTOS SUJEITOS À TRIBUTAÇÃO EXCLUSIVA/DEFINITIVA")
        print("=" * 60)
        
        if not rendimentos:
            print("Nenhum rendimento com tributação exclusiva encontrado.")
            return
        
        total_exclusivos = 0
        
        for i, r in enumerate(rendimentos, 1):
            tipo = r.get('tipo', 'Tipo não informado')
            fonte = r.get('fonte', 'Fonte não informada')
            cnpj = r.get('cnpj', 'N/A')
            valor = r.get('valor', 0)
            
            total_exclusivos += valor
            
            print(f"\nTipo #{i}: {tipo}")
            print(f"Fonte: {fonte}")
            if cnpj != 'N/A':
                print(f"CNPJ: {cnpj}")
            print(f"Valor: R$ {valor:.2f}")
            print("-" * 45)
        
        print(f"\nTotal de Rendimentos com Tributação Exclusiva: R$ {total_exclusivos:.2f}")
    
    def imprimir_bens_direitos(self) -> None:
        """
        Imprime os bens e direitos
        """
        bens = self.obter_bens_direitos()
        
        print("\n" + "=" * 60)
        print("BENS E DIREITOS")
        print("=" * 60)
        
        if not bens:
            print("Nenhum bem ou direito encontrado.")
            return
        
        total_2022 = 0
        total_2023 = 0
        
        for i, bem in enumerate(bens, 1):
            codigo = bem.get('codigo', 'N/A')
            descricao = bem.get('descricao', 'Sem descrição')
            valor_2022 = bem.get('situacao_31_12_2022', 0)
            valor_2023 = bem.get('situacao_31_12_2023', 0)
            pais = bem.get('pais', 'N/A')
            
            total_2022 += valor_2022
            total_2023 += valor_2023
            
            print(f"\nBem/Direito #{i}:")
            print(f"Código: {codigo}")
            print(f"Descrição: {descricao}")
            print(f"Valor em 31/12/2022: R$ {valor_2022:.2f}")
            print(f"Valor em 31/12/2023: R$ {valor_2023:.2f}")
            print(f"País: {pais}")
            
            # Campos adicionais específicos
            if 'cnpj' in bem:
                print(f"CNPJ: {bem['cnpj']}")
            if 'renavam' in bem:
                print(f"RENAVAM: {bem['renavam']}")
            if 'banco' in bem:
                print(f"Banco: {bem['banco']}")
            if 'agencia' in bem and bem['agencia']:
                print(f"Agência: {bem['agencia']}")
            if 'conta' in bem and bem['conta']:
                print(f"Conta: {bem['conta']}")
                
            print("-" * 45)
        
        print("\nTOTAIS:")
        print(f"Total de Bens/Direitos em 31/12/2022: R$ {total_2022:.2f}")
        print(f"Total de Bens/Direitos em 31/12/2023: R$ {total_2023:.2f}")
        variacao = total_2023 - total_2022
        if variacao > 0:
            print(f"Aumento Patrimonial: R$ {variacao:.2f}")
        elif variacao < 0:
            print(f"Diminuição Patrimonial: R$ {abs(variacao):.2f}")
        else:
            print("Sem variação patrimonial")
    
    def imprimir_dividas_onus(self) -> None:
        """
        Imprime as dívidas e ônus reais
        """
        dividas = self.obter_dividas_onus()
        
        print("\n" + "=" * 60)
        print("DÍVIDAS E ÔNUS REAIS")
        print("=" * 60)
        
        if not dividas:
            print("Nenhuma dívida ou ônus encontrado.")
            return
        
        total_2022 = 0
        total_2023 = 0
        
        for i, divida in enumerate(dividas, 1):
            descricao = divida.get('descricao', 'Sem descrição')
            valor_2022 = divida.get('situacao_31_12_2022', 0)
            valor_2023 = divida.get('situacao_31_12_2023', 0)
            
            total_2022 += valor_2022
            total_2023 += valor_2023
            
            print(f"\nDívida/Ônus #{i}:")
            print(f"Descrição: {descricao}")
            print(f"Valor em 31/12/2022: R$ {valor_2022:.2f}")
            print(f"Valor em 31/12/2023: R$ {valor_2023:.2f}")
            print("-" * 45)
        
        print("\nTOTAIS:")
        print(f"Total de Dívidas em 31/12/2022: R$ {total_2022:.2f}")
        print(f"Total de Dívidas em 31/12/2023: R$ {total_2023:.2f}")
    
    def imprimir_dependentes(self) -> None:
        """
        Imprime os dependentes
        """
        dependentes = self.obter_dependentes()
        
        print("\n" + "=" * 60)
        print("DEPENDENTES")
        print("=" * 60)
        
        if not dependentes:
            print("Nenhum dependente encontrado.")
            return
        
        for i, dep in enumerate(dependentes, 1):
            nome = dep.get('nome', 'Nome não informado')
            cpf = dep.get('cpf', 'CPF não informado')
            data_nasc = dep.get('data_nascimento', 'Data não informada')
            relacao = dep.get('relacao', 'Relação não informada')
            
            print(f"\nDependente #{i}:")
            print(f"Nome: {nome}")
            print(f"CPF: {cpf}")
            print(f"Data de Nascimento: {data_nasc}")
            print(f"Relação de Dependência: {relacao}")
            print("-" * 45)
    
    def imprimir_contas_bancarias(self) -> None:
        """
        Imprime as contas bancárias
        """
        contas = self.obter_contas_bancarias()
        
        print("\n" + "=" * 60)
        print("CONTAS BANCÁRIAS")
        print("=" * 60)
        
        if not contas:
            print("Nenhuma conta bancária encontrada.")
            return
        
        for i, conta in enumerate(contas, 1):
            tipo = conta.get('tipo', 'Tipo não informado')
            banco = conta.get('banco', 'Banco não informado')
            agencia = conta.get('agencia', '')
            numero = conta.get('conta', '')
            
            print(f"\nConta #{i}:")
            print(f"Tipo: {tipo}")
            print(f"Banco: {banco}")
            if agencia:
                print(f"Agência: {agencia}")
            if numero:
                print(f"Conta: {numero}")
            print("-" * 45)
    
    def imprimir_resumo_declaracao(self) -> None:
        """
        Imprime um resumo geral da declaração
        """
        # Dados gerais
        declarante = self.obter_declarante()
        rendimentos_trib = self.obter_rendimentos_tributaveis()
        rendimentos_isen = self.obter_rendimentos_isentos()
        rendimentos_excl = self.obter_rendimentos_exclusivos()
        bens = self.obter_bens_direitos()
        dividas = self.obter_dividas_onus()
        dependentes = self.obter_dependentes()
        
        # Cálculos de totais
        total_rendimentos_trib = sum(r.get('valor', 0) for r in rendimentos_trib)
        total_previdencia = sum(r.get('contrib_previdencia_oficial', 0) for r in rendimentos_trib)
        total_irrf = sum(r.get('imposto_retido_fonte', 0) for r in rendimentos_trib)
        
        total_isentos = sum(r.get('valor', 0) for r in rendimentos_isen)
        total_exclusivos = sum(r.get('valor', 0) for r in rendimentos_excl)
        
        total_bens_2022 = sum(b.get('situacao_31_12_2022', 0) for b in bens)
        total_bens_2023 = sum(b.get('situacao_31_12_2023', 0) for b in bens)
        
        total_dividas_2022 = sum(d.get('situacao_31_12_2022', 0) for d in dividas)
        total_dividas_2023 = sum(d.get('situacao_31_12_2023', 0) for d in dividas)
        
        patrimonio_2022 = total_bens_2022 - total_dividas_2022
        patrimonio_2023 = total_bens_2023 - total_dividas_2023
        variacao_patrimonial = patrimonio_2023 - patrimonio_2022
        
        print("\n" + "#" * 70)
        print("#" + " " * 25 + "RESUMO DA DECLARAÇÃO" + " " * 25 + "#")
        print("#" * 70)
        print(f"Declarante: {declarante.get('nome', 'N/A')}")
        print(f"CPF: {declarante.get('cpf', 'N/A')}")
        print("-" * 70)
        
        print("\n📊 RENDIMENTOS:")
        print(f"   Rendimentos Tributáveis: R$ {total_rendimentos_trib:.2f}")
        print(f"   Contribuição Previdenciária: R$ {total_previdencia:.2f}")
        print(f"   IRRF: R$ {total_irrf:.2f}")
        print(f"   Rendimentos Isentos/Não Tributáveis: R$ {total_isentos:.2f}")
        print(f"   Rendimentos com Tribut. Exclusiva: R$ {total_exclusivos:.2f}")
        
        print("\n💰 PATRIMÔNIO:")
        print(f"   Total de Bens/Direitos em 31/12/2022: R$ {total_bens_2022:.2f}")
        print(f"   Total de Bens/Direitos em 31/12/2023: R$ {total_bens_2023:.2f}")
        print(f"   Total de Dívidas em 31/12/2022: R$ {total_dividas_2022:.2f}")
        print(f"   Total de Dívidas em 31/12/2023: R$ {total_dividas_2023:.2f}")
        print(f"   Patrimônio Líquido em 31/12/2022: R$ {patrimonio_2022:.2f}")
        print(f"   Patrimônio Líquido em 31/12/2023: R$ {patrimonio_2023:.2f}")
        
        print(f"\n📈 VARIAÇÃO PATRIMONIAL: R$ {variacao_patrimonial:.2f}")
        if variacao_patrimonial > 0:
            print(f"   (Aumento de {(variacao_patrimonial/patrimonio_2022*100):.2f}% em relação a 2022)")
        elif variacao_patrimonial < 0:
            print(f"   (Diminuição de {(abs(variacao_patrimonial)/patrimonio_2022*100):.2f}% em relação a 2022)")
        
        print(f"\n👨‍👩‍👧‍👦 DEPENDENTES: {len(dependentes)}")
        print(f"💳 CONTAS BANCÁRIAS: {len(self.obter_contas_bancarias())}")
        
        print("\n" + "#" * 70)

