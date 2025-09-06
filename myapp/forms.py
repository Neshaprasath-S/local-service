from django import forms
from .models import All_User , CustomerProfileModel, ProviderProfileModel, Previous_Work , Booking,BookingReviews
from django.contrib.auth import authenticate


user_role_choices = [
       ('customer', 'Customer'),
       ('service_provider', 'Service_provider'),
]

class RegisterForm(forms.ModelForm):
       username = forms.CharField(label='Username', max_length=150, min_length=4, required=True)
       email = forms.EmailField(label='Email', max_length=254, required=True)       
       phone_number = forms.CharField(label='Phone Number', max_length=15, min_length=10, required=True)
       password = forms.CharField(label='Password', max_length=25,min_length=8 ,required=True)
       confirm_password = forms.CharField(label='Confirm Password', required=True)
       user_role= forms.ChoiceField(choices=user_role_choices ,initial='customer')
       class Meta:
              model = All_User
              fields = ['username', 'email', 'phone_number', 'password',  'user_role']
              
       def clean(self):
              cleaned_data = super().clean()
              password = cleaned_data.get('password')
              confirm_password = cleaned_data.get('confirm_password')
              if password and confirm_password:
                     password = password.strip()
                     confirm_password = confirm_password.strip()
              if password and confirm_password and password == confirm_password:
                     return cleaned_data
              else:
                     self.add_error('confirm_password', "passwords do not match")
    
    
class LoginForm(forms.Form):
       username=forms.CharField(label='Username', max_length=150, min_length=4, required=True)
       password=forms.CharField(label='Password', max_length=25, min_length=8, required=True)
       
       def clean(self):
              cleaned_data = super().clean()
              username = cleaned_data.get('username')
              password = cleaned_data.get('password').strip()
              if username and password:
                     user = authenticate(username=username, password=password)
                     if user is None:
                          raise forms.ValidationError("Invalid username or password")
          
          
          
class ChangePasswordForm(forms.Form):
      old_password =forms.CharField(max_length=25, min_length=8, required=True)
      new_password =forms.CharField(max_length=25, min_length=8, required=True)
      confirm_new_password =forms.CharField(max_length=25, min_length=8, required=True)
      
      
      def __init__(self, *args, **kwargs):
              self.user = kwargs.pop('user', None)
              super().__init__(*args, **kwargs)

      def clean(self): 
              cleaned_data = super().clean()
              old_password = cleaned_data.get('old_password').strip()
              new_password = cleaned_data.get('new_password').strip()
              confirm_new_password = cleaned_data.get('confirm_new_password').strip()
              if new_password and confirm_new_password and new_password != confirm_new_password:
                     print("New passwords do not match")
                     self.add_error('confirm_new_password', "New passwords and confirm new password do not match")
              if self.user  and not self.user.check_password(old_password):
                     print("Old password is incorrect")
                     self.add_error("old_password", "Old password is incorrect")

              return cleaned_data
                      
class CustomerProfileForm(forms.ModelForm):
      
       class Meta:
              model = CustomerProfileModel
              fields = ['profileImage', 'username', 'mobile_no', 'email', 'district', 'city', 'address']
              
       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user

class ProviderProfileForm(forms.ModelForm):

       class Meta:
              model = ProviderProfileModel

              fields = ['profileImage', 'username', 'service_name', 'banner_image', 
                        'about_content', 'mobile_no', 'email', 'district', 'city', 'address']
              
       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user       
              
class PreviousWorkForm(forms.ModelForm):
       class Meta:
              model = Previous_Work
              fields = ['service_title', 'service_image', 'service_description']
              
       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user
              for field in self.fields:
                  self.fields[field].required = True

class PreviousWorkEditForm(forms.ModelForm):
       class Meta:
              model = Previous_Work
              fields = ['service_title', 'service_image', 'service_description']

       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user
              
class ServiceFilterForm(forms.Form):
       location = forms.CharField(max_length=200, required=False)
       category = forms.ChoiceField(choices=[
           ('', 'Select Category'),
           ('plumbing', 'Plumbing'),
           ('electrical', 'Electrical'),
           ('cleaning', 'Cleaning'),
           ('carpentry', 'Carpentry'),
           ('gardening', 'Gardening'),
       ], required=False)
       rating = forms.ChoiceField(choices=[
           ('5', '5 Stars'),
           ('4', '4 Stars & up'),
           ('3', '3 Stars & up'),
           ('2', '2 Stars & up'),
           ('1', '1 Star & up'),
       ], required=False)

       def clean(self):
           cleaned_data = super().clean()
           location = cleaned_data.get('location')
           category = cleaned_data.get('category')
           rating = cleaned_data.get('rating')
           return cleaned_data
    
       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user
    
    
class bookingForm(forms.ModelForm):

       class Meta:
              model = Booking
              fields = [ 'customer_name','customer_mobile','service_type','full_address','location','booking_date', 'booking_time']
              
       def __init__(self, *args, **kwargs):
              super().__init__(*args, **kwargs)


class bookingReviewForm(forms.ModelForm):

       class Meta:
              model = BookingReviews
              fields = ['rating', 'review_text']
              
       def clean(self):
              cleaned_data = super().clean()
              rating = cleaned_data.get('rating')
              if not rating:
                   self.add_error('rating', 'Rating is required.')
              return cleaned_data

       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user

class homeSearchForm(forms.Form):
       query = forms.CharField(max_length=100, required=False)
       def clean(self):
              cleaned_data = super().clean()
              query = cleaned_data.get('query')
              return cleaned_data
       

       def __init__(self, *args, user=None, **kwargs):
              super().__init__(*args, **kwargs)
              self.user = user