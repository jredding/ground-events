import logging
import re
from datetime import datetime
from typing import List, Optional

import aiohttp

from ..models import Brewery, FoodTruckEvent
from .base import BaseParser


class BellHouseParser(BaseParser):
    """
    Parser for The Bell House venue in Brooklyn, NY.
    Extracts event information from LiveNation calendar pages.
    """

    def __init__(self, brewery: Brewery):
        super().__init__(brewery)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def parse(self, session: aiohttp.ClientSession) -> List[FoodTruckEvent]:
        """
        Parse events from The Bell House's calendar page.

        Returns:
            List of FoodTruckEvent objects
        """
        events = []

        try:
            # Get current and next month to cover events in the next 7 days
            now = datetime.now()
            months_to_fetch = [
                (now.year, now.month),
                (now.year, now.month + 1) if now.month < 12 else (now.year + 1, 1),
            ]

            for year, month in months_to_fetch:
                month_events = await self._parse_month(session, year, month)
                events.extend(month_events)

            self.logger.info(f"Parsed {len(events)} valid events from {self.brewery.name}")
            return events

        except Exception as e:
            self.logger.error(f"Error parsing {self.brewery.name}: {e}")
            return []

    async def _parse_month(
        self, session: aiohttp.ClientSession, year: int, month: int
    ) -> List[FoodTruckEvent]:
        """
        Parse events from a specific month.

        Args:
            session: aiohttp client session
            year: Year to fetch
            month: Month to fetch (1-12)

        Returns:
            List of FoodTruckEvent objects for that month
        """
        try:
            # Build calendar URL for this month
            calendar_url = f"https://www.thebellhouseny.com/shows/calendar/{year}-{month:02d}"

            soup = await self.fetch_page(session, calendar_url)
            events = []

            # Find all event links with title attributes
            event_links = soup.find_all("a", class_="chakra-link", title=True, role="group")

            self.logger.info(f"Found {len(event_links)} event links for {year}-{month:02d}")

            for link in event_links:
                try:
                    event = self._parse_event(link)
                    if event:
                        events.append(event)
                except Exception as e:
                    self.logger.warning(f"Error parsing event: {e}")
                    continue

            return events

        except Exception as e:
            self.logger.error(f"Error parsing month {year}-{month:02d}: {e}")
            return []

    def _parse_event(self, link_element) -> Optional[FoodTruckEvent]:
        """
        Parse a single event from a link element.

        Args:
            link_element: BeautifulSoup anchor element with title

        Returns:
            FoodTruckEvent object or None if parsing fails
        """
        try:
            # Get title attribute: "Event Name @ Time"
            title = link_element.get("title", "")
            if not title or "@" not in title:
                return None

            # Parse title: "Event Name @ 7:30PM"
            parts = title.split("@")
            if len(parts) != 2:
                return None

            event_name = parts[0].strip()
            time_str = parts[1].strip()

            # Get date from href URL
            # Format: "https://www.ticketmaster.com/event-name-brooklyn-new-york-11-07-2025/event/..."
            href = link_element.get("href", "")
            event_date = self._parse_date_from_url(href)

            if not event_date:
                self.logger.warning(f"Could not parse date from URL: {href}")
                return None

            # Parse time
            start_time = self._parse_time(event_date, time_str)

            return FoodTruckEvent(
                brewery_key=self.brewery.key,
                brewery_name=self.brewery.name,
                food_truck_name=event_name,
                date=event_date,
                start_time=start_time,
                end_time=None,
                description="",
            )

        except Exception as e:
            self.logger.warning(f"Error parsing event element: {e}")
            return None

    def _parse_date_from_url(self, url: str) -> Optional[datetime]:
        """
        Parse date from Ticketmaster URL.

        Args:
            url: Ticketmaster event URL containing date

        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Pattern: "brooklyn-new-york-MM-DD-YYYY"
            date_match = re.search(r"(\d{2})-(\d{2})-(\d{4})", url)
            if not date_match:
                return None

            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = int(date_match.group(3))

            return datetime(year=year, month=month, day=day)

        except Exception as e:
            self.logger.warning(f"Error parsing date from URL '{url}': {e}")
            return None

    def _parse_time(self, event_date: datetime, time_str: str) -> Optional[datetime]:
        """
        Parse time and combine with event date.

        Args:
            event_date: Date of the event
            time_str: Time string (e.g., "7:30PM", "10:00PM")

        Returns:
            datetime object with date and time or None if parsing fails
        """
        try:
            # Pattern: "7:30PM" or "10:00PM"
            time_match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", time_str, re.IGNORECASE)
            if not time_match:
                return None

            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            am_pm = time_match.group(3).upper()

            # Convert to 24-hour format
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0

            return datetime(
                year=event_date.year,
                month=event_date.month,
                day=event_date.day,
                hour=hour,
                minute=minute,
            )

        except Exception as e:
            self.logger.warning(f"Error parsing time '{time_str}': {e}")
            return None
