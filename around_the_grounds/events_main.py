"""Main entry point for around-the-grounds CLI adapted for music venue events."""

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except ImportError:
    # dotenv is optional, fall back to os.environ
    pass

from .config.settings import get_git_repository_url
from .models import Venue, MusicEvent
from .scrapers.coordinator import ScraperCoordinator, ScrapingError
from .utils.timezone_utils import format_time_with_timezone


def load_venue_config(config_path: Optional[str] = None) -> List[Venue]:
    """Load venue configuration from JSON file."""
    if config_path is None:
        config_path_obj = Path(__file__).parent / "config" / "venues.json"
    else:
        config_path_obj = Path(config_path)

    if not config_path_obj.exists():
        raise FileNotFoundError(f"Config file not found: {config_path_obj}")

    with open(config_path_obj, "r") as f:
        config = json.load(f)

    venues = []
    for venue_data in config.get("venues", []):
        venue = Venue(
            key=venue_data["key"],
            name=venue_data["name"],
            url=venue_data["url"],
            parser_config=venue_data.get("parser_config", {}),
        )
        venues.append(venue)

    return venues


def format_events_output(
    events: List[MusicEvent], errors: Optional[List[ScrapingError]] = None
) -> str:
    """Format events and errors for display."""
    output = []

    # Show events
    if events:
        output.append(f"Found {len(events)} music events:")
        output.append("")

        current_date = None
        for event in events:
            event_date = event.date.strftime("%A, %B %d, %Y")

            if current_date != event_date:
                if current_date is not None:
                    output.append("")
                output.append(f"📅 {event_date}")
                current_date = event_date

            time_str = ""
            if event.doors_time:
                time_str = f" Doors: {event.doors_time.strftime('%I:%M %p')}"
                if event.show_time:
                    time_str += f" Show: {event.show_time.strftime('%I:%M %p')}"
            elif event.show_time:
                time_str = f" Show: {event.show_time.strftime('%I:%M %p')}"

            # Add AI vision indicator for AI-generated names
            if event.ai_generated_name:
                output.append(
                    f"  🎵 {event.artist_name} 🖼️🤖 @ {event.venue_name}{time_str}"
                )
            else:
                output.append(
                    f"  🎵 {event.artist_name} @ {event.venue_name}{time_str}"
                )

            if event.min_age:
                output.append(f"     Age: {event.min_age}")
            if event.description:
                output.append(f"     {event.description}")
            if event.ticket_url:
                output.append(f"     Tickets: {event.ticket_url}")

    # Show errors
    if errors:
        user_messages = [error.to_user_message() for error in errors]
        user_messages = list(dict.fromkeys(user_messages))
        if events:
            output.append("")
            output.append("⚠️  Processing Summary:")
            output.append(f"✅ {len(events)} events found successfully")
            output.append(f"❌ {len(errors)} venues failed")
        else:
            output.append("❌ No events found - all venues failed")

        output.append("")
        output.append("❌ Errors:")
        for message in user_messages:
            output.append(f"  • {message}")

    if not events and not errors:
        output.append("No music events found for the next 7 days.")

    return "\n".join(output)


