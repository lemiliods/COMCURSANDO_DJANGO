# Generated manually for queue system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='cliente_email',
            field=models.EmailField(blank=True, help_text='E-mail para notificações', max_length=255, null=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='notificado_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Notificado em'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='prazo_envio',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Prazo para Envio'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='arquivo_prova',
            field=models.FileField(blank=True, help_text='PDF ou imagem da prova', null=True, upload_to='provas/%Y/%m/', verbose_name='Arquivo da Prova'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('na_fila', 'Na Fila de Espera'), ('notificado', 'Notificado - Aguardando Envio'), ('aguardando', 'Aguardando Análise'), ('em_analise', 'Em Análise'), ('aprovado', 'Aprovado - Aguardando Pagamento'), ('pago', 'Pago e Concluído'), ('recusado', 'Recusado'), ('expirado', 'Tempo Expirado')], default='na_fila', max_length=20, verbose_name='Status'),
        ),
    ]
