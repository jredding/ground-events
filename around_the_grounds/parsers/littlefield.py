import logging
import re
from datetime import datetime
from typing import List, Optional

import aiohttp

from ..models import Brewery, FoodTruckEvent
from .base import BaseParser


class LittlefieldParser(BaseParser):
    """
    Parser for Littlefield venue in Brooklyn, NY.
    Extracts event information from Eventbrite widgets embedded in the page.
    """

    def __init__(self, brewery: Brewery):
        super().__init__(brewery)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def parse(self, session: aiohttp.ClientSession) -> List[FoodTruckEvent]:
        """
        Parse events from Littlefield's Eventbrite-powered page.

        Returns:
            List of FoodTruckEvent objects
        """
        try:
            soup = await self.fetch_page(session, self.brewery.url)
            events = []

            # Find all event article containers
            event_articles = soup.find_all("article", class_=re.compile(r"wfea-venue__event"))

            self.logger.info(f"Found {len(event_articles)} event articles")

            for article in event_articles:
                try:
                    event = self._parse_event(article)
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

    def _parse_event(self, article) -> Optional[FoodTruckEvent]:
        """
        Parse a single event from an event article element.

        Args:
            article: BeautifulSoup article element containing event details

        Returns:
            FoodTruckEvent object or None if parsing fails
        """
        try:
            # Extract event title from the h2
            title_elem = article.find("h2", class_=re.compile(r"wfea-venue__title"))
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            if not title:
                return None

            # Find the time element with datetime attribute
            time_elem = article.find("time", class_=re.compile(r"wfea-venue__date-time"))
            if not time_elem:
                self.logger.warning(f"No time element found for event: {title}")
                return None

            # Get datetime attribute (ISO format: 2025-11-04T18:30:00-05:00)
            datetime_str = time_elem.get("datetime")
            if not datetime_str:
                # Try to parse from text content
                date_text = time_elem.get_text(strip=True)
                event_date, start_time, end_time = self._parse_datetime_from_text(date_text)
            else:
                event_date, start_time, end_time = self._parse_datetime_from_iso(datetime_str)

            if not event_date:
                self.logger.warning(f"Could not parse date for event: {title}")
                return None

            # Extract description from the excerpt
            desc_element = article.find("div", class_=re.compile(r"wfea-venue__excerpt"))
            description = ""
            if desc_element:
                description = desc_element.get_text(separator=" ", strip=True)
                # Remove "Read More »" text
                description = re.sub(r"Read More\s*».*$", "", description).strip()

            return FoodTruckEvent(
                brewery_key=self.brewery.key,
                brewery_name=self.brewery.name,
                food_truck_name=title,
                date=event_date,
                start_time=start_time,
                end_time=end_time,
                description=description,
            )

        except Exception as e:
            self.logger.warning(f"Error parsing event element: {e}")
            return None

    def _find_date_text(self, container) -> Optional[str]:
        """
        Find date text within an event container.

        Args:
            container: BeautifulSoup element containing event details

        Returns:
            Date text string or None
        """
        # Look for elements that might contain date information
        # Eventbrite widget typically has date in specific elements
        date_element = container.find(
            "div", class_=re.compile(r"wfea-date|event-date|date")
        )
        if date_element:
            return date_element.get_text(strip=True)

        # Look for any text that looks like a date
        text = container.get_text()
        date_pattern = r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})"
        match = re.search(date_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

        return None

    def _parse_datetime_from_iso(
        self, datetime_str: str
    ) -> tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        """
        Parse date and time from ISO 8601 format.

        Args:
            datetime_str: ISO datetime string (e.g., "2025-11-04T18:30:00-05:00")

        Returns:
            Tuple of (event_date, start_time, end_time)
        """
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

            # Remove timezone info to make it naive (consistent with other parsers)
            dt = dt.replace(tzinfo=None)

            # Extract just the date part
            event_date = datetime(dt.year, dt.month, dt.day)

            return event_date, dt, None

        except Exception as e:
            self.logger.warning(f"Error parsing ISO datetime '{datetime_str}': {e}")
            return None, None, None

    def _parse_datetime_from_text(
        self, date_text: str
    ) -> tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        """
        Parse date and time from text format.

        Args:
            date_text: Text containing date/time information
                      (e.g., "November 4, 2025, 6:30 pm - 11:00 pm")

        Returns:
            Tuple of (event_date, start_time, end_time)
        """
        try:
            # Pattern: "November 4, 2025, 6:30 pm - 11:00 pm"
            datetime_match = re.search(
                r"([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4}),?\s+(\d{1,2}):(\d{2})\s*(am|pm)\s*-\s*(\d{1,2}):(\d{2})\s*(am|pm)",
                date_text,
                re.IGNORECASE,
            )
            if datetime_match:
                month_str = datetime_match.group(1)
                day = int(datetime_match.group(2))
                year = int(datetime_match.group(3))
                start_hour = int(datetime_match.group(4))
                start_minute = int(datetime_match.group(5))
                start_am_pm = datetime_match.group(6).lower()
                end_hour = int(datetime_match.group(7))
                end_minute = int(datetime_match.group(8))
                end_am_pm = datetime_match.group(9).lower()

                # Convert to 24-hour format
                if start_am_pm == "pm" and start_hour != 12:
                    start_hour += 12
                elif start_am_pm == "am" and start_hour == 12:
                    start_hour = 0

                if end_am_pm == "pm" and end_hour != 12:
                    end_hour += 12
                elif end_am_pm == "am" and end_hour == 12:
                    end_hour = 0

                # Parse date
                date_obj = datetime.strptime(f"{month_str} {day} {year}", "%B %d %Y")
                start_time = datetime(
                    year=date_obj.year,
                    month=date_obj.month,
                    day=date_obj.day,
                    hour=start_hour,
                    minute=start_minute,
                )
                end_time = datetime(
                    year=date_obj.year,
                    month=date_obj.month,
                    day=date_obj.day,
                    hour=end_hour,
                    minute=end_minute,
                )

                return date_obj, start_time, end_time

            # Try just date without time range
            date_match = re.search(
                r"([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})", date_text, re.IGNORECASE
            )
            if date_match:
                month_str = date_match.group(1)
                day = int(date_match.group(2))
                year = int(date_match.group(3))

                date_obj = datetime.strptime(f"{month_str} {day} {year}", "%B %d %Y")
                return date_obj, None, None

            return None, None, None

        except Exception as e:
            self.logger.warning(f"Error parsing datetime text '{date_text}': {e}")
            return None, None, None
