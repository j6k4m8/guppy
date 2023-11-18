from pocketbase import PocketBase
from pocketbase.client import FileUpload
import subprocess
import tempfile

# import boto3
from guidance import models, gen, user, assistant, system
import re
from config import OpenAIConfig, GuppyConfig


# from pocketbase.client import FileUpload

client = PocketBase("http://127.0.0.1:8090")


# Authenticate as an admin
admin_data = client.admins.auth_with_password(
    GuppyConfig().admin_email, GuppyConfig().admin_password
)


def text_to_audio(transcript: str, audio_out: str) -> tuple[str, str]:
    """Convert transcript to audio with TTS.

    Return filename."""
    # Generalize so we can later use Polly or something

    # Write transcript to temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(transcript)
        transcript_file = f.name

    # Convert to audio
    subprocess.run(["say", "-f", transcript_file, "-o", audio_out])
    return transcript_file, audio_out


def podcast_summary_to_transcript(show_title: str, podcast_summary: str) -> str:
    """Use Guidance to generate a transcript from a podcast summary."""
    llm = models.OpenAI(
        "gpt-3.5-turbo",
        api_key=OpenAIConfig().token,
        organization=OpenAIConfig().organization,
    )

    with system():
        transcript = (
            llm
            + """You are a helpful and intelligent lecturer who hosts a podcast series. Your job is to combine the request with your own domain knowledge in order to create a {length} word lecture that is informative and entertaining. You must cover all of the material that the student has in their notes, but you may also add additional information if you believe it will be helpful. You may go longer than {length} words if you need to finish a thought.

        At the end of each paragraph, you must put in brackets the total number of words you have generated so far like this. [[132]]

        Make sure that the podcast is casual but precise, conversational, and not too dense to follow. When you introduce a new topic, spend some time explaining it. Feel free to use analogies and metaphors, and build a narrative through transition language like "we now know X, let's see how that helps us understand Y".

        Do not include speaker names or timestamps, as this transcript will be read exactly as it is written.

        Include a very brief introduction and conclusion. The introduction should explain what the lecture is about and why it is important. The conclusion should summarize the main points of the lecture. The name of the Podcast producer company is Guppy Courses.
        """
        )

        with user():
            transcript += f"""

SHOW TITLE:

---
{show_title}
---

EPISODE TITLE:

---
Introduction
---

PODCAST DESCRIPTION:

---
{podcast_summary}
---

EPISODE TRANSCRIPT:
---
"""

        with assistant():
            transcript += gen("transcript", stream_tokens=False)

    # Strip out the bracketed word counts
    stripped_lec = re.sub(r"\[\[\d+\]\]", "", transcript["transcript"])

    return stripped_lec


def create_next_show():
    show_requests = client.collection("show_requests").get_list(1, 1)
    req = show_requests.items[0]
    print(f"Creating show '{req.title}' for user <{req.creator}>")
    # tx = podcast_summary_to_transcript(req.title, req.prompt)
    tx = "example transcript"
    print(f"Transcript: {tx}")
    print("Creating audio file...")
    transcript_file, audio_file = text_to_audio(tx, "audio.mp3")

    # create the show and delete the request:
    show_creation_result = client.collection("shows").create(
        {
            "title": req.title,
            "prompt": req.prompt,
            "creator": req.creator,
        }
    )
    print(show_creation_result.id)
    # Create the new episode:
    episode_creation_result = client.collection("episodes").create(
        {
            "title": req.title,
            "show": show_creation_result.id,
            "creator": req.creator,
            "script": FileUpload(
                (
                    transcript_file,
                    open(transcript_file, "rb"),
                )
            ),
            "show_index": 0,
            "audio_file": FileUpload(
                (
                    audio_file,
                    open(audio_file, "rb"),
                )
            ),
        }
    )
    print(episode_creation_result)
    # Delete the request:
    client.collection("show_requests").delete(req.id)


if __name__ == "__main__":
    create_next_show()
