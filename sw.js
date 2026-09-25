/* Offline cache for Weaver Workout (Ron + Cindy).
   Network-first for same-origin GETs so new deploys show up on the next load;
   falls back to cache when offline. Bump CACHE on every release. */
const CACHE = "weaver-workout-v4-plain-names";
const ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./program-ron.json",
  "./program-cindy.json",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match("./index.html")))
  );
});
