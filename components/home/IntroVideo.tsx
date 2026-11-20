"use client";
import { useState } from "react";
import { CaretRightFilled } from "@ant-design/icons";
import { site } from "@/lib/content";
import { track } from "@/lib/analytics";
import { withBase } from "@/lib/path";

const isEmbed = (u: string) => /youtube\.com\/embed|youtube-nocookie\.com\/embed|player\.vimeo\.com/.test(u);

/** URL is configured via NEXT_PUBLIC_INTRO_VIDEO_URL — no layout change needed when the founder's video arrives. */
export default function IntroVideo() {
  const { url, captionsUrl, headline, description, poster } = site.video;
  const [playing, setPlaying] = useState(false);
  const play = () => { setPlaying(true); track("intro_video_played"); };
  return (
    <section className="section section--blue">
      <div className="container video-layout">
        <div className="video-frame">
          {playing && url ? (
            isEmbed(url) ? (
              <iframe src={`${url}${url.includes("?") ? "&" : "?"}autoplay=1`} title="Forge introduction video" allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen />
            ) : (
              <video src={url} controls autoPlay playsInline poster={poster ? withBase(poster) : undefined}>
                {captionsUrl && <track kind="captions" src={captionsUrl} srcLang="en" label="English" default />}
              </video>
            )
          ) : (
            <div className={`video-placeholder${poster ? " has-poster" : ""}`} style={poster ? { background: `#0B2744 url(${withBase(poster)}) center / cover no-repeat` } : undefined}>
              <button className="play-btn" onClick={play} aria-label={url ? "Play introduction video" : "Play introduction video (coming soon)"}><CaretRightFilled />{poster && <span className="play-label">Watch the introduction</span>}</button>
              {playing && !url && <span className="video-note">The introduction video is coming soon.</span>}
            </div>
          )}
        </div>
        <div>
          <div className="eyebrow">Introduction</div>
          <h2 style={{ fontSize: "clamp(26px,3.6vw,36px)", lineHeight: 1.15 }}>{headline}</h2>
          <p className="lead" style={{ marginTop: 14 }}>{description}</p>
        </div>
      </div>
    </section>
  );
}
