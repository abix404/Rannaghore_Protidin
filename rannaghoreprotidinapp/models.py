import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserInfo(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True,  # Allow null temporarily for migration
        blank=True
    )
    first_name = models.CharField(max_length=15, blank=False, null=False)
    last_name = models.CharField(max_length=15, blank=False, null=False)
    mobile_no = models.CharField(max_length=15, blank=False, null=False)  # Changed to CharField
    email = models.EmailField()
    bio = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Products(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    p_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    price = models.IntegerField(blank=True, null=True)
    categories = models.CharField(max_length=50, blank=True, null=True)
    short_description = models.CharField(max_length=100, blank=False, null=False)
    brief_description = models.CharField(max_length=500)
    brand = models.CharField(max_length=20)
    image = models.ImageField(upload_to='products_img', blank=True, null=True, default='no_image.png')
    sku = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    """
    Order model with status tracking
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
    ctrate_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    order_id = models.IntegerField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the order'
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal notes for this order (not visible to customer)'
    )

    # Timestamps for tracking
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-ctrate_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_id} - {self.user.username if self.user else 'Guest'}"

    def confirm_order(self):
        """Confirm the order"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def mark_as_processing(self):
        """Mark order as processing"""
        self.status = 'processing'
        self.save()

    def mark_as_shipped(self):
        """Mark order as shipped"""
        self.status = 'shipped'
        self.shipped_at = timezone.now()
        self.save()

    def mark_as_delivered(self):
        """Mark order as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()

    def cancel_order(self):
        """Cancel the order"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()

    def refund_order(self):
        """Mark order as refunded"""
        self.status = 'refunded'
        self.save()

    @property
    def total_amount(self):
        """Calculate total order amount"""
        if self.product:
            return self.product.price
        return 0

    @property
    def processing_time(self):
        """Calculate how long order has been processing (in hours)"""
        if self.status in ['delivered', 'cancelled'] and self.delivered_at:
            delta = self.delivered_at - self.ctrate_date
        elif self.cancelled_at and self.status == 'cancelled':
            delta = self.cancelled_at - self.ctrate_date
        else:
            delta = timezone.now() - self.ctrate_date
        return round(delta.total_seconds() / 3600, 2)


class SupportTicket(models.Model):
    """
    Support Ticket model for customer inquiries
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting on Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    SUBJECT_CHOICES = [
        ('order_inquiry', 'Order Inquiry'),
        ('shipping_issue', 'Shipping Issue'),
        ('payment_problem', 'Payment Problem'),
        ('product_question', 'Product Question'),
        ('return_request', 'Return Request'),
        ('technical_issue', 'Technical Issue'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Ticket Information
    ticket_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Customer Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    order_number = models.CharField(max_length=50, blank=True)

    # Ticket Details
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    attachment = models.FileField(upload_to='support_tickets/', blank=True, null=True)

    # Response and Resolution
    admin_response = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)

    # Customer Feedback
    rating = models.IntegerField(null=True, blank=True, help_text='Rating from 1-5')
    feedback = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Assignment
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'

    def __str__(self):
        return f"{self.ticket_number} - {self.name}"

    def mark_as_in_progress(self):
        """Mark ticket as in progress"""
        self.status = 'in_progress'
        self.save()

    def mark_as_resolved(self):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()

    def close_ticket(self):
        """Close the ticket"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()

    @property
    def response_time(self):
        """Calculate response time in hours"""
        if self.responded_at:
            delta = self.responded_at - self.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None

    @property
    def resolution_time(self):
        """Calculate resolution time in hours"""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None


class FAQ(models.Model):
    """
    Frequently Asked Questions model
    """
    CATEGORY_CHOICES = [
        ('orders', 'Orders'),
        ('shipping', 'Shipping'),
        ('payment', 'Payment'),
        ('returns', 'Returns'),
        ('account', 'Account'),
        ('products', 'Products'),
        ('general', 'General'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', '-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

    def mark_helpful(self):
        """Mark FAQ as helpful"""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])

    def mark_not_helpful(self):
        """Mark FAQ as not helpful"""
        self.not_helpful_count += 1
        self.save(update_fields=['not_helpful_count'])


class TicketReply(models.Model):
    """
    Model for ticket replies/conversation thread
    """
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    is_staff_reply = models.BooleanField(default=False)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_replies/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Ticket Reply'
        verbose_name_plural = 'Ticket Replies'

    def __str__(self):
        reply_type = "Staff" if self.is_staff_reply else "Customer"
        return f"{reply_type} reply to {self.ticket.ticket_number}"


class ContactMessage(models.Model):
    """
    General contact messages (not tickets)
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject}"