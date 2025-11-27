# 🚀 GUIA COMPLETO DE DEPLOY - COMCURSANDO DJANGO

## 📋 SISTEMA REFATORADO
**Modelo de Negócio:** Plataforma para compra de provas de concursos

---

## ⚠️ BACKUP OBRIGATÓRIO

```bash
# Fazer backup do banco ANTES de tudo
mysqldump -u comcursando_user -p comcursando > backup_$(date +%Y%m%d_%H%M%S).sql

# Senha quando solicitado: Hermelio@123
```

---

## 🔄 PASSO 1: ATUALIZAR CÓDIGO

```bash
# Conectar no servidor via SSH
ssh root@72.61.36.89

# Ir para o diretório do projeto
cd /var/www/COMCURSANDO_DJANGO

# Fazer backup local do código atual
cp -r /var/www/COMCURSANDO_DJANGO /var/www/COMCURSANDO_DJANGO_backup_$(date +%Y%m%d)

# Baixar atualizações do GitHub
git pull origin main
```

---

## 🗑️ PASSO 2: LIMPAR BANCO DE DADOS

```bash
# Conectar no MySQL
mysql -u comcursando_user -p

# Senha: Hermelio@123

# Executar limpeza
USE comcursando;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE tickets_ticket;
TRUNCATE TABLE concursos_demanda;
SET FOREIGN_KEY_CHECKS = 1;
SELECT 'Banco limpo!' AS Status;
EXIT;
```

**OU** usar o script criado:

```bash
mysql -u comcursando_user -p comcursando < limpar_banco.sql
```

---

## 📦 PASSO 3: INSTALAR DEPENDÊNCIAS

```bash
# Ativar ambiente virtual
cd /var/www/COMCURSANDO_DJANGO
source venv/bin/activate

# Instalar/atualizar pacotes
pip install -r requirements.txt

# Verificar se Pillow foi instalado
pip list | grep -i pillow
# Deve mostrar: Pillow 10.1.0
```

---

## 🗂️ PASSO 4: CRIAR DIRETÓRIOS DE UPLOAD

```bash
# Criar diretório para uploads
mkdir -p /var/www/COMCURSANDO_DJANGO/media/provas

# Ajustar permissões
sudo chown -R www-data:www-data /var/www/COMCURSANDO_DJANGO/media/
sudo chmod -R 755 /var/www/COMCURSANDO_DJANGO/media/

# Verificar
ls -la /var/www/COMCURSANDO_DJANGO/ | grep media
```

---

## 🔄 PASSO 5: MIGRATIONS

```bash
# Ainda com venv ativo
cd /var/www/COMCURSANDO_DJANGO

# Criar migrations
python manage.py makemigrations

# Verificar o que será aplicado
python manage.py showmigrations

# Aplicar migrations
python manage.py migrate

# Verificar sucesso
python manage.py check
```

---

## 🎨 PASSO 6: COLETAR ARQUIVOS ESTÁTICOS

```bash
# Coletar CSS, JS, imagens
python manage.py collectstatic --noinput

# Ajustar permissões
sudo chown -R www-data:www-data /var/www/COMCURSANDO_DJANGO/staticfiles/
```

---

## 🌐 PASSO 7: CONFIGURAR NGINX PARA MEDIA

```bash
# Editar configuração do Nginx
sudo nano /etc/nginx/sites-available/comcursando

# Adicionar ANTES do bloco location / {
```

Adicione este bloco:

```nginx
    # Servir arquivos de upload (provas)
    location /media/ {
        alias /var/www/COMCURSANDO_DJANGO/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
```

A configuração completa deve ficar:

```nginx
server {
    listen 443 ssl http2;
    server_name comcursando.com.br www.comcursando.com.br;

    # SSL
    ssl_certificate /etc/letsencrypt/live/comcursando.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/comcursando.com.br/privkey.pem;

    # Arquivos estáticos
    location /static/ {
        alias /var/www/COMCURSANDO_DJANGO/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Arquivos de upload (NOVO)
    location /media/ {
        alias /var/www/COMCURSANDO_DJANGO/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy para Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Aumentar timeout para upload de arquivos
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # Tamanho máximo de upload (10MB)
        client_max_body_size 10M;
    }
}

server {
    listen 80;
    server_name comcursando.com.br www.comcursando.com.br;
    return 301 https://$server_name$request_uri;
}
```

```bash
# Testar configuração
sudo nginx -t

# Se OK, recarregar Nginx
sudo systemctl reload nginx
```

---

## 🔄 PASSO 8: REINICIAR SERVIÇOS

```bash
# Reiniciar Gunicorn
sudo systemctl restart comcursando

# Verificar status
sudo systemctl status comcursando

# Verificar logs se houver erro
sudo journalctl -u comcursando -n 50 --no-pager
```

---

## ✅ PASSO 9: VERIFICAÇÕES

```bash
# 1. Verificar se o site está acessível
curl -I https://comcursando.com.br

# 2. Verificar admin
curl -I https://comcursando.com.br/admin/

# 3. Verificar se media está sendo servido
touch /var/www/COMCURSANDO_DJANGO/media/test.txt
curl -I https://comcursando.com.br/media/test.txt
rm /var/www/COMCURSANDO_DJANGO/media/test.txt
```

