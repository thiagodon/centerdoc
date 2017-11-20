from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Tipo, Empresa, Pagina, Documento, Backup
from .forms import TipoForm, EmpresaForm, PaginaForm, PaginaFormJ, EmpresaFormRead, DocumentoForm, PaginaFormJRead
from django.utils import timezone
import os
from os import path
import mimetypes
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
import time
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#ocr
from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
import glob

from django.conf import settings
from unicodedata import normalize

#backup
from shutil import make_archive
import datetime
import json
from django.core import serializers

class Pasta:
		titulo = None
		data = None
		usuario = None
		id = None
		tipo = None
		paginas = None
		pagina = None
		livro = None

paginas_list = []

# Create your views here.
@login_required(login_url='login:login')
def home(request):
	livros = Documento.objects.filter(removido=False)
	_livros = Documento.objects.filter(removido=True)
	paginas = Pagina.objects.filter(removido=False, documento__isnull=True, tipo__isnull=True).order_by('tipo', 'documento', 'pagina', 'lado', 'pk')
	grupos = Tipo.objects.filter(removido=False)
	_grupos = Tipo.objects.filter(removido=True)
	pastas = []
	for grupo in grupos:
		p = Pasta()
		p.titulo = grupo.nome
		p.id = grupo.pk
		p.tipo = 'g'
		p.paginas = Pagina.objects.filter(removido=False, tipo=grupo.pk).count()
		pastas.append(p)	
	for grupo in _grupos:
		if Pagina.objects.filter(removido=False, tipo=grupo.pk):
			p = Pasta()
			p.titulo = grupo.nome
			p.id = grupo.pk
			p.tipo = 'g'
			p.paginas = Pagina.objects.filter(removido=False, tipo=grupo.pk).count()
			pastas.append(p)
	for livro in livros:
		p = Pasta()
		p.titulo = livro.titulo
		p.id = livro.pk
		p.tipo = 'l'
		if Pagina.objects.filter(removido=False, documento=livro.pk):
			p.paginas = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina').last().pagina
		pastas.append(p)
	for livro in _livros:
		if Pagina.objects.filter(removido=False, documento=livro.pk):
			p = Pasta()
			p.titulo = livro.titulo
			p.id = livro.pk
			p.tipo = 'l'
			if Pagina.objects.filter(removido=False, documento=livro.pk):
				p.paginas = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina').last().pagina
			pastas.append(p)
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
		if pagina.documento:
			p.pagina = str(pagina.pagina)+'('+('Frente' if pagina.lado == 1 else 'Verso')+')'
		p.usuario = u.username
		pastas.append(p)
	paginator = Paginator(pastas, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		ps = paginator.page(page)
	except (EmptyPage, InvalidPage):
		ps = paginator.page(paginator.num_pages)

	titulo = "Todos os Documentos"	
	action = '/busca/'

	return render(request, 'ged/home.html', {'pastas':ps, 'titulo': titulo, 'action': action})

@login_required(login_url='login:login')
def home_busca(request):
	pastas = []
	if request.method=="POST":		
		paginas = Pagina.objects.filter(removido=False, texto__icontains=request.POST.get('txt_busca')).order_by('pagina', 'lado',  'documento', 'tipo', 'pk')
		for pagina in paginas:
			p = Pasta()
			p.titulo = pagina.tipo.nome
			p.id = pagina.pk
			p.tipo = 'p'
			p.data = pagina.date_add
			u = User.objects.get(pk=pagina.user_add)
			if pagina.documento:
				p.pagina = str(pagina.pagina)+'('+('Frente' if pagina.lado == 1 else 'Verso')+')'
			p.usuario = u.username
			pastas.append(p)
	paginator = Paginator(pastas, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		ps = paginator.page(page)
	except (EmptyPage, InvalidPage):
		ps = paginator.page(paginator.num_pages)

	tp = "Busca"
	filtro_id = None
	titulo = "Busca: \""+request.POST.get('txt_busca')+"\""
	action = '/busca/'

	return render(request, 'ged/home.html', {'pastas':ps, 'titulo': titulo, 'tp': tp, 'filtro_id': filtro_id, 'action': action})

@login_required(login_url='login:login')
def home_livro(request, pk):
	documento = Documento.objects.get(pk=pk)
	paginas = Pagina.objects.filter(removido=False, documento=pk).order_by('pagina', 'lado')
	pastas = []
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
		if pagina.documento:
			p.pagina = str(pagina.pagina)+'('+('Frente' if pagina.lado == 1 else 'Verso')+')'
		p.usuario = u.username
		pastas.append(p)
	paginator = Paginator(pastas, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		ps = paginator.page(page)
	except (EmptyPage, InvalidPage):
		ps = paginator.page(paginator.num_pages)

	tp = "Livro"
	filtro_id = documento.pk
	titulo = documento.titulo	
	action = '/busca/'


	return render(request, 'ged/home.html', {'pastas':ps, 'titulo': titulo, 'tp': tp, 'filtro_id': filtro_id, 'action': action})

@login_required(login_url='login:login')
def home_tipo(request, pk):
	tipo = Tipo.objects.get(pk=pk)
	paginas = Pagina.objects.filter(removido=False, tipo=pk, documento__isnull=True).order_by('tipo', 'documento', 'pagina','lado', 'pk')
	livros = Documento.objects.all()
	pastas = []
	for livro in livros:
		if Pagina.objects.filter(removido=False, documento=livro.pk, tipo=pk):
			p = Pasta()
			p.titulo = livro.titulo
			p.id = livro.pk
			p.tipo = 'l'
			if Pagina.objects.filter(removido=False, documento=livro.pk):
				p.paginas = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina').last().pagina
			pastas.append(p)
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
		if pagina.documento:
			p.pagina = str(pagina.pagina)+'('+('Frente' if pagina.lado == 1 else 'Verso')+')'
		p.usuario = u.username
		pastas.append(p)
	paginator = Paginator(pastas, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		ps = paginator.page(page)
	except (EmptyPage, InvalidPage):
		ps = paginator.page(paginator.num_pages)

	tp = "Tipo de Documento"
	filtro_id = tipo.pk
	titulo = tipo.nome	
	action = '/busca/'


	return render(request, 'ged/home.html', {'pastas':ps, 'titulo': titulo, 'tp': tp, 'filtro_id': filtro_id, 'action': action})

@login_required(login_url='login:login')
def tipo_new(request):
	if request.method=="POST":
		form = TipoForm(request.POST)
		if form.is_valid():
			tipo = form.save(commit=False)
			tipo.user_add = request.user.pk
			tipo.date_add = timezone.now()
			tipo.pasta = tipopasta(tipo.nome)
			tipo.save()
			return redirect('ged:tipo_list')
	else:
		form = TipoForm()
	return render(request, 'ged/tipo_form.html', {'form': form})

@login_required(login_url='login:login')
def tipo_edit(request, pk):
	tipo = get_object_or_404(Tipo, pk=pk)
	if request.method=="POST":
		form = TipoForm(request.POST, instance=tipo)
		if form.is_valid():
			tipo = form.save(commit=False)
			tipo.user_up = request.user.pk
			tipo.date_up = timezone.now()
			tipo.save()
			return redirect('ged:tipo_list')
	else:
		form = TipoForm(instance=tipo)
	return render(request, 'ged/tipo_form.html', {'form': form})

@login_required(login_url='login:login')
def tipo_list(request):
	grupos = Tipo.objects.filter(removido=False).order_by('nome')
	paginator = Paginator(grupos, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		gps = paginator.page(page)
	except (EmptyPage, InvalidPage):
		gps = paginator.page(paginator.num_pages)
	return render(request, 'ged/tipo_list.html', {'grupos': gps})

@login_required(login_url='login:login')
def tipo_del(request, pk):
	tipo = get_object_or_404(Tipo, pk=pk)
	tipo.removido = True
	tipo.user_del = request.user.pk
	tipo.date_del = timezone.now()
	tipo.save()
	return redirect('ged:tipo_list')

@login_required(login_url='login:login')
def livro_del(request, pk):
	livro = get_object_or_404(Documento, pk=pk)
	livro.removido = True
	livro.user_del = request.user.pk
	livro.date_del = timezone.now()
	livro.save()
	return redirect('ged:livro_list')

@login_required(login_url='login:login')
def pagina_del(request, pk):
	pagina = get_object_or_404(Pagina, pk=pk)
	pagina.removido = True
	pagina.user_del = request.user.pk
	pagina.date_del = timezone.now()
	pagina.save()
	if pagina.documento:
		return redirect(reverse('ged:home_livro', kwargs={ 'pk': pagina.documento.pk }))
	else:
		return redirect(reverse('ged:home_tipo', kwargs={ 'pk': pagina.tipo.pk }))


	# empresa
@login_required(login_url='login:login')
def empresa_new(request):
	if request.method=="POST":
		form = EmpresaForm(request.POST)
		if form.is_valid():
			empresa = form.save(commit=False)
			empresa.user_add = request.user.pk
			empresa.date_add = timezone.now()
			empresa.save()
			return redirect('ged:empresa_edit')
	else:
		form = EmpresaForm()
	return render(request, 'ged/empresa.html', {'form': form})

@login_required(login_url='login:login')
def empresa(request):
	empresa = Empresa.objects.all().first()
	if request.method=="POST":
		if empresa:
			form = EmpresaForm(request.POST, instance=empresa)
			if form.is_valid():
				empresa = form.save(commit=False)
				empresa.user_up = request.user.pk
				empresa.date_up = timezone.now()
				empresa.save()
				return redirect('ged:empresa')
		else:
			form = EmpresaForm(request.POST)
			if form.is_valid():
				empresa = form.save(commit=False)
				empresa.user_add = request.user.pk
				empresa.date_add = timezone.now()
				empresa.save()
				return redirect('ged:empresa')
	else:
		if empresa:
			form = EmpresaForm(instance=empresa)
		else:
			form = EmpresaForm()
	return render(request, 'ged/empresa.html', {'form': form, 'readonly': False})

@login_required(login_url='login:login')
def empresar(request):
	empresa = Empresa.objects.all().first()
	if empresa:
		form = EmpresaFormRead(instance=empresa)
	else:
		form = EmpresaFormRead()
	return render(request, 'ged/empresa.html', {'form': form, 'readonly': True})

@login_required(login_url='login:login')
def livro_new(request):
	if request.method=="POST":
		form = DocumentoForm(request.POST, request.FILES)
		if form.is_valid():
			livro = form.save(commit=False)
			livro.user_add = request.user.pk
			livro.date_add = timezone.now()
			livro.save()
			return redirect(reverse('ged:livro_edit', kwargs={ 'pk': livro.pk}))
	else:
		form = DocumentoForm()
	return render(request, 'ged/livro_form.html', {'form': form})

@login_required(login_url='login:login')
def livro_edit(request, pk):
	livro = get_object_or_404(Documento, pk=pk)
	if request.method=="POST":
		form = DocumentoForm(request.POST, request.FILES, instance=livro)
		if form.is_valid():
			livro = form.save(commit=False)
			livro.user_up = request.user.pk
			livro.date_up = timezone.now()
			livro.save()
			return redirect(reverse('ged:livro_edit', kwargs={ 'pk': livro.pk}))
	else:
		form = DocumentoForm(instance=livro)
	return render(request, 'ged/livro_form.html', {'form': form})

@login_required(login_url='login:login')
def pagina_new(request, livro_pk):
	time.sleep(.300)
	if livro_pk:
		try:
			livro = Documento.objects.get(pk=livro_pk)
		except Documento.DoesNotExist:
			livro = None
	if request.method=="POST":
		form = PaginaForm(request.POST, request.FILES)
		if form.is_valid():
			pagina = form.save(commit=False)
			count=1
			lado = 1
			if form.cleaned_data['doc']:
				documento = Documento.objects.get(pk=form.cleaned_data['doc'])
				_p = Pagina.objects.filter(removido=False, documento=form.cleaned_data['doc']).order_by('pagina', 'lado').last()
				if _p:
					if _p.lado > 1:
						p = _p.pagina+1
					else:
						if documento.frenteverso:
							p = _p.pagina
							lado = 2
						else:
							p = _p.pagina+1
				else:
					p = 1
			else: 
				documento = None
				p = 1
			for f in request.FILES.getlist('arquivo'):
				instance = Pagina(
					tipo = pagina.tipo,
					texto = pagina.texto,
					pagina = p,
					lado = lado,
					user_add = request.user.pk,
					date_add = timezone.now(),
					arquivo = f,
					documento = documento
				)
				instance.arquivo.name = 'arquivos/'+pagina.tipo.pasta+'/'+instance.arquivo.name 
				instance.save()
				if form.cleaned_data['ocr']=='s':
					instance.texto = get_ocr(instance.arquivo.name)
					instance.texto = str(instance.texto).replace('\\n', ' ')
					instance.save()
				if count==1:
					primeiro = instance
				count = count + 1
				if documento:
					if documento.frenteverso:
						if lado==1:
							lado = 2
						else:
							p = p+1
							lado = 1
					else:
						lado = 1
						p = p+1
				else:
					lado = 1
					p = 1
			data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': primeiro.pk }) }
			return JsonResponse(data)
		else:
			data = {'is_valid': False, 'url': reverse('ged:pagina_new_livro', kwargs={'livro_pk': (documento and documento.pk or 0) }) }
			return JsonResponse(data)
	else:
		if livro:
			form = PaginaForm(initial={'doc':livro.pk})
		else:
			form = PaginaForm()
		#form.fields['tipo'].queryset = Tipo.objects.filter(removido=False)
		action = reverse('ged:pagina_new_livro', kwargs={'livro_pk': 0 }) 
		ultima = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina', 'lado').last()
		if ultima:
			lado_livro = (ultima.lado == 1 and 'Frente' or 'Verso')
		else:
			lado_livro = 'Frente'
		tipo_livro = (livro.frenteverso == 0 and 'Não' or 'Sim')
		infor_livro = {'ultima': (ultima and ultima.pagina or 0), 'lado_livro': lado_livro, 'tipo_livro': tipo_livro}
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'infor_livro': infor_livro, 'action': action})

@login_required(login_url='login:login')
def pagina_new_tipo(request, tipo_pk):
	time.sleep(.300)
	if tipo_pk:
		try:
			tipo = Tipo.objects.get(pk=tipo_pk)
		except Tipo.DoesNotExist:
			tipo = 0
	if request.method=="POST":
		form = PaginaForm(request.POST, request.FILES)
		if form.is_valid():
			pagina = form.save(commit=False)
			if form.cleaned_data['doc']:
				documento = Documento.objects.get(pk=form.cleaned_data['doc'])
				_p = Pagina.objects.filter(removido=False, documento=form.cleaned_data['doc']).order_by('pagina').last()
				if _p:
					if _p.lado > 1:
						p = _p.pagina+1
					else:
						if documento.frenteverso:
							p = _p.pagina
							lado = 2
						else:
							p = _p.pagina+1
				else:
					p = 1
			else: 
				documento = None
				p = 1
			count=1
			lado = 1
			for f in request.FILES.getlist('arquivo'):
				instance = Pagina(
					tipo = pagina.tipo,
					texto = pagina.texto,
					pagina = p,
					lado = lado,
					user_add = request.user.pk,
					date_add = timezone.now(),
					arquivo = f,
					documento = documento
				)
				instance.arquivo.name = 'arquivos/'+pagina.tipo.pasta+'/'+instance.arquivo.name 
				instance.save()
				if form.cleaned_data['ocr']=='s':
					instance.texto = get_ocr(instance.arquivo.name)
					instance.texto = str(instance.texto).replace('\\n', ' ')
					instance.save()
				if count==1:
					primeiro = instance
				count = count + 1
				if documento:
					if documento.frenteverso:
						if lado==1:
							lado = 2
						else:
							p = p+1
							lado = 1
					else:
						lado = 1
						p = p+1
				else:
					lado = 1
					p = 1
			data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': primeiro.pk }) }
			return JsonResponse(data)
		else:
			data = {'is_valid': False, 'url': reverse('ged:pagina_new_livro', kwargs={'livro_pk': (documento and documento.pk or 0) }) }
			return JsonResponse(data)
	else:
		if tipo:
			form = PaginaForm(initial={'tipo':tipo})
		else:
			form = PaginaForm()
		#form.fields['tipo'].queryset = Tipo.objects.filter(removido=False)
		action = reverse('ged:pagina_new_tipo', kwargs={'tipo_pk': 0 }) 
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':0, 'action': action})

@login_required(login_url='login:login')
def pagina_editj(request):
	if request.method=='GET':
		return redirect(reverse('ged:pagina_edit', kwargs={'pk': request.GET.get('id')}))

@login_required(login_url='login:login')
def pagina_edit(request, pk):
	time.sleep(.300)
	pagina = Pagina.objects.get(pk=pk)
	old_pagina = Pagina.objects.get(pk=pk)
	livro = pagina.documento
	if request.method=="POST":
		form = PaginaFormJ(request.POST, request.FILES, instance=pagina)
		if form.is_valid():
			pagina = form.save(commit=False)
			if old_pagina.arquivo != pagina.arquivo:
				pagina.arquivo.name = 'arquivos/'+pagina.tipo.pasta+'/'+pagina.arquivo.name
			pagina.user_up = request.user.pk
			pagina.date_up = timezone.now()
			pagina.save()
			data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': pagina.pk }) }
			return JsonResponse(data)
		else:
			data = {'is_valid': False, 'url': reverse('ged:pagina_new_livro', kwargs={'livro_pk': (pagina.documento and pagina.documento.pk or 0) }) }
			return JsonResponse(data)
	else:
		if pagina.texto:
			form = PaginaFormJRead(instance=pagina)
		else:
			form = PaginaFormJ(instance=pagina)
		# handle_uploaded_file(get_imagem(pagina.arquivo.name))
		arquivo = pagina.arquivo.url
		#form.fields['tipo'].queryset = Tipo.objects.filter(removido=False)
		if livro:
			p = Pagina.objects.filter(removido=False, documento=livro).order_by('pagina', 'lado')
			if p.count()>1:
				if p.last().pagina==pagina.pagina:
					if p.last().lado == pagina.lado:
						anterior = True
						proximo = False
					else:
						anterior = True
						proximo = True
				else: 
					anterior = proximo = True
				if p.last().pagina > pagina.pagina:
					proximo = True
					if pagina.pagina > 1:
						anterior = True
					else: 
						if pagina.lado > 1:
							anterior=True
						else:
							anterior = False
			else:
				anterior = proximo = False
		else:
			p = Pagina.objects.filter(removido=False, pk__lt=pagina.pk)
			if p:
				anterior = True
			else:
				anterior = False
			p = Pagina.objects.filter(removido=False, pk__gt=pagina.pk)
			if p:
				proximo = True
			else:
				proximo = False
		action = reverse('ged:pagina_edit', kwargs={'pk': pagina.pk })
		if livro:
			ultima = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina', 'lado').last()
			if ultima:
				lado_livro = (ultima.lado == 1 and 'Frente' or 'Verso')
			else:
				lado_livro = 'Frente'
			tipo_livro = (livro.frenteverso == 0 and 'Não' or 'Sim')
			infor_livro = {'ultima': (ultima and ultima.pagina or 0), 'lado_livro': lado_livro, 'tipo_livro': tipo_livro}
			return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'infor_livro': infor_livro, 'anterior': anterior, 'proximo': proximo, 'action': action, 'arquivo': arquivo})
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'anterior': anterior, 'proximo': proximo, 'action': action, 'arquivo': arquivo})

@login_required(login_url='login:login')
def pagina_edit_e(request, pk):
	time.sleep(.300)
	pagina = Pagina.objects.get(pk=pk)
	old_pagina = Pagina.objects.get(pk=pk)
	livro = pagina.documento
	if request.method=="POST":
		form = PaginaFormJ(request.POST, request.FILES, instance=pagina)
		if form.is_valid():
			pagina = form.save(commit=False)
			if old_pagina.arquivo != pagina.arquivo:
				pagina.arquivo.name = 'arquivos/'+pagina.tipo.pasta+'/'+pagina.arquivo.name
			pagina.user_up = request.user.pk
			pagina.date_up = timezone.now()
			pagina.save()
			data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': pagina.pk }) }
			return JsonResponse(data)
		else:
			data = {'is_valid': False, 'url': reverse('ged:pagina_new_livro', kwargs={'livro_pk': (pagina.documento and pagina.documento.pk or 0) }) }
			return JsonResponse(data)
	else:
		form = PaginaFormJ(instance=pagina)
		# handle_uploaded_file(get_imagem(pagina.arquivo.name))
		arquivo = pagina.arquivo.url
		#form.fields['tipo'].queryset = Tipo.objects.filter(removido=False)
		if livro:
			p = Pagina.objects.filter(removido=False, documento=livro).order_by('pagina', 'lado')
			if p.count()>1:
				if p.last().pagina==pagina.pagina:
					if p.last().lado == pagina.lado:
						anterior = True
						proximo = False
					else:
						anterior = True
						proximo = True
				else: 
					anterior = proximo = True
				if p.last().pagina > pagina.pagina:
					proximo = True
					if pagina.pagina > 1:
						anterior = True
					else: 
						if pagina.lado > 1:
							anterior=True
						else:
							anterior = False
			else:
				anterior = proximo = False
		else:
			p = Pagina.objects.filter(removido=False, pk__lt=pagina.pk)
			if p:
				anterior = True
			else:
				anterior = False
			p = Pagina.objects.filter(removido=False, pk__gt=pagina.pk)
			if p:
				proximo = True
			else:
				proximo = False
		action = reverse('ged:pagina_edit', kwargs={'pk': pagina.pk })
		editar = True
		if livro:
			ultima = Pagina.objects.filter(removido=False, documento=livro.pk).order_by('pagina', 'lado').last()
			if ultima:
				lado_livro = (ultima.lado == 1 and 'Frente' or 'Verso')
			else:
				lado_livro = 'Frente'
			tipo_livro = (livro.frenteverso == 0 and 'Não' or 'Sim')
			infor_livro = {'ultima': (ultima and ultima.pagina or 0), 'lado_livro': lado_livro, 'tipo_livro': tipo_livro}
			return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'infor_livro': infor_livro, 'anterior': anterior, 'proximo': proximo, 'action': action, 'arquivo': arquivo, 'editar': editar	})
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'anterior': anterior, 'proximo': proximo, 'action': action, 'arquivo': arquivo, 'editar': editar	})

