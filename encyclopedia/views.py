from email import charset
from django.shortcuts import render
from django.urls import reverse
from . import util
from markdown2 import Markdown
from django.http import HttpResponse, HttpResponseBadRequest
from random import randint
import re
from django.shortcuts import redirect
# Instanciar para convertir markdown a html
md = Markdown()

def contains_accented_characters(text):
    regex = r'[áéíóúÁÉÍÓÚüÜñÑ]'
    return bool(re.search(regex, text))

def is_valid_content(content):
    caracteres_disponibles = r'^[\s\S]+$'
    if contains_accented_characters(content):
        return False
    return re.match(caracteres_disponibles, content) is not None


# funcion para convertir markdown a html
def markdown_to_html(entry):
    content = util.get_entry(entry)
    if content is None:
        return None
    else:
        return md.convert(content)
    
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki_page(request, title):
    html = markdown_to_html(title)
    if html is None:
        return render(request, "encyclopedia/404.html")
    else:
        try:
            return render(request, "encyclopedia/page.html", {
                "title": title,
                "html": html
            })	
        except Exception as e:
            print(e)
            return render(request, "encyclopedia/404.html")
    
# Create entry
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        exists = util.exists_entry(title)
        
        try:
            # Validar el contenido antes de guardar la nueva entrada
            if not is_valid_content(content):
                raise ValueError("Contenido no válido")
                        
            if exists:
                return render(request, "encyclopedia/create.html", {
                    "title": title,
                    "content": content,
                    "exists": True,
                    "success": False,
                })
            else:
                util.save_entry(title, content)
                return wiki_page(request, title)
        except ValueError as ve:
            return HttpResponseBadRequest(str(ve))  # Devolver un error 400 si el contenido no es válido
        except Exception as e:
            print(content)
            return render(request, "encyclopedia/create.html", {
                "title": title,
                "content": content,
                "error": True,
                "success": False,
            })
    else:
        return render(request, "encyclopedia/create.html", {
            "success": True,
        })
    
# redirect to random wiki page
def random(request):
    pages = util.list_entries()
    random_page = pages[randint(0, (len(pages))-1)]
    return wiki_page(request, random_page)

# edit page
def edit(request, title):
    if request.method == "POST":
        content = request.POST["content"]
        new_title = request.POST["title"]
        try:
            # Validar el contenido antes de guardar los cambios
            if not is_valid_content(content): 
                # Devolver un error 400 si el contenido no es válido
                return render(request, "encyclopedia/edit.html", {
                "title": new_title,
                "content": content,
                "error": True
            })

            util.save_entry(new_title, content)
            # Redirigir a la página wiki de la entrada editada
            wiki_page_url = reverse('wiki-page', args=[new_title])
            return redirect(wiki_page_url)
        except ValueError as ve:
            return HttpResponseBadRequest(str(ve))  # Devolver un error 400 si el contenido no es válido
        except Exception as e:
            return render(request, "encyclopedia/edit.html", {
                "title": new_title,
                "content": content,
                "error": True
            })
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
def search(request):
    query = request.GET['q']
    pages = util.list_entries()
    results = []
    for page in pages:
        if query.lower() in page.lower():
            results.append(page)
    results.sort()
    if len(results) == 1:
        return wiki_page(request, results[0])
    elif len(results) > 1:
        return render(request, "encyclopedia/search.html", {
            "results": results,
            "query": query
        })
    else:
        return render(request, "encyclopedia/404.html", {
            "query": query,
            "NotFound": True,
        })
    
def delete(request, title):
   response = util.delete_entry(title)
   if response:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "deleted": True,
            "title": title
        })
   else:
        return render(request, "encyclopedia/404.html")
   
def handler404(request, exception):
    return render(request, 'encyclopedia/404.html', status=404)

