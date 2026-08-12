import datetime
from django.utils import timezone
from django.core.cache import cache
from account.models import DailyActivity
from rest_framework_simplejwt.authentication import JWTAuthentication

class TimezoneMiddleware:
    """
    Middleware to read the Time-Zone-Offset header and activate the corresponding timezone.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_offset_minutes = request.headers.get('Time-Zone-Offset')
        if tz_offset_minutes:
            try:
                offset = datetime.timedelta(minutes=int(tz_offset_minutes))
                tz = datetime.timezone(offset)
                timezone.activate(tz)
            except ValueError:
                timezone.deactivate()
        else:
            timezone.deactivate()

        return self.get_response(request)

class DailyActivityMiddleware:
    """
    Middleware to ensure the user gets a daily activity logged (and awarded points) 
    the first time they make a request on any given day.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if not user.is_authenticated:
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result:
                    user, token = auth_result
            except Exception:
                pass

        if user and user.is_authenticated and hasattr(user, 'account'):
            try:
                student = user.account.student
                today = timezone.localdate()
                cache_key = f"daily_activity_{student.id}_{today.isoformat()}"
                
                # Check cache to avoid hitting the database for get_or_create on every request
                if not cache.get(cache_key):
                    # Try to get or create daily activity
                    # This Awards 1 point for login (the first action of the day)
                    activity, created = DailyActivity.objects.get_or_create(
                        student=student,
                        date=today,
                        defaults={"points_earned": 1} 
                    )
                    
                    if created:
                        # Update the student's total points since it's a new day
                        progress = student.progress
                        progress.add_points(1)
                    
                    # Set cache to expire at the end of the day (timeout=86400 is 24 hours)
                    cache.set(cache_key, True, timeout=86400)
            except Exception:
                # If the user is not a student (e.g. Teacher, Admin) or an error occurs, ignore
                pass

        response = self.get_response(request)
        return response