@login_required(login_url='login:login')
def pagina_edit_p(request):
	p = Pagina.objects.get(pk=request.GET.get('id'))
	if request.GET.get('acao')=='prop':
		pagina = Pagina.objects.filter(removido=False, documento=p.documento.pk, pagina=p.pagina, lado__gt=p.lado).first()
		if not pagina:
			pagina = Pagina.objects.filter(removido=False, documento=p.documento.pk, pagina__gt=p.pagina).order_by('pagina', 'lado').first()
	if request.GET.get('acao')=='antp':
		pagina = Pagina.objects.filter(removido=False, documento=p.documento.pk, pagina=p.pagina, lado__lt=p.lado).first()
		if not pagina:
			pagina = Pagina.objects.filter(removido=False, documento=p.documento.pk, pagina__lt=p.pagina).order_by('pagina', 'lado').last()
	if request.GET.get('acao')=='proi':
		pagina = Pagina.objects.filter(removido=False, pk__gt=p.pk, documento__isnull=True).order_by('pk').first()
	if request.GET.get('acao')=='anti':
		pagina = Pagina.objects.filter(removido=False, pk__lt=p.pk, documento__isnull=True).order_by('pk').last()
	print (pagina)
	data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': pagina.pk }) }
	return JsonResponse(data)

