from django.shortcuts import render, redirect
from django.urls import reverse
from . import util
import markdown
import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry_view(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The entry {'title'} was not found."
        })
    
    html_content = markdown.markdown(content)
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get("q", "").strip()  # Ambil query dari form

    if query:
        content = util.get_entry(query)  # Cek apakah ada entry dengan nama yang sama
        if content:
            return redirect(reverse("entry", args=[query]))  # Redirect ke halaman entry

        # Jika tidak ada entry dengan nama yang sama, cari yang mengandung query
        all_entries = util.list_entries()
        results = [entry for entry in all_entries if query.lower() in entry.lower()]

        return render(request, "encyclopedia/search.html", {
            "query": query,
            "results": results
        })

    return redirect("index")  # Jika query kosong, kembali ke halaman utama

def create_page(request):
    if request.method == "POST":
        title = request.POST["title"].strip()
        content = request.POST["content"].strip()

        # Check if the entry already exists
        if title in util.list_entries():
            return render(request, "encyclopedia/error.html", {
                "message": f"The entry '{title}' already exists."
            })
        # Masih kurang, jika membuat page baru yang sama
        # tapi menggunakan huruf besar dan kecil berbeda
        # itu masih bisa

        # Check if title and content are provided
        if title and content:
            util.save_entry(title, content)  # Save the entry
            return redirect(reverse("entry", args=[title]))  # Redirect to the new entry

        # Show an error message if fields are empty
        return render(request, "encyclopedia/create.html", {
            "error": "Both title and content are required."
        })

    return render(request, "encyclopedia/create.html")

def edit_page(request, title):
    if request.method == "POST":
        content = request.POST["content"]  # Get updated content
        util.save_entry(title, content)  # Save the updated entry
        return redirect(reverse("entry", args=[title]))  # Redirect to entry page

    # Load the existing content to show in the textarea
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' does not exist."
        })

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })

def random_page(request):
    entries = util.list_entries()  # Get all entries
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries found."
        })
    
    random_entry = random.choice(entries)  # Pick a random entry
    return redirect("entry", title=random_entry)  # Redirect to that entry
