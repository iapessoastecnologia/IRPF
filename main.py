import json
import os
import sys
import argparse
from typing import Dict, List, Any, Optional, Tuple

from Maquinador import Maquinador
from Webhook import Webhook
from pdf_2024_dados import PDF2024Dados
from GerenciaDBK import GerenciaDBK
from log import Logger
import re
from config import WEBHOOK_URL

def normalizar_texto(texto):
    """
    Normaliza o texto removendo espaços extras e padronizando pontuação.
    Exemplo: " - " → "-", " : " → ":"
    """
    if not isinstance(texto, str):
        return texto

    # Remove espaços ao redor de -, :, , e substitui múltiplos espaços por um só
    #texto = re.sub(r'\s*-\s*', ' -', texto)
   # texto = re.sub(r'\s*:\s*', ':', texto)
    #texto = re.sub(r'\s*,\s*', ', ', texto)
    #texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def processar_declaracao(caminho_dbk: str, caminho_pdf: str) -> bool:
    """
    Processa uma declaração de imposto de renda, extraindo dados do PDF e atualizando o arquivo DBK.
    
    Args:
        caminho_dbk: Caminho para o arquivo DBK a ser modificado
        caminho_pdf: Caminho para o arquivo PDF contendo a declaração
        
    Returns:
        True se o processamento foi bem-sucedido, False caso contrário
    """
    try:
        # Inicializar o logger
        logger = Logger(os.path.basename(caminho_dbk))
        
        print(f"Iniciando processamento da declaração:\n  - DBK: {caminho_dbk}\n  - PDF: {caminho_pdf}")
        
        # Inicializa o maquinador e vincula os arquivos
        maqui = Maquinador()
        
        if not maqui.vincular(caminho_dbk):
            print("Erro ao vincular arquivo DBK")
            return False
            
        if not maqui.vincularPDF(caminho_pdf):
            print("Erro ao vincular arquivo PDF")
            return False
        
        print("\nArquivos vinculados com sucesso!\n")

        # Processa os dependentes
        logger.adicionar_secao("Processamento de Dependentes")
        print("\nProcessando dependentes...")
        dependentes = maqui.pdfObjeto.obter_dependentes()
        print(f"Encontrados {len(dependentes)} dependentes")
        logger.adicionar_entrada(f"Encontrados {len(dependentes)} dependentes")
        
        for dependente in dependentes:
            codigo = dependente["codigo"]
            nome = dependente["nome"]
            dados = {
                "codigo": codigo
            }
            print(f"  - Atualizando dependente: {nome} (código: {codigo})")
            sucesso = maqui.dbkObjeto.dependentesSubs(nome, dados)
            logger.registrar_dependente(nome, codigo, sucesso)
            
            if sucesso:
                print(f"    ✅ Dependente atualizado com sucesso")
            else:
                print(f"    ❌ Falha ao atualizar dependente")
        



        # Processa os rendimentos PJ
        logger.adicionar_secao("Processamento de Rendimentos PJ")
        print("\nProcessando rendimentos de pessoa jurídica...")
        rendimentos_pj = maqui.pdfObjeto.obter_valores_rendimentos_pj()
        print(f"Encontrados {len(rendimentos_pj)} fontes pagadoras PJ")
        logger.adicionar_entrada(f"Encontrados {len(rendimentos_pj)} fontes pagadoras PJ")
        
        for fonte in rendimentos_pj:
            nome = fonte["nome"]
            print(f"  - Atualizando rendimentos de: {nome}")
            sucesso = maqui.dbkObjeto.rendimentosPJ(nome, fonte["dados"])
            logger.registrar_rendimento_pj(nome, fonte["dados"], sucesso)
            
            if sucesso:
                print(f"    ✅ Rendimentos atualizados com sucesso")
            else:
                print(f"    ❌ Falha ao atualizar rendimentos")
        


        #O PDF RETORNA TUDO MUITO CONFUSO NÃO DA CERTO!

        # # Processa os rendimentos PF
        # print("\nProcessando rendimentos de pessoa física...")
        # rendimentos_pf = maqui.pdfObjeto.obter_rendimentos_tributaveis()
        # print(f"Encontrados {len(rendimentos_pf)} fontes pagadoras PF")
        
        # for fonte in rendimentos_pf:
        #     nome = fonte["nome"]
        #     print(f"  - Atualizando rendimentos de: {nome}")
        #     if maqui.dbkObjeto.rendimentosPF(nome, fonte["dados"]):
        #         print(f"    ✅ Rendimentos atualizados com sucesso")
        #     else:
        #         print(f"    ❌ Falha ao atualizar rendimentos")



        
    
        ##BENNNNNNNNNNNNNS
        logger.adicionar_secao("Processamento de Bens e Direitos")
        print("\nProcessando Bens e Direitos...")
        
        # Usar o novo método procuraBensDBK para encontrar todas as linhas com ID '27'
        bens = maqui.dbkObjeto.procuraBensDBK()
        logger.adicionar_entrada(f"Encontrados {len(bens)} bens e direitos no arquivo DBK")
        
        # Contador para acompanhar as atualizações bem-sucedidas
        atualizacoes_sucesso = 0
        
        # Processar cada bem encontrado
        for bem in bens:
            indice_linha = bem["indice"]
            intervalos = bem["intervalos"]
            linha = bem["linha"]
            
            # Obter uma descrição resumida do bem (primeiros 50 caracteres)
            descricao = linha[20:70].strip() if len(linha) > 70 else linha[20:].strip()
            
            print(f"  - Processando bem na linha {indice_linha}...")
            
            # Verificar se a linha é longa o suficiente
            if len(linha) >= 544:
                # Extrair o valor a ser copiado (531-544)
                valor_a_copiar = linha[531:544]
                print(f"    Valor encontrado: {valor_a_copiar}")
                
                # Criar dicionário com o valor a ser atualizado
                # Usamos a chave 'valor' que corresponde ao intervalo 544-557 no config.py
                dados_atualizacao = {
                    "valor": valor_a_copiar  # Copiamos o valor de 531-544 para o intervalo 544-557
                }
                
                # Atualizar a linha com o valor copiado
                sucesso = maqui.dbkObjeto.editarID(indice_linha, dados_atualizacao, intervalos)
                logger.registrar_bem_direito(indice_linha, descricao, valor_a_copiar, sucesso)
                
                if sucesso:
                    print(f"    ✅ Bem atualizado com sucesso")
                    atualizacoes_sucesso += 1
                else:
                    print(f"    ❌ Falha ao atualizar bem")
            else:
                print(f"    ⚠️ Linha muito curta para extrair valor: {len(linha)} caracteres")
                logger.adicionar_entrada(f"Linha {indice_linha} muito curta para extrair valor: {len(linha)} caracteres", "WARNING")
        
        if not bens:
            print("Nenhum bem ou direito encontrado no arquivo DBK")
            logger.adicionar_entrada("Nenhum bem ou direito encontrado no arquivo DBK", "WARNING")
        else:
            print(f"Total de {atualizacoes_sucesso} de {len(bens)} bens atualizados com sucesso")
            logger.adicionar_entrada(f"Total de {atualizacoes_sucesso} de {len(bens)} bens atualizados com sucesso", "SUCCESS")




 # Salva o arquivo DBK modificado
        logger.adicionar_secao("Salvamento do Arquivo DBK")
        print("\nSalvando arquivo DBK modificado...")
        caminho_salvo = maqui.salvarBKP("backup")
        print(f"Arquivo salvo em: {caminho_salvo}")
        logger.adicionar_entrada(f"Arquivo DBK salvo em: {caminho_salvo}", "SUCCESS")
        
        # Finalizar o log
        logger.finalizar(caminho_salvo, True)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o processamento da declaração: {e}")
        
        # Finalizar o log com erro
        if 'logger' in locals():
            logger.adicionar_entrada(f"Erro durante o processamento: {e}", "ERROR")
            logger.finalizar("N/A", False)
            
        return False


