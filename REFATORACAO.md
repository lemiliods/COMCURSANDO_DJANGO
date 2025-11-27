# 🔄 REFATORAÇÃO COMPLETA DO SISTEMA

## 📋 O QUE MUDOU

O sistema foi **completamente refatorado** de um sistema de filas para um **sistema de compra de provas de concursos**.

### Modelo Antigo ❌
- Clientes geravam tickets para entrar em fila
- Sistema de atendimento sequencial

### Modelo Novo ✅
- **Clientes enviam provas** que fizeram (PDF ou foto)
- **Administradores validam** se a prova é real
- **Sistema paga** automaticamente via PIX se aprovado

---

## 🚀 COMO IMPLANTAR NO SERVIDOR

```bash
# 1. Ir para o diretório
cd /var/www/COMCURSANDO_DJANGO

# 2. Baixar alterações
git pull origin main

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Instalar novo pacote (Pillow para imagens)
pip install -r requirements.txt

# 5. Criar migrations
python manage.py makemigrations

# 6. IMPORTANTE: Backup do banco antes de migrar
mysqldump -u comcursando_user -p comcursando > backup_antes_migracao.sql

# 7. Aplicar migrations
python manage.py migrate

# 8. Criar diretório para uploads
mkdir -p media/provas

# 9. Ajustar permissões
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/

# 10. Coletar estáticos
python manage.py collectstatic --noinput

# 11. Reiniciar serviço
sudo systemctl restart comcursando
```

---

## 🗂️ ESTRUTURA DE DADOS

### Demanda (Concurso)
```
- concurso: Nome do concurso
- numero_edital: Número do edital
- banca: Banca organizadora
- data_concurso: Data da prova
- cargo: Cargo do concurso
- autarquia: Órgão
- valor_recompensa: R$ a pagar por prova válida (padrão: R$ 50,00)
- status:
  * aberto: Aguardando alguém enviar prova
  * em_analise: Alguém enviou, admin analisando
  * concluido: Prova aprovada e paga
  * cancelado: Demanda cancelada
```

### Ticket (Envio de Prova)
```
- demanda: FK para concurso
- cliente_nome: Nome do cliente
- cliente_pix: Chave PIX (CPF, e-mail, telefone, aleatória)
- arquivo_prova: Upload do arquivo (PDF ou imagem)
- codigo_ticket: Código único do envio (DDMMYYnnnn)
- status:
  * aguardando: Enviado, aguardando análise
  * em_analise: Admin está analisando
  * aprovado: Aprovado, aguardando pagamento
  * pago: Pago e concluído
  * recusado: Recusado (prova inválida)
- observacoes_admin: Motivo de recusa ou obs
- valor_pago: Valor que foi pago
- criado_em: Data do envio
- analisado_em: Data da análise
- pago_em: Data do pagamento
```

---

## 📝 PRÓXIMAS TAREFAS

### 1. Atualizar View Pública (home)
- Mostrar apenas concursos com `status='aberto'`
- Esconder concursos `em_analise` ou `concluido`
- Mostrar valor da recompensa

### 2. Atualizar Formulário de Envio
- Adicionar campo `cliente_pix`
- Adicionar upload de arquivo (PDF/imagem)
- Validar tipo de arquivo
- Limite de tamanho (ex: 10MB)

### 3. Atualizar Página de Sucesso
- Mostrar que o envio foi recebido
- Explicar que será analisado
- Não mostrar "posição na fila"

### 4. Atualizar Admin
- Adicionar ações:
  * "Aprovar e aguardar pagamento"
  * "Marcar como pago"
  * "Recusar prova"
- Exibir arquivo da prova
- Campo para observações
- Campo para confirmar valor pago

### 5. Configurar Nginx para Media
Adicionar ao nginx:
```nginx
location /media/ {
    alias /var/www/COMCURSANDO_DJANGO/media/;
}
```

---

## ⚠️ ATENÇÃO

### Dados Existentes
As migrations vão **adicionar novos campos** aos models existentes:
- `cliente_pix` (obrigatório)
- `arquivo_prova` (obrigatório)
- `valor_recompensa` na Demanda

**PROBLEMA**: Tickets existentes não têm esses campos!

### Soluções:
1. **Limpar dados de teste** antes de migrar:
```sql
DELETE FROM tickets;
DELETE FROM demandas;
```

2. **OU** adicionar valores default temporariamente na migration

3. **OU** fazer migration em 2 etapas:
   - Adicionar campos como nullable
   - Preencher dados
   - Tornar obrigatório

---

## 🔄 FLUXO COMPLETO DO SISTEMA

### Cliente (Frontend)
1. Acessa `/`
2. Vê lista de concursos **abertos** (sem prova)
3. Clica em "Enviar Minha Prova" (R$ XX,XX)
4. Preenche formulário:
   - Nome completo
   - Chave PIX
   - Upload da prova (PDF ou foto)
5. Envia
6. Recebe código de confirmação
7. Aguarda análise

### Admin (Backend)
1. Vê lista de envios pendentes
2. Clica no envio
3. Visualiza a prova enviada
4. **Se válida**:
   - Marca como "Aprovado"
   - Faz PIX para a chave do cliente
   - Marca como "Pago" + valor
   - Demanda fica "Concluída"
5. **Se inválida**:
   - Marca como "Recusado"
   - Adiciona motivo
   - Demanda volta para "Aberto"

---

## 🎯 PRÓXIMO PASSO

Vou atualizar as views e templates para refletir o novo modelo!

Você quer que eu:
1. Atualize agora as views públicas?
2. Atualize o admin primeiro?
3. Crie as migrations manualmente com defaults?
