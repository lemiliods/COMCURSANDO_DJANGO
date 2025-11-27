# ✅ Checklist de Deploy - COMCURSANDO Django

## 📋 Pré-Deploy (Desenvolvimento Local - CONCLUÍDO)

- [x] Projeto Django criado
- [x] Apps configurados (users, concursos, tickets)
- [x] Modelos definidos
- [x] Migrações criadas
- [x] Serializers implementados
- [x] Views e ViewSets criados
- [x] URLs configuradas
- [x] Django Admin configurado
- [x] Autenticação JWT implementada
- [x] Documentação escrita
- [x] requirements.txt criado
- [x] .env.example criado
- [x] .gitignore configurado
- [x] Scripts de migração prontos

**Total de arquivos criados: 45**

---

## 🚀 Deploy no Servidor (A FAZER)

### 1. Preparação do Servidor

- [ ] Servidor Linux/Windows configurado
- [ ] Python 3.11+ instalado
- [ ] MySQL 8.0+ instalado e rodando
- [ ] Git instalado
- [ ] Nginx ou Apache instalado (para produção)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip mysql-server nginx git

# CentOS/RHEL
sudo yum install python311 python311-pip mysql-server nginx git
```

### 2. Clone do Projeto

- [ ] Clonar repositório no servidor

```bash
cd /var/www/  # ou caminho desejado
git clone <url-do-repositorio> COMCURSANDO-DJANGO
cd COMCURSANDO-DJANGO
```

### 3. Ambiente Virtual

- [ ] Criar ambiente virtual
- [ ] Ativar ambiente virtual
- [ ] Instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate  # Linux
# ou
.\venv\Scripts\Activate.ps1  # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuração do Banco de Dados

- [ ] Criar banco de dados MySQL
- [ ] Criar usuário MySQL
- [ ] Configurar permissões

```sql
-- No MySQL
CREATE DATABASE comcursando CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'comcursando_user'@'localhost' IDENTIFIED BY 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON comcursando.* TO 'comcursando_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Variáveis de Ambiente

- [ ] Copiar .env.example para .env
- [ ] Configurar DATABASE

```bash
cp .env.example .env
nano .env  # ou vim .env
```

**Configurar no .env:**
```env
# Database
DB_NAME=comcursando
DB_USER=comcursando_user
DB_PASSWORD=senha_forte_aqui
DB_HOST=localhost
DB_PORT=3306

# Django
SECRET_KEY=gerar_uma_chave_nova_e_segura_aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,IP_DO_SERVIDOR

# JWT
JWT_SECRET_KEY=outra_chave_diferente_do_secret_key
JWT_EXPIRATION_HOURS=8
```

**Gerar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Migrações do Banco

- [ ] Executar migrações
- [ ] Verificar tabelas criadas

```bash
python manage.py migrate
```

### 7. Criar Superusuário

- [ ] Criar admin inicial

```bash
python manage.py createsuperuser
# Seguir o prompt para criar username e senha
```

### 8. Migração de Dados (Opcional)

- [ ] Verificar se há dados no sistema antigo
- [ ] Executar script de migração

```bash
python manage.py shell < scripts/migrate_data.py
```

### 9. Arquivos Estáticos

- [ ] Configurar STATIC_ROOT no settings.py
- [ ] Coletar arquivos estáticos

```bash
# Adicionar ao settings.py:
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

python manage.py collectstatic --noinput
```

### 10. Teste Local no Servidor

- [ ] Testar servidor de desenvolvimento

```bash
python manage.py runserver 0.0.0.0:8000
# Acessar: http://IP_DO_SERVIDOR:8000/admin/
```

### 11. Gunicorn (WSGI Server)

- [ ] Instalar Gunicorn
- [ ] Criar arquivo de configuração
- [ ] Testar Gunicorn

```bash
pip install gunicorn

# Criar gunicorn_config.py
nano gunicorn_config.py
```

**gunicorn_config.py:**
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

**Testar:**
```bash
mkdir -p /var/log/gunicorn
gunicorn config.wsgi:application -c gunicorn_config.py
```

### 12. Systemd Service (Auto-start)

