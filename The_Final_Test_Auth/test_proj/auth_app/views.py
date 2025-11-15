from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, UserRole
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View


def home(request):
    return HttpResponse("""
    
    <h1>Awailable endpoints:</h1>
    <ul>
        <li>POST /api/register/</li>
        <li>POST /api/login/</li> 
        <li>GET /api/profile/</li>
        <li>GET /api/products/</li>
        <li>GET /api/users/</li>
    </ul>
    """)

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already in use'}, status=400)

        user = User(email=email, name=name)
        user.set_password(password)
        user.save()

        UserRole.objects.create(user=user, role='user')
        return Response({'message': 'success'})


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email, is_active=True)
            if user.check_password(password):
                token = user.make_token()
                return Response({
                    'token': token,
                    'user': {'id': user.id, 'email': user.email, 'name': user.name}
                })
            return Response({'error': 'wrong password'}, status=401)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=401)


class ProfileView(APIView):
    def get(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Please login'}, status=401)

        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'name': user.name
        })


class ProductsView(APIView):
    def get(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Please login'}, status=401)

        products = [
            {'id': 1, 'name': 'Smartphone', 'price': 10000},
            {'id': 2, 'name': 'Notebook', 'price': 50000},
        ]
        return Response(products)


class UsersView(APIView):
    def get(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Please login'}, status=401)

        is_admin = UserRole.objects.filter(user=request.user, role='admin').exists()
        if not is_admin:
            return Response({'error': 'For admins only'}, status=403)

        users = User.objects.filter(is_active=True)
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'name': user.name
            })

        return Response(user_list)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileView(View):
    def put(self, request):
        if not hasattr(request, 'user') or not request.user:
            return JsonResponse({'error': 'Please login'}, status=401)

        user = request.user
        data = json.loads(request.body)


        if 'name' in data:
            user.name = data['name']
        if 'email' in data:

            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return JsonResponse({'error': 'This email is already in use'}, status=400)
            user.email = data['email']

        user.save()

        return JsonResponse({
            'message': 'Profile updated',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class DeleteAccountView(View):
    def post(self, request):
        if not hasattr(request, 'user') or not request.user:
            return JsonResponse({'error': 'Please login'}, status=401)

        user = request.user


        user.is_active = False
        user.save()

        return JsonResponse({'message': 'Account has been deleted'})

def auth_test_page(request):
    return render(request, 'auth_test.html')