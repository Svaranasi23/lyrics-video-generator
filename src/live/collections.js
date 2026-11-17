// The collections on the home page. One Google Sheet (same template) per collection.
// To add one: copy the template Sheet, publish it to the web, add an entry here, and push this file once.
//   slug   - used in the web address (player.html?c=slug); letters, numbers and dashes
//   title  - shown on the home page; native - the name in its own script (optional)
//   part   - what one song is called in the list heading (e.g. "Ashtapadi")
//   pubId  - the long id from the Publish-to-web link (after /d/e/, before /pub). Leave "" to be asked on each device.
//   gids   - the tab ids of that Sheet's four tabs (from the tab addresses, #gid=...)
window.COLLECTIONS = [
  {
    slug: "gita-govindam",
    title: "Gita Govindam",
    native: "గీత గోవిందం",
    part: "Ashtapadi",
    blurb: "The 24 Ashtapadis of Jayadeva",
    pubId: "",
    gids: { songs: 1233158892, verses: 1471833179, lines: 924686161, videos: 1420763163 },
  },
];
