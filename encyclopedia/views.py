from django.shortcuts import render
from . import util
from markdown2 import Markdown
from django.http import HttpResponse
from random import randint
# Instanciar para convertir markdown a html
md = Markdown()

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
        return render(request, "encyclopedia/page.html", {
            "title": title,
            "html": html
        })
    
# Create entry
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        pages = util.list_entries()
        if title in pages:
            return HttpResponse("Title already exists", status=400)
        else: 
            util.save_entry(title, content)
            pages = util.list_entries()
            return wiki_page(request, title)
    else:
        return render(request, "encyclopedia/create.html")
    

# redirect to random wiki page
def random(request):
    pages = util.list_entries()
    random_page = pages[randint(0, (len(pages))-1)]
    return wiki_page(request, random_page)

# edit page
def edit(request, title):
    if request.method == "POST":
        content = request.POST["content"]
        util.save_entry(title, content)
        return wiki_page(request, title)
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
    

# search
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
        return render(request, "encyclopedia/404.html")
    
# 404 handler
def handler404(request, exception):
    return render(request, "encyclopedia/404.html")