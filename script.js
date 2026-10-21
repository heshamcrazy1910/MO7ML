const API = location.protocol.startsWith("http") ? "" : "http://localhost:8765";
const $ = id => document.getElementById(id);
let mode = "video", info = null;

const say = (t, err) => { $("msg").textContent = t; $("msg").className = "msg" + (err ? " err" : ""); };
const fmt = s => s ? `${Math.floor(s/60)}:${String(s%60).padStart(2,"0")}` : "";

$("paste").onclick = async () => {
  try { $("url").value = await navigator.clipboard.readText(); } catch { say("اسمح بالوصول للحافظة أو الصق الرابط يدويًا.", true); }
};

$("fetch").onclick = async () => {
  const url = $("url").value.trim();
  if (!url) return say("الصق رابط الأول.", true);
  $("fetch").disabled = true; $("result").hidden = true; say("جاري تحليل الرابط...");
  try {
    const r = await fetch(`${API}/api/info?url=${encodeURIComponent(url)}`);
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || "الرابط مش مدعوم.");
    info = d;
    $("thumb").src = d.thumbnail || "";
    $("title").textContent = d.title || "بدون عنوان";
    $("meta").textContent = d.playlist ? `قائمة تشغيل · ${d.count} عنصر` : [d.uploader, fmt(d.duration)].filter(Boolean).join(" · ");
    $("plBox").hidden = !d.playlist; $("count").textContent = d.count;
    $("result").hidden = false; say("");
  } catch (e) {
    say(e.message.includes("fetch") ? "السيرفر مش شغال. شغّل server.py الأول." : e.message, true);
  } finally { $("fetch").disabled = false; }
};

document.querySelectorAll(".seg button").forEach(b => b.onclick = () => {
  document.querySelectorAll(".seg button").forEach(x => x.classList.remove("on"));
  b.classList.add("on"); mode = b.dataset.mode;
  $("qualityBox").hidden = mode === "audio";
});

$("download").onclick = () => {
  const p = new URLSearchParams({
    url: $("url").value.trim(), mode, quality: $("quality").value,
    playlist: info && info.playlist && $("whole").checked ? "1" : "0"
  });
  say("السيرفر بيجهّز الملف، التحميل هيبدأ تلقائيًا. القوائم الكبيرة بتاخد وقت.");
  const a = document.createElement("a");
  a.href = `${API}/api/download?${p}`; document.body.appendChild(a); a.click(); a.remove();
};
