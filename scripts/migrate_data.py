"""
Script para migrar dados do sistema Node.js antigo para o Django.

Pré-requisitos:
1. Banco de dados MySQL rodando
2. Migrações Django aplicadas (python manage.py migrate)
3. Ajustar as credenciais do banco no .env

Como usar:
python manage.py shell < scripts/migrate_data.py
"""

import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import AdminUser
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket
from django.db import connection


def migrate_admin_users():
    """
    Migra os usuários da tabela admin_users antiga.
    
    Nota: As senhas do sistema antigo estão em bcrypt,
    Django também suporta bcrypt, mas pode ser necessário 
    recriar as senhas manualmente.
    """
    print("=== Migrando Usuários Administradores ===")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, password, createdAt, updatedAt 
            FROM admin_users
        """)
        
        usuarios_antigos = cursor.fetchall()
    
    usuarios_migrados = 0
    
    for row in usuarios_antigos:
        user_id, username, password_hash, created_at, updated_at = row
        
        # Verifica se já existe
        if AdminUser.objects.filter(username=username).exists():
            print(f"❌ Usuário '{username}' já existe, pulando...")
            continue
        
        try:
            # Cria novo usuário
            user = AdminUser.objects.create(
                username=username,
                email=f"{username}@comcursando.com",
                is_active=True,
                is_staff=True,
                is_superuser=True,
                date_joined=created_at
            )
            
            # Define a senha (precisa recriar pois formato pode ser diferente)
            # Senha padrão temporária - ALTERAR depois!
            user.set_password('Comcursando2025!')
            user.save()
            
            usuarios_migrados += 1
            print(f"✅ Usuário '{username}' migrado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao migrar usuário '{username}': {str(e)}")
    
    print(f"\n✅ {usuarios_migrados} usuários migrados com sucesso!\n")


def migrate_demandas():
    """
    Migra as demandas da tabela antiga.
    """
    print("=== Migrando Demandas ===")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, concurso, numero_edital, banca, data_concurso,
                   cargo, autarquia, status, criado_em
            FROM demandas
        """)
        
        demandas_antigas = cursor.fetchall()
    
    demandas_migradas = 0
    
    for row in demandas_antigas:
        (demanda_id, concurso, numero_edital, banca, data_concurso,
         cargo, autarquia, status, criado_em) = row
        
        # Verifica se já existe
        if Demanda.objects.filter(id=demanda_id).exists():
            print(f"❌ Demanda ID {demanda_id} já existe, pulando...")
            continue
        
        try:
            demanda = Demanda.objects.create(
                id=demanda_id,
                concurso=concurso,
                numero_edital=numero_edital,
                banca=banca,
                data_concurso=data_concurso,
                cargo=cargo,
                autarquia=autarquia,
                status=status or 'aberta',
                criado_em=criado_em
            )
            
            demandas_migradas += 1
            print(f"✅ Demanda '{concurso}' migrada com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao migrar demanda ID {demanda_id}: {str(e)}")
    
    print(f"\n✅ {demandas_migradas} demandas migradas com sucesso!\n")


def migrate_tickets():
    """
    Migra os tickets da tabela antiga.
    """
    print("=== Migrando Tickets ===")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, demanda_id, cliente_nome, codigo_ticket, 
                   status, criado_em, finalizado_em
            FROM tickets
        """)
        
        tickets_antigos = cursor.fetchall()
    
    tickets_migrados = 0
    
    for row in tickets_antigos:
        (ticket_id, demanda_id, cliente_nome, codigo_ticket,
         status, criado_em, finalizado_em) = row
        
        # Verifica se já existe
        if Ticket.objects.filter(codigo_ticket=codigo_ticket).exists():
            print(f"❌ Ticket '{codigo_ticket}' já existe, pulando...")
            continue
        
        # Verifica se a demanda existe
        try:
            demanda = Demanda.objects.get(id=demanda_id)
        except Demanda.DoesNotExist:
            print(f"❌ Demanda ID {demanda_id} não encontrada para ticket '{codigo_ticket}', pulando...")
            continue
        
        try:
            ticket = Ticket.objects.create(
                id=ticket_id,
                demanda=demanda,
                cliente_nome=cliente_nome,
                codigo_ticket=codigo_ticket,
                status=status or 'aguardando',
                criado_em=criado_em,
                finalizado_em=finalizado_em
            )
            
            tickets_migrados += 1
            print(f"✅ Ticket '{codigo_ticket}' migrado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao migrar ticket '{codigo_ticket}': {str(e)}")
    
    print(f"\n✅ {tickets_migrados} tickets migrados com sucesso!\n")


def main():
    """
    Executa a migração completa.
    """
    print("\n" + "="*60)
    print("  MIGRAÇÃO DE DADOS - COMCURSANDO")
    print("  Node.js → Django")
    print("="*60 + "\n")
    
    try:
        # Migra na ordem correta (usuários → demandas → tickets)
        migrate_admin_users()
        migrate_demandas()
        migrate_tickets()
        
        print("="*60)
        print("  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60 + "\n")
        
        print("📝 IMPORTANTE:")
        print("- Todos os usuários foram criados com senha temporária: 'Comcursando2025!'")
        print("- É NECESSÁRIO alterar as senhas através do Django Admin")
        print("- Acesse: http://localhost:8000/admin/")
        print("")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A MIGRAÇÃO: {str(e)}\n")


if __name__ == '__main__':
    main()