def main():
    # Caminho para a pasta 'consulta'
    pasta_consulta = 'dadosT'  # Substitua pelo caminho real
    # Lista para armazenar os pares (PDF, DBK)
    pares_pdf_dbk = []
    # Lista para armazenar pastas com erro
    pastas_com_erro = []

    # Verifica se deve usar processamento paralelo
    usar_paralelo = '--paralelo' in sys.argv
    max_workers = None
    
    # Processa argumentos de linha de comando de forma simples
    for i, arg in enumerate(sys.argv):
        if arg == '--pasta' and i + 1 < len(sys.argv):
            pasta_consulta = sys.argv[i + 1]
        elif arg == '--max-workers' and i + 1 < len(sys.argv):
            try:
                max_workers = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    print(f"Buscando declarações na pasta: {pasta_consulta}")
    
    # Percorre todas as subpastas da pasta 'consulta'
    for nome_pasta in os.listdir(pasta_consulta):
        # Monta corretamente o caminho até a pasta: dados/nome_pasta/DOC
        caminho_pasta = os.path.join(pasta_consulta, nome_pasta)
        
        if os.path.isdir(caminho_pasta):
            # Lista os arquivos da subpasta
            arquivos = os.listdir(caminho_pasta)

            # Filtra arquivos PDF e DBK
            pdfs = [f for f in arquivos if f.lower().endswith('.pdf')]
            dbks = [f for f in arquivos if f.lower().endswith('.dbk')]

            # Verifica se há exatamente um de cada
            if len(pdfs) == 1 and len(dbks) == 1:
                caminho_pdf = os.path.join(caminho_pasta, pdfs[0])
                caminho_dbk = os.path.join(caminho_pasta, dbks[0])
                pares_pdf_dbk.append((caminho_pdf, caminho_dbk))
            else:
                erro_info = {
                    'pasta': nome_pasta,
                    'caminho': caminho_pasta,
                    'num_pdfs': len(pdfs),
                    'num_dbks': len(dbks),
                    'pdfs': pdfs,
                    'dbks': dbks
                }
                pastas_com_erro.append(erro_info)
                print(f"[!] Erro na pasta: {caminho_pasta} - PDF: {len(pdfs)}, DBK: {len(dbks)}")

    # Verifica se encontrou algum par de arquivos
    if not pares_pdf_dbk:
        print(f"[!] Nenhum par de arquivos PDF/DBK encontrado na pasta {pasta_consulta}")
        sys.exit(1)
    
    print(f"Encontrados {len(pares_pdf_dbk)} pares de arquivos PDF/DBK para processamento")
    if pastas_com_erro:
        print(f"Encontradas {len(pastas_com_erro)} pastas com erro")
    
    # Decide entre processamento sequencial ou paralelo
    if usar_paralelo:
        # Importa o módulo de thread apenas se for usar processamento paralelo
        from thread import ProcessadorParalelo
        print(f"\n🚀 Iniciando processamento PARALELO com {max_workers or 'auto'} workers\n")
        processador = ProcessadorParalelo(max_workers=max_workers)
        resultados = processador.processar(
            pares_pdf_dbk,
            processar_declaracao,
            paralelo=True
        )
        
        # Verifica se todos os processamentos foram bem-sucedidos
        todos_sucesso = all(sucesso for _, sucesso in resultados)
        
        # Gera relatório final
        print("\n=== RELATÓRIO FINAL ===")
        print(f"Total de declarações processadas: {len(resultados)}")
        print(f"Declarações com sucesso: {sum(1 for _, sucesso in resultados if sucesso)}")
        print(f"Declarações com falha: {sum(1 for _, sucesso in resultados if not sucesso)}")
        
        if pastas_com_erro:
            print(f"\nPastas com erro ({len(pastas_com_erro)}):\n")
            for i, erro in enumerate(pastas_com_erro, 1):
                print(f"  {i}. {erro['pasta']}:")
                print(f"     - PDFs: {erro['num_pdfs']} {erro['pdfs'] if erro['pdfs'] else ''}")
                print(f"     - DBKs: {erro['num_dbks']} {erro['dbks'] if erro['dbks'] else ''}")
        print("====================")
        
        if todos_sucesso:
            print("\n✅ Todos os processamentos foram concluídos com sucesso!")
            return 0
        else:
            print("\n⚠️ Alguns processamentos falharam. Verifique os logs para mais detalhes.")
            return 1
    else:
        # Processamento sequencial original
        sucessos = 0
        falhas = 0
        
        for pdf, dbk in pares_pdf_dbk:
            sucesso = processar_declaracao(dbk, pdf)
            
            if sucesso:
                sucessos += 1
                print("\n✅ Processamento concluído com sucesso!")
            else:
                falhas += 1
                print("\n❌ Processamento falhou!")
                # Não interrompe mais o processamento em caso de falha
                # sys.exit(1)
        
        # Gera relatório final
        print("\n=== RELATÓRIO FINAL ===")
        print(f"Total de declarações processadas: {sucessos + falhas}")
        print(f"Declarações com sucesso: {sucessos}")
        print(f"Declarações com falha: {falhas}")
        
        if pastas_com_erro:
            print(f"\nPastas com erro ({len(pastas_com_erro)}):\n")
            for i, erro in enumerate(pastas_com_erro, 1):
                print(f"  {i}. {erro['pasta']}:")
                print(f"     - PDFs: {erro['num_pdfs']} {erro['pdfs'] if erro['pdfs'] else ''}")
                print(f"     - DBKs: {erro['num_dbks']} {erro['dbks'] if erro['dbks'] else ''}")
        print("====================")
        
        if falhas == 0:
            print("\n✅ Todos os processamentos foram concluídos com sucesso!")
            return 0
        else:
            print("\n⚠️ Alguns processamentos falharam. Verifique os logs para mais detalhes.")
            return 1

    
if __name__ == '__main__':
    sys.exit(main())
   

   

if __name__ == "__main__":
    main()