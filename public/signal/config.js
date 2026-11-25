/* Tells the pages where the engine is.
   live:false  sample data only (this is what the public GitHub Pages preview uses).
   live:true   the pages call the API. When the backend serves these pages itself it answers /config.js with
               {live: true, api: ""} (same address). If the pages are hosted elsewhere, set api to the backend's
               address, e.g. {live: true, api: "https://your-backend.example.com"}, and list the pages' address
               in the backend's FORGE_CORS_ORIGINS setting. */
window.SIGNAL = { live: false, api: "" };
