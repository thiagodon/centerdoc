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

class PaginaFormJ(forms.ModelForm):
	doc = forms.IntegerField(widget = forms.HiddenInput(), label='',  required = False)
	tipo = forms.ModelChoiceField(queryset= Tipo.objects.filter(removido=False))
	class Meta:
		model = Pagina
		fields = ( 'tipo', 'texto', 'pagina',  'arquivo', 'pagina', 'doc',)

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

class DocumentoForm(forms.ModelForm):
	class Meta:
		model = Documento
		fields = ('capa', 'titulo', 'informacoes', 'paginas', 'ano', )