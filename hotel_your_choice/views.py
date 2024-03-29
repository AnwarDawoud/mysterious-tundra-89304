# hotel_your_choice/views.py
from urllib.parse import quote
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Comment, CustomUser, Hotel, Booking, Photo, UserActivity, Rating, Amenity
from .forms import YourBookingForm, CustomRegistrationForm, HotelForm, RatingForm, CommentForm, ModifyBookingForm
import logging
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Sum, Avg 
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.http import HttpResponse
from django.views import View
from .models import Hotel, Booking, Rating, Comment
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.db import IntegrityError
import xlsxwriter

logger = logging.getLogger(__name__)


def view_hotels(request):
    hotels = Hotel.objects.all().prefetch_related('rated_bookings__ratings__user')
    

    context = {'hotels': hotels}
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            rating_id = request.POST.get('rating_id')

            if rating_id:
                rating = get_object_or_404(Rating, id=rating_id)

                # Check if the rating belongs to an active booking
                if rating.booking.status == 'active':
                    comment = Comment(text=text, rating=rating, booking=rating.booking)
                    comment.save()

                    # Update the context to include the new comment for the specific hotel
                    hotel = rating.hotel
                    hotel.rated_bookings.set(
                        Booking.objects.filter(hotel=hotel, status='active', ratings__isnull=False)
                    )
                    context['hotels'] = hotels  # Update only if needed

                    messages.success(request, 'Comment added successfully.')
                else:
                    messages.error(request, 'Booking is not active. Comment cannot be added.')
            else:
                messages.error(request, 'Invalid Rating ID. Comment cannot be added.')
        else:
            messages.error(request, 'Invalid comment form. Please check the form.')

    context['comment_form'] = CommentForm()
    return render(request, 'hotel_your_choice/common/view_hotels.html', context)

@login_required
@require_POST
@csrf_protect

def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def add_comment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.booking = booking

            # Set the timestamp field explicitly before saving
            comment.timestamp = timezone.now()

            comment.save()

            # Update like and dislike counts
            likes_count = comment.likes_count
            dislikes_count = comment.dislikes_count

            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'comment_text': comment.text,
                'likes_count': likes_count,
                'dislikes_count': dislikes_count,
            })

    return JsonResponse({'status': 'error', 'errors': form.errors})


def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.likes_count += 1

    # Update the timestamp field
    comment.timestamp = timezone.now()

    comment.save()
    return JsonResponse({'likes_count': comment.likes_count})


def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.dislikes_count += 1

    # Update the timestamp field
    comment.timestamp = timezone.now()

    comment.save()
    return JsonResponse({'dislikes_count': comment.dislikes_count})


