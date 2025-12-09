from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.contrib import messages
from .models import (
    Products, Cart, Order, UserInfo,
    SupportTicket, FAQ, TicketReply, ContactMessage
)


# ============================================================================
# PRODUCTS ADMIN
# ============================================================================
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = [
        'product_image', 'name', 'brand', 'price',
        'categories', 'sku', 'stock_status', 'p_id'
    ]
    list_filter = ['categories', 'brand']
    search_fields = ['name', 'brand', 'sku', 'short_description']
    readonly_fields = ['p_id', 'product_image_preview']
    list_per_page = 20
    ordering = ['-name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'categories', 'sku')
        }),
        ('Product Details', {
            'fields': ('short_description', 'brief_description', 'price')
        }),
        ('Media', {
            'fields': ('image', 'product_image_preview')
        }),
        ('System', {
            'fields': ('p_id',),
            'classes': ('collapse',)
        }),
    )

    def product_image(self, obj):
        """Display small thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No Image</span>')

    product_image.short_description = 'Image'

    def product_image_preview(self, obj):
        """Display larger preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="border-radius: 10px; border: 2px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No Image Uploaded</span>')

    product_image_preview.short_description = 'Image Preview'

    def stock_status(self, obj):
        """Show stock status with color indicator"""
        return format_html(
            '<span style="color: green; font-weight: bold;">● In Stock</span>'
        )

    stock_status.short_description = 'Status'


# ============================================================================
# CART ADMIN
# ============================================================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product_name', 'product_image_thumb',
        'quantity', 'unit_price', 'total_price_display', 'added_date'
    ]
    list_filter = ['user', 'product__categories']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['total_price_display']
    list_per_page = 25

    def product_name(self, obj):
        """Display product name with link"""
        return obj.product.name

    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'

    def product_image_thumb(self, obj):
        """Display product thumbnail"""
        if obj.product.image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 5px; object-fit: cover;" />',
                obj.product.image.url
            )
        return '-'

    product_image_thumb.short_description = 'Image'

    def unit_price(self, obj):
        """Display unit price"""
        return f"৳{obj.product.price}"

    unit_price.short_description = 'Unit Price'
    unit_price.admin_order_field = 'product__price'

    def total_price_display(self, obj):
        """Display total price with formatting"""
        total = obj.total_price()
        return format_html(
            '<strong style="color: #28a745; font-size: 14px;">৳{}</strong>',
            total
        )

    total_price_display.short_description = 'Total'

    def added_date(self, obj):
        """Display when item was added (placeholder)"""
        return '-'

    added_date.short_description = 'Added On'


