function formatBytes(bytes, decimals = 1, force = "GB") {
  if (bytes === 0) return "0 Byte";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  let i = Math.floor(Math.log(bytes) / Math.log(k));
  if (force != "" && sizes.includes(force)) {
    i = sizes.indexOf(force);
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  }
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

/* Returns the difference between two dates in days or weeks or months */
function getDeltaTime(date) {
  if (typeof date === "string") {
    date = new Date(date);
  }
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  if (years > 0) return `${years} year${years > 1 ? "s" : ""}`;
  else if (months > 0) return `${months} month${months > 1 ? "s" : ""}`;
  else if (weeks > 0) return `${weeks} week${weeks > 1 ? "s" : ""}`;
  else if (days > 0) return `${days} day${days > 1 ? "s" : ""}`;
  else return "today";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0)
      return decodeURIComponent(c.substring(nameEQ.length, c.length));
  }
  return null;
}
function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  var cookieString = name + "=" + value + expires + "; path=/";
  document.cookie = cookieString;
}

function getCurrentConnectType() {
  const host = window.location.hostname;
  if (host == "localhost" || host == "127.0.0.1") {
    return "LOCAL";
  } else if (
    host.startsWith("192.168.") ||
    host.startsWith("10.0.") ||
    host.startsWith("172.16.")
  ) {
    return "LAN";
  } else {
    return "WAN";
  }
}

function sanitizeHTML(str) {
  var temp = document.createElement("div");
  temp.textContent = str;
  return temp.innerHTML;
}
