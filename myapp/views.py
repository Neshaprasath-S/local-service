from urllib import request
from django.contrib import messages
from django.shortcuts import render ,redirect, get_object_or_404
from .forms import ChangePasswordForm, CustomerProfileForm, PreviousWorkForm, RegisterForm, LoginForm, ProviderProfileForm, ServiceFilterForm,bookingForm, bookingReviewForm 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate , login as auth_login, logout as auth_logout  
from django.contrib.auth.decorators import login_required
from .models import All_User, CustomerProfileModel, ProviderProfileModel, Previous_Work, Booking , BookingReviews, AverageRating
from django.db.models import Q , Avg
from django.core.paginator import Paginator
# Create your views here.
def home(request):
       return render(request, 'home.html')

def about(request):
       return render(request, 'about.html')

def login(request):
       if request.method == 'POST':
              form = LoginForm(request.POST)
              if form.is_valid():
                     username = form.cleaned_data['username']
                     password = form.cleaned_data['password'].strip()
                     user = authenticate(username=username, password=password)
                     if user is not None:
                          auth_login(request, user)
                          return redirect('mainapp:dashboard')
       else:
              form = LoginForm()

       return render(request, 'login.html', context={'form': form})

def register(request):
       if request.method == 'POST':
             
              form = RegisterForm(request.POST)
              if form.is_valid():
                     user= form.save(commit=False)
                     password= form.cleaned_data['password'].strip()
                     user.set_password(password)
                     if form.cleaned_data['user_role']== 'service_provider':
                          user.is_service_provider = True
                     else:
                          user.is_customer = True
                     user.save()
                     return redirect('mainapp:login')
       else:
              form = RegisterForm()
       return render(request,'register.html', context={'form': form})

def logout(request):
       auth_logout(request)
       return redirect('mainapp:home')

def service(request):
       service_list= ProviderProfileModel.objects.all()
       paginator = Paginator(service_list, 4)  # Show 4 services per page
       page_number = request.GET.get('page')
       page_obj = paginator.get_page(page_number)
       form = ServiceFilterForm()
       filter_items = {}
       if request.method == 'GET':
              form = ServiceFilterForm(request.GET)
              print("GET request received with filters:", request.GET)
              
              if form.is_valid():
                     location = form.cleaned_data.get('location')
                     category = form.cleaned_data.get('category')
                     rating = form.cleaned_data.get('rating')
                     filters = Q()
                     location = location.strip()
                     if location:
                            filters &= (Q(city__iexact=location ) | Q(district__icontains=location))
                     if category:
                            print("Category filter applied:", category)
                            filters &= Q(service_name__icontains=category)
                     if rating:
                            filters &= Q(average_rating__rating__gte=float(rating))
                     if filters:
                            service_list = service_list.filter(filters)
                            paginator = Paginator(service_list, 4)  # Show 4 services per page
                            page_number = request.GET.get('page')
                            page_obj = paginator.get_page(page_number)
                            filter_items = {
                                'location': location,
                                'category': category,
                                'rating': rating
                            }
       return render(request,'service.html', context={'page_obj': page_obj , 'form': form, 'filter_items': filter_items})


def providerdetails(request, provider_slug):
       provider = ProviderProfileModel.objects.filter(slug=provider_slug).first()
       service_choices = Booking.SERVICE_TYPE_CHOICES
       previous_work = Previous_Work.objects.filter(service_provider=provider)
       rating= AverageRating.objects.filter(service_provider=provider).first()
       return render (request,"providerdetails.html", context={'provider': provider, 'service_choices': service_choices, 'previous_work': previous_work, 'rating': rating})


def dashboard(request):
       if request.user.is_authenticated:
              if request.user.is_service_provider:
                     profile = ProviderProfileModel.objects.filter(user=request.user).first()
                     bookings = Booking.objects.filter(service_provider=profile).select_related('customer')
                     upcoming_booking = bookings.filter(status__in=('pending','accept')).order_by('-booking_date')
                     history = bookings.filter(status__in=('complete','cancelled','reject')).order_by('-booking_date')
                     completed = bookings.filter(status='complete')
                     rating = completed.aggregate(avg_rating=Avg('reviews__rating'))['avg_rating']
                     rejected = bookings.filter(status='reject').count()
                     previous_work = Previous_Work.objects.filter(service_provider=profile)
                     if rating is not None:
                            rating = round(rating, 1)
                     booking_reviews = BookingReviews.objects.filter(service_provider=profile)
                     return render(request, 'provider_dashboard.html', context={'user': request.user, 'profile': profile, 'all_bookings': bookings, 'upcoming_booking': upcoming_booking, 'history': history , 'booking_reviews': booking_reviews, 'rating': rating , 'rejected': rejected, 'completed': completed, 'previous_work': previous_work    })
              elif request.user.is_customer:
                     profile = CustomerProfileModel.objects.filter(user=request.user).first()
                     bookings = Booking.objects.filter(customer=profile).select_related('service_provider')
                     upcoming_booking = bookings.filter(status__in=('pending', 'accept')).order_by('-booking_date')
                     history = bookings.filter(status__in=('complete','cancel','reject')).order_by('-booking_date')
                     booking_reviews = BookingReviews.objects.filter(customer=profile)
                     completed = bookings.filter(status='complete').count()
                     canceled = bookings.filter(status='cancel').count()
                     return render(request, 'customer_dashboard.html', context={ 'user': request.user, 'profile':profile ,'all_bookings': bookings, 'upcoming_booking': upcoming_booking, 'history': history, 'booking_reviews': booking_reviews, 'completed': completed, 'canceled': canceled})

       else:
              return redirect('mainapp:login')
       
