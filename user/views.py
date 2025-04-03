from django.shortcuts import render
from .models import *
from django.http import HttpResponse
import datetime
from django.db import connection
import numpy as np

# from .recommendation.data_preparation import prepare_data
# from .recommendation.sentiment_analysis import analyze_sentiment
# from .recommendation.embedding import generate_user_embeddings, generate_product_embeddings
# from .recommendation.recommendation_model import train_recommendation_model

import torch
# Create your views here.


def about(req):
    noofitemsincart = addtocart.objects.all().count()
    return render(req, 'user/about.html', {"noofitemsincart":noofitemsincart})


def contactus(request):
    noofitemsincart = addtocart.objects.all().count()
    status = False
    if request.method == 'POST':
        Name = request.POST.get("name", "")
        Mobile = request.POST.get("mobile", "")
        Email = request.POST.get("email", "")
        Message = request.POST.get("msg", "")
        x = contact(name=Name, email=Email, mobile=Mobile, message=Message)
        x.save()
        status = True
        # return HttpResponse("<script>alert('Thanks for enquiry...');window.location.href='/user/contactus/'</script>")

    return render(request, 'user/contactus.html', {'S': status,"noofitemsincart":noofitemsincart})


def services(req):
    return render(req, 'user/services.html')


def myorders(request):
    userid = request.session.get('userid')
    oid = request.GET.get('oid')
    noofitemsincart = addtocart.objects.all().count()
    orderdata = ""
    if userid:
        cursor = connection.cursor()
        cursor.execute(
            "select o.*,p.* from user_order o,user_product p where o.pid=p.id and o.userid='" + str(userid) + "'")
        orderdata = cursor.fetchall()
        if oid:
            result = order.objects.filter(id=oid, userid=userid)
            result.delete()
            return HttpResponse(
                "<script>alert('your order has been cancelled');window.location.href='/user1/myorders'</script>")

    return render(request, 'user/myorders.html', {"pendingorder": orderdata ,"noofitemsincart":noofitemsincart})

def myprofile(request):
    user = request.session.get('userid')  # Get the logged-in user's email from the session
    pdata = profile.objects.filter(email=user).first()  # Fetch the user's profile
    noofitemsincart = addtocart.objects.all().count()

    if pdata:
        # Split the interests field into a list
        interests_list = pdata.interests.split(', ') if pdata.interests else []
    else:
        interests_list = []

    if user:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get("name", "")
            DOB = request.POST.get("dob", "").strip()  # Get and strip the DOB field
            mobile = request.POST.get("mobile", "")
            password = request.POST.get("passwd", "")
            address = request.POST.get("address", "")
            selected_genres = request.POST.get("interests", "")  # Get the comma-separated genres

            # Validate DOB
            if DOB:
                try:
                    # Ensure the DOB is in the correct format
                    datetime.datetime.strptime(DOB, "%Y-%m-%d")
                    pdata.dob = DOB
                except ValueError:
                    return HttpResponse(
                        "<script>alert('Invalid date format. Please use YYYY-MM-DD.');window.location.href='/user1/myprofile/';</script>"
                    )
            else:
                pdata.dob = None  # Set to None if DOB is empty

            # Update profile fields
            pdata.name = name
            pdata.mobile = mobile
            pdata.passwd = password
            pdata.address = address
            pdata.interests = selected_genres  # Save the updated interests

            # Update profile picture if provided
            if 'ppic' in request.FILES:
                pdata.ppic = request.FILES['ppic']

            # Save the updated profile
            pdata.save()

            return HttpResponse(
                "<script>alert('Your profile updated successfully..');window.location.href='/user1/myprofile/'</script>"
            )

    return render(request, 'user/myprofile.html', {
        "profile": pdata,
        "noofitemsincart": noofitemsincart,
        "interests_list": interests_list,
    })

def prod(request):
    cdata = category.objects.all().order_by('-id')
    noofitemsincart = addtocart.objects.all().count()
    x = request.GET.get('abc')
    # pdata=""
    if x is not None:
        pdata = product.objects.filter(category=x)
    else:
        pdata = product.objects.all().order_by('-id')
    return render(request, 'user/products.html', {"cat": cdata, "products": pdata ,"noofitemsincart":noofitemsincart})


