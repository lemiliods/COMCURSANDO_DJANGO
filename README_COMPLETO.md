# COMCURSANDO - Sistema de Gerenciamento de Filas para Concursos Públicos

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![DRF](https://img.shields.io/badge/DRF-3.14-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema completo para gerenciamento de filas de atendimento vinculadas a concursos públicos, desenvolvido em Django com Django REST Framework.

</div>

---

## 📋 Sobre o Projeto

O **COMCURSANDO** é uma solução para organizar e gerenciar filas de atendimento relacionadas a processos de concursos públicos. O sistema permite:

- 📝 Cadastro e gerenciamento de concursos/editais (demandas)
- 🎫 Geração automática de tickets com código único
- 📊 Controle de fila por demanda
- 👥 Gestão de usuários administradores
- 🔐 Autenticação segura via JWT
- 📱 API RESTful completa
- 🎨 Painel administrativo Django

---

## 🚀 Tecnologias Utilizadas

### Backend
- **Django 5.0** - Framework web Python
- **Django REST Framework 3.14** - API REST
- **MySQL** - Banco de dados relacional
- **PyJWT 2.8** - Autenticação JWT
- **bcrypt 4.1** - Hash de senhas

### Ferramentas
- **django-cors-headers** - CORS para API
- **django-filter** - Filtros avançados
- **python-decouple** - Gerenciamento de variáveis de ambiente

---

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.11 ou superior
- MySQL 8.0 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

#### 1️⃣ Clone o repositório
```bash
git clone <url-do-repositorio>
cd COMCURSANDO-DJANGO
```

#### 2️⃣ Crie e ative o ambiente virtual
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### 3️⃣ Instale as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4️⃣ Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# Windows: notepad .env
# Linux/Mac: nano .env
```

Variáveis importantes:
```env
DB_NAME=comcursando
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306

SECRET_KEY=sua_chave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

JWT_SECRET_KEY=sua_chave_jwt
JWT_EXPIRATION_HOURS=8
```

#### 5️⃣ Crie o banco de dados
```bash
# No MySQL
CREATE DATABASE comcursando CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 6️⃣ Execute as migrações
```bash
python manage.py migrate
```

#### 7️⃣ Crie um superusuário
```bash
python manage.py createsuperuser
```

#### 8️⃣ Execute o servidor
```bash
python manage.py runserver
```

Acesse:
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

---

## 📁 Estrutura do Projeto

```
COMCURSANDO-DJANGO/
├── 📂 apps/
│   ├── 👤 users/              # Autenticação e usuários
│   │   ├── models.py         # Modelo AdminUser
│   │   ├── serializers.py    # Serializers de usuário
│   │   ├── views.py          # Views de login e listagem
│   │   ├── authentication.py # JWT customizado
│   │   └── admin.py          # Configuração do admin
│   │
│   ├── 📝 concursos/          # Gerenciamento de demandas
│   │   ├── models.py         # Modelo Demanda
│   │   ├── serializers.py    # Serializers de demanda
│   │   ├── views.py          # ViewSet CRUD
│   │   └── admin.py          # Configuração do admin
│   │
│   └── 🎫 tickets/            # Sistema de tickets
│       ├── models.py         # Modelo Ticket
│       ├── serializers.py    # Serializers de ticket
│       ├── views.py          # ViewSet CRUD + actions
│       └── admin.py          # Configuração do admin
│
├── ⚙️ config/                 # Configurações Django
│   ├── settings.py           # Settings principal
│   ├── urls.py               # URLs do projeto
│   └── wsgi.py               # WSGI config
│
├── 📜 scripts/                # Scripts utilitários
│   └── migrate_data.py       # Migração de dados antigos
│
├── 🌐 venv/                   # Ambiente virtual Python
│
├── 📄 requirements.txt        # Dependências Python
├── 📄 .env.example            # Template de variáveis
├── 📄 .gitignore              # Arquivos ignorados
├── 📄 README.md               # Este arquivo
├── 📄 API_DOCS.md             # Documentação da API
└── 📄 COMMANDS.md             # Comandos úteis
```

---

## 🎯 Funcionalidades Principais

### 🔐 Autenticação
- Login com JWT (JSON Web Token)
- Token com expiração configurável (padrão: 8 horas)
- Middleware de autenticação customizado
- Suporte a múltiplos usuários administradores

### 📊 Gerenciamento de Demandas
- CRUD completo de concursos/editais
- Filtros por status, banca, cargo
- Busca em múltiplos campos
- Ordenação customizável
- Status: `aberta`, `em_andamento`, `finalizada`, `cancelada`

### 🎫 Sistema de Tickets
- Geração automática de código único (formato: `DDMMYYnnnn`)
- Cálculo automático de posição na fila
- Vinculação com demandas
- Finalização de tickets
- Consulta de fila por demanda
- Status: `aguardando`, `em_atendimento`, `finalizado`, `cancelado`

### 🎨 Django Admin
- Interface administrativa completa
- Listagem customizada por modelo
- Filtros e busca configurados
- Readonly fields quando necessário
- Organização em fieldsets

---

## 🌐 API Endpoints

### Autenticação
| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/login` | Login (retorna JWT) | ❌ |

### Usuários
| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/users/` | Listar usuários | ✅ |
| GET | `/api/users/{id}/` | Detalhes de usuário | ✅ |

### Demandas
| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/demandas/` | Listar demandas | ✅ |
| POST | `/api/demandas/` | Criar demanda | ✅ |
| GET | `/api/demandas/{id}/` | Detalhes de demanda | ✅ |
| PUT | `/api/demandas/{id}/` | Atualizar demanda | ✅ |
| PATCH | `/api/demandas/{id}/` | Atualização parcial | ✅ |
| DELETE | `/api/demandas/{id}/` | Deletar demanda | ✅ |

### Tickets
| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/tickets/` | Listar tickets | ✅ |
| POST | `/api/tickets/` | Criar ticket | ✅ |
| GET | `/api/tickets/{id}/` | Detalhes de ticket | ✅ |
| PUT | `/api/tickets/{id}/` | Atualizar ticket | ✅ |
| PATCH | `/api/tickets/{id}/` | Atualização parcial | ✅ |
| DELETE | `/api/tickets/{id}/` | Deletar ticket | ✅ |
| POST | `/api/tickets/{id}/finalizar/` | Finalizar ticket | ✅ |
| GET | `/api/tickets/fila_demanda/` | Fila de uma demanda | ✅ |

📖 **Documentação completa**: Consulte [API_DOCS.md](API_DOCS.md)

---

## 🛠️ Comandos Úteis

### Desenvolvimento
```bash
# Rodar servidor
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell interativo
python manage.py shell
```

### Migração de Dados
```bash
# Migrar dados do sistema Node.js antigo
python manage.py shell < scripts/migrate_data.py
```

### Produção
```bash
# Coletar arquivos estáticos
python manage.py collectstatic

# Rodar com Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

📖 **Comandos completos**: Consulte [COMMANDS.md](COMMANDS.md)

---

## 📊 Modelo de Dados

### AdminUser (Usuários)
- username, email, password
- is_active, is_staff, is_superuser
- date_joined, last_login

### Demanda (Concursos)
- concurso, numero_edital, banca
- data_concurso, cargo, autarquia
- status, criado_em, atualizado_em

### Ticket (Fila)
- demanda (FK), cliente_nome
- codigo_ticket (único, auto-gerado)
- status, posicao_fila (calculada)
- criado_em, finalizado_em

---

## 🔒 Segurança

✅ Autenticação JWT com expiração  
✅ Senhas com bcrypt  
✅ CORS configurado  
✅ Variáveis de ambiente para secrets  
✅ CSRF protection  
✅ Django security middleware  

⚠️ **Importante em Produção:**
- `DEBUG=False`
- SECRET_KEY forte e aleatório
- HTTPS/SSL
- Firewall configurado
- Backup regular

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Desenvolvedor

Desenvolvido com ❤️ para gerenciamento eficiente de filas em processos de concursos públicos.

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a [documentação da API](API_DOCS.md)
2. Veja os [comandos úteis](COMMANDS.md)
3. Abra uma issue no repositório

---

**COMCURSANDO** - Organize suas filas com eficiência! 🚀
