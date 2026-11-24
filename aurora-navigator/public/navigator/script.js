/* ============================================================
   Aurora Navigator — main script
   ============================================================ */

const MAPTILER_API_KEY = ""; 

const STYLES = {
  dark:  "https://tiles.openfreemap.org/styles/dark",
  light: "https://tiles.openfreemap.org/styles/liberty",
};

/* ---------- DOM ---------- */
const $ = (id) => document.getElementById(id);
const form        = $("routeForm");
const startLatEl  = $("startLat");
const startLngEl  = $("startLng");
const endLatEl    = $("endLat");
const endLngEl    = $("endLng");
const submitBtn   = $("submitBtn");
const swapBtn     = $("swapBtn");
const useMyLocBtn = $("useMyLocation");
const themeToggle = $("themeToggle");
const collapseBtn = $("collapseBtn");
const panel       = $("panel");
const errorBox    = $("errorBox");
const statsBox    = $("stats");
const statDist    = $("statDistance");
const statDur     = $("statDuration");
const toastEl     = $("toast");

/* ---------- Theme ---------- */
const savedTheme = localStorage.getItem("aurora-theme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

/* ---------- Map ---------- */
const map = new maplibregl.Map({
  container: "map",
  style: STYLES[savedTheme],
  center: [2.3522, 48.8566], 
  zoom: 11,
  attributionControl: { compact: true },
});
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");

let startMarker = null;
let endMarker   = null;
let routeAnimId = null;

/* ---------- Helpers ---------- */
function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toastEl.classList.remove("show"), 2200);
}

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = false;
}
function clearError() { errorBox.hidden = true; errorBox.textContent = ""; }

function validCoord(lat, lng) {
  return Number.isFinite(lat) && Number.isFinite(lng) &&
         lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}

function markInvalid(el, isInvalid) {
  el.classList.toggle("invalid", isInvalid);
}

function formatDistance(m) {
  if (m < 1000) return `${Math.round(m)} m`;
  return `${(m / 1000).toFixed(m < 10000 ? 2 : 1)} km`;
}

