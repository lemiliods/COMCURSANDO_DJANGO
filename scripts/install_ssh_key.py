# -*- coding: utf-8 -*-
import paramiko
import os

SERVER = "72.61.36.89"
USER = "root"
PASS = "Leds@131610@234645?"

# Ler chave pública
pubkey_path = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa.pub')
with open(pubkey_path, 'r') as f:
    pubkey = f.read().strip()

# Conectar e instalar chave
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASS)

commands = [
    'mkdir -p ~/.ssh',
    'chmod 700 ~/.ssh',
    f'echo "{pubkey}" >> ~/.ssh/authorized_keys',
    'chmod 600 ~/.ssh/authorized_keys'
]

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()

ssh.close()
print("[OK] Chave SSH instalada! Agora voce pode conectar sem senha.")
