#!/usr/bin/env python3
"""
Script para atualizar projeto no servidor via SSH com autenticação por senha
Usando Paramiko para conexão SSH segura
"""
import paramiko
import sys

SERVER_IP = "72.61.36.89"
USERNAME = "root"
PASSWORD = "Leds@131610@234645?"
PROJECT_PATH = "/var/www/concursando"

print("=" * 80)
print("ATUALIZANDO PROJETO NO SERVIDOR")
print("=" * 80)

try:
    # Criar cliente SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"\n[CONECTANDO] {USERNAME}@{SERVER_IP}...")
    ssh.connect(SERVER_IP, username=USERNAME, password=PASSWORD, timeout=10)
    print("✓ Conectado com sucesso!")
    
    # Primeiro, descobrir onde está o projeto COMCURSANDO
    print("\n[DESCOBRINDO] Localização do projeto COMCURSANDO no servidor...")
    stdin, stdout, stderr = ssh.exec_command("find / -name 'COMCURSANDO*' -type d 2>/dev/null | head -10")
    found_dirs = stdout.read().decode().strip().split('\n')
    print(f"Diretórios encontrados: {found_dirs}")
    
    # Procurar por manage.py em qualquer lugar
    stdin, stdout, stderr = ssh.exec_command("find / -path '*/COMCURSANDO*' -name 'manage.py' 2>/dev/null | head -1")
    manage_file = stdout.read().decode().strip()
    
    if manage_file:
        PROJECT_PATH = '/'.join(manage_file.split('/')[:-1])
        print(f"✓ Projeto COMCURSANDO encontrado em: {PROJECT_PATH}")
    else:
        print("✗ Projeto COMCURSANDO não encontrado!")
        print("\n[INFO] Procurando por qualquer Django project...")
        stdin, stdout, stderr = ssh.exec_command("find /var/www -name 'manage.py' -type f 2>/dev/null")
        all_projects = stdout.read().decode().strip()
        print(f"Todos os projetos Django encontrados:\n{all_projects}")
        sys.exit(1)
    
    # Comandos a executar
    commands = [
        f"cd {PROJECT_PATH} && pwd",
        f"cd {PROJECT_PATH} && git status",
        f"cd {PROJECT_PATH} && git pull origin main",
        f"cd {PROJECT_PATH} && python3 manage.py migrate",
        f"cd {PROJECT_PATH} && python3 manage.py collectstatic --noinput",
        f"cd {PROJECT_PATH} && systemctl restart gunicorn 2>/dev/null || echo 'Gunicorn não reiniciou'",
    ]
    
    for cmd in commands:
        print(f"\n[EXECUTANDO] {cmd}")
        print("-" * 80)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print(output)
        if error:
            print(f"ERRO: {error}")
    
    ssh.close()
    print("\n" + "=" * 80)
    print("✓ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    sys.exit(1)