@login_required(login_url='login:login')
def paginacao(request):
	p = Pagina.objects.get(pk=request.GET.get('id'))
	# print(str(request.GET.get('id'))+' - '+str(p.pk)+' - '+str(request.GET.get('livro'))+' - '+str(p.documento.pk) +' - '+str(request.GET.get('lado'))+' - '+str(p.lado)+' - '+str(request.GET.get('pagina')+' - '+str(p.pagina)) )
	if str(p.pagina) == request.GET.get('pagina') and str(p.lado) == request.GET.get('lado'):
		data = {'is_valid': True, 'msg': ''}
		return JsonResponse(data)
	if not Pagina.objects.filter(removido=False, pagina=request.GET.get('pagina'), lado=request.GET.get('lado')):
		data = {'is_valid': True, 'msg': ''}
		return JsonResponse(data)
	data = {'is_valid': False, 'msg': 'Por favor escolher outra página.'}
	return JsonResponse(data)


@login_required(login_url='login:login')
def pagina_list(request):
	paginas = Pagina.objects.filter(removido=False)
	return render(request, 'ged/pagina_list.html', {'paginas': paginas})

@login_required(login_url='login:login')
def livro_list(request):
	livros = Documento.objects.filter(removido=False)
	paginator = Paginator(livros, 12)
	try:
		page = int(request.GET.get('page', '1'))	
	except ValueError:
		page = 1

	try:
		lvs = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lvs = paginator.page(paginator.num_pages)
	return render(request, 'ged/livro_list.html', {'livros': lvs})

