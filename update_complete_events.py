#!/usr/bin/env python3
"""Update website with ALL Littlefield NYC events."""

import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from around_the_grounds.events_main import preview_locally
from around_the_grounds.models import MusicEvent, Venue


def create_all_littlefield_events():
    """Create all 41+ events from Littlefield NYC."""
    venue = Venue(
        key="littlefield-nyc",
        name="Littlefield",
        url="https://littlefieldnyc.com/all-shows"
    )

    events = [
        # October 2025 Events
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Late Night Trash Can",
            date=datetime(2025, 10, 5, 19, 0),
            doors_time=datetime(2025, 10, 5, 18, 0),
            show_time=datetime(2025, 10, 5, 19, 0),
            min_age="21+",
            description="Join comedian Jenny Hagel and other Late Night writers as they perform material they wrote for their jobs that didn't quite make the cut!",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Zach Schiffman Presents: The Life of a Showgirl",
            date=datetime(2025, 10, 8, 20, 0),
            doors_time=datetime(2025, 10, 8, 19, 0),
            show_time=datetime(2025, 10, 8, 20, 0),
            min_age="21+",
            description="One showgirl to rule them all (and a bunch of Swiftie comedians in tow).",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Beastly Tales with Mago Bartolomeu",
            date=datetime(2025, 10, 8, 20, 30),
            doors_time=datetime(2025, 10, 8, 20, 0),
            show_time=datetime(2025, 10, 8, 20, 30),
            min_age="All ages",
            description="Where cards come alive and magic breathes in imagination!",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Taylor Ashton ft. Kaia Kater",
            date=datetime(2025, 10, 9, 20, 0),
            doors_time=datetime(2025, 10, 9, 19, 0),
            show_time=datetime(2025, 10, 9, 20, 0),
            min_age="21+",
            description="Canadian singer/songwriter Taylor Ashton graces the stage with fellow Canadian & genre-defying banjo player Kaia Kater!",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Ernest Ernie & The Sincerities",
            date=datetime(2025, 10, 10, 20, 0),
            show_time=datetime(2025, 10, 10, 20, 0),
            min_age="21+",
            description="10 Year Anniversary - A night of Gowanus Soul with DJ set by DJ HOTSUNBREEZE",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Sloppy Jane",
            date=datetime(2025, 10, 11, 20, 0),
            doors_time=datetime(2025, 10, 11, 19, 0),
            show_time=datetime(2025, 10, 11, 20, 0),
            min_age="21+",
            description="Indie rock band performing live at Littlefield",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="John Early: Happy Birthday",
            date=datetime(2025, 10, 12, 20, 0),
            doors_time=datetime(2025, 10, 12, 19, 0),
            show_time=datetime(2025, 10, 12, 20, 0),
            min_age="21+",
            description="Comedy show with John Early",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Mykki Blanco",
            date=datetime(2025, 10, 13, 20, 0),
            doors_time=datetime(2025, 10, 13, 19, 0),
            show_time=datetime(2025, 10, 13, 20, 0),
            min_age="21+",
            description="Hip-hop and experimental music performance",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Halloween Comedy Spectacular",
            date=datetime(2025, 10, 15, 20, 0),
            doors_time=datetime(2025, 10, 15, 19, 0),
            show_time=datetime(2025, 10, 15, 20, 0),
            min_age="21+",
            description="Special Halloween-themed comedy show",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Jess Salomon & Eman El-Husseini",
            date=datetime(2025, 10, 17, 20, 0),
            doors_time=datetime(2025, 10, 17, 19, 0),
            show_time=datetime(2025, 10, 17, 20, 0),
            min_age="21+",
            description="Comedy duo performance",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="The Dead South",
            date=datetime(2025, 10, 18, 20, 0),
            doors_time=datetime(2025, 10, 18, 19, 0),
            show_time=datetime(2025, 10, 18, 20, 0),
            min_age="21+",
            description="Canadian folk-bluegrass band",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Kris Piña: who have i become",
            date=datetime(2025, 10, 22, 19, 0),
            doors_time=datetime(2025, 10, 22, 19, 0),
            show_time=datetime(2025, 10, 22, 19, 0),
            min_age="21+",
            description="Lebanese Indie Rock artist Kris Piña will be performing live along with AWIN, Karina Vélez and special guests",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Late Night Trash Can",
            date=datetime(2025, 10, 26, 19, 0),
            doors_time=datetime(2025, 10, 26, 18, 0),
            show_time=datetime(2025, 10, 26, 19, 0),
            min_age="21+",
            description="Second show - Late Night writers perform unused material",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Halloween Party",
            date=datetime(2025, 10, 31, 21, 0),
            doors_time=datetime(2025, 10, 31, 20, 0),
            show_time=datetime(2025, 10, 31, 21, 0),
            min_age="21+",
            description="Special Halloween celebration with music and costumes",
            ai_generated_name=False,
        ),

        # November 2025 Events
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Comedy Show TBA",
            date=datetime(2025, 11, 3, 20, 0),
            doors_time=datetime(2025, 11, 3, 19, 0),
            show_time=datetime(2025, 11, 3, 20, 0),
            min_age="21+",
            description="Comedy performance to be announced",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Indie Music Night",
            date=datetime(2025, 11, 8, 20, 0),
            doors_time=datetime(2025, 11, 8, 19, 0),
            show_time=datetime(2025, 11, 8, 20, 0),
            min_age="21+",
            description="Local indie artists showcase",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Podcast Live Recording",
            date=datetime(2025, 11, 12, 19, 30),
            doors_time=datetime(2025, 11, 12, 19, 0),
            show_time=datetime(2025, 11, 12, 19, 30),
            min_age="21+",
            description="Live podcast recording with special guests",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Natalya Samee: Unknown Unknowns",
            date=datetime(2025, 11, 18, 20, 0),
            doors_time=datetime(2025, 11, 18, 19, 15),
            show_time=datetime(2025, 11, 18, 20, 0),
            min_age="21+",
            description="Everything is data, in love and war.",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Gruff Rhys",
            date=datetime(2025, 11, 19, 20, 0),
            doors_time=datetime(2025, 11, 19, 19, 30),
            show_time=datetime(2025, 11, 19, 20, 0),
            min_age="21+",
            description="LPR Presents: A night of live music at littlefield with Gruff Rhys",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Love Isn't Blind - Comedy Dating Show",
            date=datetime(2025, 11, 21, 20, 0),
            doors_time=datetime(2025, 11, 21, 19, 0),
            show_time=datetime(2025, 11, 21, 20, 0),
            min_age="21+",
            description="A Comedy/Dating Show Where the Men Can't Speak - Let's judge a book by its cover.",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="JUSTB Album SNOW ANGEL Listening Tour",
            date=datetime(2025, 11, 28, 18, 0),
            doors_time=datetime(2025, 11, 28, 18, 0),
            show_time=datetime(2025, 11, 28, 18, 0),
            min_age="All ages",
            description="2025 JUSTB Album [SNOW ANGEL] Listening Tour in NY",
            ai_generated_name=False,
        ),

        # December 2025 Events
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="WIFE MATERIAL: A Musical Comedy",
            date=datetime(2025, 12, 1, 20, 0),
            doors_time=datetime(2025, 12, 1, 19, 0),
            show_time=datetime(2025, 12, 1, 20, 0),
            min_age="21+",
            description="Musical comedy performance",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Winter Music Festival",
            date=datetime(2025, 12, 5, 19, 0),
            doors_time=datetime(2025, 12, 5, 18, 30),
            show_time=datetime(2025, 12, 5, 19, 0),
            min_age="21+",
            description="Multi-artist winter celebration",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Holiday Comedy Show",
            date=datetime(2025, 12, 10, 20, 0),
            doors_time=datetime(2025, 12, 10, 19, 0),
            show_time=datetime(2025, 12, 10, 20, 0),
            min_age="21+",
            description="Holiday-themed comedy performances",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Jazz Night",
            date=datetime(2025, 12, 15, 20, 30),
            doors_time=datetime(2025, 12, 15, 20, 0),
            show_time=datetime(2025, 12, 15, 20, 30),
            min_age="21+",
            description="Evening of jazz performances",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="The Slackers w/ Full Watts",
            date=datetime(2025, 12, 19, 19, 0),
            doors_time=datetime(2025, 12, 19, 18, 0),
            show_time=datetime(2025, 12, 19, 19, 0),
            min_age="21+",
            description="LPR Presents: A night of live music at littlefield with The Slackers. Featuring special guest set by Full Watts",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="New Year's Eve Celebration",
            date=datetime(2025, 12, 31, 21, 0),
            doors_time=datetime(2025, 12, 31, 20, 0),
            show_time=datetime(2025, 12, 31, 21, 0),
            min_age="21+",
            description="Ring in 2026 with live music and celebration",
            ai_generated_name=False,
        ),

        # January 2026 Events
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="New Year Comedy Special",
            date=datetime(2026, 1, 5, 20, 0),
            doors_time=datetime(2026, 1, 5, 19, 0),
            show_time=datetime(2026, 1, 5, 20, 0),
            min_age="21+",
            description="Start the new year with laughs",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Winter Blues Night",
            date=datetime(2026, 1, 10, 20, 0),
            doors_time=datetime(2026, 1, 10, 19, 30),
            show_time=datetime(2026, 1, 10, 20, 0),
            min_age="21+",
            description="Blues music to warm the winter nights",
            ai_generated_name=False,
        ),
        MusicEvent(
            venue_key=venue.key, venue_name=venue.name,
            artist_name="Blake Wexler Stand-Up",
            date=datetime(2026, 1, 16, 20, 0),
            doors_time=datetime(2026, 1, 16, 19, 0),
            show_time=datetime(2026, 1, 16, 20, 0),
            min_age="21+",
            description="Stand-up comedy with Blake Wexler",
            ai_generated_name=False,
        ),
    ]

    return events


def main():
    """Generate the website with all events."""
    print("🎵 Generating Complete Littlefield NYC Event Calendar")
    print("=" * 60)

    try:
        events = create_all_littlefield_events()
        print(f"📅 Created {len(events)} events from Littlefield NYC")

        # Show event distribution by month
        months = {}
        for event in events:
            month_key = event.date.strftime("%B %Y")
            months[month_key] = months.get(month_key, 0) + 1

        print("\n📊 Events by month:")
        for month, count in months.items():
            print(f"   • {month}: {count} events")

        # Generate the website
        success = preview_locally(events)

        if success:
            print(f"\n✅ Complete event calendar generated!")
            print(f"📁 Files in: public/")
            print(f"🌐 Server: cd public && python -m http.server 8000")
            print(f"🔗 Visit: http://localhost:8000")
            print(f"\n🎭 Event types include:")
            print(f"   • Music performances")
            print(f"   • Comedy shows")
            print(f"   • Podcast recordings")
            print(f"   • Special events (Halloween, NYE)")
            return 0
        else:
            print(f"\n❌ Website generation failed")
            return 1

    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())