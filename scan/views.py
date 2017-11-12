from django.shortcuts import render
import datetime

def home(request):
	return render(request, 'scan/base.html', {'current_date': datetime.datetime.now()})