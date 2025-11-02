"""Tests for Roulette parser."""

import aiohttp
import pytest
from aioresponses import aioresponses
from freezegun import freeze_time

from around_the_grounds.models import Brewery
from around_the_grounds.parsers.roulette import RouletteParser


class TestRouletteParser:
    """Test the RouletteParser class."""

    @pytest.fixture
    def brewery(self) -> Brewery:
        """Create a test brewery for Roulette."""
        return Brewery(
            key="roulette",
            name="Roulette",
            url="https://roulette.org/calendar/",
            parser_config={
                "note": "Experimental music venue in Brooklyn with event calendar",
                "selectors": {
                    "event_container": "div.event",
                    "event_title": "h2.event-title a",
                    "event_time": "div.event-time",
                    "event_desc": "div.event-desc"
                }
            },
        )

    @pytest.fixture
    def parser(self, brewery: Brewery) -> RouletteParser:
        """Create a parser instance."""
        return RouletteParser(brewery)

    @pytest.fixture
    def sample_html(self) -> str:
        """Sample HTML with event data."""
        return """
        <html>
        <body>
            <div class="list-events">
                <div class="event">
                    <h2 class="event-title">
                        <a href="https://roulette.org/event/test-event/">Test Concert Event</a>
                    </h2>
                    <div class="event-img">
                        <a href="https://roulette.org/event/test-event/"><img src="test.jpg" /></a>
                    </div>
                    <div class="event-time">Tuesday, November 4, 2025. 7:00 pm</div>
                    <div class="event-price">Tickets $15</div>
                    <a class="event-purchase" href="https://example.com/tickets" target="_blank">Purchase Tickets</a>
                    <div class="event-desc">
                        A participatory exploration of experimental music.
                    </div>
                </div>
                <div class="event">
                    <h2 class="event-title">
                        <a href="https://roulette.org/event/jazz-night/">Jazz Performance</a>
                    </h2>
                    <div class="event-img">
                        <a href="https://roulette.org/event/jazz-night/"><img src="jazz.jpg" /></a>
                    </div>
                    <div class="event-time">Wednesday, November 5, 2025. 8:00 pm</div>
                    <div class="event-price">Tickets $25</div>
                    <a class="event-purchase" href="https://example.com/tickets2" target="_blank">Purchase Tickets</a>
                    <div class="event-desc">
                        An evening of contemporary jazz music.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @pytest.mark.asyncio
    @freeze_time("2025-11-02")
    async def test_parse_events(self, parser: RouletteParser, sample_html: str) -> None:
        """Test parsing events from HTML."""
        with aioresponses() as m:
            m.get(parser.brewery.url, status=200, body=sample_html)

            async with aiohttp.ClientSession() as session:
                events = await parser.parse(session)

                assert len(events) == 2

                # Check first event
                event1 = events[0]
                assert event1.brewery_key == "roulette"
                assert event1.brewery_name == "Roulette"
                assert event1.food_truck_name == "Test Concert Event"
                assert event1.date.month == 11
                assert event1.date.day == 4
                assert event1.date.year == 2025
                assert event1.start_time is not None
                assert event1.start_time.hour == 19  # 7pm
                assert event1.start_time.minute == 0
                assert event1.description == "A participatory exploration of experimental music."

                # Check second event
                event2 = events[1]
                assert event2.food_truck_name == "Jazz Performance"
                assert event2.date.day == 5
                assert event2.start_time.hour == 20  # 8pm

    @pytest.mark.asyncio
    async def test_parse_empty_schedule(self, parser: RouletteParser) -> None:
        """Test parsing when no events are found."""
        empty_html = "<html><body><div class='list-events'></div></body></html>"

        with aioresponses() as m:
            m.get(parser.brewery.url, status=200, body=empty_html)

            async with aiohttp.ClientSession() as session:
                events = await parser.parse(session)

                assert len(events) == 0

    @pytest.mark.asyncio
    async def test_parse_event_without_time(self, parser: RouletteParser) -> None:
        """Test parsing event with missing time element."""
        html_no_time = """
        <html><body>
            <div class="event">
                <h2 class="event-title"><a href="#">Event Title</a></h2>
            </div>
        </body></html>
        """

        with aioresponses() as m:
            m.get(parser.brewery.url, status=200, body=html_no_time)

            async with aiohttp.ClientSession() as session:
                events = await parser.parse(session)

                # Should skip events without time
                assert len(events) == 0

    @pytest.mark.asyncio
    async def test_parse_network_error(self, parser: RouletteParser) -> None:
        """Test handling of network errors."""
        with aioresponses() as m:
            m.get(parser.brewery.url, exception=aiohttp.ClientError("Network error"))

            async with aiohttp.ClientSession() as session:
                with pytest.raises(ValueError, match="Failed to parse brewery website"):
                    await parser.parse(session)

    def test_parse_datetime_valid(self, parser: RouletteParser) -> None:
        """Test parsing valid datetime string."""
        time_text = "Tuesday, November 4, 2025. 7:00 pm"
        date_obj, start_time, end_time = parser._parse_datetime(time_text)

        assert date_obj is not None
        assert date_obj.year == 2025
        assert date_obj.month == 11
        assert date_obj.day == 4

        assert start_time is not None
        assert start_time.hour == 19  # 7pm
        assert start_time.minute == 0

        assert end_time is None  # Roulette doesn't provide end times

    def test_parse_datetime_am(self, parser: RouletteParser) -> None:
        """Test parsing AM time."""
        time_text = "Monday, December 1, 2025. 11:30 am"
        date_obj, start_time, end_time = parser._parse_datetime(time_text)

        assert start_time is not None
        assert start_time.hour == 11
        assert start_time.minute == 30

    def test_parse_datetime_noon(self, parser: RouletteParser) -> None:
        """Test parsing 12 pm (noon)."""
        time_text = "Monday, December 1, 2025. 12:00 pm"
        date_obj, start_time, end_time = parser._parse_datetime(time_text)

        assert start_time is not None
        assert start_time.hour == 12
        assert start_time.minute == 0

    def test_parse_datetime_midnight(self, parser: RouletteParser) -> None:
        """Test parsing 12 am (midnight)."""
        time_text = "Monday, December 1, 2025. 12:00 am"
        date_obj, start_time, end_time = parser._parse_datetime(time_text)

        assert start_time is not None
        assert start_time.hour == 0
        assert start_time.minute == 0

    def test_parse_datetime_invalid(self, parser: RouletteParser) -> None:
        """Test parsing invalid datetime string."""
        time_text = "Invalid date format"
        date_obj, start_time, end_time = parser._parse_datetime(time_text)

        assert date_obj is None
        assert start_time is None
        assert end_time is None
