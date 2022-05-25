from django.contrib.auth import get_user_model, authenticate, password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)
    name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email уже занят')
        return email

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.pop('password_confirm')
        if password1 != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def save(self):
        data = self.validated_data
        user = User.objects.create_user(**data)
        user.set_activation_code()
        user.send_activation_email()


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    activation_code = serializers.CharField(max_length=8,
                                            min_length=8)

    def validate(self, attrs):
        email = attrs.get('email')
        activation_code = attrs.get('activation_code')

        if not User.objects.filter(email=email,
                                   activation_code=activation_code).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return attrs

    def activate(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(required=True)

#     def validate_email(self, email):
#         if not User.objects.filter(email=email).exists():
#             raise serializers.ValidationError('Пользователь не найден')
#         return email

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')
#         user = User.objects.get(email=email)
#         if not user.check_password(password):
#             raise serializers.ValidationError('Неверный пароль')
#         if not user.is_active:
#             raise serializers.ValidationError('Аккаунт не активен')
#         attrs['user'] = user
#         return attrs


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, required=True)


    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.pop('password')
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise serializers.ValidationError('Неверный пароль')
        if user and user.is_active:
            refresh = self.get_token(user)
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def create_new_password(self):
        from django.utils.crypto import get_random_string
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        random_password = get_random_string(8)
        user.set_password(random_password)
        user.send_new_password(random_password)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                ('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': ("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)


    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'old_password', 'new_password','confirm_password']



    def update(self, instance, validated_data):

        instance.password = validated_data.get('password', instance.password)

        if not validated_data['new_password']:
              raise serializers.ValidationError({'new_password': 'not found'})

        if not validated_data['old_password']:
              raise serializers.ValidationError({'old_password': 'not found'})

        if not instance.check_password(validated_data['old_password']):
              raise serializers.ValidationError({'old_password': 'wrong password'})

        if validated_data['new_password'] != validated_data['confirm_password']:
            raise serializers.ValidationError({'passwords': 'passwords do not match'})

        if validated_data['new_password'] == validated_data['confirm_password'] and instance.check_password(validated_data['old_password']):
            # instance.password = validated_data['new_password']
            print(instance.password)
            instance.set_password(validated_data['new_password'])
            print(instance.password)
            instance.save()
            return instance
        return instance

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)
#     password_confirm = serializers.CharField(required=True)
#
#     def validate_old_password(self, old_password):
#         user = self.context['request'].user
#         if not user.check_password(old_password):
#             raise serializers.ValidationError('Укажите верный пароль')
#         return old_password
#
#     def validate(self, attrs):
#         password1 = attrs.get('new_password')
#         password2 = attrs.get('password_confirm')
#         if password1 != password2:
#             raise serializers.ValidationError('Пароли не совпадают')
#         return attrs
#
#     def set_new_password(self):
#         user = self.context['request'].user
#         password = self.validated_data.get('new_password')
#         user.set_password(password)
#

