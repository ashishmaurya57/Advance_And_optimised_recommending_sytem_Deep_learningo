from django.contrib import admin

# Register your models here.
from .models import *
#admin.site.register(contact)

class contactAdmin(admin.ModelAdmin):
    list_display=("name","mobile","email","message")
admin.site.register(contact,contactAdmin)

class categoryAdmin(admin.ModelAdmin):
    list_display=("id","cname","cpic","cdate")
admin.site.register(category,categoryAdmin)

class profileAdmin(admin.ModelAdmin):
    list_display=("name","dob","mobile","email","passwd","ppic","address", "interests")
admin.site.register(profile,profileAdmin)

class productAdmin(admin.ModelAdmin):
    list_display=("id","name","ppic","language","hardcover","publisher","tprice","disprice","pdes","category","pdate")
admin.site.register(product,productAdmin)

class orderAdmin(admin.ModelAdmin):
    list_display=("id","pid","userid","remarks","status","odate")
admin.site.register(order,orderAdmin)

class addtocartAdmin(admin.ModelAdmin):
    list_display=("id","pid","userid","status","cdate")
admin.site.register(addtocart,addtocartAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__name', 'rating')

admin.site.register(Review, ReviewAdmin)