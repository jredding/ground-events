import logging
import re
from datetime import datetime
from typing import List, Optional

import aiohttp

from ..models import Brewery, FoodTruckEvent
from .base import BaseParser


class UnionHallParser(BaseParser):
    """
    Parser for Union Hall venue in Brooklyn, NY.
    Extracts event information from Spacecrafted CMS with Eventbrite integration.
    """

    def __init__(self, brewery: Brewery):
        super().__init__(brewery)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def parse(self, session: aiohttp.ClientSession) -> List[FoodTruckEvent]:
        """
        Parse events from Union Hall's calendar page.

        Returns:
            List of FoodTruckEvent objects
        """
        try:
            soup = await self.fetch_page(session, self.brewery.url)
            events = []

            # Find all event items
            event_items = soup.find_all("div", class_="eventColl-item")

            self.logger.info(f"Found {len(event_items)} event items")

            for item in event_items:
                try:
                    event = self._parse_event(item)
                    if event:
                        events.append(event)
                except Exception as e:
                    self.logger.warning(f"Error parsing event: {e}")
                    continue

            self.logger.info(f"Parsed {len(events)} valid events from {self.brewery.name}")
            return events

        except Exception as e:
            self.logger.error(f"Error parsing {self.brewery.name}: {e}")
            return []

    def _parse_event(self, item) -> Optional[FoodTruckEvent]:
        """
        Parse a single event from an event item element.

        Args:
            item: BeautifulSoup element containing event details

        Returns:
            FoodTruckEvent object or None if parsing fails
        """
        try:
            # Extract event title
            title_elem = item.find("h2", class_="eventColl-eventInfo")
            if not title_elem:
                # Try alternate location
                title_elem = item.find("div", class_="eventColl-eventTitle")
                if not title_elem:
                    return None

            # Get the link text or h2 text
            title_link = title_elem.find("a")
            if title_link:
                title = title_link.get_text(strip=True)
            else:
                title = title_elem.get_text(strip=True)

            if not title:
                return None

            # Extract date from eventColl-dateInfo
            date_info = item.find("div", class_="eventColl-dateInfo")
            if not date_info:
                self.logger.warning(f"No date info found for event: {title}")
                return None

            # Get month and date
            month_elem = date_info.find("span", class_="eventColl-month")
            date_elem = date_info.find("span", class_="eventColl-date")

            if not month_elem or not date_elem:
                self.logger.warning(f"Missing month or date for event: {title}")
                return None

            month_text = month_elem.get_text(strip=True)
            date_text = date_elem.get_text(strip=True)

            # Parse the date
            event_date = self._parse_date(month_text, date_text)
            if not event_date:
                self.logger.warning(f"Could not parse date for event: {title}")
                return None

            # Extract artist names if available
            artists_elem = item.find("h3", class_="eventColl-artistNames")
            description = ""
            if artists_elem:
                description = artists_elem.get_text(strip=True)

            return FoodTruckEvent(
                brewery_key=self.brewery.key,
                brewery_name=self.brewery.name,
                food_truck_name=title,
                date=event_date,
                start_time=None,  # Union Hall doesn't show specific times on calendar view
                end_time=None,
                description=description,
            )

        except Exception as e:
            self.logger.warning(f"Error parsing event element: {e}")
            return None

    def _parse_date(self, month_text: str, date_text: str) -> Optional[datetime]:
        """
        Parse date from month and date strings.

        Args:
            month_text: Month abbreviation (e.g., "Nov")
            date_text: Day of month (e.g., "02")

        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Get current year (assume events are in current or next year)
            current_year = datetime.now().year
            current_month = datetime.now().month

            # Parse month abbreviation
            month_num = datetime.strptime(month_text, "%b").month

            # If the month is before current month, assume next year
            year = current_year
            if month_num < current_month:
                year = current_year + 1

            day = int(date_text)

            # Create datetime object
            event_date = datetime(year=year, month=month_num, day=day)

            return event_date

        except Exception as e:
            self.logger.warning(f"Error parsing date '{month_text} {date_text}': {e}")
            return None
