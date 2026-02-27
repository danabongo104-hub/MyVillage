from rest_framework import serializers
from .models import Post, Comment, Like
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    # author is read_only because the author is always the
    # logged-in user making the request — not client-supplied.
    # This prevents user A from posting a comment attributed to user B.
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    # This tells the currently logged-in user whether they've
    # already liked this post — drives the like/unlike button
    # state on any frontend without a separate API call.
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'content',
            'media_url',
            'created_at',
            'updated_at',
            'likes_count',
            'comments_count',
            'comments',
            'is_liked_by_user'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        # We access the request from context — DRF passes the request
        # into serializer context automatically when called from a view.
        # This is why we never pass user data as a field —
        # we read it from the authenticated request instead.
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']