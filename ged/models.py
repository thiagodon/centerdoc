from django.db import models

# Create your models here.

class Tipo(models.Model):
	nome = models.CharField(verbose_name='Nome', max_length=200)
	pasta = models.CharField(verbose_name='Nome', max_length=200)
	removido = models.BooleanField(default=False)
	user_add = models.IntegerField()
	date_add = models.DateField()
	user_up = models.IntegerField(blank=True, null=True)
	date_up = models.DateField(blank=True, null=True)
	user_del = models.IntegerField(blank=True, null=True)
	date_del = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.nome

class Empresa(models.Model):
	cnpj = models.CharField(verbose_name='CNPJ', max_length = 200)
	razao_social = models.CharField(verbose_name='Razão Social', max_length = 200)
	fantasia = models.CharField(verbose_name='Nome Fantasia', max_length = 200)
	ie = models.CharField(verbose_name='Inscrição Estadual', max_length =200) 
	logradouro = models.CharField(verbose_name='Logradouro', max_length = 200)
	numero = models.IntegerField(verbose_name='Número')
	bairro = models.CharField(verbose_name='Bairro', max_length = 200)
	estado = models.CharField(verbose_name='Estado', max_length = 2)
	cidade = models.CharField(verbose_name='Cidade', max_length = 200)
	cep = models.CharField (verbose_name='CEP', max_length = 200)
	telefone = models.CharField(verbose_name='Telefone', max_length = 100)
	email = models.EmailField(verbose_name='Email')
	site = models.URLField(verbose_name='Site')
	user_add = models.IntegerField()
	date_add = models.DateField()
	user_up = models.IntegerField(blank=True, null=True)
	date_up = models.DateField(blank=True, null=True)
	user_del = models.IntegerField(blank=True, null=True)
	date_del = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.fantasia + ' - ' + self.cnpj

class Documento(models.Model):
	titulo = models.CharField(verbose_name="Título", max_length=200)
	informacoes = models.TextField(verbose_name="Informações")
	palavras_chave = models.CharField(verbose_name="Palavras Chave", max_length=200)
	texto = models.TextField(verbose_name="Texto")
	paginas = models.IntegerField(verbose_name="Quantidade de Páginas")
	capa = models.FileField(upload_to='capas')
	frenteverso = models.IntegerField(verbose_name="Frente e Verso", null=True, blank=True)
	ano = models.IntegerField(verbose_name="Ano")
	removido = models.BooleanField(default=False)
	user_add = models.IntegerField()
	date_add = models.DateField()
	user_up = models.IntegerField(blank=True, null=True)
	date_up = models.DateField(blank=True, null=True)
	user_del = models.IntegerField(blank=True, null=True)
	date_del = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.titulo

class TipoDocumento(models.Model):
	documento = models.ForeignKey('Documento', verbose_name='Documento', related_name='documento_tipodocumento', on_delete=models.CASCADE, blank=True, null=True)


class Pagina(models.Model):
	titulo = models.CharField(verbose_name="Título", max_length=200)
	tipo = models.ForeignKey('Tipo', verbose_name='Tipo', related_name='pagina_tipo', on_delete=models.CASCADE, blank=False, null=False)
	documento = models.ForeignKey('Documento', verbose_name='Documento', related_name='documento_paginas', on_delete=models.CASCADE, blank=True, null=True)
	palavras_chave = models.CharField(verbose_name='Palavras chave', max_length = 200)
	pagina = models.IntegerField(verbose_name='Página número')
	arquivo = models.FileField()
	texto = models.TextField(verbose_name='Informações')
	lado = models.IntegerField(verbose_name="Lado", null=True, blank=True)
	inicio = models.TextField(verbose_name='Inicia com')
	fim = models.TextField(verbose_name='Termina com')
	removido = models.BooleanField(default=False)
	user_add = models.IntegerField()
	date_add = models.DateField()
	user_up = models.IntegerField(blank=True, null=True)
	date_up = models.DateField(blank=True, null=True)
	user_del = models.IntegerField(blank=True, null=True)
	date_del = models.DateField(blank=True, null=True)

	def __str__(self):
		return self.tipo.nome

class NomePagina(models.Model):
	nome = models.CharField(verbose_name="Nome Citado", max_length=255, blank=True, null=True)
	pagina = models.ForeignKey('Pagina', verbose_name='Pagina', related_name='nome_pagina', on_delete=models.CASCADE, blank=True, null=True)

class Backup(models.Model):
	user_add = models.IntegerField()
	date_add = models.DateField()
