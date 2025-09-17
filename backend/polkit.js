/* globals polkit */

polkit.addRule(function (action, subject) {
  if (
    action.id == "org.freedesktop.systemd1.manage-units" &&
    subject.user == "pi"
  ) {
    return polkit.Result.YES
  }
})
