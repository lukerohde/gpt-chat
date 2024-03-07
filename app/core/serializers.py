from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from core.models import MessageModel, UserProfile
from rest_framework.serializers import ModelSerializer, CharField


class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username', read_only=True)
    recipient = CharField(source='recipient.username')
    
    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, username=validated_data['recipient']['username'])

        
        print(validated_data)
        
        user_profile_bot_data = validated_data.get('metadata', {}).pop('user_profile_bot_data', None)
        
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user,
                           metadata=validated_data.get('metadata',{}))
        msg.save()

        if user_profile_bot_data:
            profile, _ = UserProfile.objects.get_or_create(user=recipient)
            profile.bot_data[user.username] = user_profile_bot_data
            result = profile.save()
            
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body', 'metadata')


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)