# ============================================================================
# ORDER ADMIN (ENHANCED WITH ORDER MANAGEMENT)
# ============================================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user_name', 'product_name',
        'product_price', 'order_date', 'status_badge'
    ]
    list_filter = ['status', 'ctrate_date', 'user']
    search_fields = ['order_id', 'user__username', 'product__name']
    readonly_fields = ['order_id', 'ctrate_date', 'order_summary']
    date_hierarchy = 'ctrate_date'
    list_per_page = 25
    ordering = ['-ctrate_date']

    # Add custom actions for order management
    actions = [
        'confirm_orders',
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'cancel_orders',
        'mark_as_refunded'
    ]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'ctrate_date', 'user')
        }),
        ('Product Details', {
            'fields': ('product', 'order_summary')
        }),
    )

    def order_number(self, obj):
        """Display formatted order number"""
        formatted_id = f"{obj.order_id:04d}"
        return format_html(
            '<strong style="color: #007bff;">RP-{}</strong>',
            formatted_id
        )

    order_number.short_description = 'Order #'
    order_number.admin_order_field = 'order_id'

    def user_name(self, obj):
        """Display user with email"""
        if obj.user:
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                obj.user.username,
                obj.user.email
            )
        return '-'

    user_name.short_description = 'Customer'
    user_name.admin_order_field = 'user__username'

    def product_name(self, obj):
        """Display product name"""
        return obj.product.name if obj.product else '-'

    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'

    def product_price(self, obj):
        """Display product price"""
        if obj.product:
            return format_html('<strong>৳{}</strong>', obj.product.price)
        return '-'

    product_price.short_description = 'Amount'

    def order_date(self, obj):
        """Display formatted order date"""
        return obj.ctrate_date.strftime('%B %d, %Y at %I:%M %p')

    order_date.short_description = 'Order Date'
    order_date.admin_order_field = 'ctrate_date'

    def status_badge(self, obj):
        """Display order status with dynamic color badge"""
        # Check if Order model has a status field
        if hasattr(obj, 'status'):
            status_colors = {
                'pending': ('#ffc107', '#000'),  # Yellow
                'confirmed': ('#17a2b8', '#fff'),  # Cyan
                'processing': ('#007bff', '#fff'),  # Blue
                'shipped': ('#6f42c1', '#fff'),  # Purple
                'delivered': ('#28a745', '#fff'),  # Green
                'cancelled': ('#dc3545', '#fff'),  # Red
                'refunded': ('#6c757d', '#fff'),  # Gray
            }
            bg_color, text_color = status_colors.get(obj.status, ('#6c757d', '#fff'))
            display_text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.upper()

            return format_html(
                '<span style="background: {}; color: {}; padding: 5px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
                bg_color, text_color, display_text
            )
        else:
            # Default fallback if no status field
            return format_html(
                '<span style="background: #ffc107; color: #000; padding: 5px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">PROCESSING</span>'
            )

    status_badge.short_description = 'Status'

    def order_summary(self, obj):
        """Display order summary in detail view"""
        if obj.product:
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
                '<p><strong>Product:</strong> {}</p>'
                '<p><strong>Price:</strong> ৳{}</p>'
                '<p><strong>Brand:</strong> {}</p>'
                '<p><strong>Category:</strong> {}</p>'
                '</div>',
                obj.product.name,
                obj.product.price,
                obj.product.brand,
                obj.product.categories
            )
        return 'No product information'

    order_summary.short_description = 'Order Summary'

    # ========================================================================
    # CUSTOM ADMIN ACTIONS FOR ORDER MANAGEMENT
    # ========================================================================

    def confirm_orders(self, request, queryset):
        """Confirm selected orders"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='confirmed')
            self.message_user(
                request,
                f'{updated} order(s) have been confirmed.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    confirm_orders.short_description = '✓ Confirm Selected Orders'

    def mark_as_processing(self, request, queryset):
        """Mark orders as processing"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='processing')
            self.message_user(
                request,
                f'{updated} order(s) marked as processing.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    mark_as_processing.short_description = '⚙️ Mark as Processing'

    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='shipped')
            self.message_user(
                request,
                f'{updated} order(s) marked as shipped.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    mark_as_shipped.short_description = '📦 Mark as Shipped'

    def mark_as_delivered(self, request, queryset):
        """Mark orders as delivered"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='delivered')
            self.message_user(
                request,
                f'{updated} order(s) marked as delivered.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    mark_as_delivered.short_description = '✓ Mark as Delivered'

    def cancel_orders(self, request, queryset):
        """Cancel selected orders"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='cancelled')
            self.message_user(
                request,
                f'{updated} order(s) have been cancelled.',
                messages.WARNING
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    cancel_orders.short_description = '✗ Cancel Selected Orders'

    def mark_as_refunded(self, request, queryset):
        """Mark orders as refunded"""
        if hasattr(Order, 'status'):
            updated = queryset.update(status='refunded')
            self.message_user(
                request,
                f'{updated} order(s) marked as refunded.',
                messages.INFO
            )
        else:
            self.message_user(
                request,
                'Order status field not found in the model.',
                messages.ERROR
            )

    mark_as_refunded.short_description = '💰 Mark as Refunded'


# ============================================================================
# USER INFO ADMIN
# ============================================================================
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'mobile_no', 'bio_preview']
    search_fields = ['first_name', 'last_name', 'email', 'mobile_no']
    list_per_page = 25

    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Name'

    def bio_preview(self, obj):
        """Display bio preview"""
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '-'

    bio_preview.short_description = 'Bio'


# ============================================================================
# SUPPORT TICKET ADMIN
# ============================================================================
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'name', 'email', 'subject_display',
        'status_badge', 'priority_badge', 'created_at_display',
        'response_time_display'
    ]
    list_filter = ['status', 'priority', 'subject', 'created_at']
    search_fields = ['ticket_number', 'name', 'email', 'order_number', 'message']
    readonly_fields = [
        'ticket_number', 'created_at', 'updated_at',
        'response_time', 'resolution_time'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ['-created_at']

    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'status', 'priority', 'assigned_to')
        }),
        ('Customer Information', {
            'fields': ('name', 'email', 'phone', 'order_number')
        }),
        ('Ticket Details', {
            'fields': ('subject', 'message', 'attachment')
        }),
        ('Response & Resolution', {
            'fields': ('admin_response', 'resolution_notes')
        }),
        ('Feedback', {
            'fields': ('rating', 'feedback'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'responded_at',
                'resolved_at', 'closed_at', 'response_time', 'resolution_time'
            ),
            'classes': ('collapse',)
        }),
    )

    def subject_display(self, obj):
        """Display subject"""
        return obj.get_subject_display()

    subject_display.short_description = 'Subject'
    subject_display.admin_order_field = 'subject'

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'open': '#dc3545',
            'in_progress': '#ffc107',
            'waiting_customer': '#17a2b8',
            'resolved': '#28a745',
            'closed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: #fff; padding: 5px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper()
        )

    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        """Display priority with color badge"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background: {}; color: #fff; padding: 5px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )

    priority_badge.short_description = 'Priority'

    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime('%b %d, %Y %I:%M %p')

    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'

    def response_time_display(self, obj):
        """Display response time"""
        if obj.response_time:
            return f"{obj.response_time}h"
        return format_html('<span style="color: #dc3545;">Pending</span>')

    response_time_display.short_description = 'Response Time'

    actions = ['mark_in_progress', 'mark_resolved', 'close_tickets']

    def mark_in_progress(self, request, queryset):
        """Mark selected tickets as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} ticket(s) marked as in progress.')

    mark_in_progress.short_description = 'Mark as In Progress'

    def mark_resolved(self, request, queryset):
        """Mark selected tickets as resolved"""
        for ticket in queryset:
            ticket.mark_as_resolved()
        self.message_user(request, f'{queryset.count()} ticket(s) marked as resolved.')

    mark_resolved.short_description = 'Mark as Resolved'

    def close_tickets(self, request, queryset):
        """Close selected tickets"""
        for ticket in queryset:
            ticket.close_ticket()
        self.message_user(request, f'{queryset.count()} ticket(s) closed.')

    close_tickets.short_description = 'Close Tickets'


