from django.shortcuts import redirect

def esta_logueado(view):
    def interna(request, *args, **kwargs):
        if request.session.get('logueado', False):
            return view(request, *args, **kwargs)
        elif request.session.get('logueadoA', False):
            return redirect('/bienvenida_adminA')
        elif request.session.get('autenticadoA', False):
            return redirect('/multifactorA')
        else:
            return redirect('/login')
    return interna

def dos_pasos(view):
    def interna(request, *args, **kwargs):
        if request.session.get('autenticado', False):
            return view(request, *args, **kwargs)
        elif request.session.get('autenticadoA', False):
            return redirect('/multifactorA')
        elif request.session.get('logueadoA', False):
            return redirect('/bienvenida_adminA')
        else:
            return redirect('/login')
    return interna

def esta_logueadoA(view):
    def interna(request, *args, **kwargs):
        if request.session.get('logueadoA', False):
            return view(request, *args, **kwargs)
        else:
            return redirect('/login')
    return interna

def dos_pasosA(view):
    def interna(request, *args, **kwargs):
        if request.session.get('autenticadoA', False):
            return view(request, *args, **kwargs)
        else:
            return redirect('/login')
    return interna
