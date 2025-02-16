# Generated by Django 5.1.5 on 2025-01-15 14:40

import biblioteca.models
import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('codigo_autor', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'autor',
                'verbose_name_plural': 'autores',
            },
        ),
        migrations.CreateModel(
            name='Cdd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'cdd',
            },
        ),
        migrations.CreateModel(
            name='Editora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'editora',
            },
        ),
        migrations.CreateModel(
            name='Exemplar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tombo', models.CharField(max_length=45)),
                ('numero_exemplar', models.IntegerField()),
                ('etiqueta_gerada', models.BooleanField()),
                ('baixa', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'exemplar',
                'verbose_name_plural': 'exemplares',
            },
        ),
        migrations.CreateModel(
            name='Leitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('ra', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'verbose_name': 'leitor',
                'verbose_name_plural': 'leitores',
            },
        ),
        migrations.CreateModel(
            name='Local_Publicacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'local_publicacao',
            },
        ),
        migrations.CreateModel(
            name='Emprestimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_emprestimo', models.DateField(default=datetime.date.today)),
                ('data_devolucao', models.DateField(default=biblioteca.models.get_default_return_date)),
                ('devolvido', models.BooleanField(default=False)),
                ('leitor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('exemplar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.exemplar')),
            ],
            options={
                'verbose_name': 'emprestimo',
                'verbose_name_plural': 'emprestimos',
            },
        ),
        migrations.CreateModel(
            name='Livro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('subtitulo', models.CharField(max_length=100, null=True)),
                ('ano', models.IntegerField()),
                ('edicao', models.IntegerField()),
                ('isbn', models.CharField(max_length=13, null=True)),
                ('iniciais_titulo', models.CharField(max_length=2)),
                ('cdd', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.cdd')),
                ('editora', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.editora')),
                ('local_publicacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.local_publicacao')),
            ],
            options={
                'verbose_name': 'livro',
                'verbose_name_plural': 'livros',
            },
        ),
        migrations.AddField(
            model_name='exemplar',
            name='livro',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.livro'),
        ),
        migrations.CreateModel(
            name='LivroTemAutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.autor')),
                ('livro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='biblioteca.livro')),
            ],
            options={
                'verbose_name': 'livro_tem_autor',
                'verbose_name_plural': 'livro_tem_autores',
            },
        ),
    ]
