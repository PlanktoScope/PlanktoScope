import { readFile } from "fs/promises";
import child_process from "child_process";
import { promisify } from "util";

const execFile = promisify(child_process.execFile);

const path = "/var/lib/overlays/overrides/etc/machine-name";

export async function getName() {
  let data;

  try {
    data = await readFile(path, {
      encoding: "utf8",
    });
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
    data = "";
  }

  return data.trim() || null;
}

export async function getHostname() {
  const { stdout } = await execFile("hostnamectl", ["hostname"]);

  return stdout?.trim() || null;
}
