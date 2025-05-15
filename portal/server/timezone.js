import child_process from "child_process";
import { promisify } from "util";

const execFile = promisify(child_process.execFile);

const { stdout } = await execFile("timedatectl", [
  "list-timezones",
  "--no-pager",
]);

const timezones = stdout
  .split("\n")
  .filter((tz) => !!tz)
  .map((tz) => {
    return { value: tz, label: tz };
  });
export { timezones };

export async function setTimezone(timezone) {
  await execFile("timedatectl", ["set-timezone", timezone]);
}

export async function getTimezone() {
  const { stdout } = await execFile("timedatectl", [
    "show",
    `--property=Timezone`,
    "--value",
  ]);

  return stdout?.trim() || null;
}
