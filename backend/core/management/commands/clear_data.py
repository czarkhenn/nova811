import json
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from tickets.models import Ticket, UserLog, TicketLog

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to clear all data from the database.
    
    Usage:
        python manage.py clear_data
    """
    
    help = 'Clear all data from the database'

    def handle(self, *args, **options):
        """Main command handler."""
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting database clear process...')
            )
            
            # Clear all data
            self._clear_all_data()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Database cleared successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during clearing: {str(e)}')
            )
            raise CommandError(f'Clear failed: {str(e)}')

    def _clear_all_data(self):
        """Clear all data from the database."""
        self.stdout.write('🧹 Clearing all data from database...')
        
        # Get counts before deletion
        ticket_count = Ticket.objects.count()
        user_log_count = UserLog.objects.count()
        ticket_log_count = TicketLog.objects.count()
        user_count = User.objects.count()
        
        # Delete in order to respect foreign key constraints
        # 1. Delete logs first (they reference tickets and users)
        UserLog.objects.all().delete()
        TicketLog.objects.all().delete()
        
        # 2. Delete tickets (they reference users)
        Ticket.objects.all().delete()
        
        # 3. Delete all users (including superusers)
        User.objects.all().delete()
        
        self.stdout.write(
            f'   Deleted {ticket_count} tickets, {user_log_count} user logs, '
            f'{ticket_log_count} ticket logs, and {user_count} users'
        )