@login_required(login_url='login:login')
def backup_list(request):
	bs = Backup.objects.all()
	class _Backup:
		usuario = None
		data = None
	backups = []	
	for b in bs:
		_backup = _Backup()
		_backup.usuario = User.objects.get(pk=b.user_add)
		_backup.data = b.date_add
		backups.append(_backup)
	paginator = Paginator(backups, 12)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1
	try:
		bacs = paginator.page(page)
	except (EmptyPage, InvalidPage):
		bacs = paginator.page(paginator.num_pages)
	return render(request, 'ged/backup.html', {'backups': bacs})

@login_required(login_url='login:login')
def backup(request):
	time.sleep(.300)
	arq = open(os.path.join(settings.MEDIA_ROOT,'arquivos/backup.txt'), 'w')
	texto = []
	paginas = serializers.serialize('json', Pagina.objects.all())
	texto.append(paginas)
	texto.append('\n')
	texto.append('\n')
	documentos = serializers.serialize('json', Documento.objects.all())
	texto.append(documentos)
	texto.append('\n')
	texto.append('\n')
	empresas = serializers.serialize('json', Empresa.objects.all())
	texto.append(empresas)
	texto.append('\n')
	texto.append('\n')
	tipos = serializers.serialize('json', Tipo.objects.all())
	texto.append(tipos)
	texto.append('\n')
	texto.append('\n')
	users = serializers.serialize('json', User.objects.all())
	texto.append(users)
	texto.append('\n')
	texto.append('\n')
	arq.writelines(texto)
	arq.close()

	make_archive(os.path.join(settings.MEDIA_ROOT,'backups/backup'+timezone.now().strftime('%Y%m%d')), 'zip', os.path.join(settings.MEDIA_ROOT, 'arquivos'))
	b = Backup(
			user_add = request.user.pk, 
			date_add = timezone.now()
			)
	b.save()
	filePath = os.path.join(settings.MEDIA_ROOT,'backups/backup'+timezone.now().strftime('%Y%m%d'))+'.zip'
	if os.path.exists(filePath):
		data = {'is_valid': True, 'url': '/media/backups/backup'+timezone.now().strftime('%Y%m%d')+'.zip' }
		return JsonResponse(data)
	data = {'is_valid': False, 'url': reverse('ged:backup_list') }
	return JsonResponse(data)
		# fsock = open(filePath,"rb")
		# response = HttpResponse(fsock, content_type='application/zip')
		# response['Content-Disposition'] = 'attachment; filename=backup'+timezone.now().strftime('%Y%m%d')+'.zip'
		# return response

