from itertools import product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context
from django.db.models import Q
from .models import *
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import JsonResponse
from .models import SupportTicket, FAQ
from datetime import datetime
import uuid


# my views here.

def home(request):
    products = Products.objects.all()
    context = {
        'products': products,
    }
    return render(request, template_name='shop/home.html', context=context)


def product_details(request, p_id):
    product = get_object_or_404(Products, p_id=p_id)
    return render(request, 'shop/product_details.html', {'p': product})


def about_us(request):
    return render(request, template_name='shop/about_us.html')


def sing_in(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')

                # Redirect to 'next' parameter if it exists, otherwise go to home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Display form errors
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'SingIn_SingUp/sing_in.html', {'form': form})


def sing_up(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # 1. Save the User (Username, First Name, Last Name, Email, Password)
            user = form.save()

            # 2. Get the Mobile Number and save to UserInfo
            mobile_no = form.cleaned_data.get('mobile_no')

            # 3. Create UserInfo record (keeping original structure without user FK)
            try:
                UserInfo.objects.create(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    mobile_no=int(mobile_no),  # Convert to integer as per your model
                    email=user.email
                )
                messages.success(request, "Account created successfully! Please login.")
                return redirect('sing_in')
            except Exception as e:
                # If UserInfo creation fails, delete the user and show error
                user.delete()
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            # Display specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignupForm()

    return render(request, 'SingIn_SingUp/sing_up.html', {'form': form})


@login_required
def sing_out_view(request):
    """
    Handle user logout
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    else:
        # Allow GET request for logout as well
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')


@login_required
def buy_now(request, p_id):
    try:
        product = Products.objects.get(id=p_id)
    except Products.DoesNotExist:
        return redirect('home')  # Redirect if product doesn't exist

    # Generate Order Number (Example: RP-0001)
    order_number = f"RP-{Order.objects.count() + 1:04d}"

    # Pass data to the template
    context = {
        'user_name': request.user.username,
        'order_number': order_number,
        'product_name': product.name,
        'quantity': 1,  # Default quantity
        'status': 'Ordered'  # Default status
    }

    return render(request, 'shop/buy_now.html', context)


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    unique_product_count = cart_items.count()  # Counting unique products

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'unique_product_count': unique_product_count
    })


@login_required
def add_to_cart(request, p_id):
    product = Products.objects.get(p_id=p_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1  # Increase quantity if already exists
        cart_item.save()

    return redirect('cart')


@login_required
def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


def all_products(request):
    # Get search query from GET parameters
    search_query = request.GET.get('search', '')

    # Filter products based on search query
    if search_query:
        products = Products.objects.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(categories__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    else:
        products = Products.objects.all()

    # Get all unique categories for filter
    categories = Products.objects.values_list('categories', flat=True).distinct()

    context = {
        'products': products,
        'search_query': search_query,
        'categories': categories,
        'product_count': products.count()
    }

    return render(request, template_name='shop/all_products.html', context=context)


# Help & Support Page
def help_support(request):
    """
    Display the help and support page with FAQs
    """
    # Get all FAQs ordered by category and order
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')

    context = {
        'faqs': faqs,
    }

    return render(request, 'shop/help_support.html', context)


# Submit Support Ticket
def submit_support_ticket(request):
    """
    Handle support ticket submission
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone', '')
            order_number = request.POST.get('order_number', '')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            attachment = request.FILES.get('attachment', None)

            # Validate required fields
            if not all([name, email, subject, message]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('help_support')

            # Generate ticket number
            ticket_number = generate_ticket_number()

            # Create support ticket
            ticket = SupportTicket.objects.create(
                ticket_number=ticket_number,
                name=name,
                email=email,
                phone=phone,
                order_number=order_number,
                subject=subject,
                message=message,
                status='open',
            )

            # Handle attachment if provided
            if attachment:
                # Validate file size (5MB max)
                if attachment.size > 5 * 1024 * 1024:
                    messages.error(request, 'Attachment size must be less than 5MB.')
                    ticket.delete()
                    return redirect('help_support')

                ticket.attachment = attachment
                ticket.save()

            # Send confirmation email to customer
            send_ticket_confirmation_email(ticket)

            # Send notification email to support team
            send_support_team_notification(ticket)

            messages.success(
                request,
                f'Your support ticket has been submitted successfully! '
                f'Ticket Number: {ticket_number}. '
                f'We will respond to your email within 24 hours.'
            )

            return redirect('help_support')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('help_support')

    return redirect('help_support')


# Generate Ticket Number
def generate_ticket_number():
    """
    Generate a unique ticket number
    """
    return f'TICKET-{uuid.uuid4().hex[:8].upper()}'


# Send Ticket Confirmation Email
def send_ticket_confirmation_email(ticket):
    """
    Send confirmation email to customer
    """
    try:
        subject = f'Support Ticket Received - {ticket.ticket_number}'
        message = f"""
Dear {ticket.name},

Thank you for contacting Rannaghore Protidin Support!

We have received your support ticket and our team will review it shortly.

Ticket Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ticket Number: {ticket.ticket_number}
Subject: {ticket.get_subject_display()}
Status: {ticket.get_status_display()}
Submitted: {ticket.created_at.strftime('%B %d, %Y at %I:%M %p')}

Your Message:
{ticket.message}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What happens next?
• Our support team will review your ticket
• You'll receive a response within 24 hours
• Check your email for updates

You can reply directly to this email if you have additional information to add to your ticket.

Need urgent help?
📞 Call us: +880 1234-567890 (Mon-Fri, 9AM-6PM)
💬 WhatsApp: +880 1234-567890

Thank you for your patience!

Best regards,
Rannaghore Protidin Support Team
        """

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[ticket.email],
        )

        email.send(fail_silently=True)

    except Exception as e:
        print(f"Customer email sending failed: {str(e)}")


# Send Support Team Notification
def send_support_team_notification(ticket):
    """
    Send notification email to support team
    """
    try:
        subject = f'New Support Ticket - {ticket.ticket_number}'
        message = f"""
New Support Ticket Received

Ticket Number: {ticket.ticket_number}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Customer Information:
Name: {ticket.name}
Email: {ticket.email}
Phone: {ticket.phone or 'Not provided'}
Order Number: {ticket.order_number or 'Not provided'}

Subject: {ticket.get_subject_display()}
Status: {ticket.get_status_display()}
Submitted: {ticket.created_at.strftime('%B %d, %Y at %I:%M %p')}

Message:
{ticket.message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action Required:
Please review and respond to this ticket within 24 hours.

View ticket in admin panel:
{settings.SITE_URL}/admin/app/supportticket/{ticket.id}/
        """

        # Send to support team email
        support_email = getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[support_email],
            fail_silently=True,
        )

    except Exception as e:
        print(f"Support team notification failed: {str(e)}")


