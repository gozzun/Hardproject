from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    # is_active가 처음에 False로 설정되는 오류가 있어서 초기값을 True로 고정시켜줌.
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = User
        fields = '__all__'