def caminho(tipo):
	c = tipo.pasta
	while(tipo):
		tipo = tipo.tipo
		if tipo:
			c = tipo.pasta +'/'+c
	return c

def handle_uploaded_file(file):
	pasta = os.path.join(settings.MEDIA_ROOT, 'tmp/')
	if not os.path.exists(pasta):
		os.mkdir(pasta)
	file.save(pasta+'img.jpg')	

def get_imagem(file):
	file_path = os.path.join(settings.MEDIA_ROOT, file)
	image_pdf = Image(filename=file_path)
	imagem_jpeg = image_pdf.convert('jpeg')
	return imagem_jpeg

def get_ocr(file):
	tool = pyocr.get_available_tools()[0]
	lang = tool.get_available_languages()[0]

	req_image = []
	final_text = []

	file_path = os.path.join(settings.MEDIA_ROOT, file)

	image_pdf = Image(filename=file_path, resolution=300)
	imagem_jpeg = image_pdf.convert('jpeg')

	for img in imagem_jpeg.sequence:
		img_page = Image(image=img)
		req_image.append(img_page.make_blob('jpeg'))

	for img in req_image:
		txt = tool.image_to_string(
			PI.open(io.BytesIO(img)),
			lang=lang,
			builder=pyocr.builders.TextBuilder()
			)
		final_text.append(txt)
	return final_text

def tipopasta(text):
	text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
	text = text.replace(" ", "")
	return text

# def pagina_newj(request):
# 	if request.method=="POST":
# 		f = request.FILES['arquivo']
# 		if request.POST['doc']:
# 			documento = Documento.objects.get(pk=request.POST['doc'])
# 		else: 
# 			documento = None
# 		if request.POST['tipo']:
# 			tipo = Tipo.objects.get(pk=request.POST['tipo'])
# 		else: 
# 			tipo = None
# 		try:
# 			_p = Pagina.objects.last()
# 		except Pagina.DoesNotExist:
# 			_p = None
# 		p = int(_p.pk)+2
# 		if request.POST['primeiro']:
# 			p = p - request.POST['primeiro']
# 		else: 
# 			p = 1
# 		pagina = Pagina(
# 										tipo = tipo,
# 										texto = '',
# 										pagina = p,
# 										user_add = request.user.pk,
# 										date_add = timezone.now(),
# 										arquivo = f,
# 										documento = documento
# 									)
# 		pagina.arquivo.name = 'arquivos/'+tipo.nome+'/'+pagina.arquivo.name 
# 		pagina.save()
# 		data = {'is_valid': True, 'pk': pagina.pk }
# 		return JsonResponse(data)
# 	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro})
