import logging
import os
import csv
import sys

import coloredlogs
import openreview
from dotenv import load_dotenv

coloredlogs.install(level="DEBUG")

load_dotenv()  # take environment variables from .env.

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
VENUEID = os.getenv("VENUEID")

logger = logging.getLogger(__name__)


def author_emails():

    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net", username=USERNAME, password=PASSWORD
    )
    client.impersonate(VENUEID)
    preferred_emails_invitation_id = VENUEID + "/-/Preferred_Emails"

    all_accepted_authors = set()

    accepted_submissions = client.get_all_notes(content={"venueid": VENUEID})

    data = []
    for submission in accepted_submissions:
        for author in submission.content["authorids"]["value"]:
            all_accepted_authors.add(author)

    profiles = openreview.tools.get_profiles(
        client,
        list(all_accepted_authors),
        with_preferred_emails=True,
    )

    # print(profiles[1].get_preferred_email())

    for submission in accepted_submissions:
        for authorid in submission.content["authorids"]["value"]:
            prof = next((obj for obj in profiles if obj.id == authorid), None)
            if prof:
                author_name = prof.content["names"][0]["fullname"]
                author_email = prof.get_preferred_email()
            else:
                author_name = authorid
                author_email = "Missing from openreview profile"

            sub_row = [
                submission.id,
                submission.content["title"]["value"],
                author_name,
                author_email,
            ]
            data.append(sub_row)

    # Retrieve all decisions
    # decisions = client.get_all_notes(
    #     invitation=f"{VENUEID}/-/Submission.*/Decision", details="replies"
    # )
    #
    # # Extract decision content
    # for decision in decisions:
    #     print(f"Paper: {decision.forum}")
    #     print(f"Decision: {decision.content['decision']['value']}")

    # Create a writer that targets sys.stdout
    writer = csv.writer(sys.stdout)
    writer.writerows(data)


if __name__ == "__main__":
    author_emails()
