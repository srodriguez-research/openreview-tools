import csv
import os

import openreview
from openreview.api import OpenReviewClient
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# ── Configuration ──────────────────────────────────────────────────────────────
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
VENUE_ID = os.getenv("VENUEID")
OUTPUT_FILE = "submissions_export.csv"
# ─────────────────────────────────────────────────────────────────────────────


# Map raw OpenReview decision strings → normalised status labels.
# Adjust the keys if your venue uses different wording.
STATUS_MAP = {
    "Accept (Full)": "Accepted (Full)",
    "Accept (Short)": "Accepted (Short)",
    "Accept (Poster)": "Accepted (Poster)",
    "Reject": "Rejected",
}


def export_submissions(
    client: OpenReviewClient, venue_id
):  # Connect to OpenReview API v2
    client.impersonate(venue_id)

    venue_group = client.get_group(venue_id)
    submission_name = venue_group.content["submission_name"]["value"]

    # Accepted papers have their venueid set to the venue's ID
    submissions = client.get_all_notes(invitation=f"{venue_id}/-/Submission")
    print(f"Found {len(submissions)} submission(s).")

    # Fetch all decision notes; each one's `forum` points to its parent submission.
    decisions = client.get_all_notes(
        invitation=f"{venue_id}/-/{submission_name}", details="replies"
    )
    replies = [
        reply
        for submission in decisions
        for reply in submission.details["replies"]
        if any(invitation.endswith("Decision") for invitation in reply["invitations"])
    ]
    print(f"Found {len(replies)} decision note(s)")

    decision_map = {
        r["forum"]: r["content"].get("decision", {}).get("value", "N/A")
        for r in replies
    }

    preferred_emails_invitation_id = venue_id + "/-/Preferred_Emails"

    # ── Pass 1: collect every tilde ID across all submissions ────────────────────
    all_author_ids = set()
    for note in tqdm(submissions, desc="Collecting author IDs", unit=" paper"):
        for author_id in note.content.get("authorids", {}).get("value", []):
            if "@" not in author_id:  # tilde IDs need a profile lookup
                all_author_ids.add(author_id)

    # Fetch all profiles in one call, with unobfuscated preferred e-mails
    profiles = openreview.tools.get_profiles(
        client,
        list(all_author_ids),
        with_preferred_emails=preferred_emails_invitation_id,
    )
    print(
        f"Fetched {len(profiles)} profile(s) for {len(all_author_ids)} unique tilde ID(s)."
    )

    # Build tilde-ID → e-mail map
    profile_map = {}
    for profile in tqdm(profiles, desc="Building profile map", unit=" profile"):
        email = profile.get_preferred_email()
        print(f"{email=}")
        profile_map[profile.id] = email
        for name_entry in profile.content.get("names", []):
            username = name_entry.get("username")
            if username:
                profile_map[username] = email
        print(profile_map)

    # ── Pass 2: build rows ────────────────────────────────────────────────────────
    rows = []
    for note in tqdm(submissions, desc="Processing submissions", unit=" paper"):
        title = note.content.get("title", {}).get("value", "N/A")
        authors = note.content.get("authors", {}).get("value", [])
        author_ids = note.content.get("authorids", {}).get("value", [])

        emails = []
        for author_id in author_ids:
            if "@" in author_id:
                emails.append(author_id)  # already a plain e-mail
            else:
                emails.append(profile_map.get(author_id, "N/A"))

        rows.append(
            {
                "title": title,
                "authors": "; ".join(authors),
                "emails": "; ".join(emails),
                "status": decision_map.get(note.id, "N/A"),
            }
        )

    # Write results to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "authors", "emails", "status"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} record(s) to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net",
        username=USERNAME,
        password=PASSWORD,
    )
    export_submissions(client, VENUE_ID)
