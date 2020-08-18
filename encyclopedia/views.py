from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse

from . import util

import random

import markdown2

class searchQuery(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'Search', 'placeholder': 'Search Encyclopedia'}))

class newPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type Here...'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "query_data": searchQuery()
    })

def entry(request, title):

    data = util.get_entry(title)
    if data is  None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page Not Found!",
            "query_data": searchQuery()
        })
    content = markdown2.markdown(data)
    title = content.split('h1')[1][1:-2]
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content,
        "query_data": searchQuery()
    })

def search(request):
    query_data = searchQuery(request.GET)
    if query_data.is_valid():
        q = query_data.cleaned_data["q"]
        if q.upper() in [entry.upper() for entry in util.list_entries()]:
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={"title": q}))
        else:
            match_list = []
            for entry in util.list_entries():
                if q.upper() in entry.upper():
                    match_list.append(entry)
            return render(request, "encyclopedia/search.html", {
                "entries": match_list, 
                "query_data": searchQuery()
            })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "Not Valid Form"
        })

def create(request):
    if request.method == "POST":
        new_page_data = newPageForm(request.POST)
        if new_page_data.is_valid():
            title = new_page_data.cleaned_data["title"]
            content = new_page_data.cleaned_data["content"]
            if title.upper() in [entry.upper() for entry in util.list_entries()]:
                return render(request, "encyclopedia/create.html", {
                    "new_page_data": new_page_data,
                    "message": "The Page Already Exists!", 
                    "query_data": searchQuery()
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={"title": title}))
    return render(request, "encyclopedia/create.html", {
        "new_page_data": newPageForm(), 
        "query_data": searchQuery()
    })

def edit(request, title):
    if request.method == "POST":
        edit_page_data = newPageForm(request.POST)
        if edit_page_data.is_valid():
            title_latest = edit_page_data.cleaned_data["title"]
            if title_latest != title:
                edit_page_data.cleaned_data["title"] = title
                return render(request, "encyclopedia/edit.html", {
                    "edit_page_data": edit_page_data,
                    "title": title, 
                    "message": "You Cannot Change The Title!", 
                    "query_data": searchQuery()
                })
            else:
                content = edit_page_data.cleaned_data["content"]
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={"title": title}))
        else:
            return render(request, "encyclopedia/error.html", {
                "message": "Not Valid Form", 
                "query_data": searchQuery()
            })

    content = util.get_entry(title)
    data = {
        "title": title,
        "content": content
    }
    edit_page_data = newPageForm(data)

    if edit_page_data.is_valid():
        edit_page_data.cleaned_data["title"] = title
        edit_page_data.cleaned_data["content"] = content
        return render(request, "encyclopedia/edit.html", {
            "edit_page_data": edit_page_data,
            "title": title, 
            "query_data": searchQuery()
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "Not Valid Form", 
            "query_data": searchQuery()
        })

def random_page(request):
    title = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={"title": title}))
