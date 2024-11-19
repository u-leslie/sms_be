import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib import messages

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = now()

            if last_activity:
                last_activity_time = datetime.datetime.fromisoformat(last_activity)
                elapsed_time = (current_time - last_activity_time).total_seconds()
                
                # Log out if more than 30 minutes (or SESSION_COOKIE_AGE)
                if elapsed_time > settings.SESSION_COOKIE_AGE:
                    request.session.flush()  # Log the user out
                    messages.info(request, "You have been logged out due to inactivity.")
                    return redirect('login')  # Redirect to login page

            # Update last activity timestamp
            request.session['last_activity'] = current_time.isoformat()

        return self.get_response(request)
