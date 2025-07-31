from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import State, Contribution

# Unregister the default User admin
admin.site.unregister(User)

# Define an inline admin descriptor for Contribution model
# This allows us to display contributions directly on the user's page
class ContributionInline(admin.TabularInline):
    model = Contribution
    # Show limited fields for a compact view
    fields = ('state', 'category', 'submitted_at')
    readonly_fields = ('state', 'category', 'submitted_at')
    extra = 0  # Don't show extra empty forms for adding new contributions here
    can_delete = False # We don't want to delete contributions from the user page
    show_change_link = True # Add a link to the full contribution object

# Define a new User admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ContributionInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_contribution_count')

    def get_contribution_count(self, obj):
        return obj.contribution_set.count()
    get_contribution_count.short_description = 'Contributions Count'

# Register your other models
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('author', 'state', 'category', 'submitted_at')
    list_filter = ('state', 'category', 'author')
    search_fields = ('text_content', 'author__username')
    date_hierarchy = 'submitted_at'

