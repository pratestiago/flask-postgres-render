import subprocess
from datetime import datetime
import os

# ===== CONFIGURAÇÕES =====
PG_BIN = r"C:\Program Files\PostgreSQL\18\bin"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

BACKUP_DIR = r"C:\backups_postgres\cartola_fc"

# ========================

# Garante que a pasta existe
os.makedirs(BACKUP_DIR, exist_ok=True)

# Data para o nome do arquivo
data = datetime.now().strftime("%Y-%m-%d_%H-%M")

backup_file = os.path.join(
    BACKUP_DIR,
    f"{DB_NAME}_{data}.backup"
)

comando = [
    os.path.join(PG_BIN, "pg_dump.exe"),
    "-h", DB_HOST,
    "-p", DB_PORT,
    "-U", DB_USER,
    "-F", "c",      # formato custom (.backup)
    "-b",
    "-v",
    "-f", backup_file,
    DB_NAME
]

try:
    subprocess.run(comando, check=True)
    print(f"✅ Backup criado com sucesso: {backup_file}")
except subprocess.CalledProcessError as e:
    print("❌ Erro ao criar backup")
    print(e)
