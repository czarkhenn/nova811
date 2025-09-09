from celery import shared_task
from django.utils import timezone
import logging

from .services import ExpirationService

logger = logging.getLogger(__name__)


@shared_task
def check_expiring_tickets():
    """
    Celery task to check for expiring tickets and send alerts.
    Runs every hour to check for tickets expiring within 48 hours.
    """
    try:
        logger.info("Starting expiring tickets check...")
        
        # Send expiration alerts
        alert_count = ExpirationService.send_expiration_alerts()
        
        logger.info(f"Expiring tickets check completed. {alert_count} alerts sent.")
        return {
            'status': 'success',
            'alerts_sent': alert_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in check_expiring_tickets task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def mark_expired_tickets():
    """
    Celery task to automatically mark expired tickets as closed.
    Runs daily to clean up expired tickets.
    """
    try:
        logger.info("Starting expired tickets cleanup...")
        
        # Mark expired tickets
        updated_count = ExpirationService.mark_expired_tickets()
        
        logger.info(f"Expired tickets cleanup completed. {updated_count} tickets marked as expired.")
        return {
            'status': 'success',
            'tickets_expired': updated_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in mark_expired_tickets task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def cleanup_old_logs():
    """
    Celery task to clean up old log entries.
    Runs weekly to remove logs older than 90 days.
    """
    try:
        from datetime import timedelta
        from .models import UserLog, TicketLog
        
        logger.info("Starting old logs cleanup...")
        
        # Calculate cutoff date (90 days ago)
        cutoff_date = timezone.now() - timedelta(days=90)
        
        # Delete old user logs
        user_logs_deleted = UserLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        # Delete old ticket logs
        ticket_logs_deleted = TicketLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        total_deleted = user_logs_deleted + ticket_logs_deleted
        
        logger.info(f"Old logs cleanup completed. {total_deleted} log entries deleted.")
        return {
            'status': 'success',
            'user_logs_deleted': user_logs_deleted,
            'ticket_logs_deleted': ticket_logs_deleted,
            'total_deleted': total_deleted,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_logs task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def generate_ticket_reports():
    """
    Celery task to generate periodic ticket reports.
    Runs daily to generate summary reports for admins.
    """
    try:
        from .selectors import DashboardSelector
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        logger.info("Starting ticket reports generation...")
        
        # Get summary statistics
        status_summary = list(DashboardSelector.get_ticket_summary_by_status())
        contractor_summary = list(DashboardSelector.get_ticket_summary_by_contractor())
        
        # Log summary to console (can be extended to email/database)
        logger.info("=== DAILY TICKET REPORT ===")
        logger.info("Tickets by Status:")
        for item in status_summary:
            logger.info(f"  {item['status']}: {item['count']}")
        
        logger.info("Tickets by Contractor:")
        for item in contractor_summary:
            contractor_name = f"{item['assigned_contractor__first_name']} {item['assigned_contractor__last_name']}"
            logger.info(f"  {contractor_name}: {item['total_tickets']} total, {item['open_tickets']} open")
        
        logger.info("Ticket reports generation completed.")
        return {
            'status': 'success',
            'status_summary': status_summary,
            'contractor_summary': contractor_summary,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in generate_ticket_reports task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }
