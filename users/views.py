from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework import status
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from users.serializators import UserModelSerializer


class UserViewSet(ViewSet):
    queryset: QuerySet = User.objects.all()
    serializer_class = UserModelSerializer

    def list(self, request: Request) -> Response:
        serializer = UserModelSerializer(
            self.queryset, many=True
        )
        if not serializer.data:
            return Response(
                status=status.HTTP_404_NOT_FOUND, 
                data={"error": "users not found"}
            )
        return Response(
            data=serializer.data, 
            status=status.HTTP_200_OK
        )

    def create(
        self, request: Request
    ) -> Response:
        s = UserModelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            User.objects.create(
                username=s.validated_data.get("username"),
                first_name=s.validated_data.get("first_name"),
                last_name=s.validated_data.get("last_name"),
                email=s.validated_data.get("email"),
                password=make_password(
                    s.validated_data.get("password")
            ))
            
            return Response(
                data={"message": "success"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def retrieve(
        self, request: Request, pk=None
    ) -> Response:
        try:
            user = User.objects.get(pk=pk)
            serializer = UserModelSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(
        self, request: Request, pk=None
    ) -> Response:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserModelSerializer(user, data=request.data)
        if serializer.is_valid():
            if 'password' in serializer.validated_data:
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(
        self, request: Request, pk=None
    ) -> Response:
        user = User.objects.filter(pk=pk).first()
        password = request.data.get("password")
        if password:
            user.password = make_password(password)
            user.save()
            return Response({"message": "password update"}, status=200)
        else:
            return Response({"message": "Password not save"}, status=400)
        



    def destroy(
        self, request: Request, pk=None
    ) -> Response:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)