from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Tipo, Empresa, Pagina, Documento
from .forms import TipoForm, EmpresaForm, PaginaForm, PaginaFormJ, EmpresaFormRead, DocumentoForm
from django.utils import timezone
import os
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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

class Pasta:
		titulo = None
		data = None
		usuario = None
		id = None
		tipo = None

paginas_list = []

# Create your views here.
@login_required(login_url='login:login')
def home(request):
	livros = Documento.objects.filter(removido=False)
	_livros = Documento.objects.filter(removido=True)
	paginas = Pagina.objects.filter(removido=False, documento__isnull=True, tipo__isnull=True)
	grupos = Tipo.objects.filter(removido=False)
	_grupos = Tipo.objects.filter(removido=True)
	pastas = []
	for grupo in grupos:
		p = Pasta()
		p.titulo = grupo.nome
		p.id = grupo.pk
		p.tipo = 'g'
		pastas.append(p)	
	for grupo in _grupos:
		if Pagina.objects.filter(removido=False, tipo=grupo.pk):
			p = Pasta()
			p.titulo = grupo.nome
			p.id = grupo.pk
			p.tipo = 'g'
			pastas.append(p)
	for livro in livros:
		p = Pasta()
		p.titulo = livro.titulo
		p.id = livro.pk
		p.tipo = 'l'
		pastas.append(p)
	for livro in _livros:
		if Pagina.objects.filter(removido=False, documento=livro.pk):
			p = Pasta()
			p.titulo = livro.titulo
			p.id = livro.pk
			p.tipo = 'l'
			pastas.append(p)
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
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
		paginas = Pagina.objects.filter(removido=False, texto__icontains=request.POST.get('txt_busca'))
		for pagina in paginas:
			p = Pasta()
			p.titulo = pagina.tipo.nome
			p.id = pagina.pk
			p.tipo = 'p'
			p.data = pagina.date_add
			u = User.objects.get(pk=pagina.user_add)
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
	paginas = Pagina.objects.filter(removido=False, documento=pk)
	pastas = []
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
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
	paginas = Pagina.objects.filter(removido=False, tipo=pk, documento__isnull=True)
	livros = Documento.objects.all()
	pastas = []
	for livro in livros:
		if Pagina.objects.filter(removido=False, documento=livro.pk, tipo=pk):
			p = Pasta()
			p.titulo = livro.titulo
			p.id = livro.pk
			p.tipo = 'l'
			pastas.append(p)
	for pagina in paginas:
		p = Pasta()
		p.titulo = pagina.tipo.nome
		p.id = pagina.pk
		p.tipo = 'p'
		p.data = pagina.date_add
		u = User.objects.get(pk=pagina.user_add)
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
	return render(request, 'ged/tipo_list.html', {'grupos': grupos})

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
			if form.cleaned_data['doc']:
				documento = Documento.objects.get(pk=form.cleaned_data['doc'])
			else: 
				documento = None
			count=1
			p = 1
			for f in request.FILES.getlist('arquivo'):
				instance = Pagina(
					tipo = pagina.tipo,
					texto = pagina.texto,
					pagina = p,
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
					p = count
				else:
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
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'action': action})

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
			else: 
				documento = None
			count=1
			p = 1
			for f in request.FILES.getlist('arquivo'):
				instance = Pagina(
					tipo = pagina.tipo,
					texto = pagina.texto,
					pagina = p,
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
					p = count
				else:
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
	livro = pagina.documento
	if request.method=="POST":
		form = PaginaFormJ(request.POST, request.FILES, instance=pagina)
		#form.fields['tipo'].queryset = Tipo.objects.filter(removido=False)
		if form.is_valid():
			pagina = form.save(commit=False)
			if form.cleaned_data['doc']:
				pagina.documento = Documento.objects.get(pk=form.cleaned_data['doc'])
			if pagina.arquivo:
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
			p = Pagina.objects.filter(documento=livro)
			if p.count()>1:
				if p.count()==pagina.pagina:
					anterior = True
					proximo = False
				else: 
					anterior = proximo = True
				if p.count() > pagina.pagina:
					proximo = True
					if pagina.pagina > 1:
						anterior = True
					else: 
						anterior = False
			else:
				anterior = proximo = False
		else:
			p = Pagina.objects.filter(pk__lt=pagina.pk)
			if p:
				anterior = True
			else:
				anterior = False
			p = Pagina.objects.filter(pk__gt=pagina.pk)
			if p:
				proximo = True
			else:
				proximo = False
		action = reverse('ged:pagina_edit', kwargs={'pk': pagina.pk })
	return render(request, 'ged/pagina_form.html', {'form': form, 'livro':livro, 'anterior': anterior, 'proximo': proximo, 'action': action, 'arquivo': arquivo})

@login_required(login_url='login:login')
def pagina_edit_p(request):
	p = Pagina.objects.get(pk=request.GET.get('id'))
	if request.GET.get('acao')=='prop':
		pagina = Pagina.objects.filter(documento=p.documento.pk, pagina__gt=p.pagina).first()
	if request.GET.get('acao')=='antp':
		pagina = Pagina.objects.filter(documento=p.documento.pk, pagina__lt=p.pagina).last()
	if request.GET.get('acao')=='proi':
		pagina = Pagina.objects.filter(pk__gt=p.pk, documento__isnull=True).first()
	if request.GET.get('acao')=='anti':
		pagina = Pagina.objects.filter(pk__lt=p.pk, documento__isnull=True).last()
	data = {'is_valid': True, 'url': reverse('ged:pagina_edit', kwargs={'pk': pagina.pk }) }
	return JsonResponse(data)


@login_required(login_url='login:login')
def pagina_list(request):
	paginas = Pagina.objects.filter(removido=False)
	return render(request, 'ged/pagina_list.html', {'paginas': paginas})

@login_required(login_url='login:login')
def livro_list(request):
	livros = Documento.objects.filter(removido=False)
	return render(request, 'ged/livro_list.html', {'livros': livros})

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