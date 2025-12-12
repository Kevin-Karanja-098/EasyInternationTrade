import os
from django.utils.text import slugify

def id_front_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "id_front")

def id_back_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "id_back")

def dl_front_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "driver_license_front")

def dl_back_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "driver_license_back")

def business_license_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "business_license")

def face_photo_upload_path(instance, filename):
    return _user_doc_path(instance, filename, "face_photo")

def _user_doc_path(instance, filename, doc_type):
    base, ext = os.path.splitext(filename)
    user = instance.user
    name = slugify(f"{user.first_name}_{user.last_name}")
    new_name = f"{name}_{doc_type}{ext}".lower()
    return f"documents/{user.id}/{new_name}"
