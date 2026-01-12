#!/usr/bin/env python
"""
Script de diagnóstico para identificar problemas nos dados
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.concursos.models import Demanda
from apps.tickets.models import Ticket
from django.db import connection

print("=" * 80)
print("DIAGNÓSTICO DE DADOS DO PROJETO COMCURSANDO")
print("=" * 80)

# 1. Verificar estrutura do banco
print("\n[1] VERIFICANDO ESTRUTURA DO BANCO...")
with connection.cursor() as cursor:
    cursor.execute("DESCRIBE demandas;")
    print("\nCampos da tabela 'demandas':")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")

# 2. Listar todas as demandas
print("\n[2] DEMANDAS CADASTRADAS:")
demandas = Demanda.objects.all()
print(f"Total: {demandas.count()}")
for d in demandas:
    tickets_count = d.tickets.count()
    tickets_ativos = d.tickets.filter(status__in=['na_fila', 'notificado', 'aguardando', 'em_analise']).count()
    tem_prova = d.tem_prova_aprovada
    print(f"\n  ID: {d.id}")
    print(f"  Concurso: {d.concurso}")
    print(f"  Cargo: {d.cargo}")
    print(f"  Status: {d.status}")
    print(f"  Total de Tickets: {tickets_count}")
    print(f"  Tickets Ativos: {tickets_ativos}")
    print(f"  Tem Prova Aprovada: {tem_prova}")

# 3. Verificar tickets
print("\n[3] TICKETS CADASTRADOS:")
tickets = Ticket.objects.all()
print(f"Total: {tickets.count()}")
status_count = {}
for ticket in tickets:
    status = ticket.status
    status_count[status] = status_count.get(status, 0) + 1
    
print("\nDistribuição por Status:")
for status, count in sorted(status_count.items()):
    print(f"  - {status}: {count}")

# 4. Verificar inconsistências
print("\n[4] VERIFICANDO INCONSISTÊNCIAS:")
problemas = []

# Verificar demandas com status inválido
for d in demandas:
    if d.status not in ['aberto', 'em_analise', 'concluido', 'cancelado']:
        problemas.append(f"Demanda {d.id} tem status inválido: {d.status}")

# Verificar tickets órfãos
print(f"\n  ✓ Demandas: {demandas.count()}")
print(f"  ✓ Tickets: {tickets.count()}")

if problemas:
    print(f"\n  ⚠ PROBLEMAS ENCONTRADOS ({len(problemas)}):")
    for p in problemas:
        print(f"    - {p}")
else:
    print(f"\n  ✓ Nenhum problema encontrado!")

print("\n" + "=" * 80)
