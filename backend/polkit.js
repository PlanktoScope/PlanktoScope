/* globals polkit */

// https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.systemd1.html#Security

polkit.addRule(function (action, subject) {
  if (
    action.id == "org.freedesktop.systemd1.manage-units" &&
    subject.user == "pi"
  ) {
    return polkit.Result.YES
  }

  if (
    action.id == "org.freedesktop.systemd1.manage-unit-files" &&
    subject.user == "pi"
  ) {
    return polkit.Result.YES
  }

  return false
})
