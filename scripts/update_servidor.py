#!/usr/bin/env python
"""
Script para conectar ao servidor e atualizar o projeto
"""
import subprocess
import sys

# Credenciais do servidor
SERVER_IP = "72.61.36.89"
USERNAME = "root"
PASSWORD = "Leds@131610@234645?"
PROJECT_PATH = "/var/www/concursando"

def run_ssh_command(command):
    """Executar comando via SSH usando stdin para password"""
    try:
        # Usar expect ou sshpass via Python
        import pexpect
        
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no {USERNAME}@{SERVER_IP}"
        child = pexpect.spawn(ssh_cmd)
        child.expect('password:', timeout=10)
        child.sendline(PASSWORD)
        child.sendline(command)
        child.expect(pexpect.EOF, timeout=30)
        output = child.before.decode('utf-8')
        return output
    except ImportError:
        print("pexpect não está instalado. Tentando com subprocess...")
        # Alternativa com subprocess
        ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', f'{USERNAME}@{SERVER_IP}', command]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, input=PASSWORD)
        return result.stdout

# Executar comandos
print("=" * 80)
print("ATUALIZANDO PROJETO NO SERVIDOR")
print("=" * 80)

commands = [
    f"cd {PROJECT_PATH} && pwd",
    f"cd {PROJECT_PATH} && git status",
    f"cd {PROJECT_PATH} && git pull origin main",
    f"cd {PROJECT_PATH} && python manage.py migrate",
    f"cd {PROJECT_PATH} && python manage.py collectstatic --noinput",
]

for cmd in commands:
    print(f"\n[EXECUTANDO] {cmd}")
    print("-" * 80)
    try:
        output = run_ssh_command(cmd)
        print(output)
    except Exception as e:
        print(f"ERRO: {e}")

print("\n" + "=" * 80)
print("ATUALIZAÇÃO CONCLUÍDA")
print("=" * 80)
