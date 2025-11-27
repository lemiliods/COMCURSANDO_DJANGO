# COMCURSANDO - Sistema de Gerenciamento de Filas para Concursos

Sistema Django para gerenciar demandas de concursos públicos e filas de atendimento.

## Configuração

1. Criar ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente:
```bash
copy .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Criar banco de dados MySQL:
```sql
CREATE DATABASE comcursando CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Executar migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Criar superusuário:
```bash
python manage.py createsuperuser
```

7. Rodar servidor:
```bash
python manage.py runserver
```

## Acesso

- **Admin Django**: http://localhost:8000/admin
- **API REST**: http://localhost:8000/api/
- **Documentação API**: http://localhost:8000/api/docs/

## Estrutura

```
COMCURSANDO-DJANGO/
├── config/              # Configurações do projeto
├── apps/
│   ├── users/          # Gestão de usuários admin
│   ├── concursos/      # Demandas de concursos
│   └── tickets/        # Sistema de filas
├── requirements.txt
└── manage.py
```

## Credenciais Padrão

Após migração, use o superusuário que você criar.
