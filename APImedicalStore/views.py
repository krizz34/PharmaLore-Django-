from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from rest_framework import status
from rest_framework.authtoken.models import Token
from medicalStore.forms import medicForm
from medicalStore.models import medic
from .serializers import medicSerializer



@api_view(['POST'])
@permission_classes((AllowAny,))
def apiSignup(request):
    form = UserCreationForm(data=request.data)
    if form.is_valid():
        user = form.save()
        return Response("account created successfully", status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def apiLogin(request):
    username_instance = request.data.get("username")
    password_instance = request.data.get("password")
    
    if username_instance is None or password_instance is None:
        return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
    else:
        user = authenticate(username=username_instance, password=password_instance)
        
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': '{}'.format(token.key)}, status=HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apiLogout(request):
    request.auth.delete()
    return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apiCreate(request):
    createData = medicForm(request.POST)
    if createData.is_valid():
        product = createData.save()
        return Response({'id':product.id}, status = status.HTTP_201_CREATED)
    return Response(createData.errors, status= status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def apiRead(request):
    products = medic.objects.all()
    serializer = medicSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def apiUpdate(request, pk):
    product_instance = get_object_or_404(medic, pk=pk)
    form = medicForm(request.data, instance=product_instance)
    if form.is_valid():
        form.save()
        serializer = medicSerializer(product_instance)
        return Response(serializer.data)
    else:
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def apiDelete(request, pk):
    try:
        product_instance = medic.objects.get(pk=pk)
    except product_instance.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    product_instance.delete()
    return Response("deleted successfully")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def apiSearch(request, Mname):
    medicines = medic.objects.filter(Mname__icontains=Mname)
    
    if medicines.exists():
        serializer = medicSerializer(medicines, many=True)
        return Response(serializer.data)
    else:
        return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)