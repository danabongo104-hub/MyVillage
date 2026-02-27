from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from posts.models import Post
from posts.serializers import PostSerializer


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # grab ids of everyone the current user follows
        # then filter posts to only those authors
        # ordering is handled by Post.Meta — newest first
        followed_users = self.request.user.following.values_list('id', flat=True)
        return Post.objects.filter(author_id__in=followed_users)

    def get_serializer_context(self):
        return {'request': self.request}


class SearchPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.query_params.get('q', '')
        if not keyword:
            return Post.objects.none()
        # icontains = case-insensitive search
        return Post.objects.filter(content__icontains=keyword)