- [ ] Criar service file
- [ ] Habilitar e iniciar serviço

```bash
sudo nano /etc/systemd/system/comcursando.service
```

**/etc/systemd/system/comcursando.service:**
```ini
[Unit]
Description=COMCURSANDO Gunicorn Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/COMCURSANDO-DJANGO
Environment="PATH=/var/www/COMCURSANDO-DJANGO/venv/bin"
ExecStart=/var/www/COMCURSANDO-DJANGO/venv/bin/gunicorn config.wsgi:application -c gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Ativar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable comcursando
sudo systemctl start comcursando
sudo systemctl status comcursando
```

### 13. Nginx (Reverse Proxy)

- [ ] Configurar Nginx
- [ ] Testar configuração
- [ ] Reiniciar Nginx

```bash
sudo nano /etc/nginx/sites-available/comcursando
```

**/etc/nginx/sites-available/comcursando:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/COMCURSANDO-DJANGO/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

**Ativar:**
```bash
sudo ln -s /etc/nginx/sites-available/comcursando /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 14. SSL/HTTPS (Certbot)

- [ ] Instalar Certbot
- [ ] Obter certificado SSL
- [ ] Configurar auto-renovação

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### 15. Firewall

- [ ] Configurar firewall
- [ ] Permitir apenas portas necessárias

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
sudo ufw status
```

### 16. Testes de Produção

- [ ] Testar login no admin
- [ ] Testar API endpoints
- [ ] Verificar logs

```bash
# Testar admin
curl https://seu-dominio.com/admin/

# Testar API
curl -X POST https://seu-dominio.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua_senha"}'

# Ver logs
sudo journalctl -u comcursando -f
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/error.log
```

### 17. Monitoramento e Backup

- [ ] Configurar backup automático do banco
- [ ] Configurar logs rotate
- [ ] Instalar ferramenta de monitoramento (opcional)

**Backup automático (cron):**
```bash
sudo crontab -e

# Adicionar linha para backup diário às 2am:
0 2 * * * /var/www/COMCURSANDO-DJANGO/backup.sh
```

**backup.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/comcursando"
mkdir -p $BACKUP_DIR

# Backup do banco
mysqldump -u comcursando_user -p'senha' comcursando > $BACKUP_DIR/db_$DATE.sql

# Backup dos dados Django
source /var/www/COMCURSANDO-DJANGO/venv/bin/activate
cd /var/www/COMCURSANDO-DJANGO
python manage.py dumpdata > $BACKUP_DIR/data_$DATE.json

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
```

### 18. Segurança Extra

- [ ] Desabilitar root SSH login
- [ ] Configurar fail2ban
- [ ] Atualizar pacotes do sistema
- [ ] Configurar rate limiting (opcional)

```bash
# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Rate limiting com django-ratelimit (opcional)
pip install django-ratelimit
# Adicionar ao requirements.txt
```

---

## 📊 Checklist Pós-Deploy

- [ ] Site acessível via HTTPS
- [ ] Django Admin funcionando
- [ ] API retornando respostas corretas
- [ ] SSL válido (cadeado verde)
- [ ] Logs sem erros críticos
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Documentação atualizada com URLs de produção

---

## 🔧 Manutenção

### Atualizar código
```bash
cd /var/www/COMCURSANDO-DJANGO
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart comcursando
```

### Ver logs em tempo real
```bash
sudo journalctl -u comcursando -f
```

### Reiniciar serviço
```bash
sudo systemctl restart comcursando
```

### Verificar status
```bash
sudo systemctl status comcursando
sudo systemctl status nginx
```

---

## 📞 Suporte

- [README_COMPLETO.md](README_COMPLETO.md) - Documentação completa
- [API_DOCS.md](API_DOCS.md) - Endpoints da API
- [COMMANDS.md](COMMANDS.md) - Comandos úteis
- [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Resumo da migração

---

## ✅ Status Atual

**Desenvolvimento Local:** ✅ COMPLETO (45 arquivos criados)  
**Deploy em Servidor:** ⏳ PENDENTE

Siga o checklist acima quando estiver pronto para fazer o deploy! 🚀
