import random
from django import forms
from django.utils import html
from markdown2 import Markdown, markdown
from django.urls import reverse
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render

from . import util

class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search wiki"
    }))

class CreateForm(forms.Form):
    title = forms.CharField(label='',widget=forms.TextInput(attrs={
        "placeholder": "Page Title"
    }))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "placeholder": "Enter page contents using Github Markdown"
    }))

class EditForm(forms.Form):
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "placeholder": "Enter page contents using GitHub Markdown"
    }))

def index(request):
    return render(request, "encyclopedia/index.html",{
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })


def entry(request, title):
    entry_name = util.get_entry(title)
    if entry_name != None:
        entry_HTML = Markdown().convert(entry_name)
        return render(request, "encyclopedia/entry.html",{
            "title": title,
            "entry": entry_HTML,
            "search_form": SearchForm(),
        })
    else:
        related_titles = util.related_titles(title)
        
        return render(request, "enxyxlopedia/error.html", {
            "title": title,
            "related_titles": related_titles,
            "search_form": SearchForm()
        })
   
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_name = util.get_entry(title)

            print('search request: ', title)
            
            if entry_name:
                return redirect(reverse('entry', args=[title]))
            else:
                related_titles = util.related_titles(title)

                return render(request, "encyclopedia/search.html", {
                    "title": title,
                    "realated_search": related_titles,
                    "search_form": SearchForm()
                })

        #otherwise form not posted or form not valid return to index page:
        return redirect(reverse('index'))

def create(request):
    if request.method == "GET":
       return render(request, "encyclopedia/create.html",{
           "create_form": CreateForm(),
           "search_form": SearchForm()
       })

    elif request.method == "POST":
        form = CreateForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
        else:
            messages.error(request, 'Entry form not valid, please enter a valid entry.')
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "search_form": SearchForm()
            })

        if util.get_entry(title):
            messages.error(request, "This page title already exists. Please go to that page and edit the entry instead.")
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "search_form": SearchForm()
            })

        else: 
            util.save_entry(title, text)
            messages.success(request, f'New page "{title}" created successfully!')
            return redirect(reverse('entry', args=[title]))

def edit(request, title):
    if request.method == "GET":
        text = util.get_entry(title)

        if text == None:
            messages.error(request, f'"{title}"" page does not exist and can\'t be edited, please create a new page instead!')
        return render(request,"encyclopedia/edit.html", {
            "title": title, 
            "edit_form": EditForm(initial={'text': text}),
            "search_form": SearchForm()
        })
    
    elif request.method == "POST":
        form = EditForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['text']
            util.save_entry(title, text)
            messages.success(request, f'Entry "{title}" updated successfully!')
            return redirect(reverse('entry', args=[title]))
        
        else:
            messages.error(request, f'Editing form not valid, please try again!')
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "edit_form": form,
                "search_form": SearchForm()
            })

def random_title(request):
    #random wiki entry
    titles = util.list_entries()
    title = random.choice(titles)

    return redirect(reverse('entry', args=[title]))