# ============================================================================
# FAQ ADMIN
# ============================================================================
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = [
        'question_preview', 'category_badge', 'order',
        'is_active', 'views', 'helpful_count',
        'created_at_display'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    readonly_fields = ['views', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    list_per_page = 25
    ordering = ['category', 'order']

    fieldsets = (
        ('FAQ Content', {
            'fields': ('category', 'question', 'answer', 'order')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('views', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def question_preview(self, obj):
        """Display question preview"""
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question

    question_preview.short_description = 'Question'

    def category_badge(self, obj):
        """Display category with badge"""
        return format_html(
            '<span style="background: #007bff; color: #fff; padding: 5px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            obj.get_category_display().upper()
        )

    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'

    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime('%b %d, %Y')

    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'


# ============================================================================
# TICKET REPLY ADMIN
# ============================================================================
@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'reply_type', 'user_display',
        'message_preview', 'created_at_display'
    ]
    list_filter = ['is_staff_reply', 'created_at']
    search_fields = ['ticket__ticket_number', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ['-created_at']

    def ticket_number(self, obj):
        """Display ticket number"""
        return obj.ticket.ticket_number

    ticket_number.short_description = 'Ticket'

    def reply_type(self, obj):
        """Display reply type badge"""
        if obj.is_staff_reply:
            return format_html(
                '<span style="background: #007bff; color: #fff; padding: 3px 8px; '
                'border-radius: 10px; font-size: 10px;">STAFF</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: #fff; padding: 3px 8px; '
            'border-radius: 10px; font-size: 10px;">CUSTOMER</span>'
        )

    reply_type.short_description = 'Type'

    def user_display(self, obj):
        """Display user"""
        if obj.user:
            return obj.user.username
        return '-'

    user_display.short_description = 'User'

    def message_preview(self, obj):
        """Display message preview"""
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message

    message_preview.short_description = 'Message'

    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime('%b %d, %Y %I:%M %p')

    created_at_display.short_description = 'Replied At'


# ============================================================================
# CONTACT MESSAGE ADMIN
# ============================================================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'phone', 'subject_preview',
        'is_read_badge', 'created_at_display'
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ['-created_at']

    actions = ['mark_as_read', 'mark_as_unread']

    def subject_preview(self, obj):
        """Display subject preview"""
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject

    subject_preview.short_description = 'Subject'

    def is_read_badge(self, obj):
        """Display read status"""
        if obj.is_read:
            return format_html('<span style="color: #28a745;">✓ Read</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">● Unread</span>')

    is_read_badge.short_description = 'Status'

    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime('%b %d, %Y %I:%M %p')

    created_at_display.short_description = 'Received'

    def mark_as_read(self, request, queryset):
        """Mark messages as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')

    mark_as_read.short_description = 'Mark as Read'

    def mark_as_unread(self, request, queryset):
        """Mark messages as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')

    mark_as_unread.short_description = 'Mark as Unread'


# ============================================================================
# CUSTOMIZE ADMIN SITE
# ============================================================================
admin.site.site_header = "Rannaghore Protidin Administration"
admin.site.site_title = "Rannaghore Protidin Admin"
admin.site.index_title = "Welcome to Rannaghore Protidin Admin Panel"