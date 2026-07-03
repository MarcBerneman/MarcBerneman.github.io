from __future__ import annotations

import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
INPUT_FILE = ROOT / "video.txt"
OUTPUT_FILE = ROOT / "videos_processed.json"


def read_video_ids(path: pathlib.Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path.name}")

    video_ids: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        video_ids.append(line)

    return video_ids


def fetch_metadata(video_id: str) -> dict[str, str]:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    endpoint = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
        {"url": video_url, "format": "json"}
    )

    request = urllib.request.Request(
        endpoint,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        payload = {}

    title = payload.get("title") or video_id
    thumbnail_url = payload.get("thumbnail_url") or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    return {
        "id": video_id,
        "title": title,
        "thumbnail_url": thumbnail_url,
        "watch_url": video_url,
    }


def main() -> int:
    try:
        video_ids = read_video_ids(INPUT_FILE)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    processed = [fetch_metadata(video_id) for video_id in video_ids]
    OUTPUT_FILE.write_text(json.dumps(processed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {len(processed)} video entries to {OUTPUT_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())