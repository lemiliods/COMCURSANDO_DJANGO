# API COMCURSANDO - Documentação

## Endpoints Disponíveis

### Autenticação

#### POST /api/auth/login
Realiza login e retorna token JWT.

**Request Body:**
```json
{
  "username": "admin",
  "password": "sua_senha"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "date_joined": "2025-11-27T16:00:00",
    "last_login": null
  }
}
```

### Usuários

#### GET /api/users/
Lista todos os usuários administradores ativos.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `username` - Filtrar por username
- `is_active` - Filtrar por status (true/false)
- `search` - Buscar em username, email, nome
- `ordering` - Ordenar (date_joined, username, -date_joined, -username)

### Demandas (Concursos)

#### GET /api/demandas/
Lista todas as demandas.

#### POST /api/demandas/
Cria nova demanda.

**Request Body:**
```json
{
  "concurso": "TJ-SP",
  "numero_edital": "001/2025",
  "banca": "VUNESP",
  "data_concurso": "2025-12-15",
  "cargo": "Escrevente Técnico Judiciário",
  "autarquia": "Tribunal de Justiça de São Paulo",
  "status": "aberta"
}
```

#### GET /api/demandas/{id}/
Detalhes de uma demanda específica.

#### PUT /api/demandas/{id}/
Atualiza demanda completa.

#### PATCH /api/demandas/{id}/
Atualização parcial de demanda.

#### DELETE /api/demandas/{id}/
Remove demanda.

**Query Parameters:**
- `status` - Filtrar por status (aberta, em_andamento, finalizada, cancelada)
- `banca` - Filtrar por banca
- `cargo` - Filtrar por cargo
- `search` - Buscar em concurso, edital, cargo, autarquia
- `ordering` - Ordenar (criado_em, data_concurso, concurso)

### Tickets

#### GET /api/tickets/
Lista todos os tickets.

#### POST /api/tickets/
Cria novo ticket (código gerado automaticamente).

**Request Body:**
```json
{
  "demanda": 1,
  "cliente_nome": "João Silva"
}
```

**Response:**
```json
{
  "id": 1,
  "demanda": 1,
  "demanda_detalhes": {
    "id": 1,
    "concurso": "TJ-SP",
    "numero_edital": "001/2025",
    ...
  },
  "cliente_nome": "João Silva",
  "codigo_ticket": "2711250001",
  "status": "aguardando",
  "posicao_fila": 1,
  "criado_em": "2025-11-27T16:30:00",
  "finalizado_em": null
}
```

#### GET /api/tickets/{id}/
Detalhes de um ticket.

#### PUT /api/tickets/{id}/
Atualiza ticket.

#### PATCH /api/tickets/{id}/
Atualização parcial de ticket.

#### DELETE /api/tickets/{id}/
Remove ticket.

#### POST /api/tickets/{id}/finalizar/
Finaliza um ticket específico.

**Response:**
```json
{
  "id": 1,
  "codigo_ticket": "2711250001",
  "status": "finalizado",
  "finalizado_em": "2025-11-27T17:00:00",
  ...
}
```

#### GET /api/tickets/fila_demanda/?demanda_id=1
Lista todos os tickets aguardando de uma demanda específica.

**Query Parameters:**
- `demanda_id` - ID da demanda (obrigatório)
- `demanda` - Filtrar por demanda
- `status` - Filtrar por status (aguardando, em_atendimento, finalizado, cancelado)
- `search` - Buscar por código ou nome do cliente
- `ordering` - Ordenar (criado_em, status)

## Formato do Código do Ticket

O código é gerado automaticamente no formato: **DDMMYYnnnn**

- **DD** - Dia (01-31)
- **MM** - Mês (01-12)
- **YY** - Ano (00-99)
- **nnnn** - Sequencial do dia (0001-9999)

Exemplo: `2711250001` = 27/11/2025, primeiro ticket do dia

## Status Disponíveis

### Demanda
- `aberta` - Demanda aberta para novos tickets
- `em_andamento` - Demanda em andamento
- `finalizada` - Demanda finalizada
- `cancelada` - Demanda cancelada

### Ticket
- `aguardando` - Aguardando atendimento (na fila)
- `em_atendimento` - Em atendimento no momento
- `finalizado` - Atendimento finalizado
- `cancelado` - Ticket cancelado

## Autenticação

Todas as rotas (exceto `/api/auth/login`) requerem autenticação via JWT.

Incluir o token no header de todas as requisições:
```
Authorization: Bearer <seu_token_jwt>
```

Token expira em 8 horas (configurável via `JWT_EXPIRATION_HOURS` no .env).

## Paginação

Todas as listagens são paginadas com 10 itens por página (configurável).

**Response:**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/tickets/?page=2",
  "previous": null,
  "results": [...]
}
```

## Códigos de Erro Comuns

- `400 Bad Request` - Dados inválidos
- `401 Unauthorized` - Token inválido ou expirado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro no servidor
