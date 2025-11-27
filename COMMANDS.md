# Comandos Úteis - COMCURSANDO Django

## Ambiente de Desenvolvimento

### Ativar ambiente virtual
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Criar arquivo .env
```bash
# Copiar o template
cp .env.example .env

# Editar com suas configurações
# No Windows, use: notepad .env
# No Linux/Mac, use: nano .env
```

## Migrações do Banco de Dados

### Criar migrações
```bash
python manage.py makemigrations
```

### Aplicar migrações
```bash
python manage.py migrate
```

### Verificar status das migrações
```bash
python manage.py showmigrations
```

### Reverter migração
```bash
python manage.py migrate app_name migration_name
# Exemplo: python manage.py migrate users 0001
```

## Gerenciamento de Usuários

### Criar superusuário
```bash
python manage.py createsuperuser
```

### Mudar senha de usuário
```bash
python manage.py changepassword username
```

## Servidor de Desenvolvimento

### Rodar servidor
```bash
python manage.py runserver
# Acessa em: http://127.0.0.1:8000/

# Rodar em porta diferente
python manage.py runserver 8080

# Permitir acesso externo
python manage.py runserver 0.0.0.0:8000
```

### Rodar com auto-reload desabilitado
```bash
python manage.py runserver --noreload
```

## Django Shell

### Abrir shell interativo
```bash
python manage.py shell
```

### Executar script Python
```bash
python manage.py shell < scripts/migrate_data.py
```

## Testes

### Rodar todos os testes
```bash
python manage.py test
```

### Rodar testes de um app específico
```bash
python manage.py test apps.users
python manage.py test apps.concursos
python manage.py test apps.tickets
```

### Rodar com cobertura
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera relatório HTML
```

## Coleta de Arquivos Estáticos (Produção)

### Coletar arquivos estáticos
```bash
python manage.py collectstatic
```

### Coletar sem confirmação
```bash
python manage.py collectstatic --noinput
```

## Limpeza e Manutenção

### Limpar sessões expiradas
```bash
python manage.py clearsessions
```

### Verificar problemas no projeto
```bash
python manage.py check
```

### Verificar apenas apps específicos
```bash
python manage.py check apps.users
```

## Dados Iniciais

### Criar fixtures (backup de dados)
```bash
python manage.py dumpdata > backup.json
python manage.py dumpdata apps.users > users_backup.json
python manage.py dumpdata apps.demandas > demandas_backup.json
```

### Carregar fixtures
```bash
python manage.py loaddata backup.json
```

## Banco de Dados

### Abrir shell do banco de dados
```bash
python manage.py dbshell
```

### Resetar banco de dados (CUIDADO!)
```bash
# 1. Apagar banco
python manage.py flush

# 2. Ou deletar migrações e recriar
# Deletar arquivos em apps/*/migrations/*.py (exceto __init__.py)
python manage.py makemigrations
python manage.py migrate
```

## Migração de Dados do Sistema Antigo

### Executar script de migração
```bash
python manage.py shell < scripts/migrate_data.py
```

## Produção (Deployment)

### Variáveis de ambiente importantes
```bash
# .env de produção
DEBUG=False
SECRET_KEY=seu_secret_key_seguro_e_aleatorio
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DB_PASSWORD=senha_segura_do_banco
JWT_SECRET_KEY=chave_jwt_diferente_do_secret_key
```

### Gunicorn (Servidor WSGI)
```bash
# Instalar
pip install gunicorn

# Rodar
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Com workers
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx (Configuração exemplo)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /static/ {
        alias /caminho/para/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Supervisor (Gerenciador de processos)
```ini
[program:comcursando]
command=/caminho/para/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/caminho/para/COMCURSANDO-DJANGO
user=seu_usuario
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/comcursando.log
```

## Logs e Debug

### Ver logs do Django
```bash
# Se configurado para arquivo
tail -f logs/django.log

# Logs do Gunicorn
tail -f logs/gunicorn.log
```

### Debug com Django Debug Toolbar
```bash
pip install django-debug-toolbar
# Adicionar ao INSTALLED_APPS e MIDDLEWARE no settings.py
```

## Backup Completo

### Script de backup
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup do banco
python manage.py dumpdata > $BACKUP_DIR/data.json

# Backup dos arquivos de mídia (se houver)
cp -r media $BACKUP_DIR/

echo "Backup criado em: $BACKUP_DIR"
```

## URLs Importantes

- **Django Admin**: http://localhost:8000/admin/
- **API Login**: http://localhost:8000/api/auth/login
- **API Users**: http://localhost:8000/api/users/
- **API Demandas**: http://localhost:8000/api/demandas/
- **API Tickets**: http://localhost:8000/api/tickets/

## Dicas de Segurança

1. **Nunca commitar o arquivo .env**
2. **Usar SECRET_KEY diferente em produção**
3. **DEBUG=False em produção**
4. **HTTPS em produção (SSL/TLS)**
5. **Firewall configurado (apenas portas necessárias)**
6. **Backup regular do banco de dados**
7. **Logs de acesso e erro monitorados**
8. **Senhas fortes para usuários admin**
9. **JWT_SECRET_KEY diferente do SECRET_KEY**
10. **Rate limiting configurado (django-ratelimit)**
