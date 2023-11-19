import abc
import re
from typing import Optional
import json
from dataclasses import dataclass
from guidance import models, gen, system, assistant, user

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

    def create_episode_audio(
        self, EpisodeWithTranscript
    ) -> EpisodeWithTranscriptAndAudio:
        """Create a new episode from a given description."""
        ...

    def create_all_episodes(self) -> list[EpisodeWithTranscriptAndAudio]:
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

Do not include speaker names or timestamps, as this transcript will be read exactly as it is written.

Include a very brief introduction and conclusion. The introduction should explain what the lecture is about and why it is important. The conclusion should summarize the main points of the lecture. The name of the Podcast producer company is Guppy Courses."""
            )

        with user():
            transcript += f"""\
---
SHOW TITLE: {self.title}
ALL PREVIOUS EPISODES:
"""
            for i, ep in enumerate(curriculum):
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
