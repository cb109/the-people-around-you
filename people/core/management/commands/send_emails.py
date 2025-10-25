from datetime import datetime
import textwrap

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from people.core.models import Person
from people.core.mailing import send_email_via_gmail

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = datetime.today().date()
        formatted_today = today.strftime("%d.%m.%Y")

        for user in (
            User.objects.filter(is_active=True)
            .exclude(email__exact="")
            .order_by("created_at")
        ):
            persons = Person.objects.filter(created_by=user).order_by(
                "name", "created_at"
            )
            if not persons.exists():
                continue

            event_descriptions_text = ""
            event_descriptions_html = "<ul>"

            for person in persons:
                if (
                    person.date_of_birth
                    and person.date_of_birth.day == today.day
                    and person.date_of_birth.month == today.month
                ):
                    formatted_date_of_birth = person.date_of_birth.strftime("%d.%m.%Y")

                    event_descriptions_text += f"- Birthday: {person.name} turned {person.age} years today (born {formatted_date_of_birth})\n"
                    event_descriptions_html += f"<li>Birthday: <b>{person.name}</b> turned <b>{person.age}</b> years today (born {formatted_date_of_birth})</li>"

                if (
                    person.date_of_death
                    and person.date_of_death.day == today.day
                    and person.date_of_death.month == today.month
                ):
                    formatted_date_of_death = person.date_of_death.strftime("%d.%m.%Y")
                    died_years_ago = today.year - person.date_of_death.year
                    age = person.get_age(ignore_death=True)

                    event_descriptions_text += f"- Death: {person.name} left us {died_years_ago} years ago (deceased {formatted_date_of_death}, would be {age} years old now)\n"
                    event_descriptions_html += f"<li>Death: <b>{person.name}</b> left us <b>{died_years_ago}</b> years ago (deceased {formatted_date_of_death}, would be {age} years old now)</li>"

            event_descriptions_html += "</ul>"

            if not event_descriptions_text:
                continue

            send_email_via_gmail(
                recipient=user.email,
                subject=(
                    f"[people] Today in the lives of the people around you ({formatted_today})"
                ),
                body=textwrap.dedent(
                    f"""
                    {event_descriptions_text}

                    Go to page: <a href='{settings.SITE_URL}' target="_blank">{settings.SITE_URL}</a>
                """
                ),
                html=textwrap.dedent(
                    f"""
                    {event_descriptions_html}

                    Go to page: <a href='{settings.SITE_URL}' target="_blank">{settings.SITE_URL}</a>
                """
                ),
            )