def signup(req):
    noofitemsincart = addtocart.objects.all().count()
    if req.method == "POST":
        name = req.POST.get("name", "")
        DOB = req.POST.get("dob", "")
        email = req.POST.get("email", "")
        mobile = req.POST.get("mobile", "")
        password = req.POST.get("passwd", "")
        address = req.POST.get("address", "")
        picname = req.FILES['ppic']
        interests = req.POST.get("interests", "")  # Get the comma-separated genres

        # Check if the email is already registered
        d = profile.objects.filter(email=email)
        if d.count() > 0:
            return HttpResponse("<script>alert('Already registered..');window.location.href='/user1/signup/'</script>")
        else:
            # Save the new user profile
            profile(
                name=name,
                dob=DOB,
                mobile=mobile,
                email=email,
                passwd=password,
                address=address,
                ppic=picname,
                interests=interests  # Save the interests field
            ).save()
            return HttpResponse(
                "<script>alert('Registered successfully..');window.location.href='/user1/signup/'</script>"
            )

    return render(req, 'user/signup.html', {"noofitemsincart": noofitemsincart})


def home(req):
    cdata = category.objects.all().order_by('-id')[0:6]
    pdata = product.objects.all().order_by('-id')[0:12]
    noofitemsincart = addtocart.objects.all().count()

    return render(req, 'user/index.html', {"data": cdata, "products": pdata, "noofitemsincart": noofitemsincart})


def signin(req):
    noofitemsincart = addtocart.objects.all().count()
    if req.method == 'POST':
        uname = req.POST.get('email', "")
        pwd = req.POST.get('passwd', "")
        checkuser = profile.objects.filter(email=uname, passwd=pwd)
        if (checkuser):
            req.session["userid"] = uname

            return HttpResponse(
                "<script>alert('Logged In Successfully..');window.location.href='/user1/signin/';</script>")
        else:
            return HttpResponse(
                "<script>alert('User Id or Password is incorrect');window.location.href='/user1/signin/';</script>")
    return render(req, 'user/signin.html',{"noofitemsincart":noofitemsincart})


def viewdetails(request):
    noofitemsincart = addtocart.objects.all().count()
    product_id = request.GET.get('msg')  # Get the product ID from the query parameter

    # Strip any trailing slashes from the product_id
    if product_id:
        product_id = product_id.rstrip('/')

    # Fetch the product details (use .first() to get a single object)
    product_obj = product.objects.filter(id=product_id).first()

    # Check if the product exists
    if not product_obj:
        return HttpResponse("<script>alert('Product not found.');window.location.href='/user1/home/';</script>")

    # Fetch reviews for the product
    reviews = Review.objects.filter(product=product_obj).order_by('-created_at')

    if request.method == "POST":
        if request.session.get('userid'):  # Ensure the user is logged in
            user = profile.objects.get(email=request.session.get('userid'))  # Get the logged-in user
            rating = int(request.POST.get('rating', 1))  # Get the rating from the form
            comment = request.POST.get('comment', '')  # Get the comment from the form

            # Save the review
            Review.objects.create(product=product_obj, user=user, rating=rating, comment=comment)

            return HttpResponse(
                "<script>alert('Your review has been submitted successfully.');window.location.href='/user1/viewdetails?msg={}/';</script>".format(product_id)
            )
        else:
            return HttpResponse(
                "<script>alert('You need to log in to submit a review.');window.location.href='/user1/signin/';</script>"
            )

    return render(request, 'user/viewdetails.html', {
        "product": product_obj,
        "reviews": reviews,
        "noofitemsincart": noofitemsincart,
    })
