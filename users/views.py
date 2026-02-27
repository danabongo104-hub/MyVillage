from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import User, TherapistProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateUserSerializer
)
from notifications.models import Notification


class RegisterView(generics.CreateAPIView):
    # open to everyone, you can't require auth to sign up
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # log them in immediately after registering
        # so the client doesn't need a separate login call
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user, context={'request': request}).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": f"Welcome to MyVillage, {user.username}."
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    # anyone logged in can view a profile
    # but you can only edit your own
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'
    queryset = User.objects.all()

    def get_serializer_class(self):
        # swap to the update serializer on PATCH/PUT requests
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateUserSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            return Response(
                {"error": "You can only edit your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)

        if target == request.user:
            return Response(
                {"error": "You can't follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.following.filter(id=target.id).exists():
            # already following — so unfollow
            request.user.following.remove(target)
            return Response({"status": "unfollowed", "user": username})
        else:
            request.user.following.add(target)

            # notify the person who just got followed
            Notification.objects.create(
                recipient=target,
                sender=request.user,
                notification_type='follow'
            )

            return Response({"status": "followed", "user": username})


class TherapistListView(generics.ListAPIView):
    # parents use this to discover therapists
    # we only surface verified ones — unverified shouldn't appear
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            role=User.THERAPIST,
            therapist_profile__is_verified=True
        )


class UserFollowersView(generics.ListAPIView):
    # returns everyone following a given user
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.followers.all()


class UserFollowingView(generics.ListAPIView):
    # returns everyone a given user follows
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.following.all()