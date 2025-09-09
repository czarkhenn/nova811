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
    Management command to import test users and tickets from JSON fixture data.
    
    Usage:
        python manage.py seed_test_data
    """
    
    help = 'Import test users and tickets from fixtures/seed_data.json'

    def add_arguments(self, parser):
        """Add command line arguments."""
        pass

    def handle(self, *args, **options):
        """Main command handler."""
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting test data import process...')
            )
            
            # Load seed data from JSON file
            seed_data = self._load_seed_data()
            
            # Import users and tickets
            with transaction.atomic():
                self._seed_users(seed_data['users'])
                self._seed_tickets(seed_data['tickets'])
            
            self.stdout.write(
                self.style.SUCCESS('✅ Test data import completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during import: {str(e)}')
            )
            raise CommandError(f'Import failed: {str(e)}')

    def _load_seed_data(self):
        """Load seed data from JSON fixture file."""
        fixture_path = os.path.join('fixtures', 'seed_data.json')
        
        if not os.path.exists(fixture_path):
            raise CommandError(f'Fixture file not found: {fixture_path}')
        
        try:
            with open(fixture_path, 'r') as file:
                data = json.load(file)
                
            # Validate required keys
            if 'users' not in data or 'tickets' not in data:
                raise CommandError('Invalid fixture format: missing users or tickets')
                
            self.stdout.write(f'📁 Loaded seed data from {fixture_path}')
            return data
            
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON in fixture file: {str(e)}')


    def _seed_users(self, users_data):
        """Import test users from data."""
        self.stdout.write('👥 Importing test users...')
        
        created_count = 0
        skipped_count = 0
        
        for user_data in users_data:
            email = user_data['email']
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                skipped_count += 1
                self.stdout.write(f'   ⏭️  Skipped existing user: {email}')
                continue
            
            try:
                # Create user with proper password hashing
                user = User.objects.create_user(
                    email=email,
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    phone_number=user_data.get('phone_number', ''),
                    two_factor_enabled=user_data.get('two_factor_enabled', False)
                )
                
                created_count += 1
                role_display = user.get_role_display()
                self.stdout.write(f'   ✅ Created {role_display}: {email}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create user {email}: {str(e)}')
                )
                raise
        
        self.stdout.write(
            self.style.SUCCESS(
                f'   📊 Users: {created_count} created, {skipped_count} skipped'
            )
        )

    def _seed_tickets(self, tickets_data):
        """Import test tickets from data."""
        self.stdout.write('🎫 Importing test tickets...')
        
        created_count = 0
        skipped_count = 0
        
        for ticket_data in tickets_data:
            try:
                # Get user references
                assigned_contractor = self._get_user_by_email(
                    ticket_data['assigned_contractor_email']
                )
                created_by = self._get_user_by_email(
                    ticket_data['created_by_email']
                )
                
                # Calculate expiration date
                expiration_date = self._calculate_expiration_date(
                    ticket_data['expiration_days_from_now']
                )
                
                # Check if similar ticket already exists
                if self._ticket_exists(ticket_data['organization'], ticket_data['location']):
                    skipped_count += 1
                    self.stdout.write(
                        f'   ⏭️  Skipped existing ticket: {ticket_data["organization"]}'
                    )
                    continue
                
                # Create ticket
                ticket = Ticket.objects.create(
                    organization=ticket_data['organization'],
                    location=ticket_data['location'],
                    status=ticket_data['status'],
                    notes=ticket_data['notes'],
                    expiration_date=expiration_date,
                    assigned_contractor=assigned_contractor,
                    created_by=created_by,
                    updated_by=created_by
                )
                
                created_count += 1
                status_display = ticket.get_status_display()
                self.stdout.write(
                    f'   ✅ Created {status_display} ticket: {ticket.ticket_number} - {ticket.organization}'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'   ❌ Failed to create ticket for {ticket_data["organization"]}: {str(e)}'
                    )
                )
                raise
        
        self.stdout.write(
            self.style.SUCCESS(
                f'   📊 Tickets: {created_count} created, {skipped_count} skipped'
            )
        )

    def _get_user_by_email(self, email):
        """Get user by email or raise error if not found."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'User not found: {email}')

    def _calculate_expiration_date(self, days_from_now):
        """Calculate expiration date based on days from now."""
        return timezone.now() + timedelta(days=days_from_now)

    def _ticket_exists(self, organization, location):
        """Check if a ticket with similar organization and location exists."""
        return Ticket.objects.filter(
            organization=organization,
            location=location
        ).exists()
