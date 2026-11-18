// The collections on the home page. One Google Sheet (same template) per collection.
// To add one: copy the template Sheet, publish it to the web, add an entry here, and push this file once.
//   slug   - used in the web address (player.html?c=slug); letters, numbers and dashes
//   title  - shown on the home page; native - the name in its own script (optional)
//   names  - the name in each language: te, dev, en. The page header follows the language dropdown.
//   part   - what one song is called in the list heading (e.g. "Ashtapadi")
//   pubId  - the long id from the Publish-to-web link (after /d/e/, before /pub). Leave "" to be asked on each device.
//   gids   - the tab ids of that Sheet's four tabs (from the tab addresses, #gid=...)
window.COLLECTIONS = [
  {
    slug: "jayadeva-ashtapadi",
    title: "Jayadeva Ashtapadi",
    native: "జయదేవ అష్టపది",
    names: { te: "జయదేవ అష్టపది", dev: "जयदेव अष्टपदी", en: "Jayadeva Ashtapadi" },
    part: "Ashtapadi",
    blurb: "The 24 Ashtapadis from Jayadeva's Gita Govindam",
    pubId: "2PACX-1vQlQR-cUihBNeOPL8TshhHIN3TyCqTjd43hEY8LmzDnIb7KG3GNHMNIZrPpLm6jqrEdf_XN39HuEze6",
    gids: { songs: 1233158892, verses: 1471833179, lines: 924686161, videos: 1420763163 },
  },
  {
    slug: "traditional-songs",
    title: "Lalitha Sangeetham",
    native: "లలిత సంగీతం",
    names: { te: "లలిత సంగీతం", en: "Lalitha Sangeetham" },
    part: "",
    blurb: "Aarti, mangalam and other light classical and traditional songs",
    pubId: "2PACX-1vTfg4reBO2qx4W88TLbMnK8Ve9h08ya3hEkNJHRU1BBx1qXImEcJelCgCNnluMJxlmynYZr6GIBqJuq",
    gids: { songs: 1233158892, lines: 924686161, videos: 1420763163 },  // no Verses tab: not needed for these songs
  },
  {
    slug: "annamayya-songs",
    title: "Annamayya Songs",
    native: "అన్నమయ్య కీర్తనలు",
    names: { te: "అన్నమయ్య కీర్తనలు", en: "Annamayya Songs" },
    part: "",
    blurb: "Keertanas of Tallapaka Annamacharya",
    pubId: "2PACX-1vSw7C5nJptbrY5r9HBaXRgiGGF85BRLCbrahxCoH5_oE74wA-8L4dcXXwcfozrInZ0IhT8uutpgTjfZ",
    gids: { songs: 1233158892, verses: 1471833179, lines: 924686161, videos: 1420763163 },
  },
  {
    slug: "harathi-songs",
    title: "Harathi Songs",
    native: "హారతి పాటలు",
    names: { te: "హారతి పాటలు", en: "Harathi Songs" },
    part: "",
    blurb: "Harathi songs",
    pubId: "2PACX-1vQ7vbfj-CiVhBuqNCyqnGqrXFUXVP8Ph-_IZ7xxVV0YEj7ysGNC8Ahw1uqxklGAAz5nntgqEJsi8yZb",
    gids: { songs: 1233158892, verses: 1471833179, lines: 924686161, videos: 1420763163 },
  },
  // Spare entry for the next collection: copy it, fill it in, and remove the two slashes at the start of each line.
  // {
  //   slug: "kirtanas",
  //   title: "Kirtanas",
  //   native: "",
  //   names: { te: "", dev: "", en: "Kirtanas" },
  //   part: "Kirtana",
  //   blurb: "",
  //   pubId: "",
  //   gids: { songs: 0, verses: 0, lines: 0, videos: 0 },
  // },
];
