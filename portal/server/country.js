import { readFile, writeFile } from "fs/promises";

// We don't use files from "sudo dpkg-query -L wireless-regdb"
// because the tool to read them crda was removed in Bookworm
const iso3166tab = await readFile("/usr/share/zoneinfo/iso3166.tab", {
  encoding: "utf8",
});
let countries = [];
for (const line of iso3166tab.split("\n")) {
  if (line.startsWith("#")) continue;
  const [value, label] = line.split("\t");
  if (value && label) {
    countries.push({ value, label });
  }
}
countries = countries.sort((a, b) => {
  return a.label.localeCompare(b.label);
});

export { countries };

const path = "/etc/modprobe.d/cfg80211_regdomain.conf";

// We don't use `iw reg get` and `iw reg set`
// because
// * it is temporary
// * wifi needs to be disconnected for get to reflect set
export async function setWifiRegulatoryDomain(code) {
  await writeFile(path, `options cfg80211 ieee80211_regdom=${code}`);
}

// TODO: set by default to 00 which is global setting
export async function getWifiRegulatoryDomain() {
  let data;

  try {
    await readFile(path, {
      encoding: "utf8",
    });
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
    data = "";
  }

  const [, code] = data.match(/options cfg80211 ieee80211_regdom=(.*$)/);
  return code || null;
}
