from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from bot.models import Bot

class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = (
            'botname',
            'end_point'
        )


class BotRegisterAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def put(self, request, *args, **kwargs):
        botname = request.data.get('botname')

        if botname:
            try:
                bot = Bot.objects.get(botname=botname)
                if bot.owner != request.user:
                    # If the bot exists and is not owned by the current user, return a 403 Forbidden
                    return Response({"detail": "You do not have permission to modify this bot."},
                                    status=status.HTTP_403_FORBIDDEN)
            except Bot.DoesNotExist:
                # If the bot does not exist, create a new one for the current user
                bot = Bot(owner=request.user, botname=botname)

            # Update the bot instance with the provided data
            serializer = BotSerializer(bot, data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Get the token for the bot_user
                bot_token = Token.objects.get(user=bot.bot_user)

                return Response({"bot_token": bot_token.key}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Bot name is required."}, status=status.HTTP_400_BAD_REQUEST)
        

#curl -X PUT "https://app:3000/bot/register/" -H "Authorization: 7e69832bd81c0d6f833e639f03a04c24e4499723"      -H "Content-Type: application/json"  -d '{"botname": "example_bot", "http://bot:8001/api/message/example_bot" }'