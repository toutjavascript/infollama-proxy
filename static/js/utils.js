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

/* Generate a long text non sense string */
function generateText(length = 132000) {
  var lorem = `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim.
Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit.
Ut velit mauris, egestas sed, gravida nec, ornare ut, mi. Aenean ut orci vel massa suscipit pulvinar. Nulla sollicitudin. Fusce varius, ligula non tempus aliquam, nunc turpis ullamcorper nibh, in tempus sapien eros vitae ligula. Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur aliquet pellentesque diam. Integer quis metus vitae elit lobortis egestas. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi vel erat non mauris convallis vehicula. Nulla et sapien. Integer tortor tellus, aliquam faucibus, convallis id, congue eu, quam. Mauris ullamcorper felis vitae erat. Proin feugiat, augue non elementum posuere, metus purus iaculis lectus, et tristique ligula justo vitae magna.
Aliquam convallis sollicitudin purus. Praesent aliquam, enim at fermentum mollis, ligula massa adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce vulputate sem at sapien. Vivamus leo. Aliquam euismod libero eu enim. Nulla nec felis sed leo placerat imperdiet. Aenean suscipit nulla in justo. Suspendisse cursus rutrum augue. Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel rhoncus faucibus, felis magna fermentum augue, et ultricies lacus lorem varius purus. Curabitur eu amet.
Morbi nisl eros, dignissim nec, malesuada et, convallis quis, augue. Vestibulum ante ipsum primis in faucibus orci.`;

  const nbTokens = estimateTokens(lorem);
  console.log(estimateTokens(lorem));

  let text = "";
  for (let i = 0; i < Math.ceil(length / nbTokens); i++) {
    text += lorem;
  }
  console.log(estimateTokens(text));

  return text;
}
/**
 * Estimate the number of tokens in a string for LLM context usage.
 * @param {string} text - The input string.
 * @returns {number} - The estimated number of tokens.
 */
function estimateTokens(text) {
  if (!text) return 0;
  // Split the text by spaces and punctuation marks
  const tokens = text.match(/\w+|[^\s\w]/g);
  return tokens ? Math.round(tokens.length * 1.4) : 0;
}