def generate_web_data(
    events: List[MusicEvent], error_messages: Optional[List[str]] = None
) -> dict:
    """Generate web-friendly JSON data from events with Eastern timezone information."""
    web_events = []

    for event in events:
        # Convert event to web format with Eastern timezone indicators for NYC
        web_event = {
            "date": event.date.isoformat(),
            "artist": event.artist_name,
            "artist_name": event.artist_name,  # Alias for compatibility
            "venue": event.venue_name,
            "venue_name": event.venue_name,  # Alias for compatibility
            # Format times with Eastern timezone indicators
            "doors_time": (
                format_time_with_timezone(event.doors_time, include_timezone=True)
                if event.doors_time
                else None
            ),
            "show_time": (
                format_time_with_timezone(event.show_time, include_timezone=True)
                if event.show_time
                else None
            ),
            "end_time": (
                format_time_with_timezone(event.end_time, include_timezone=True)
                if event.end_time
                else None
            ),
            # Also include raw time strings without timezone for backward compatibility
            "doors_time_raw": (
                event.doors_time.strftime("%I:%M %p").lstrip("0")
                if event.doors_time
                else None
            ),
            "show_time_raw": (
                event.show_time.strftime("%I:%M %p").lstrip("0")
                if event.show_time
                else None
            ),
            "description": event.description,
            "min_age": event.min_age,
            "age_restriction": event.min_age,  # Alias for compatibility
            "ticket_url": event.ticket_url,
            "price": event.price,
            "timezone": "ET",  # Explicit timezone indicator for Eastern Time
        }

        # Add AI extraction indicator
        if event.ai_generated_name:
            web_event["extraction_method"] = "vision"
            web_event["artist"] = f"{event.artist_name} 🖼️🤖"

        web_events.append(web_event)

    unique_error_messages = list(dict.fromkeys(error_messages or []))

    return {
        "events": web_events,
        "updated": datetime.now(timezone.utc).isoformat(),
        "total_events": len(web_events),
        "timezone": "ET",  # Global timezone indicator for Eastern Time
        "timezone_note": "All event times are in Eastern Time (ET), which includes both EST and EDT depending on the date.",
        "errors": unique_error_messages,
    }


def deploy_to_web(
    events: List[MusicEvent],
    errors: Optional[List[ScrapingError]] = None,
    git_repo_url: Optional[str] = None,
) -> bool:
    """Generate web data and deploy to Vercel via git."""
    try:
        # Get repository URL with fallback chain
        repository_url = get_git_repository_url(git_repo_url)

        # Generate web data
        error_messages = [error.to_user_message() for error in errors or []]
        error_messages = list(dict.fromkeys(error_messages))
        web_data = generate_web_data(events, error_messages)

        print(f"✅ Generated web data: {len(events)} events")
        print(f"📍 Target repository: {repository_url}")

        # Use GitHub App authentication for deployment (like Temporal workflow)
        return _deploy_with_github_auth(web_data, repository_url)

    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False


def _deploy_with_github_auth(web_data: dict, repository_url: str) -> bool:
    """Deploy web data to git repository using GitHub App authentication."""
    import shutil
    import tempfile

    from .utils.github_auth import GitHubAppAuth

    try:
        print("🔐 Using GitHub App authentication for deployment...")

        # Create temporary directory for git operations
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "repo"

            # Clone the repository
            print(f"📥 Cloning repository {repository_url}...")
            subprocess.run(
                ["git", "clone", repository_url, str(repo_dir)],
                check=True,
                capture_output=True,
            )

            # Configure git user in the cloned repository
            subprocess.run(
                ["git", "config", "user.email", "steve.androulakis@gmail.com"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Around the Grounds Bot"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )

            # Copy template files from public_template to cloned repo
            public_template_dir = Path.cwd() / "public_template"
            target_public_dir = repo_dir / "public"

            print(f"📋 Copying template files from {public_template_dir}...")

            # For events, use events-index.html as index.html
            shutil.copytree(public_template_dir, target_public_dir, dirs_exist_ok=True)

            # Replace index.html with events-index.html if it exists
            events_index = target_public_dir / "events-index.html"
            main_index = target_public_dir / "index.html"
            if events_index.exists():
                shutil.copy2(events_index, main_index)
                events_index.unlink()  # Remove the duplicate

            # Write generated web data to cloned repository
            json_path = target_public_dir / "data.json"
            with open(json_path, "w") as f:
                json.dump(web_data, f, indent=2)

            print(f"📝 Updated data.json with {web_data.get('total_events', 0)} events")

            # Add all files in public directory
            subprocess.run(
                ["git", "add", "public/"], cwd=repo_dir, check=True, capture_output=True
            )

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--staged", "--quiet"],
                cwd=repo_dir,
                capture_output=True,
            )
            if result.returncode == 0:
                print("ℹ️  No changes to deploy")
                return True

            # Commit changes
            commit_msg = f"🎵 Update event data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )

            # Set up GitHub App authentication and configure remote
            auth = GitHubAppAuth(repository_url)
            access_token = auth.get_access_token()

            authenticated_url = f"https://x-access-token:{access_token}@github.com/{auth.repo_owner}/{auth.repo_name}.git"
            subprocess.run(
                ["git", "remote", "set-url", "origin", authenticated_url],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )

            # Push to origin
            print(f"🚀 Pushing to {repository_url}...")
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )
            print("✅ Deployed successfully! Changes will be live shortly.")

            return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
        print(f"❌ Git operation failed: {error_msg}")
        return False
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False