@login_required
def CustomerProfile(request):
       print('CustomerProfile view accessed')
       CustomerProfile=CustomerProfileModel.objects.filter(user=request.user).first()
       print(CustomerProfile)
       if CustomerProfile is None:
              return redirect('mainapp:CustomerProfileEdit')
       return render (request ,'CustomerProfile.html', context={'profile': CustomerProfile , 'user': request.user})

@login_required
def ProviderProfile(request):
       print('ProviderProfile view accessed')
       ProviderProfile=ProviderProfileModel.objects.filter(user=request.user).first()
       if ProviderProfile is None:
              return redirect('mainapp:ProviderProfileEdit')  
       return render (request ,'ProviderProfile.html', context={'profile': ProviderProfile , 'user': request.user})


@login_required
def CustomerProfileEdit(request):
       profile ,created=CustomerProfileModel.objects.get_or_create(user=request.user)
       if request.method == 'POST':
              form = CustomerProfileForm(request.POST, request.FILES, instance=profile ,user=request.user)
              if form.is_valid():
                     profile.save()
                     # if created:
                     #         messages.success(request, "Profile created successfully")
                     # else:
                     #         messages.success(request, "Profile updated successfully")
                     return redirect('mainapp:CustomerProfile')
       else:
              form = CustomerProfileForm(instance=profile, user=request.user)
       return render(request, 'CustomerProfileEdit.html', context={'form': form})


def ProviderProfileCreate(request):
       if request.method == 'POST':
              form = ProviderProfileForm(request.POST, request.FILES, user=request.user)
              if form.is_valid():
                     profile = form.save(commit=False)
                     profile.user = request.user
                     profile.save()
                     return redirect('mainapp:ProviderProfile')
       else:
              form = ProviderProfileForm(user=request.user)

       return render(request, 'ProviderProfileEdit.html', context={'form': form})


@login_required
def ProviderProfileEdit(request):
       profile = get_object_or_404(ProviderProfileModel, user=request.user)
       if request.method == 'POST':
              form = ProviderProfileForm(request.POST, request.FILES, instance=profile ,user=request.user)
              if form.is_valid():
                     profile.save()
                     return redirect('mainapp:ProviderProfile')
       else:
              form = ProviderProfileForm(instance=profile, user=request.user)

       return render(request, 'ProviderProfileEdit.html', context={'form': form ,'profile': profile })


@login_required
def changepassword(request):
       if request.method == 'POST':
              form = ChangePasswordForm(request.POST, user=request.user)
              if form.is_valid():
                     newpassword = form.cleaned_data.get('new_password')
                     request.user.set_password(newpassword)
                     request.user.save()
                     update_session_auth_hash(request, request.user)
                     # print("Password changed successfully")
                     messages.success(request, "Password changed successfully")
                     if request.user.is_service_provider:
                          return redirect('mainapp:ProviderProfile')
                     elif request.user.is_customer:
                          return redirect('mainapp:CustomerProfile')
                     else:
                          return redirect('mainapp:home')

       else:
              form = ChangePasswordForm(user=request.user)
              
       if request.user.is_service_provider:
              return render(request, 'ProviderProfileEdit.html', context={'form': form})
       elif request.user.is_customer:
              return render(request, 'CustomerProfileEdit.html', context={'form': form})
       else:
              return redirect('mainapp:home')

def Add_previous_work(request):
       print("Add_previous_work view accessed")
       if request.method == 'POST':
              form = PreviousWorkForm(request.POST, request.FILES, user=request.user)
              if form.is_valid():
                     previous_work = form.save(commit=False)
                     provider_profile = ProviderProfileModel.objects.filter(user=request.user).first()
                     previous_work.service_provider = provider_profile
                     previous_work.save()
                     print("Previous work added successfully")
                     messages.success(request, "Previous work added successfully")
                     return redirect('mainapp:dashboard')
       else:
              form = PreviousWorkForm(user=request.user)

       return redirect('mainapp:dashboard', context={'form': form})