def delete_experience(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        Comment.objects.filter(booking_id=booking_id).delete()
        Rating.objects.filter(booking_id=booking_id).delete()
        return redirect('hotel_your_choice:view_hotels')

    return HttpResponse("Method not allowed", status=405)


@login_required
def hotel_manager_dashboard(request):
    hotels_managed = Hotel.objects.filter(manager=request.user)

    if hotels_managed.exists():
        bookings = Booking.objects.filter(hotel__in=hotels_managed)
    else:
        bookings = []

    return render(request, 'hotel_your_choice/hotel_manager/dashboard.html', {'bookings': bookings})

@login_required
def handle_amenities(hotel_instance, amenity_ids):
    print("Handling Amenities...")
    
    # Clear existing amenities
    hotel_instance.amenities = ''

    # Iterate through amenity_ids and append them to the amenities field
    amenities = Amenity.objects.filter(id__in=amenity_ids)
    amenity_names = ', '.join(amenity.name for amenity in amenities)
    hotel_instance.amenities = amenity_names
    hotel_instance.save()

    print(f"Amenities updated: {hotel_instance.amenities}")

def handle_other_photos(hotel_instance, other_photos):
    print("Handling Other Photos...")

    hotel_instance.other_photos.clear()  # Clear existing photos

    for photo in other_photos:
        try:
            # Create a new Photo instance and link it to the current Hotel instance
            photo_instance = Photo.objects.create(image=photo, hotel=hotel_instance)
            hotel_instance.other_photos.add(photo_instance)
        except Exception as e:
            print(f'Error uploading photo: {e}')

    hotel_instance.save()

    print(f"Other Photos updated: {hotel_instance.other_photos.all()}")



@login_required
def add_hotel(request):
    if request.method == 'POST':
        hotel_form = HotelForm(request.POST, request.FILES)
        if hotel_form.is_valid():
            try:
                with transaction.atomic():
                    # Process the form data and save the hotel instance
                    hotel_instance = hotel_form.save(commit=False)
                    hotel_instance.manager = request.user
                    hotel_instance.save()

                    # Handle other photos within the transaction
                    try:
                        handle_other_photos(hotel_instance, request.FILES.getlist('other_photos'))
                    except Exception as e:
                        # Handle any exceptions related to other photos but continue with the transaction
                        print(f'Error handling other photos: {e}')
                    
                    # Commit the transaction
                    messages.success(request, 'Hotel added successfully!')
                    return redirect('hotel_your_choice:view_hotels')
            except Exception as e:
                # Handle any exceptions that occur during the transaction
                messages.error(request, f'Error adding hotel: {e}')
        else:
            # Handle form validation errors
            print("Form errors:", hotel_form.errors)
            messages.error(request, 'Error adding hotel. Please check the form.')
    else:
        hotel_form = HotelForm()

    amenities = Amenity.objects.all()
    return render(request, 'hotel_your_choice/hotel_manager/add_hotel.html', {'hotel_form': hotel_form, 'amenities': amenities})

@login_required
def delete_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.user == hotel.manager:
        hotel.delete()
        messages.success(request, 'Hotel deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this hotel.')
    return redirect('hotel_your_choice:view_hotels')



@login_required
def edit_hotel(request, hotel_id):
    hotel_instance = get_object_or_404(Hotel, id=hotel_id)

    # Check if the logged-in user is the manager of the hotel
    if request.user != hotel_instance.manager:
        messages.error(request, 'You do not have permission to edit this hotel.')
        return redirect('hotel_your_choice:view_hotels')

    if request.method == 'POST':
        hotel_form = HotelForm(request.POST, request.FILES, instance=hotel_instance)
        if hotel_form.is_valid():
            try:
                with transaction.atomic():
                    hotel_instance = hotel_form.save()

                    # Handle amenities (unchanged)
                    amenities_str = request.POST.get('amenities', '')  # Get comma-separated string of amenities
                    amenities_list = [amenity.strip() for amenity in amenities_str.split(',')]  # Split string into list
                    hotel_instance.amenities = ', '.join(amenities_list)  # Join list back into comma-separated string

                    # Save the updated hotel instance
                    hotel_instance.save()

                    # Handle other photos
                    handle_other_photos(hotel_instance, request.FILES.getlist('other_photos'))

                    messages.success(request, 'Hotel edited successfully!')
                    return redirect('hotel_your_choice:view_hotels')
            except Exception as e:
                # Handle any exceptions that occur during the transaction
                messages.error(request, f'Error editing hotel: {e}')
        else:
            messages.error(request, 'Error editing hotel. Please check the form.')
    else:
        hotel_form = HotelForm(instance=hotel_instance)

    return render(
        request,
        'hotel_your_choice/hotel_manager/edit_hotel.html',
        {'hotel_form': hotel_form, 'hotel': hotel_instance}
    )


@login_required
def manage_bookings(request, booking_id=None):
    # Get all bookings for the hotels managed by the user
    bookings = Booking.objects.filter(hotel__manager=request.user)

    # Add sorting and filtering logic based on user input (you can customize this)
    sort_by = request.GET.get('sort_by', 'check_in_date')
    status_filter = request.GET.get('status_filter', 'all')

    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    bookings = bookings.order_by(sort_by)

    # Pagination logic (you can adjust the number per page)
    page = request.GET.get('page', 1)
    items_per_page = 10  # Adjust as needed
    paginator = Paginator(bookings, items_per_page)

    try:
        bookings = paginator.page(page)
    except PageNotAnInteger:
        bookings = paginator.page(1)
    except EmptyPage:
        bookings = paginator.page(paginator.num_pages)

    # Additional features
    if request.method == 'POST':
        # Handle form submissions for modifying bookings
        modify_form = ModifyBookingForm(request.POST)
        if modify_form.is_valid():
            # Process the modification and save the changes
            booking_id = modify_form.cleaned_data['booking_id']
            modified_booking = get_object_or_404(Booking, id=booking_id)
            # Update booking details based on the form data
            # Modify the code below based on your form and model structure
            # Example: modified_booking.status = modify_form.cleaned_data['new_status']
            modified_booking.save()

            # Redirect to the Manage Bookings page after modification
            return HttpResponseRedirect(request.path_info)
    else:
        modify_form = ModifyBookingForm()

    # View Booking Details logic
    if booking_id:
        selected_booking = get_object_or_404(Booking, id=booking_id)
        return render(request, 'hotel_your_choice/hotel_manager/view_booking_details.html', {'selected_booking': selected_booking})

    return render(request, 'hotel_your_choice/hotel_manager/manage_bookings.html', {
        'bookings': bookings,
        'modify_form': modify_form,
    })


def generate_excel(request):
    # Fetch all bookings or filter based on your requirements
    bookings = Booking.objects.all()

    # Create a BytesIO buffer to store the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=bookings.xlsx'

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Write the header row.
    header_format = workbook.add_format({'bold': True})
    headers = ['ID', 'Check-in Date', 'Check-out Date', 'Status', 'Guests', 'User ID', 'Username', 'Email', 'Hotel Name']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    # Define a date format
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

    # Write the booking data.
    for row_num, booking in enumerate(bookings, start=1):
        worksheet.write(row_num, 0, booking.id)
        worksheet.write(row_num, 1, booking.check_in_date, date_format)
        worksheet.write(row_num, 2, booking.check_out_date, date_format)
        worksheet.write(row_num, 3, booking.status)
        worksheet.write(row_num, 4, booking.guests)
        worksheet.write(row_num, 5, booking.user.id)
        worksheet.write(row_num, 6, booking.user.username)
        worksheet.write(row_num, 7, booking.user.email)

        # Include hotel name if available
        if hasattr(booking, 'hotel') and booking.hotel:
            worksheet.write(row_num, 8, booking.hotel.name)
        else:
            worksheet.write(row_num, 8, 'N/A')

    workbook.close()

    return response


def view_booking_details(request, booking_id):
    # Fetch the selected booking
    selected_booking = get_object_or_404(Booking, id=booking_id)

    # Render the template with the booking details
    return render(request, 'hotel_your_choice/hotel_manager/view_booking_details.html', {'selected_booking': selected_booking})

from django.db import IntegrityError, transaction

@login_required
def book_hotel(request, hotel_id, hotel_name):
    available_hotels = Hotel.objects.all()

    if request.method == 'POST':
        form = YourBookingForm(request.POST)

        if form.is_valid():
            selected_hotel_id = form.cleaned_data['hotel'].id
            selected_hotel = get_object_or_404(Hotel, pk=selected_hotel_id)

            check_in_date = form.cleaned_data['check_in_date']
            check_out_date = form.cleaned_data['check_out_date']
            guests = form.cleaned_data['guests']
            reschedule_booking_id = form.cleaned_data.get('existing_booking_id')

            try:
                with transaction.atomic():
                    if reschedule_booking_id:
                        # Reschedule existing booking logic
                        existing_booking = get_object_or_404(Booking, pk=reschedule_booking_id, user=request.user)

                        # Cancel the original booking
                        existing_booking.cancel()

                        # Create a new booking with the rescheduled dates
                        new_booking = Booking.objects.create(
                            user=request.user,
                            hotel=selected_hotel,
                            check_in_date=check_in_date,
                            check_out_date=check_out_date,
                            guests=guests
                        )

                        messages.success(request, f"Booking rescheduled successfully. New Booking ID: {new_booking.id}")
                    else:
                        # Check for double booking before creating a new booking
                        if Booking.objects.filter(
                            hotel=selected_hotel,
                            check_in_date__lt=check_out_date,
                            check_out_date__gt=check_in_date
                        ).exists():
                            messages.error(request, "Selected dates are not available. Please choose different dates.")
                        else:
                            # Create a new booking
                            new_booking = Booking.objects.create(
                                user=request.user,
                                hotel=selected_hotel,
                                check_in_date=check_in_date,
                                check_out_date=check_out_date,
                                guests=guests
                            )

                            messages.success(request, f"Booking created successfully. New Booking ID: {new_booking.id}")

                            # Redirect to the client dashboard after a successful booking
                            return redirect('hotel_your_choice:client_dashboard')

            except IntegrityError as e:
                messages.error(request, "An error occurred while processing your booking. Please try again.")
        else:
            print("Form errors:", form.errors)
    else:
        form = YourBookingForm(initial={'hotel': hotel_id})

    context = {
        'hotel_name': hotel_name,
        'form': form,
        'available_hotels': available_hotels,
        'selected_hotel_id': hotel_id,
        'selected_hotel_name': hotel_name,
    }

    return render(request, 'hotel_your_choice/client/book_hotel.html', context)


def reschedule_booking(request):
    # Your implementation here
    pass

def cancel_booking(request):
    # Your implementation here
    pass

from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import YourBookingForm

@login_required
def client_dashboard(request):
    active_and_rescheduled_bookings = Booking.objects.filter(
        user=request.user,
    ).exclude(status='canceled')

    if request.method == 'POST':
        action = request.POST.get('action')
        booking_id = request.POST.get('booking_id')

        try:
            booking_id = int(booking_id)
        except ValueError:
            print(f"Invalid booking ID: {booking_id}")
            messages.error(request, "Invalid booking ID.")
            return redirect('hotel_your_choice:client_dashboard')

        print(f"Booking ID after conversion: {booking_id}")

        if action == 'reschedule_booking':
            new_check_in_date = request.POST.get('new_check_in_date')
            new_check_out_date = request.POST.get('new_check_out_date')

            if new_check_in_date and new_check_out_date:
                booking = get_object_or_404(Booking, id=booking_id, user=request.user)

                # Create a rescheduled booking using YourBookingForm
                form_data = {
                    'user': booking.user,
                    'hotel': booking.hotel,
                    'check_in_date': new_check_in_date,
                    'check_out_date': new_check_out_date,
                    'guests': booking.guests,
                    'reschedule_booking': True,  # Indicate this is a rescheduled booking
                }
                form = YourBookingForm(form_data, instance=booking)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Booking rescheduled successfully.")
                else:
                    messages.error(request, "Invalid rescheduling data. Please try again.")
            else:
                messages.error(request, "Invalid rescheduling data. Please try again.")

        elif action == 'cancel_booking':
            print(f"Attempting to cancel booking with ID: {booking_id}")
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            print(f"Booking found: {booking}")

            booking.status = 'canceled'
            booking.canceled_by = request.user
            booking.save()

            messages.success(request, "Booking canceled successfully.")

        return redirect('hotel_your_choice:client_dashboard')

    context = {'bookings': active_and_rescheduled_bookings, 'booking_form': YourBookingForm()}
    return render(request, 'hotel_your_choice/client/client_dashboard.html', context)


@login_required
def rate_experience(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    user = request.user

    # Check if the user has already rated this booking
    existing_rating = Rating.objects.filter(booking=booking, user=user).first()

    if existing_rating:
        messages.warning(request, 'You have already rated this booking. Rating update is not allowed.')
        return redirect('hotel_your_choice:client_dashboard')  # Change this to the appropriate URL for the client dashboard

    if request.method == 'POST':
        form = RatingForm(request.POST)

        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            text = form.cleaned_data['text']

            # Get the hotel associated with the booking
            hotel_id = booking.hotel.id

            # Create a new rating with the hotel_id
            new_rating = Rating(booking=booking, user=user, rating=rating_value, text=text, hotel_id=hotel_id)
            new_rating.save()
            messages.success(request, 'Rating added successfully.')

            # You can adjust the redirect based on your requirements
            return redirect('hotel_your_choice:client_dashboard')  # Change this to the appropriate URL

        else:
            messages.error(request, 'Invalid rating form. Please try again.')

    else:
        form = RatingForm()

    return render(request, 'hotel_your_choice/client/rate_experience.html', {'booking': booking, 'form': form})

   
# Site Administrator Views
def get_analytics_data():
    # Replace this with your actual logic to fetch analytics data
    return {'total_bookings': 100, 'revenue': 5000, 'average_rating': 4.5}

@login_required
def system_overview(request):
    total_bookings = Booking.objects.count()
    revenue = Booking.objects.aggregate(total_revenue=Sum('guests'))['total_revenue']
    average_rating = Booking.objects.aggregate(average_rating=Avg('rating'))['average_rating']

    analytics_data = {
        'total_bookings': total_bookings,
        'revenue': revenue,
        'average_rating': average_rating,
    }

    return render(request, 'hotel_your_choice/site_administrator/system_overview.html', {'analytics': analytics_data})

@login_required
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'hotel_your_choice/site_administrator/manage_users.html', {'users': users})

@login_required
def troubleshoot(request):
    # Implement logic for troubleshooting
    return render(request, 'hotel_your_choice/site_administrator/troubleshoot.html')

# Authentication and Authorization Views
def register_view(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            # Get the next available user ID
            next_user_id = CustomUser.objects.order_by('-id').first().id + 1 if CustomUser.objects.exists() else 1

            # Set the ID in the form data
            form.cleaned_data['id'] = next_user_id

            user = form.save(commit=False)
            user.save()

            messages.success(request, f"Welcome, {user.username}! You are now registered.")
            return redirect('hotel_your_choice:view_hotels')
        else:
            messages.error(request, "Registration failed. Please correct the errors in the form.")
    else:
        form = CustomRegistrationForm()

    return render(request, 'hotel_your_choice/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('hotel_your_choice:view_hotels')
        else:
            messages.error(request, "Login failed. Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'hotel_your_choice/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('hotel_your_choice:view_hotels')



class CustomPasswordResetView(View):
    template_name = 'hotel_your_choice/password_reset.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        try:
            # Retrieve the user by username
            user = get_user_model().objects.get(username=username)

            if user:
                # Allow the user to reset their password
                user.set_password(new_password)
                user.save()

                return redirect('login')  # Redirect to your login page

        except get_user_model().DoesNotExist:
            pass  # Handle the case where the user does not exist

        return render(request, self.template_name)
    
class CustomPasswordResetConfirmView(View):
    template_name = 'hotel_your_choice/password_reset_confirm.html'  # Create this template

    def get(self, request, email, token):
        context = {'email': email, 'token': token}
        return render(request, self.template_name, context)

    def post(self, request, email, token):
        try:
            # Verify the token against the stored token
            user = get_user_model().objects.get(email=email, reset_token=token)

            if user:
                # Allow the user to reset their password
                new_password = request.POST.get('new_password')
                user.set_password(new_password)
                user.reset_token = None  # Clear the reset token after resetting the password
                user.save()

                messages.success(request, 'Password reset successfully.')
                return redirect('login')  # Redirect to your login page

        except get_user_model().DoesNotExist:
            pass  # Handle the case where the user or token does not exist

        messages.error(request, 'Invalid email or token.')
        return render(request, self.template_name, {'email': email, 'token': token})
        

@login_required
def unsubscribe_view(request):
    if request.method == 'POST':
        user = request.user

        # Implement logic for user unsubscribe
        # For example, set a flag in the user's profile indicating unsubscribed status
        # Replace 'is_subscribed' with the field that indicates the subscription status in your User model
        User = get_user_model()

        try:
            user_profile = User.objects.get(pk=user.pk)
            user_profile.is_subscribed = False  # Set the flag to indicate unsubscribed status
            user_profile.save()

            # Log the user out
            logout(request)

            # Remove the user from the user database
            user_profile.delete()

            # Display a success message
            messages.success(request, 'You have been unsubscribed successfully.')

            # Redirect to the home page or any other desired page after successful unsubscribe and logout
            return redirect('hotel_your_choice:view_hotels')

        except User.DoesNotExist:
            # Handle the case where the user doesn't exist (optional)
            messages.error(request, 'User not found.')
    return render(request, 'hotel_your_choice/unsubscribe.html')

# JSON response views
@login_required
def get_analytics_data(request):
    # Replace this with your actual logic to fetch analytics data
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(total_revenue=Sum('guests'))['total_revenue']
    average_rating = Booking.objects.aggregate(average_rating=Avg('rating'))['average_rating']

    # Include additional data
    total_hotels = Hotel.objects.count()
    average_guests = Booking.objects.aggregate(average_guests=Avg('guests'))['average_guests']
    total_clients = CustomUser.objects.filter(is_client_user=True).count()
    total_managers = CustomUser.objects.filter(is_hotel_manager=True).count()
    occupied_rooms = Booking.objects.aggregate(occupied_rooms=Sum('guests'))['occupied_rooms']
    avg_booking_duration = 0  # Calculate average booking duration based on your logic

    analytics_data = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'average_rating': average_rating,
        'total_hotels': total_hotels,
        'average_guests': average_guests,
        'total_clients': total_clients,
        'total_managers': total_managers,
        'occupied_rooms': occupied_rooms,
        'avg_booking_duration': avg_booking_duration,
    }

    return JsonResponse(analytics_data)

@login_required
def manage_users(request):
    # Fetch all CustomUser objects from the database
    users = CustomUser.objects.all()

    # Render the users into an HTML template
    html = render_to_string('hotel_your_choice/site_administrator/manage_users.html', {'users': users})

    # Return the rendered HTML as a JSON response
    return render(request, 'hotel_your_choice/site_administrator/manage_users.html', {'users': users})


@login_required
def view_activities(request, user_id):
    # Retrieve user activities log (customize as needed)
    user_activities = UserActivity.objects.filter(user_id=user_id)
    context = {
        'user_activities': user_activities,
        'user_id': user_id,
    }
    return render(request, 'hotel_your_choice/site_administrator/manage_users.html', context)

# API endpoint for fetching user data
@require_GET
def get_user_data(request):
    # Your logic to retrieve user data from the database
    # For demonstration purposes, assume you have a User model with appropriate fields
    users = CustomUser.objects.all()
    user_data = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return JsonResponse(user_data, safe=False)

@require_GET
def load_user_activities(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Your logic to retrieve user activities from the database
    # For demonstration purposes, assume you have a UserActivity model with appropriate fields
    user_activities = UserActivity.objects.filter(user=user)
    activities_data = [{'activity': activity.activity, 'timestamp': activity.timestamp} for activity in user_activities]

    return JsonResponse(activities_data, safe=False)

@require_POST
def add_user(request):
    # Extract user data from the request
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')

    # Your logic to create a new user in the database
    # For demonstration purposes, assume you have a User model with appropriate fields
    new_user = User.objects.create(username=username, email=email)

    return JsonResponse({'message': 'User added successfully', 'user_id': new_user.id})

# API endpoint for updating user permissions
@require_http_methods(['PUT'])
def update_permissions(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Extract new permissions from the request
    new_permissions = request.POST.get('permissions', '')

    # Your logic to update user permissions in the database
    # For demonstration purposes, assume you have a 'permissions' field in your User model
    user.permissions = new_permissions
    user.save()

    return JsonResponse({'message': 'Permissions updated successfully'})

# API endpoint for deleting a user
@require_http_methods(['DELETE'])
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Your logic to delete the user from the database
    user.delete()

    return JsonResponse({'message': 'User deleted successfully'})

# API endpoint for viewing user logs
@require_GET
def view_user_logs(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Your logic to retrieve user logs from the database
    # For demonstration purposes, assume you have a UserActivity model with appropriate fields
    user_logs = UserActivity.objects.filter(user=user)
    logs_data = [{'activity': log.activity, 'timestamp': log.timestamp} for log in user_logs]

    return JsonResponse(logs_data, safe=False)

# API endpoint for approving ratings
@require_http_methods(['PUT'])
def approve_ratings(request, rating_id):
    rating = get_object_or_404(Rating, pk=rating_id)

    # Your logic to approve the rating in the database
    # For demonstration purposes, assume you have an 'approved' field in your Rating model
    rating.approved = True
    rating.save()

    return JsonResponse({'message': 'Rating approved successfully'})

# API endpoint for viewing user ratings
@require_GET
def view_user_ratings(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Your logic to retrieve user ratings from the database
    # For demonstration purposes, assume you have a Rating model with appropriate fields
    user_ratings = Rating.objects.filter(user=user)
    ratings_data = [{'rating': rating.rating, 'comment': rating.comment, 'approved': rating.approved} for rating in user_ratings]

    return JsonResponse(ratings_data, safe=False)

