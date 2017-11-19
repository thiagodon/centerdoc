from django import forms
from .models import Tipo, Empresa, Pagina, Documento

class TipoForm(forms.ModelForm):
	
	class Meta:
		model = Tipo
		fields = ('nome', )


class EmpresaForm(forms.ModelForm):
	class Meta:
		model = Empresa
		fields = ('cnpj', 'razao_social', 'fantasia', 'ie', 'logradouro', 'numero', 'bairro', 'estado', 'cidade', 'cep', 'telefone', 'email', 'site', )

class EmpresaFormRead(EmpresaForm):
  def __init__(self, *args, **kwargs):
    super(EmpresaForm, self).__init__(*args, **kwargs)
    instance = getattr(self, 'instance', None)
    for key in self.fields.keys():
      self.fields[key].widget.attrs['readonly'] = True

LADO_CHOICES = (
    ("1", "Frente"),
    ("2", "Verso")
)

class PaginaFormJ(forms.ModelForm):
	doc = forms.IntegerField(widget = forms.HiddenInput(), label='',  required = False)
	tipo = forms.ModelChoiceField(queryset= Tipo.objects.filter(removido=False))
	lado = forms.ChoiceField(label='Lado', choices=LADO_CHOICES, initial="1")

	class Meta:
		model = Pagina
		fields = ( 'tipo', 'texto', 'pagina', 'lado', 'arquivo', 'pagina', 'doc',)

class PaginaFormJRead(PaginaFormJ):
	def __init__(self, *args, **kwargs):
		super(PaginaFormJ, self).__init__(*args, **kwargs)
		instance = getattr(self, 'instance', None)
		for key in self.fields.keys():
			self.fields[key].widget.attrs['readonly'] = True
			self.fields[key].widget.attrs['disabled'] = True

OCR_CHOICES = (
    ("s", "Usar OCR"),
    ("n", "Não usar OCR")
)


class PaginaForm(forms.ModelForm):
	doc = forms.IntegerField(widget = forms.HiddenInput(), label='', required = False)
	tipo = forms.ModelChoiceField(queryset= Tipo.objects.filter(removido=False))
	ocr = forms.ChoiceField(label='OCR', choices=OCR_CHOICES, initial="n")
	class Meta:
		model = Pagina
		fields = ( 'tipo', 'ocr', 'arquivo', 'doc',)

LIVRO_CHOICES = (
    ("1", "Sim"),
    ("0", "Não")
)

class DocumentoForm(forms.ModelForm):
	frenteverso = forms.ChoiceField(label='Frente e Verso', choices=LIVRO_CHOICES)
	class Meta:
		model = Documento
		fields = ('capa', 'titulo', 'informacoes', 'paginas', 'ano', 'frenteverso')