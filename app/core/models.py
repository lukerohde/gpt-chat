from django.contrib.auth.models import User
from django.db.models import (Model, TextField, DateTimeField, JSONField, ForeignKey, 
                              CASCADE, OneToOneField)

# Signal to create or update User profile
from django.db.models.signals import post_save
from django.dispatch import receiver

import markdown
import bleach

class MessageModel(Model):
    """
    This class represents a chat message. It has a owner (user), timestamp and
    the message body.

    """
    user = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
                      related_name='from_user', db_index=True)
    recipient = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient',
                           related_name='to_user', db_index=True)
    timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                              db_index=True)
    body = TextField('body')

    metadata = JSONField(default=dict)

    def __str__(self):
        return str(self.id)

    def characters(self):
        """
        Toy function to count body characters.
        :return: body's char number
        """
        return len(self.body)
    
    def markdown(self):
        sanitized_body = bleach.clean(self.body)
        return markdown.markdown(sanitized_body, extensions=['fenced_code'])

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()  # Trimming whitespaces from the body
        super(MessageModel, self).save(*args, **kwargs)


    def notice(self):
        if 'notice' in self.metadata: 
            return self.metadata['notice']
    
    def notices(self):
        return self.metadata.get('notices',[])

    # Meta
    class Meta:
        app_label = 'core'
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-timestamp',)

class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    # Add additional fields here
    bot_data = JSONField(default=dict)
     

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()