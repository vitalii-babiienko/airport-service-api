from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user and set the password correctly"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True,
    )
    password = serializers.CharField(
        label=_("Password"),
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."),
                    code="authorization",
                )
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                code="authorization",
            )

        attrs["user"] = user
        return attrs