def service_booking(request ,provider_slug):
       provider = get_object_or_404(ProviderProfileModel, slug=provider_slug)
       service_choices = Booking.SERVICE_TYPE_CHOICES
       customer = CustomerProfileModel.objects.filter(user=request.user).first()
       if customer is None:
              messages.error(request, "Please complete your customer profile before booking.")
              return redirect('mainapp:CustomerProfileEdit')
       
       if request.method == 'POST':
              # print("Service booking form submitted")
              form = bookingForm(request.POST)
              if form.is_valid() :
                     booking = form.save(commit=False)
                     booking.customer = customer
                     booking.service_provider = provider
                     booking.status = 'pending'
                     booking.save()
                     # print("Service booked successfully")
                     messages.success(request, "Service booked successfully")
                     return redirect('mainapp:dashboard')
              # if not form.is_valid():
              #        print(form.errors)
       else:
              form = bookingForm()
       return render(request, 'providerdetails.html', context={'form': form ,'service_choices': service_choices , 'provider': provider})

def update_booking_status(request , booking_id , action):
       booking = get_object_or_404(Booking, id=booking_id)
       if request.method == 'POST':
              if request.user == booking.service_provider.user:
                     if action == 'accept':
                            booking.status = 'accept'
                            booking.save()
                     elif action == 'reject':
                            booking.status = 'reject'
                            booking.save()
              elif request.user == booking.customer.user:
                     if action == 'complete':
                            booking.status = 'complete'
                            booking.save()
                     elif action == 'cancel':
                            booking.status = 'cancel'
                            booking.save()                    
       return redirect('mainapp:dashboard')


def booking_review(request, booking_id):
    #print("Booking review initiated")
    booking = get_object_or_404(Booking, id=booking_id)
    review = BookingReviews.objects.filter(booking=booking).first()
    if review:
        messages.error(request, "Review already submitted for this booking.")
        return redirect('mainapp:dashboard')
    if request.method == 'POST':
        form = bookingReviewForm(request.POST)
        if form.is_valid():
            #print("Review form is valid")
            review = form.save(commit=False)
            review.booking = booking
            review.customer = booking.customer
            review.service_provider = booking.service_provider
            review.save()
            avg = BookingReviews.objects.filter( service_provider=booking.service_provider ).aggregate(Avg("rating"))["rating__avg"]
            average_rating_obj, created = AverageRating.objects.get_or_create( service_provider=booking.service_provider )
            average_rating_obj.rating = round(avg, 1) if avg else 0
            average_rating_obj.save()
            #print("Review submitted successfully.")
            messages.success(request, "Review submitted successfully.")
            return redirect('mainapp:dashboard')
        else:
            #print("Form is invalid:", form.errors)
            messages.error(request, "Invalid review submission.")
            return redirect('mainapp:dashboard')
    else:
        form = bookingReviewForm()
    return redirect('mainapp:dashboard')


def rewrite_booking_review(request, review_id):
    #print("Rewrite booking review initiated")
    review = get_object_or_404(BookingReviews, id=review_id)
    booking = review.booking  
    if request.method == 'POST':
        form = bookingReviewForm(request.POST, instance=review)
        if form.is_valid():
            #print("Review form is valid")
            updated_review = form.save(commit=False)
            updated_review.booking = booking
            updated_review.customer = booking.customer
            updated_review.service_provider = booking.service_provider
            updated_review.save()
            avg = BookingReviews.objects.filter( service_provider=booking.service_provider ).aggregate(Avg("rating"))["rating__avg"]
            average_rating_obj, created = AverageRating.objects.get_or_create( service_provider=booking.service_provider )
            average_rating_obj.rating = round(avg, 1) if avg else 0
            average_rating_obj.save()
            messages.success(request, "Review updated successfully.")
            return redirect('mainapp:dashboard')
        else:
            #print("Form is invalid:", form.errors)
            messages.error(request, "Error updating review.")
            return redirect('mainapp:dashboard')
    else:
        form = bookingReviewForm(instance=review)
    return redirect('mainapp:dashboard')


def previous_work_Edit(request, work_id):
       work = get_object_or_404(Previous_Work, id=work_id)
       if request.method == 'POST':
              form = PreviousWorkForm(request.POST, request.FILES, instance=work)
              if form.is_valid():
                     form.save()
                     messages.success(request, "Previous work updated successfully.")
                     return redirect('mainapp:dashboard')
              else:
                     messages.error(request, "Not updating previous work.")
       else:
              form = PreviousWorkForm(instance=work_id)
       return redirect('mainapp:dashboard', {'form': form})

def previous_work_delete(request, work_id):
       work = get_object_or_404(Previous_Work, id=work_id)
       work.delete()
       return redirect('mainapp:dashboard')

def forgotpassword(request):
       pass