def process(request):

    userid = request.session.get('userid')
    pid = request.GET.get('pid')
    btn = request.GET.get('bn')
    print(userid, pid, btn)
    if userid is not None:
        if btn == 'cart':
            checkcartitem = addtocart.objects.filter(pid=pid, userid=userid)
            if checkcartitem.count() == 0:
                addtocart(pid=pid, userid=userid, status=True, cdate=datetime.datetime.now()).save()
            else:
                return HttpResponse(
                    "<script>alert('Your item is successfully added to cart..');window.location.href='/user1/cart/'</script>")

        elif btn == 'order':
            order(pid=pid, userid=userid, remarks="pending", status=True, odate=datetime.datetime.now()).save()
            return HttpResponse(
                "<script>alert('your order has confirmed...');window.location.href='/user1/myorders/'</script>")

        elif btn == 'orderfromcart':
            res = addtocart.objects.filter(pid=pid, userid=userid)
            res.delete()
            order(pid=pid, userid=userid, remarks="pending", status=True, odate=datetime.datetime.now()).save()
            return HttpResponse(
                "<script>alert('your order has confirmed...');window.location.href='/user1/myorders/'</script>")
        return render(request, 'user/process.html', {"alreadylogin": True})

    else:
        return HttpResponse("<script>window.location.href='/user1/signin/'</script>")


def logout(request):
    del request.session['userid']
    # return render(request,'user/logout.html')
    return HttpResponse("<script>window.location.href='/user1/home/'</script>")


def cart(request):
    noofitemsincart = addtocart.objects.all().count()
    if request.session.get('userid'):
        userid = request.session.get('userid')
        cursor = connection.cursor()
        cursor.execute("select c.*,p.* from user_addtocart c,user_product p where p.id=c.pid")
        cartdata = cursor.fetchall()
        pid = request.GET.get('pid')
        if request.GET.get('pid'):
            res = addtocart.objects.filter(id=pid, userid=userid)
            res.delete()
            return HttpResponse(
                "<script>alert('Your product has been removed successfully');window.location.href='/user1/cart/'</script>")

    return render(request, 'user/cart.html',{"cart":cartdata,"noofitemsincart":noofitemsincart})
from collections import Counter
from .models import SearchLog, profile

def update_user_interests(user):
    # Get all search queries for the user
    searches = SearchLog.objects.filter(user=user).values_list('query', flat=True)
    
    # Count the frequency of each search term
    search_counts = Counter(searches)
    
    # Get the top 5-10 most common search terms
    top_interests = [term for term, _ in search_counts.most_common(10)]
    
    # Update the user's interests field
    user.interests = ", ".join(top_interests)
    user.save()


def search_view(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  # Get the search query from the request
        results = []  # Initialize an empty list for search results

        # Check if the user is logged in
        if request.session.get('userid'):
            user = profile.objects.get(email=request.session.get('userid'))  # Get the logged-in user's profile

            if query:
                # Log the search query
                SearchLog.objects.create(user=user, query=query)

                # Update user interests
                update_user_interests(user)

                # Perform the actual search logic
                results = product.objects.filter(name__icontains=query)  # Search for products by name

        # Render the search results page
        return render(request, 'user/search_results.html', {'query': query, 'results': results})
# def recommend_products(request):
#     user_id = request.session.get('userid')
#     if not user_id:
#         return HttpResponse("<script>alert('Please log in to see recommendations.');window.location.href='/user1/signin/';</script>")

#     # Prepare data
#     user_data, product_data, review_data, search_data = prepare_data()
#     print("Data prepared successfully.")

#     # Generate embeddings
#     user_embeddings = generate_user_embeddings(user_data, search_data)
#     product_embeddings = generate_product_embeddings(product_data)
#     print("Embeddings generated successfully.")

#     # Train recommendation model
#     model = train_recommendation_model(user_embeddings, product_embeddings, review_data)
#     print("Recommendation model trained successfully.")

#     # Get recommendations for the current user
#     user_emb = user_embeddings[user_id]
#     scores = model(torch.tensor([np.concatenate([user_emb, product_emb]) for product_emb in product_embeddings]))
#     recommended_products = product_data.iloc[np.argsort(scores.detach().numpy().flatten())[::-1][:10]]
#     print("Recommended products:", recommended_products)

#     return render(request, 'user/recommendations.html', {'products': recommended_products})