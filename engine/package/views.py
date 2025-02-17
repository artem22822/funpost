from django.views.generic import View
from django.shortcuts import render, redirect
from engine import models
from . import forms
from telegram import Telegram


class List(View):
    def get(self, request):
        packages = models.Package.objects.all().order_by('-id')
        return render(request, 'package/list.html', {'packages': packages})


class Request(View):
    def get(self, request):
        slug = request.GET['slug']
        form = forms.RequestForm()
        return render(request, 'create.html', {'form': form, 'slug': slug})

    def post(self, request):
        form = forms.RequestForm(request.POST)
        slug = request.POST['slug']
        if form.is_valid():
            form.save()
            # Telegram.new_package()

            return redirect('creator:creator_login', slug=slug)

        return render(request, 'create.html', {'form': form, 'slug': slug})


class RequestUpdate(View):
    def get(self, request):
        try:
            uuid = request.GET['accept']
            request = models.Request.objects.get(uuid=uuid)
            request.status = 0
            request.save()
            creator = request.model
            return redirect('creators:profile', slug=creator.slug)

        except KeyError:
            uuid = request.GET['reject']
            request = models.Request.objects.get(uuid=uuid)
            request.status = 1
            request.save()
            creator = request.model
            return redirect('creators:profile', slug=creator.slug)
