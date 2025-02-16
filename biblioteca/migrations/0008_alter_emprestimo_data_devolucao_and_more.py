# Generated by Django 5.1.5 on 2025-01-18 03:00

import biblioteca.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0007_alter_livrotemautor_autor_alter_livrotemautor_livro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emprestimo',
            name='data_devolucao',
            field=models.DateField(default=biblioteca.models.get_default_return_date, verbose_name='Data de Devolução'),
        ),
        migrations.AlterField(
            model_name='emprestimo',
            name='data_emprestimo',
            field=models.DateField(default=datetime.date.today, verbose_name='Data de Empréstimo'),
        ),
        migrations.AlterField(
            model_name='exemplar',
            name='numero_exemplar',
            field=models.IntegerField(verbose_name='Número de Exemplar'),
        ),
        migrations.AlterField(
            model_name='livro',
            name='ano',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livro',
            name='edicao',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livro',
            name='isbn',
            field=models.CharField(blank=True, default='', max_length=13),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='livro',
            name='subtitulo',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
    ]