# Search FAQs (AJAX)
def search_faqs(request):
    """
    Search FAQs based on query
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip().lower()

        if not query:
            return JsonResponse({'results': []})

        # Search in questions and answers
        faqs = FAQ.objects.filter(
            is_active=True
        ).filter(
            models.Q(question__icontains=query) |
            models.Q(answer__icontains=query)
        )[:10]

        results = [
            {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category
            }
            for faq in faqs
        ]

        return JsonResponse({'results': results})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Get FAQs by Category (AJAX)
def get_faqs_by_category(request):
    """
    Get FAQs filtered by category
    """
    if request.method == 'GET':
        category = request.GET.get('category', 'all')

        if category == 'all':
            faqs = FAQ.objects.filter(is_active=True)
        else:
            faqs = FAQ.objects.filter(is_active=True, category=category)

        results = [
            {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category
            }
            for faq in faqs
        ]

        return JsonResponse({'results': results})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Track Ticket Status
def track_ticket(request):
    """
    Allow customers to track their support ticket
    """
    ticket = None

    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number')
        email = request.POST.get('email')

        try:
            ticket = SupportTicket.objects.get(
                ticket_number=ticket_number,
                email=email
            )
        except SupportTicket.DoesNotExist:
            messages.error(request, 'Ticket not found. Please check your ticket number and email.')

    context = {
        'ticket': ticket,
    }

    return render(request, 'track_ticket.html', context)


# Close Ticket (Customer)
def close_ticket(request, ticket_id):
    """
    Allow customer to close their ticket
    """
    if request.method == 'POST':
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            ticket.status = 'closed'
            ticket.closed_at = datetime.now()
            ticket.save()

            messages.success(request, 'Your ticket has been closed successfully.')
        except SupportTicket.DoesNotExist:
            messages.error(request, 'Ticket not found.')

    return redirect('help_support')


# Rate Support (Customer Satisfaction)
def rate_support(request, ticket_id):
    """
    Allow customer to rate support quality
    """
    if request.method == 'POST':
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            rating = int(request.POST.get('rating', 0))
            feedback = request.POST.get('feedback', '')

            if 1 <= rating <= 5:
                ticket.rating = rating
                ticket.feedback = feedback
                ticket.save()

                messages.success(request, 'Thank you for your feedback!')
            else:
                messages.error(request, 'Invalid rating value.')

        except SupportTicket.DoesNotExist:
            messages.error(request, 'Ticket not found.')
        except ValueError:
            messages.error(request, 'Invalid rating value.')

    return redirect('help_support')
