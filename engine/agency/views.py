from django.views.generic import View
from django.shortcuts import render, redirect
from engine import models
from . import forms


class List(View):
    def get(self, request):
        agencies = models.Agency.objects.all().order_by('-id')

        return render(request, 'agency/list.html', dict(agencies=agencies))


class Create(View):
    def get(self, request):
        form = forms.Create()
        return render(request, 'create.html', {'form': form})

    def post(self, request):
        form = forms.Create(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agency:list')
        else:
            return render(request, 'create.html', {'form': form})


class Profile(View):
    def get(selfm, request, uuid):
        agency = models.Agency.objects.get(uuid=uuid)
        creators = models.Creator.objects.filter(agency=agency.pk)

        return render(request, 'agency/profile.html', dict(
            agency=agency,
            creators=creators,
        ))
