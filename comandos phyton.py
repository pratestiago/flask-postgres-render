--  comandos phyton

🪜 PASSO 1 — REMOVER a variável DATABASE_URL

No mesmo terminal onde você rodou o script:

Remove-Item Env:DATABASE_URL


🪜 PASSO 2 — Confirmar que ela foi removida
echo $env:DATABASE_URL

Resultado esperado:

(nada)


Se não aparecer nada → perfeito ✅


🪜 PASSO 3 — Rodar o script novamente
python copa_brasil_db.py



🔁 QUANDO QUISER VOLTAR PARA O NEON

No mesmo terminal:

$env:DATABASE_URL="postgresql://SEU_USUARIO:SUA_SENHA@SEU_HOST/SEU_BANCO"
python copa_brasil_db.py



--------------------------------


🪜 PASSO A PASSO — IMPORTAR NO BANCO LOCAL
1️⃣ Abrir o terminal no VS Code
2️⃣ Ativar o ambiente virtual
venv\Scripts\activate

3️⃣ Garantir que NÃO existe DATABASE_URL
echo $env:DATABASE_URL


Se aparecer algo, remover:

Remove-Item Env:DATABASE_URL

4️⃣ Rodar o script
python importar_rodada_csv.py