from django.contrib.admin import ModelAdmin, site
from .models import Bot


class BotAdmin(ModelAdmin):
    #readonly_fields = (,)
    search_fields = ('id', 'botname', 'openai_completion_model')
    list_display = ('id', 'botname', 'openai_completion_model', 'openai_temperature', 'openai_response_tokens')
    list_display_links = ('id',)
    list_filter = ('openai_completion_model',)


site.register(Bot, BotAdmin)