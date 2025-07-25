# config.py
# Arquivo de configurau00e7u00e3o centralizada para o sistema IRPF-PROJETO-2025

# URL do webhook para processamento de PDFs
WEBHOOK_URL = "https://linomenezes54.app.n8n.cloud/webhook/pdf"


VALOR_TAMANHO_PADRAO = 13  

# Mapeamento de IDs para tipos de dados no arquivo DBK
DBK_ID_MAPPING = {
    "25": "Dependentes",
    "21": "Rendimentos PJ",
    "26": "Rendimentos PF",
    "27": "Bens e Direitos",
    "84": "Rendimentos Isentos Tipo 1",
    "86": "Rendimentos Isentos Tipo 2"
}

# Intervalos de posiu00e7u00f5es para cada tipo de dado no arquivo DBK
DBK_INTERVALOS = {
    "25": {  # Dependentes
        "codigo": (18, 20),
    },
    "21": {  # Rendimentos PJ
        "rendimentos": (87, 100),
        "previdencia": (100, 113),
        "impostoretido": (113, 126),
        "decimoterceiro": (126, 139),
        "irpfdecimoterceiro": (147, 160)
    },
    "27": {
        "valor": (544, 557)
    },
    #89 e 88 mesma categoria
    "88": {
        "valor": (103, 116)
    },
    "89": {
        "valor": (103, 116)
    }
    # Adicione outros intervalos conforme necessu00e1rio
}
 
# Configurau00e7u00f5es de arquivos
BACKUP_EXTENSION = ".bak"  # Extensão para arquivos de backup
NEW_FILE_PREFIX = "NEW-"   # Prefixo para novos arquivos gerados

# Configurau00e7u00f5es de timeout para requisiu00e7u00f5es HTTP
HTTP_TIMEOUT = 30  # segundos
