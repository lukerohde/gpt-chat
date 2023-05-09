from django.contrib.admin import ModelAdmin, site
from .models import Bot


class BotAdmin(ModelAdmin):
    #readonly_fields = (,)
    search_fields = ('id', 'botname', 'end_point', 'description')
    list_display = ('id', 'botname', 'end_point', 'description', 'config')
    list_display_links = ('id',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user # bot is owned by its creator - the current user
        super().save_model(request, obj, form, change)

site.register(Bot, BotAdmin)