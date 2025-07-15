from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Profile
from django.contrib.auth.decorators import login_required

def register_or_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')

        if not username or not phone_number:
            return HttpResponse("Preencha username e telefone", status=400)

        try:
            profile = Profile.objects.get(phone_number=phone_number)
            user = profile.user
            if user.username != username:
                return HttpResponse("Usuário não confere com telefone", status=400)
        except Profile.DoesNotExist:
            user = User.objects.create(username=username)
            Profile.objects.create(user=user, phone_number=phone_number)

        login(request, user)  # abre sessão
        return redirect('profile')

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'phone_number': profile.phone_number,
    })