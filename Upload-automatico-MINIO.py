import requests
import json
import os
from datetime import datetime
import s3fs

# ==================== CONFIGURAÇÕES ====================

# --- Configurações da Fonte de Dados ---
API_URL = "https://dummyjson.com/products"
DATA_PATH = "./data_raw/"

# --- Configurações do Data Lake (MinIO) ---
# SUBSTITUA PELOS SEUS DADOS DO MINIO
MINIO_ENDPOINT = "URL_DO_SEU_ENDPOINT_MINI"
# SUBSTITUA PELO NOME DO SEU BUCKET NO MINIO
MINIO_BUCKET_NAME = "NOME_DO_SEU_BUCKET" 
# SUBSTITUA PELA SUA ACCESS KEY DO MINIO
MINIO_ACCESS_KEY = "SUA_ACCESS_KEY"
# SUBSTITUA PELA SUA SECRET KEY DO MINIO
MINIO_SECRET_KEY = "SUA_SECRET_KEY"

# =======================================================

os.makedirs(DATA_PATH, exist_ok=True)

def coletar_e_salvar_localmente():
    """Coleta os dados da API e salva em um arquivo JSON local."""
    # (Esta função não muda)
    print("Iniciando a coleta de dados da API...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        dados = response.json()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"products_{timestamp}.json"
        filepath = os.path.join(DATA_PATH, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"[OK] Dados coletados e salvos localmente em: {filepath}")
        return filepath, filename
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição à API: {e}")
        return None, None

def enviar_para_minio(filepath, filename):
    """Envia um arquivo local para o bucket MinIO usando s3fs."""
    print(f"Iniciando o upload para o bucket MinIO '{MINIO_BUCKET_NAME}'...")
    
    try:
        # 1. Criar o sistema de arquivos S3 para o MinIO.
        # É necessário passar as credenciais e o endpoint.
        s3 = s3fs.S3FileSystem(
            key=MINIO_ACCESS_KEY,
            secret=MINIO_SECRET_KEY,
            client_kwargs={'endpoint_url': MINIO_ENDPOINT}
        )
        
        # 2. Caminho de destino no bucket
        caminho_remoto = f"{MINIO_BUCKET_NAME}/{filename}"
        
        # 3. Fazer o upload
        s3.put(filepath, caminho_remoto)
        
        print(f"[OK] Arquivo '{filename}' enviado com sucesso para '{caminho_remoto}'.")

    except Exception as e:
        print(f"[ERRO] Falha ao enviar para o MinIO: {e}")

if __name__ == "__main__":
    print("--- INICIANDO PROCESSO DE INGESTÃO (com MinIO) ---")
    
    filepath_local, filename_s3 = coletar_e_salvar_localmente()
    
    if filepath_local and filename_s3:
        enviar_para_minio(filepath_local, filename_s3)
        
    print("--- PROCESSO DE INGESTÃO FINALIZADO ---")