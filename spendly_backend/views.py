from pathlib import Path
from django.http import HttpResponse, FileResponse, Http404
from django.views.static import serve as static_serve

def frontend_index(request):
    root = Path(__file__).resolve().parent.parent.parent
    index_path = root / "index.html"
    if not index_path.exists():
        raise Http404()
    return FileResponse(open(index_path, "rb"), content_type="text/html")

def frontend_static(request, path):
    root = Path(__file__).resolve().parent.parent.parent
    return static_serve(request, path, document_root=str(root))