function formatDuration(s) {
  const h = Math.floor(s / 3600);
  const m = Math.round((s % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} min`;
}

function makeMarkerEl(kind, label) {
  const el = document.createElement("div");
  el.className = `marker-pin marker-${kind}`;
  el.title = label;
  return el;
}

/* ---------- Markers ---------- */
function setMarker(which, lng, lat) {
  const isStart = which === "start";
  if (isStart && startMarker) { startMarker.remove(); startMarker = null; }
  if (!isStart && endMarker)  { endMarker.remove();   endMarker   = null; }

  const el = makeMarkerEl(isStart ? "start" : "end", isStart ? "Start" : "Destination");
  const popup = new maplibregl.Popup({ offset: 24, closeButton: false })
    .setText(isStart ? "Start" : "Destination");

  const marker = new maplibregl.Marker({ element: el, anchor: "bottom" })
    .setLngLat([lng, lat])
    .setPopup(popup)
    .addTo(map);

  el.addEventListener("mouseenter", () => marker.togglePopup());
  el.addEventListener("mouseleave", () => marker.togglePopup());

  if (isStart) startMarker = marker; else endMarker = marker;
}

/* ---------- Route layer ---------- */
function ensureRouteSource() {
  if (!map.getSource("route")) {
    map.addSource("route", {
      type: "geojson",
      data: { type: "Feature", geometry: { type: "LineString", coordinates: [] } },
    });
    map.addLayer({
      id: "route-glow",
      type: "line",
      source: "route",
      layout: { "line-cap": "round", "line-join": "round" },
      paint: {
        "line-color": "#7c5cff",
        "line-width": 12,
        "line-opacity": 0.25,
        "line-blur": 6,
      },
    });
    map.addLayer({
      id: "route-line",
      type: "line",
      source: "route",
      layout: { "line-cap": "round", "line-join": "round" },
      paint: {
        "line-color": "#00d4ff",
        "line-width": 5,
      },
    });
  }
}

function animateRoute(coords) {
  ensureRouteSource();
  cancelAnimationFrame(routeAnimId);

  const total = coords.length;
  const duration = Math.min(1800, 400 + total * 4); 
  const start = performance.now();

  const step = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    const count = Math.max(2, Math.floor(eased * total));
    const slice = coords.slice(0, count);
    map.getSource("route").setData({
      type: "Feature",
      geometry: { type: "LineString", coordinates: slice },
    });
    if (t < 1) routeAnimId = requestAnimationFrame(step);
  };
  routeAnimId = requestAnimationFrame(step);
}

function fitToRoute(coords) {
  const bounds = coords.reduce(
    (b, c) => b.extend(c),
    new maplibregl.LngLatBounds(coords[0], coords[0])
  );
  map.fitBounds(bounds, { padding: { top: 80, bottom: 80, left: 420, right: 80 }, duration: 1200 });
}

/* ---------- Routing Logic (Corrected Speed Calculation) ---------- */
async function fetchRoute(profile, start, end) {
  // Average speeds in meters per second (m/s)
  const speeds = {
    driving: 13.89, // ~50 km/h
    cycling: 5.56,  // ~20 km/h
    walking: 1.39   // ~5 km/h
  };

  // Map our UI profiles to OSRM service profiles
  // 'driving' -> 'car', 'cycling' -> 'bicycle', 'walking' -> 'foot'
  const osrmProfile = profile === "cycling" ? "bicycle" : profile === "walking" ? "foot" : "car";
  
  // Note: Standard OSRM demo server uses 'bicycle' and 'foot' instead of 'bike'
  const url = `https://router.project-osrm.org/route/v1/${osrmProfile}/${start[0]},${start[1]};${end[0]},${end[1]}?overview=full&geometries=geojson`;
  
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Routing failed. The selected mode might not be available for this path.`);
  }
  
  const data = await res.json();
  if (!data.routes || !data.routes.length) {
    throw new Error("No route found between these points.");
  }

  const route = data.routes[0];
  
  // LOGIC CHANGE: 
  // OSRM returns duration in seconds based on traffic/road speeds.
  // We override it here using your specific speed constants.
  const distanceInMeters = route.distance;
  const speedInMps = speeds[profile] || speeds.driving;
  const calculatedDuration = distanceInMeters / speedInMps;

  return {
    geometry: route.geometry,
    distance: distanceInMeters,
    duration: calculatedDuration, 
  };
}

/* ---------- Submit ---------- */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();

  const sLat = parseFloat(startLatEl.value);
  const sLng = parseFloat(startLngEl.value);
  const eLat = parseFloat(endLatEl.value);
  const eLng = parseFloat(endLngEl.value);

  const sValid = validCoord(sLat, sLng);
  const eValid = validCoord(eLat, eLng);

  if (!sValid || !eValid) {
    showError("Please enter valid coordinates.");
    return;
  }
  
  const profile = (document.querySelector('input[name="profile"]:checked') || {}).value || "driving";

  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  try {
    setMarker("start", sLng, sLat);
    setMarker("end",   eLng, eLat);

    const route = await fetchRoute(profile, [sLng, sLat], [eLng, eLat]);
    const coords = route.geometry.coordinates;

    fitToRoute(coords);
    setTimeout(() => animateRoute(coords), 250);

    statDist.textContent = formatDistance(route.distance);
    statDur.textContent  = formatDuration(route.duration);
    statsBox.hidden = false;
  } catch (err) {
    showError(err.message || "Something went wrong.");
  } finally {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
});

/* ---------- Features ---------- */
swapBtn.addEventListener("click", () => {
  [startLatEl.value, endLatEl.value] = [endLatEl.value, startLatEl.value];
  [startLngEl.value, endLngEl.value] = [endLngEl.value, startLngEl.value];
  showToast("Locations swapped");
});

useMyLocBtn.addEventListener("click", () => {
  if (!navigator.geolocation) return showError("Geolocation not supported.");
  useMyLocBtn.disabled = true;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      startLatEl.value = pos.coords.latitude.toFixed(6);
      startLngEl.value = pos.coords.longitude.toFixed(6);
      useMyLocBtn.disabled = false;
      showToast("Location detected");
    },
    (err) => {
      useMyLocBtn.disabled = false;
      showError(err.message);
    }
  );
});

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("aurora-theme", theme);
  const currentRoute = map.getSource("route") && map.getSource("route")._data;
  map.setStyle(STYLES[theme]);
  map.once("styledata", () => {
    if (currentRoute) {
      ensureRouteSource();
      map.getSource("route").setData(currentRoute);
    }
  });
}

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  applyTheme(next);
});

/* Find your collapseBtn listener at the bottom and replace with this: */

collapseBtn.addEventListener("click", () => {
  const isCollapsed = panel.classList.toggle("collapsed");
  
  // Update Accessibility and Tooltip
  collapseBtn.setAttribute("aria-expanded", !isCollapsed);
  collapseBtn.title = isCollapsed ? "Expand panel" : "Collapse panel";
  
  // Optional: Add a toast for feedback
  showToast(isCollapsed ? "Panel hidden" : "Panel expanded");
});
/* ---------- Prefill Demo ---------- */
startLatEl.value = "48.8566";
startLngEl.value = "2.3522";
endLatEl.value   = "48.8584";
endLngEl.value   = "2.2945";