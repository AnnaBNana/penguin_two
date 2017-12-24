from django.contrib import admin
from .models import Post
from django_summernote.admin import SummernoteModelAdmin


class PostAdmin(SummernoteModelAdmin):
    search_fields = [
        "title",
        "text"
    ]

# class CommentAdmin(SummernoteModelAdmin):
#     pass

# class IntroAdmin(SummernoteModelAdmin):
#     def has_add_permission(self, request):
#         base_add_permission = super(admin.ModelAdmin, self).has_add_permission(request)
#         if base_add_permission:
#             count = Intro.objects.all().count()
#             if count == 0:
#                 return True
#         return False


admin.site.register(Post,PostAdmin)


