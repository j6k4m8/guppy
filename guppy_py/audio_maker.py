def lecture_notes_to_lecture_file(lecture_notes: str, word_length: int = 200) -> str:
    """
    Returns a file path of a folder containing the transcript and audio mp3.
    """

    # create a uuid for the lecture
    uuid = str(uuid4())
    # Create a folder for the lecture
    ep_path = pathlib.Path(f"lectures/{uuid}")
    ep_path.mkdir(parents=True, exist_ok=True)

    guidance.llm = guidance.llms.OpenAI(
        "gpt-3.5-turbo",
        api_key=OpenAIConfig().token,
        organization=OpenAIConfig().organization,
    )

    lecture_generator = guidance.Program(
        """
{{#system~}}
You are a helpful and intelligent study assistant. You are tasked with helping a student prepare for an important exam. Your job is to combine the student's notes with your own domain knowledge in order to create a {{length}} word lecture that is informative and entertaining. You must cover all of the material that the student has in their notes, but you may also add additional information if you believe it will be helpful. You may go longer than 500 words if you need to finish a thought.

At the end of each paragraph, you must put in brackets the total number of words you have generated so far like this. [[132]]

Make sure that the podcast is casual but precise, conversational, and not too dense to follow. When you introduce a new topic, spend some time explaining it. Feel free to use analogies and metaphors, and build a narrative through transition language like "we now know X, let's see how that helps us understand Y".

Include a very brief introduction and conclusion. The introduction should explain what the lecture is about and why it is important. The conclusion should summarize the main points of the lecture.

The student's notes are as follows:
{{~/system}}

{{#user~}}
NOTES:

---
{{notes}}
---

LECTURE:
---
{{~/user}}

{{#assistant~}}
{{gen 'lecture'}}
{{~/assistant}}

"""
    )

    def lecture_to_audio(lecture_notes: str, output_file: str, aws_profile: str):
        # Set up the Polly client
        session = boto3.Session(profile_name=aws_profile)
        client = session.client("polly")

        # Convert the lecture notes to audio
        response = client.synthesize_speech(
            Text=lecture_notes,
            OutputFormat="mp3",
            VoiceId="Joanna",
            Engine="neural",
        )

        # Save the audio to a file
        with open(output_file, "wb") as f:
            f.write(response["AudioStream"].read())

    lec = lecture_generator(
        notes=lecture_notes,
        length=f"{word_length-100}-{word_length+100}",
    )

    # Strip out the bracketed word counts
    stripped_lec = re.sub(r"\[\[\d+\]\]", "", lec["lecture"])

    # Create a folder for the lecture
    ep_path = pathlib.Path(f"lectures/{uuid}")
    ep_path.mkdir(parents=True, exist_ok=True)

    # Save the transcript to a file:
    with open(f"lectures/{uuid}/transcript.txt", "w") as f:
        f.write(stripped_lec)
    # Save the lecture to a file:
    lecture_to_audio(stripped_lec, f"lectures/{uuid}/episode.mp3", "kordinglab")

    return uuid
