"""
Script para verificar e diagnosticar problemas nos dados do projeto.
Uso: python manage.py shell < scripts/verificar_dados.py
"""

from apps.concursos.models import Demanda
from apps.tickets.models import Ticket
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("DIAGNÓSTICO DO PROJETO COMCURSANDO")
print("="*80 + "\n")

# 1. Verificar todas as demandas
print("1️⃣ VERIFICANDO DEMANDAS...")
print("-" * 80)

demandas = Demanda.objects.all()
print(f"   Total de demandas: {demandas.count()}")

for d in demandas:
    total_tickets = d.tickets.count()
    tickets_ativos = d.tickets.filter(
        status__in=['na_fila', 'notificado', 'aguardando', 'em_analise']
    ).count()
    tickets_aprovados = d.tickets.filter(
        status__in=['pago', 'aprovado']
    ).count()
    
    print(f"\n   📌 {d.concurso}")
    print(f"      • Edital: {d.numero_edital}")
    print(f"      • Cargo: {d.cargo}")
    print(f"      • Órgão: {d.autarquia}")
    print(f"      • Banca: {d.banca}")
    print(f"      • Data: {d.data_concurso}")
    print(f"      • Status: {d.get_status_display()}")
    print(f"      • Total tickets: {total_tickets}")
    print(f"      • Tickets ativos: {tickets_ativos}")
    print(f"      • Tickets aprovados/pagos: {tickets_aprovados}")
    print(f"      • Tem prova aprovada: {d.tem_prova_aprovada}")
    print(f"      • Envios pendentes: {d.envios_pendentes}")

# 2. Verificar tickets
print("\n\n2️⃣ VERIFICANDO TICKETS...")
print("-" * 80)

tickets = Ticket.objects.all()
print(f"   Total de tickets: {tickets.count()}")

# Agrupar por status
for status_code, status_display in Ticket.STATUS_CHOICES:
    count = Ticket.objects.filter(status=status_code).count()
    if count > 0:
        print(f"   • {status_display}: {count}")

# 3. Tickets por demanda
print("\n\n3️⃣ TICKETS POR DEMANDA...")
print("-" * 80)

demandas_com_tickets = Demanda.objects.annotate(
    ticket_count=Count('tickets')
).filter(ticket_count__gt=0).order_by('-ticket_count')

for d in demandas_com_tickets:
    print(f"\n   {d.concurso}")
    print(f"      Total: {d.ticket_count} tickets")
    for status_code, status_display in Ticket.STATUS_CHOICES:
        count = d.tickets.filter(status=status_code).count()
        if count > 0:
            print(f"      • {status_display}: {count}")

# 4. Verificar Itabira especificamente
print("\n\n4️⃣ VERIFICANDO DEMANDAS DE ITABIRA...")
print("-" * 80)

itabira = Demanda.objects.filter(autarquia__icontains='Itabira')
print(f"   Total de demandas de Itabira: {itabira.count()}")

for d in itabira:
    print(f"\n   {d.concurso}")
    print(f"      • Cargo: {d.cargo}")
    print(f"      • Total tickets: {d.tickets.count()}")

# 5. Verificar inconsistências
print("\n\n5️⃣ VERIFICANDO INCONSISTÊNCIAS...")
print("-" * 80)

# Demandas sem tickets
demandas_sem_tickets = Demanda.objects.annotate(
    ticket_count=Count('tickets')
).filter(ticket_count=0)

if demandas_sem_tickets.exists():
    print(f"\n   ⚠️  Demandas sem tickets: {demandas_sem_tickets.count()}")
    for d in demandas_sem_tickets:
        print(f"      • {d.concurso} (ID: {d.id})")

# Tickets órfãos (sem demanda)
tickets_orphan = Ticket.objects.filter(demanda__isnull=True).count()
if tickets_orphan > 0:
    print(f"\n   ⚠️  Tickets órfãos (sem demanda): {tickets_orphan}")

# Demandas duplicadas
duplicadas = (
    Demanda.objects
    .values('numero_edital')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)
if duplicadas.exists():
    print(f"\n   ⚠️  Demandas duplicadas (mesmo edital): {duplicadas.count()}")
    for dup in duplicadas:
        print(f"      • Edital {dup['numero_edital']}: {dup['count']} registros")

print("\n" + "="*80)
print("FIM DO DIAGNÓSTICO")
print("="*80 + "\n")
