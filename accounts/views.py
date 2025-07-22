from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Profile # Assumindo que você tem um modelo Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages # Importar o módulo messages

def register_or_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')

        if not username or not phone_number:
            messages.error(request, "Por favor, preencha o nome de usuário e o telefone.")
            return render(request, 'accounts/login.html')

        try:
            # Tenta encontrar um perfil com o número de telefone fornecido
            profile = Profile.objects.get(phone_number=phone_number)
            user = profile.user

            # Se o perfil existe, verifica se o nome de usuário corresponde
            if user.username != username:
                messages.error(request, "O nome de usuário não corresponde ao telefone fornecido.")
                return render(request, 'accounts/login.html')
            
            # Se tudo corresponde, faz o login do usuário existente
            login(request, user)
            messages.success(request, f"Bem-vindo de volta, {user.username}!")
            return redirect('home')

        except Profile.DoesNotExist:
            # Se o perfil não existe, é uma tentativa de novo registro.
            # Primeiro, verifica se o nome de usuário já está em uso.
            if User.objects.filter(username=username).exists():
                messages.error(request, "Este nome de usuário já está em uso. Por favor, escolha outro ou faça login com seu telefone e nome de usuário existentes.")
                return render(request, 'accounts/login.html')
            
            # Se o nome de usuário não está em uso, cria um novo usuário e perfil
            try:
                user = User.objects.create_user(username=username, password=None) # Use create_user para hashing de senha se for adicionar senhas
                # Se você não usa senhas, User.objects.create(username=username) ainda é válido
                Profile.objects.create(user=user, phone_number=phone_number)
                login(request, user)
                messages.success(request, f"Conta criada e login realizado com sucesso, {user.username}!")
                return render(request, 'core/home.html')
            except Exception as e:
                # Captura qualquer outro erro durante a criação (ex: validação de modelo)
                messages.error(request, f"Ocorreu um erro ao criar sua conta: {e}")
                return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')

def logout_view(request):
    """
    Realiza o logout do usuário e redireciona para a página de login.
    """
    logout(request)
    messages.info(request, "Você foi desconectado com sucesso.")
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    data = {
        "username": user.username,
        "phone": str(profile.phone_number) if profile.phone_number else "Sem telefone",
    }
    return JsonResponse(data)