# تشغيل:  pip install flask flask-cors yt-dlp   ثم   python server.py
# لازم ffmpeg يكون منزّل (لدمج الصوت والصورة وتحويل MP3)
import os, re, shutil, tempfile, threading, webbrowser, zipfile, traceback
try:
    from flask import Flask, request, jsonify, send_file, after_this_request
    from flask_cors import CORS
    import yt_dlp
except Exception:
    traceback.print_exc()
    input("\nA library is missing. Run:  python -m pip install flask flask-cors yt-dlp   then press Enter")
    raise SystemExit

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, expose_headers=["Content-Disposition"])

@app.get("/")
def home():
    return app.send_static_file("index.html")

@app.get("/api/info")
def info():
    url = request.args.get("url", "").strip()
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": "in_playlist"}) as y:
            d = y.extract_info(url, download=False)
    except Exception as e:
        return jsonify(error=re.sub(r"\x1b\[[0-9;]*m", "", str(e))), 400
    pl = d.get("_type") == "playlist"
    n = len(list(d.get("entries") or [])) if pl else 0
    thumb = d.get("thumbnail") or ((d.get("thumbnails") or [{}])[-1].get("url"))
    return jsonify(title=d.get("title"), thumbnail=thumb, uploader=d.get("uploader"),
                   duration=d.get("duration"), playlist=pl, count=n)

@app.get("/api/download")
def download():
    url = request.args.get("url", "").strip()
    mode = request.args.get("mode", "video")
    q = re.sub(r"\D", "", request.args.get("quality", "1080")) or "1080"
    pl = request.args.get("playlist") == "1"
    tmp = tempfile.mkdtemp()

    @after_this_request
    def cleanup(resp):
        resp.call_on_close(lambda: shutil.rmtree(tmp, ignore_errors=True))
        return resp

    name = "%(playlist_index)02d - %(title).80s.%(ext)s" if pl else "%(title).80s.%(ext)s"
    opts = {"quiet": True, "noplaylist": not pl, "ignoreerrors": pl,
            "outtmpl": os.path.join(tmp, name), "restrictfilenames": False}
    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    else:
        opts["format"] = f"bv*[height<={q}]+ba/b[height<={q}]/b"
        opts["merge_output_format"] = "mp4"
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
    except Exception as e:
        return jsonify(error=str(e)), 400

    files = sorted(f for f in os.listdir(tmp) if not f.endswith((".part", ".ytdl")))
    if not files:
        return jsonify(error="التحميل فشل."), 400
    if len(files) == 1:
        return send_file(os.path.join(tmp, files[0]), as_attachment=True, download_name=files[0])
    z = os.path.join(tmp, "playlist.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        for f in files:
            zf.write(os.path.join(tmp, f), f)
    return send_file(z, as_attachment=True, download_name="playlist.zip")

if __name__ == "__main__":
    try:
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8765")).start()
        app.run(port=8765, threaded=True)
    except Exception:
        traceback.print_exc()
        input("\nServer failed to start. Copy the error above, then press Enter")
