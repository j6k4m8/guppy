


routerAdd(
    "GET", "/pod/:id", (c) => {
        const show = $app.dao().findRecordById("shows", c.pathParam('id'));
        const episodes = $app.dao().findRecordsByFilter(
            "episodes",
            "show = {:showId}",
            "show_index",
            0,
            0,
            { showId: show.id }
        );


        const PODCAST_XML = `
<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"  xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel>
        <title>{{SHOW_TITLE}}</title>
        <link>{{URL}}</link>
        <language>en-us</language>
        <itunes:author>Guppy Courses</itunes:author>
        <itunes:summary>{{SHOW_DESCRIPTION}}</itunes:summary>
        <itunes:owner>
            <itunes:name>Guppy Courses</itunes:name>
            <itunes:email>
                guppy@matelsky.com
            </itunes:email>
        </itunes:owner>
        <itunes:image href="https://example.com/podcast.jpg"/>
        <itunes:category text="Technology"/>
        <itunes:explicit>no</itunes:explicit>

        {{EPISODES}}
    </channel>
</rss></xml>

`;

        const EPISODE_XML = `
<item>
    <title>{{EPISODE_TITLE}}</title>
    <itunes:author>Guppy Courses</itunes:author>
    <itunes:summary>{{SHOW_DESCRIPTION}}</itunes:summary>
    <itunes:duration>00:02:00</itunes:duration>
    <enclosure
        url="{{EPISODE_AUDIO_URL}}"
        type="audio/mpeg"
        length="1234567"
    />
    <guid>{{EPISODE_AUDIO_URL}}</guid>

    <pubDate>{{CREATED_DATE}}</pubDate>
</item>
`;


        let episodeXML = "";
        for (let episode of episodes) {
            episodeXML += EPISODE_XML
                .replace("{{EPISODE_TITLE}}", episode.get("title"))
                .replace("{{SHOW_DESCRIPTION}}", episode.get("summary"))
                .replaceAll("{{EPISODE_AUDIO_URL}}", `http://127.0.0.1:8090/api/files/episodes/${episode.get("id")}/${episode.get("audio_file")}`)
                .replace("{{CREATED_DATE}}", episode.get("createdDate"));
        }

        const out = PODCAST_XML
            .replace("{{SHOW_TITLE}}", show.get("title"))
            .replace("{{SHOW_DESCRIPTION}}", show.get("prompt"))
            .replace("{{URL}}", "https://guppy.jordan.matelsky.com")
            .replace("{{EPISODES}}", episodeXML);


        console.log(JSON.stringify(episodes, null, 2))
        // return c.json(200, { show, episodes })
        return c.html(200, out, "application/xml");
    }
)
