import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Respondent
from django.db.models.signals import post_save

# Suppression du fichier image quand l’objet est supprimé
@receiver(post_delete, sender=Respondent)
def delete_image_on_object_delete(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# Suppression de l’ancienne image si on en envoie une nouvelle
@receiver(pre_save, sender=Respondent)
def delete_old_image_on_update(sender, instance, **kwargs):
    try:
        old_instance = Respondent.objects.get(pk=instance.pk)
    except Respondent.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

@receiver(post_save, sender=User)
def add_user_to_basic_group(sender, instance, created, **kwargs):
    if created:
        basic_group, _ = Group.objects.get_or_create(name='basic')
        instance.groups.add(basic_group)