def preview_locally(
    events: List[MusicEvent], errors: Optional[List[ScrapingError]] = None
) -> bool:
    """Generate web files locally in public/ directory for preview."""
    import shutil

    try:
        # Generate web data
        error_messages = [error.to_user_message() for error in errors or []]
        error_messages = list(dict.fromkeys(error_messages))
        web_data = generate_web_data(events, error_messages)

        # Set up paths
        public_template_dir = Path.cwd() / "public_template"
        local_public_dir = Path.cwd() / "public"

        # Ensure public_template exists
        if not public_template_dir.exists():
            print(f"❌ Template directory not found: {public_template_dir}")
            return False

        # Create or clear public directory
        if local_public_dir.exists():
            shutil.rmtree(local_public_dir)

        # Copy template files to public/
        print(f"📋 Copying template files from {public_template_dir}...")
        shutil.copytree(public_template_dir, local_public_dir)

        # Replace index.html with events-index.html if it exists
        events_index = local_public_dir / "events-index.html"
        main_index = local_public_dir / "index.html"
        if events_index.exists():
            shutil.copy2(events_index, main_index)
            events_index.unlink()  # Remove the duplicate

        # Write generated web data to local public directory
        json_path = local_public_dir / "data.json"
        with open(json_path, "w") as f:
            json.dump(web_data, f, indent=2)

        print(f"✅ Generated local preview: {len(events)} events")
        print(f"📁 Preview files in: {local_public_dir}")
        print("🌐 To serve locally: cd public && python -m http.server 8000")
        print("🔗 Then visit: http://localhost:8000")

        return True

    except Exception as e:
        print(f"❌ Error during local preview generation: {e}")
        return False


async def scrape_events(config_path: Optional[str] = None) -> tuple:
    """Scrape music event schedules from all configured venues."""
    venues = load_venue_config(config_path)

    if not venues:
        print("No venues configured.")
        return [], []

    # The ScraperCoordinator expects objects with a .key attribute and parser registry
    # We need to adapt it to work with venues instead of breweries
    coordinator = ScraperCoordinator()

    # Convert venues to brewery-like objects for compatibility
    adapted_venues = []
    for venue in venues:
        # Create a mock brewery object that the coordinator can work with
        class MockBrewery:
            def __init__(self, venue):
                self.key = venue.key
                self.name = venue.name
                self.url = venue.url
                self.parser_config = venue.parser_config

        adapted_venues.append(MockBrewery(venue))

    events = await coordinator.scrape_all(adapted_venues)
    errors = coordinator.get_errors()

    return events, errors


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the events CLI."""
    parser = argparse.ArgumentParser(
        description="Track music venue event schedules"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument(
        "--config", "-c", help="Path to venue configuration JSON file"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--deploy",
        "-d",
        action="store_true",
        help="Deploy results to web (generate JSON and push to git)",
    )
    parser.add_argument(
        "--git-repo",
        help="Git repository URL for deployment (default: littlefield-events)",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Generate web files locally in public/ directory for preview",
    )

    args = parser.parse_args(argv)

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("🎵 Littlefield NYC Events - Music Event Tracker")
    print("=" * 55)

    try:
        events, errors = asyncio.run(scrape_events(args.config))
        output = format_events_output(events, errors)
        print(output)

        # Deploy to web if requested
        if args.deploy and events:
            deploy_to_web(events, errors, args.git_repo)

        # Generate local preview if requested
        if args.preview and events:
            preview_locally(events, errors)

        # Return appropriate exit code
        if errors and not events:
            return 1  # Complete failure
        elif errors:
            return 2  # Partial success
        else:
            return 0  # Complete success
    except Exception as e:
        print(f"Critical Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())