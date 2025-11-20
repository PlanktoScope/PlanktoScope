/* globals polkit */

// https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.systemd1.html#Security

const allowed_actions = [
  "org.freedesktop.systemd1.manage-units",
  "org.freedesktop.systemd1.manage-unit-files",
  "org.freedesktop.NetworkManager.wifi.scan",
  "org.freedesktop.NetworkManager.network-control",
  "org.freedesktop.NetworkManager.settings.modify.system",
]

polkit.addRule(function (action, subject) {
  if (allowed_actions.indexOf(action.id) > -1 && subject.user == "pi") {
    return polkit.Result.YES
  }

  return polkit.Result.NO
})
