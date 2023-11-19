import abc
import json
import re
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from typing import Optional

import boto3
from guidance import assistant, gen, models, system, user

ShowDescription = str
ShowTitle = str
EpisodeTitle = str
EpisodeDescription = str
Transcript = str
Filename = str


@dataclass
class EpisodeWithDescription:
    # ShowTitle, ShowDescription, EpisodeTitle, EpisodeDescription
    show_title: ShowTitle
    show_description: ShowDescription
    episode_title: EpisodeTitle
    episode_description: EpisodeDescription


@dataclass
class EpisodeWithTranscript(EpisodeWithDescription):
    transcript: Transcript


@dataclass
class EpisodeWithTranscriptAndAudio(EpisodeWithTranscript):
    audio_file: Filename


_WPM = 110


class AudioMaker(abc.ABC):
    """A class that creates an audio file from a given transcript."""

    def create_audio_file(
        self, transcript: Transcript, requested_filename: Filename
    ) -> Filename:
        """Create an audio file from a given transcript."""
        ...


class MacSayFfmpegAudioMaker(AudioMaker):
    """A TTS generator that uses the (low quality) built in macOS voices.

    Transformation from aiff to mp3 is done using ffmpeg.
    """

    @staticmethod
    def get_available_voices(locale: str = "en_US") -> list[str]:
        # say -v '?' | grep en_US | cut -d' ' -f1
        # Implemented with subprocess (with pipes). To pipe from one subprocess
        # to another, use the stdout of the first as the stdin of the second.
        voices_raw = subprocess.Popen(
            ["say", "-v", "?"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        grep = subprocess.Popen(
            ["grep", locale], stdin=voices_raw.stdout, stdout=subprocess.PIPE
        )
        cut = subprocess.Popen(
            ["cut", "-d", " ", "-f1"], stdin=grep.stdout, stdout=subprocess.PIPE
        )
        voices_raw.stdout.close()
        grep.stdout.close()
        voices_raw.wait()
        grep.wait()
        output = cut.communicate()[0].strip()
        cut.stdout.close()
        cut.wait()
        return output.decode("utf-8").split("\n")

    def __init__(
        self,
        voice: Optional[str] = None,
        check_available: bool = True,
        wpm: Optional[int] = None,
    ):
        self.voice = voice
        self.wpm = wpm
        if check_available:
            assert voice in self.get_available_voices(), f"{voice} is not available"

    def create_audio_file(
        self, transcript: Transcript, requested_filename: Filename
    ) -> Filename:
        """Create an audio file from a given transcript."""
        # Create a temporary file for the aiff
        temp_filename = f"{requested_filename}.aiff"
        # Save transcript to a deleted temporary file:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(transcript.encode("utf-8"))
            f.flush()
            # Convert the transcript to an aiff file
            subprocess.run(
                [
                    "say",
                    "-f",
                    f.name,
                    "-o",
                    temp_filename,
                ]
                + (["-r", str(self.wpm)] if self.wpm else [])
                + (["-v", self.voice] if self.voice else []),
                check=True,
            )
        # Convert the aiff file to an mp3 file
        subprocess.run(["ffmpeg", "-i", temp_filename, requested_filename], check=True)
        # Delete the temporary aiff file
        subprocess.run(["rm", temp_filename], check=True)
        return requested_filename


class PiperAudioMaker(AudioMaker):
    """A TTS generator that uses the Piper.cpp library.

    https://github.com/rhasspy/piper
    """

    def __init__(self, path_to_piper: str, model: str = "en-US-lessac-medium.onnx"):
        self.path_to_piper = path_to_piper
        self.model = model

    def create_audio_file(
        self, transcript: Transcript, requested_filename: Filename
    ) -> Filename:
        """Create an audio file from a given transcript."""
        # Create a temporary file for the aiff
        temp_filename = f"{requested_filename}.wav"
        # Save transcript to a deleted temporary file:
        # Convert the transcript to a wav file
        subprocess.run(
            [
                self.path_to_piper,
                "--model",
                self.model,
                "--output_file",
                temp_filename,
            ],
            check=True,
            input=transcript.encode("utf-8"),
        )
        # Convert the aiff file to an mp3 file
        subprocess.run(["ffmpeg", "-i", temp_filename, requested_filename], check=True)
        # Delete the temporary aiff file
        subprocess.run(["rm", temp_filename], check=True)
        return requested_filename


class AWSPollyAudioMaker(AudioMaker):
    """A TTS tool that uses AWS Polly to create audio files."""

    def __init__(self, aws_profile: Optional[str] = None, voice: str = "Joanna"):
        self.aws_profile = aws_profile
        self._aws_region = "us-east-1"
        self.voice = voice

    def create_audio_file(
        self, transcript: Transcript, requested_filename: Filename
    ) -> Filename:
        """Create an audio file from a given transcript."""
        # Set up the Polly client
        session = boto3.Session(
            profile_name=self.aws_profile, region_name=self._aws_region
        )
        client = session.client("polly")

        # Convert the lecture notes to audio
        response = client.synthesize_speech(
            Text=transcript,
            OutputFormat="mp3",
            VoiceId=self.voice,
            Engine="neural",
        )

        # Save the audio to a file
        with open(requested_filename, "wb") as f:
            f.write(response["AudioStream"].read())

        return requested_filename


class ShowGenerator(abc.ABC):
    """A class that creates a show from a given text prompt."""

    title: ShowTitle
    show_description: ShowDescription
    episode_length_minutes: float
    episode_count: int

    def create_curriculum(self) -> list[EpisodeWithDescription]:
        """Create a curriculum for the show."""
        ...

    def create_episode_transcript(
        self, curriculum: list[EpisodeWithDescription], index: int
    ) -> EpisodeWithTranscript:
        """Create a new episode from a given description."""
        ...

    def create_all_episodes(self) -> list[EpisodeWithTranscript]:
        """Create all episodes for the show.

        Incrementally creates shows, since each show will have awareness of the
        contents of the previous episode.

        """
        ...


class OpenAIGuidanceShowGenerator(ShowGenerator):
    """Generate a show using the OpenAI API."""

    def __init__(
        self,
        title: ShowTitle,
        show_description: ShowDescription,
        openai_key: str,
        openai_organization: Optional[str] = None,
        episode_count: int = 10,
        episode_length_minutes: float = 5,
    ):
        self.title = title
        self.show_description = show_description
        self._openai_key = openai_key
        self._openai_organization = openai_organization
        self.episode_count = episode_count
        self.episode_length_minutes = episode_length_minutes
        self.llm = models.OpenAI(
            "gpt-3.5-turbo", api_key=openai_key, organization=openai_organization
        )

    def create_curriculum(self) -> list[EpisodeWithDescription]:
        """Create a curriculum for the show."""
        with system():
            response = self.llm + (
                "You are a helpful and intelligent lecturer who hosts a "
                "podcast series. Your job is to combine the request with your "
                "own domain knowledge in order to plan a lecture series that "
                "is informative and entertaining."
            )

        with user():
            response += (
                "Produce a curriculum overview with titles and short episode "
                f"summaries for {self.episode_count} episodes, each roughly "
                f"{self.episode_length_minutes} minutes long. The material "
                "should be scoped appropriately for the length of each "
                "episode. Short descriptions should be one or two sentences. "
                "\n"
                "The name of the Podcast producer company is Guppy Courses."
                "An example of an episode description is as follows:"
                "\n---\n"
                '{"episode_title": "Episode 2: Vienna", '
                '"episode_description": "We discuss Beethoven\'s move to Vienna '
                "and his early professional life there. We also discuss his "
                "relationship with Haydn and Mozart, and the influence they "
                'had on his early compositions."}'
                "\n---\n"
                "The curriculum should be written in JSON format. Here is the "
                "show information that has been requested: \n"
            )
            response += f"""\
            {{
                "show_title": "{self.title}",
                "show_description": "{self.show_description}",
                "episode_count": {self.episode_count}
            }}

            Please provide the `episodes` array of `episode_title` and
            `episode_description`, with {self.episode_count} entries, one on
            each line. It should look like this:

            ```
            {{"episode_title": "Episode 1: Introduction", "episode_description": "We discuss the life and work of Ludwig van Beethoven, the famous composer."}}
            {{"episode_title": "Episode 2: Vienna", "episode_description": "We discuss Beethoven's move to Vienna and his early professional life there. We also discuss his relationship with Haydn and Mozart, and the influence they had on his early compositions."}}
            ```

            etc.
            Nest your response in triple-backticks, like this: ```
            """

        with assistant():
            response += "```" + gen("curriculum", stop="```") + "```"

        try:
            loaded = json.loads(response["curriculum"])
        except json.decoder.JSONDecodeError:
            print("Error decoding JSON response from OpenAI.")
            print(response["curriculum"])
            raise

        return [
            EpisodeWithDescription(
                ShowTitle(self.title),
                ShowDescription(self.show_description),
                EpisodeTitle(ep["episode_title"]),
                EpisodeDescription(ep["episode_description"]),
            )
            for ep in loaded["episodes"]
        ]

    def create_episode_transcript(
        self,
        curriculum: list[EpisodeWithDescription],
        index: int,
        word_length: Optional[int] = None,
    ) -> EpisodeWithTranscript:
        """
        Create a transcript for an individual episode.

        Arguments:
            curriculum: The curriculum for the show.
            index: The index of the episode to create.

        """
        word_length = word_length or int(self.episode_length_minutes * _WPM)
        with system():
            transcript = (
                self.llm
                + f"""\
You are a helpful and intelligent lecturer who hosts a podcast series. Your job is to combine the request with your own domain knowledge in order to create a {word_length} word lecture that is informative and entertaining. You must cover all of the material that the student has in their notes, but you may also add additional information if you believe it will be helpful. You may go longer than {word_length} words if you need to finish a thought.

At the end of each paragraph, you must put in brackets the total number of words you have generated so far like this. [[132]]

Make sure that the podcast is casual but precise, conversational, and not too dense to follow. When you introduce a new topic, spend some time explaining it. Feel free to use analogies and metaphors, and build a narrative through transition language like "we now know X, let's see how that helps us understand Y".

IMPORTANT: DO NOT include speaker markings like "HOST: ", and DO NOT include timestamps or section/chapter headers like [INTRODUCTION], as this transcript will be read exactly as it is written. If you include these items, you will be punished, as this is NOT correct.

Include a VERY brief introduction and conclusion. The introduction should explain what the lecture is about and why it is important. You may reference other episodes ("recall from Episode 3" etc) if you need to. The conclusion should summarize the main points of the lecture. The name of the Podcast producer company is Guppy Courses."""
            )

        with user():
            transcript += f"""\
---
SHOW TITLE: {self.title}
ALL PREVIOUS EPISODES:
"""
            for i, ep in enumerate(curriculum[:index]):
                transcript += f"""\
{i + 1}. {ep.episode_title}: {ep.episode_description}
"""
            transcript += f"""\
---
THIS EPISODE TITLE: {curriculum[index].episode_title}
---
THIS EPISODE DESCRIPTION: {curriculum[index].episode_description}
---
THIS EPISODE TRANSCRIPT:
"""
        with assistant():
            transcript += gen("transcript")

        # Strip out the bracketed word counts
        stripped_lec = re.sub(r"\[\[\d+\]\]", "", transcript["transcript"])

        return EpisodeWithTranscript(
            ShowTitle(self.title),
            ShowDescription(self.show_description),
            EpisodeTitle(curriculum[index].episode_title),
            EpisodeDescription(curriculum[index].episode_description),
            Transcript(stripped_lec),
        )

    def create_all_episodes(self) -> list[EpisodeWithTranscript]:
        """Create all episodes serially."""
        curriculum = self.create_curriculum()
        episodes = []
        for i in range(self.episode_count):
            episodes.append(self.create_episode_transcript(curriculum, i))
        return episodes


class ShowMaker:
    """A class that creates a show from a given text prompt."""

    def __init__(self, show_generator: ShowGenerator, audio_maker: AudioMaker):
        self.show_generator = show_generator
        self.audio_maker = audio_maker

    def create_show(self) -> list[EpisodeWithTranscriptAndAudio]:
        """Create a show from a given text prompt."""
        episodes = self.show_generator.create_all_episodes()
        audioed_episodes = []
        for i, ep in enumerate(episodes):
            rand = uuid.uuid4()
            filename = self.audio_maker.create_audio_file(
                ep.transcript, f"{i}-{rand}.mp3"
            )
            audioed_episodes.append(
                EpisodeWithTranscriptAndAudio(
                    ep.show_title,
                    ep.show_description,
                    ep.episode_title,
                    ep.episode_description,
                    ep.transcript,
                    filename,
                )
            )
        return audioed_episodes
