"use client";
import { useState } from "react";
import { CaretRightFilled } from "@ant-design/icons";
import { site } from "@/lib/content";
import { track } from "@/lib/analytics";

const isEmbed = (u: string) => /youtube\.com\/embed|youtube-nocookie\.com\/embed|player\.vimeo\.com/.test(u);

/** URL is configured via NEXT_PUBLIC_INTRO_VIDEO_URL — no layout change needed when the founder's video arrives. */
export default function IntroVideo() {
  const { url, captionsUrl, headline, description } = site.video;
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
              <video src={url} controls autoPlay playsInline>
                {captionsUrl && <track kind="captions" src={captionsUrl} srcLang="en" label="English" default />}
              </video>
            )
          ) : (
            <div className="video-placeholder">
              <button className="play-btn" onClick={play} aria-label={url ? "Play introduction video" : "Play introduction video (placeholder)"}><CaretRightFilled /></button>
              <strong style={{ fontSize: 18 }}>{url ? "Watch the introduction" : "Introductory video coming soon"}</strong>
              {playing && !url && <span style={{ fontSize: 14, maxWidth: 360 }}>Video placeholder — the founder's video will be added by setting <code>NEXT_PUBLIC_INTRO_VIDEO_URL</code>.</span>}
              {!playing && <span style={{ fontSize: 14, opacity: .85 }}>The grant-management problem and the Forge approach</span>}
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
