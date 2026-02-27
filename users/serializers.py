from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, ParentProfile, TherapistProfile


class ParentProfileSerializer(serializers.ModelSerializer):
    """
    ModelSerializer automatically generates fields from the model.
    """
    class Meta:
        model = ParentProfile
        fields = ['number_of_children', 'children_age_range', 'concerns']


class TherapistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapistProfile
        fields = [
            'license_number',
            'specialization',
            'years_of_experience',
            'is_verified',
            'accepting_clients'
        ]
        # is_verified is read_only because only an admin can set this.
        # If left writable, a therapist could verify themselves.
        read_only_fields = ['is_verified']


class UserSerializer(serializers.ModelSerializer):
    """
    This is the READ serializer — used when returning user data
    in responses. It is never used for creating or updating users.
    Separating read and write serializers keeps each one focused
    and prevents accidentally exposing write logic in read responses.
    """
    parent_profile = ParentProfileSerializer(read_only=True)
    therapist_profile = TherapistProfileSerializer(read_only=True)

    # SerializerMethodField lets us compute a value that doesn't
    # exist as a direct model field. followers.count() is a database
    # aggregation — we calculate it here rather than storing it as
    # a column, because stored counts go stale and cause data inconsistency.
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'bio',
            'profile_picture',
            'parent_profile',
            'therapist_profile',
            'followers_count',
            'following_count'
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class RegisterSerializer(serializers.ModelSerializer):
    """
    This is the WRITE serializer — only used for registration.
    It handles password confirmation, role validation, and
    nested profile creation all in one place.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
        # validate_password enforces Django's built-in password rules:
        # minimum length, not too common, not entirely numeric.
        # write_only=True means password NEVER appears in any response.
        # This is non-negotiable for security.
    )
    password2 = serializers.CharField(write_only=True, required=True)

    # These are optional at the top level — a parent won't send
    # therapist_profile data and vice versa.
    parent_profile = ParentProfileSerializer(required=False)
    therapist_profile = TherapistProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'role',
            'bio',
            'profile_picture',
            'parent_profile',
            'therapist_profile'
        ]

    def validate(self, attrs):
        """
        validate() runs after individual field validation.
        Cross-field validation — rules that involve more than
        one field at a time — always goes here.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )

        # Therapists must supply a license number at registration.
        # We enforce this at the serializer level so it never reaches
        # the database layer without this check passing.
        role = attrs.get('role')
        if role == User.THERAPIST:
            therapist_data = attrs.get('therapist_profile', {})
            if not therapist_data.get('license_number'):
                raise serializers.ValidationError(
                    {"license_number": "Therapists must provide a license number."}
                )
        return attrs

    def create(self, validated_data):
        """
        create() only runs after ALL validation passes.
        We pop nested data before calling create_user because
        Django's create_user doesn't know what to do with
        nested dictionaries — it only handles flat User fields.
        """
        parent_data = validated_data.pop('parent_profile', None)
        therapist_data = validated_data.pop('therapist_profile', None)
        validated_data.pop('password2')

        # create_user instead of create — this hashes the password.
        # Using .create() directly stores plain text. Never do that.
        user = User.objects.create_user(**validated_data)

        # The signal already created the profile via post_save.
        # We just update it with the data the client sent.
        if parent_data and user.is_parent:
            ParentProfile.objects.filter(user=user).update(**parent_data)

        if therapist_data and user.is_therapist:
            TherapistProfile.objects.filter(user=user).update(**therapist_data)

        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Separate serializer for profile updates.
    Users should not be able to change their role after registration
    — that would let a parent promote themselves to therapist.
    We simply don't include 'role' in this serializer's fields.
    """
    parent_profile = ParentProfileSerializer(required=False)
    therapist_profile = TherapistProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['bio', 'profile_picture', 'parent_profile', 'therapist_profile']

    def update(self, instance, validated_data):
        parent_data = validated_data.pop('parent_profile', None)
        therapist_data = validated_data.pop('therapist_profile', None)

        # Update the base User fields
        instance = super().update(instance, validated_data)

        # Update nested profile if data was sent
        if parent_data and instance.is_parent:
            ParentProfile.objects.filter(user=instance).update(**parent_data)

        if therapist_data and instance.is_therapist:
            TherapistProfile.objects.filter(user=instance).update(**therapist_data)

        return instance