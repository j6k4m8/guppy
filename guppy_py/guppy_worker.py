import pathlib
from pocketbase import PocketBase
from pocketbase.client import FileUpload
from generate_show import OpenAIGuidanceShowGenerator, AWSPollyAudioMaker
from config import OpenAIConfig, GuppyConfig


# from pocketbase.client import FileUpload

client = PocketBase("http://127.0.0.1:8090")


# Authenticate as an admin
admin_data = client.admins.auth_with_password(
    GuppyConfig().admin_email, GuppyConfig().admin_password
)


def create_next_show():
    show_requests = client.collection("show_requests").get_list(
        1, 1, {"status": "queued"}
    )
    req = show_requests.items[0]
    # Update the request to the "creating" state:
    client.collection("show_requests").update(req.id, {"status": "creating"})
    try:
        print(f"Creating show '{req.title}' for user <{req.creator}>")
        # Create the show:
        show_generator = OpenAIGuidanceShowGenerator(
            title=req.title,
            show_description=req.prompt,
            episode_count=5,
            episode_length_minutes=1.5,
            openai_key=OpenAIConfig().token,
            openai_organization=OpenAIConfig().organization,
        )
        curriculum = show_generator.create_curriculum()
        eps = show_generator.create_all_episodes(curriculum)
        print(f"Created {len(eps)} episodes")
        # Write the transcripts to disk in CWD/{req.id}/transcripts:
        # Make the directory:
        pathlib.Path(f"{req.id}/transcripts").mkdir(parents=True, exist_ok=True)
        pathlib.Path(f"{req.id}/audio").mkdir(parents=True, exist_ok=True)
        # Write the transcripts:
        for i, ep in enumerate(eps):
            with open(f"{req.id}/transcripts/{i}.txt", "w") as f:
                f.write(ep.transcript)
        # Create the audio files:
        audio_maker = AWSPollyAudioMaker(
            aws_profile=GuppyConfig().aws_profile,
        )
        for i, ep in enumerate(eps):
            audio_maker.create_audio_file(
                ep.transcript,
                f"{req.id}/audio/{i}.mp3",
            )

        # Create the show:
        show_creation_result = client.collection("shows").create(
            {
                "title": req.title,
                "prompt": req.prompt,
                "curriculum": "\n".join(
                    [
                        f" • {ep.episode_title}: {ep.episode_description}"
                        for ep in curriculum
                    ]
                ),
                "creator": req.creator,
            }
        )
        print(f"Created show {show_creation_result.id}")

        # Create the episodes:
        for i, ep in enumerate(eps):
            transcript_file = f"{req.id}/transcripts/{i}.txt"
            audio_file = f"{req.id}/audio/{i}.mp3"
            episode_creation_result = client.collection("episodes").create(
                {
                    "title": ep.episode_title,
                    "summary": ep.episode_description,
                    "show": show_creation_result.id,
                    "creator": req.creator,
                    "script": FileUpload(
                        (
                            transcript_file,
                            open(transcript_file, "rb"),
                        )
                    ),
                    "show_index": i,
                    "audio_file": FileUpload(
                        (
                            audio_file,
                            open(audio_file, "rb"),
                        )
                    ),
                }
            )
            print(f"* Created episode {i}: {episode_creation_result.id}")

        # Delete the request:
        client.collection("show_requests").delete(req.id)

    except Exception as e:
        print("Error creating show:")
        print(e)
        client.collection("show_requests").update(req.id, {"status": "error"})
        return


if __name__ == "__main__":
    create_next_show()
