from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Smitch


# manually unregister Group
admin.site.unregister(Group)

class ProfileIniline(admin.StackedInline):
    model = Profile

# manually extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileIniline]


admin.site.unregister(User)

# Manually register user
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)


#Manually register smitches
admin.site.register(Smitch)