---

## 🧪 PASSO 10: TESTE COMPLETO

### 1. Criar Demanda (Admin)
```
1. Acesse: https://comcursando.com.br/admin/
2. Login: seu_usuario
3. Vá em "Concursos" → "Adicionar Demanda"
4. Preencha:
   - Concurso: "TRF 1ª Região"
   - Número Edital: "001/2025"
   - Banca: "CESPE"
   - Data: 20/12/2025
   - Cargo: "Técnico Judiciário"
   - Autarquia: "Tribunal Regional Federal"
   - Valor Recompensa: 50.00
   - Status: "aberto"
5. Salvar
```

### 2. Enviar Prova (Cliente)
```
1. Acesse: https://comcursando.com.br
2. Veja o concurso listado
3. Clique em "Enviar Prova"
4. Preencha:
   - Nome: Seu Nome
   - Chave PIX: seu@email.com
   - Arquivo: Upload de PDF ou imagem
5. Enviar
6. Verificar mensagem de sucesso
```

### 3. Validar Prova (Admin)
```
1. Vá em "Envios de Prova"
2. Clique no envio
3. Clique em "Ver Prova" para visualizar
4. Opções:
   - ✓ Aprovar Prova
   - ✗ Recusar Prova
   - 💰 Marcar como Pago (após aprovar)
```

---

## 🔍 LOGS E TROUBLESHOOTING

```bash
# Logs do Django/Gunicorn
sudo journalctl -u comcursando -f

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs do MySQL
sudo tail -f /var/log/mysql/error.log

# Verificar processos
ps aux | grep gunicorn
ps aux | grep nginx

# Espaço em disco
df -h

# Permissões do diretório media
ls -la /var/www/COMCURSANDO_DJANGO/media/
```

---

## 📊 COMANDOS ÚTEIS

```bash
# Ver demandas no banco
mysql -u comcursando_user -p -e "SELECT id, concurso, status, valor_recompensa FROM comcursando.concursos_demanda;"

# Ver envios de prova
mysql -u comcursando_user -p -e "SELECT codigo_ticket, cliente_nome, cliente_pix, status FROM comcursando.tickets_ticket;"

# Resetar senha de admin Django
cd /var/www/COMCURSANDO_DJANGO
source venv/bin/activate
python manage.py changepassword seu_usuario
```

---

## ⚠️ PROBLEMAS COMUNS

### Erro: "No module named 'PIL'"
```bash
source venv/bin/activate
pip install Pillow==10.1.0
sudo systemctl restart comcursando
```

### Erro: Upload não funciona
```bash
# Verificar permissões
sudo chown -R www-data:www-data /var/www/COMCURSANDO_DJANGO/media/
sudo chmod -R 755 /var/www/COMCURSANDO_DJANGO/media/

# Verificar Nginx
sudo nginx -t
grep -n "client_max_body_size" /etc/nginx/sites-available/comcursando
```

### Erro: Migrations não aplicam
```bash
# Ver estado das migrations
python manage.py showmigrations

# Aplicar migration específica
python manage.py migrate tickets 0001

# Criar migrations fake (apenas se necessário)
python manage.py migrate --fake
```

### Site não carrega
```bash
# Verificar serviços
sudo systemctl status comcursando
sudo systemctl status nginx

# Reiniciar tudo
sudo systemctl restart comcursando
sudo systemctl restart nginx
```

---

## 📝 CHECKLIST FINAL

- [ ] Backup do banco criado
- [ ] Código atualizado (git pull)
- [ ] Banco limpo (TRUNCATE)
- [ ] Pillow instalado
- [ ] Diretório media/ criado
- [ ] Migrations aplicadas
- [ ] Static files coletados
- [ ] Nginx configurado para /media/
- [ ] Nginx client_max_body_size configurado
- [ ] Serviços reiniciados
- [ ] Teste de envio de prova funcionando
- [ ] Visualização de arquivo funcionando
- [ ] Admin de aprovação funcionando

---

## 🎯 FLUXO DO SISTEMA

```
1. ADMIN cria Demanda (concurso)
   ↓
2. CLIENTE vê concurso no home
   ↓
3. CLIENTE envia prova (PDF/imagem) + PIX
   ↓
4. Demanda fica "em_analise" (some do home)
   ↓
5. ADMIN vê prova no admin
   ↓
6a. Se VÁLIDA:
    - Admin aprova
    - Admin faz PIX
    - Admin marca como "pago"
    - Demanda fica "concluído"
    
6b. Se INVÁLIDA:
    - Admin recusa
    - Demanda volta para "aberto"
    - Aparece no home novamente
```

---

## 📞 SUPORTE

- Servidor: 72.61.36.89
- Domínio: comcursando.com.br
- Banco: MySQL (comcursando)
- Projeto: /var/www/COMCURSANDO_DJANGO
- Venv: /var/www/COMCURSANDO_DJANGO/venv

**Pronto para deploy! 🚀**
