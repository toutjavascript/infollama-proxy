/* Infollama.js file to be included in index.html web UI */

const user = {
  user_name: "",
  user_type: "",
};
const proxy = {
  models: [],
  needModelDisplayUpdate: false,
  ps: [],
  device: {},
  ping: {},
  lastPing: 0,
  lastPingSuccess: 0,
  nbPing: 0,
  validToken: false,
};

function sanitizeHTML(str) {
  var temp = document.createElement("div");
  temp.textContent = str;
  return temp.innerHTML;
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
function logout() {
  var logoutModal = new bootstrap.Modal(document.getElementById("logoutModal"));
  logoutModal.show();

  document.getElementById("confirmLogout").addEventListener(
    "click",
    function () {
      var token = getCookie("proxy-token");
      if (token) {
        setCookie("proxy-token", "", -1);
        document.cookie =
          "token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
      }
      location.reload();
    },
    { once: true }
  );
}

function ping(token = "") {
  return new Promise((resolve, reject) => {
    if (token == "") {
      token = getCookie("proxy-token");
    }
    proxy.lastPing = new Date();
    proxy.nbPing++;
    fetch("/info/ping", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        proxy.lastPingSuccess = new Date();
        proxy.ping = data;
        const iconHeart = document.getElementById("icon-heart");
        iconHeart.classList.add("green-heart");
        iconHeart.classList.remove("broken-heart");
        updateTooltipTitle("icon-heart", "Proxy and Ollama servers are up");
        proxy.lastPingData = resolve(data);
      })
      .catch((error) => {
        const iconHeart = document.getElementById("icon-heart");
        iconHeart.classList.remove("green-heart");
        iconHeart.classList.add("broken-heart");
        updateTooltipTitle("icon-heart", "Proxy or Ollama servers not reached");
        reject(error);
      });
  });
}

function getDevice() {
  if (!proxy.validToken) {
    /* Return resolved if not logged in */
    return new Promise((resolve, reject) => {
      resolve({ ended: true });
    });
  }
  return new Promise((resolve, reject) => {
    var token = getCookie("proxy-token");
    if (token) {
      fetch("/info/device", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          proxy.device = data;
          resolve(data);
        })
        .catch((error) => {
          console.error("Error on getDevice():", error);
          reject(error);
        });
    } else {
      const message = "Please give a valid token to see the UI.";
      document.getElementById("promise-result").innerHTML = message;
      reject(message);
    }
  });
}

function getPS() {
  if (!proxy.validToken) {
    /* Return resolved if not logged in */
    return new Promise((resolve, reject) => {
      resolve({ ended: true });
    });
  }
  return new Promise((resolve, reject) => {
    var token = getCookie("proxy-token");
    if (token) {
      fetch("/info/ps", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          proxy.ps = data.models;
          resolve(data);
        })
        .catch((error) => {
          console.error("Error on getPS():", error);
          reject(error);
        });
    } else {
      const message = "Please give a valid token to see the UI.";
      document.getElementById("promise-result").innerHTML = message;
      reject(message);
    }
  });
}

function getVersion() {
  var token = getCookie("proxy-token");
  return new Promise((resolve, reject) => {
    fetch("/api/version", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        proxy.ollama_version = data.version;
        resolve(data);
      })
      .catch((error) => {
        console.error("Error on getVersion():", error);
        reject(error);
      });
  });
}

function getModels() {
  return new Promise((resolve, reject) => {
    var token = getCookie("proxy-token");
    fetch("/api/tags", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (JSON.stringify(proxy.models) != JSON.stringify(data.models)) {
          proxy.needModelDisplayUpdate = true;
          proxy.models = data.models;
        } else {
          proxy.needModelDisplayUpdate = false;
        }
        resolve(data);
      })
      .catch((error) => {
        console.error("Error on getModels():", error);
        reject(error);
      });
  });
}
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

/* Display software and network card */
function displaySoft() {
  const cardElement = document.getElementById("card-soft");
  const type = sanitizeHTML(proxy.ping.user.user_type);
  let api = "view models, view device and chat completion API";
  if (type == "admin") {
    api = "all the APIs of Ollama";
  }
  let lanAccess = sanitizeHTML(
    "http://" + proxy.ping.config.lan_ip + ":" + proxy.ping.config.port
  );
  if (proxy.ping.config.host != "0.0.0.0") {
    lanAccess = "not possible (change host to 0.0.0.0)";
  }
  let html = `
  <div class="">Your token is associated to <b>${sanitizeHTML(
    proxy.ping.user.user_name
  )}</b></div>
  <div class="">As <b>${type}</b>, you have access to ${api}</div>
  <div class=""><b>Infollama Proxy:</b> v${sanitizeHTML(
    proxy.ping.proxy_version
  )}</div>
  <div class=""><b>Ollama Server:</b> v${sanitizeHTML(
    proxy.ping.ollama_version
  )}</div>
  <div class=""><b>Cors Policy, Allow-Origin:</b> ${sanitizeHTML(
    proxy.ping.config.cors_policy
  )}</div>
  <div class=""><b>LAN API access:</b> ${lanAccess}</div>
  <div class=""><b>WAN API access:</b> Work in progress with Ngrok</div>
  
  
  `;
  cardElement.innerHTML = html;
}

/* Display the available models on the card table-available-models */
function displayModels() {
  /* Check if proxy.models has changed and need a display update */
  if (!proxy.needModelDisplayUpdate) return false;

  const tableElement = document.getElementById("table-available-models");
  const titleElement = document.getElementById("title-available-models");
  let html = "",
    title = "";
  if (proxy.models.length == 0) {
    title = "No model available on Ollama";
    html = "<thead><tr><th>No available Model</th></tr></thead>";
  } else {
    let size = 0;
    html +=
      "<thead><tr><th class='sortable'>Name</th><th class='text-end sortable'>File Size</th><th class='text-end sortable'>Params</th><th class='text-end sortable'>Family</th><th class='text-end sortable'>Quantization</th><th class='text-end sortable'>Installed</th></tr></thead>";
    html += "<tbody>";
    for (let i = 0; i < proxy.models.length; i++) {
      pill1 = `<span class="badge bg-info rounded-pill">${sanitizeHTML(
        proxy.models[i].details.family
      )}</span>`;
      pill2 = `<span class="badge bg-secondary rounded-pill">${sanitizeHTML(
        proxy.models[i].details.parameter_size
      )}</span>`;
      pill3 = `<span class="badge bg-secondary rounded-pill">${sanitizeHTML(
        proxy.models[i].details.quantization_level
      )}</span>`;
      installed = getDeltaTime(proxy.models[i].modified_at);
      size += proxy.models[i].size;
      html +=
        "<tr data-digest='" +
        sanitizeHTML(proxy.models[i].digest) +
        "'><td>" +
        sanitizeHTML(proxy.models[i].name) +
        "</td><td class='text-end' data-sort='" +
        sanitizeHTML(proxy.models[i].size) +
        "'>" +
        formatBytes(proxy.models[i].size) +
        "</td><td class='text-end'>" +
        pill2 +
        "</td><td class='text-end'>" +
        pill1 +
        "</td><td class='text-end' data-sort='" +
        sanitizeHTML(
          proxy.models[i].details.quantization_level.replace(/([QF])/g, "")
        ) +
        "'>" +
        pill3 +
        "</td><td class='text-end' data-sort='" +
        sanitizeHTML(proxy.models[i].modified_at) +
        "'>" +
        installed +
        "</td></tr>";
    }
    title = `${proxy.models.length} model${
      proxy.models.length > 1 ? "s" : ""
    } available using ${formatBytes(size)} on disk`;
    html += "</tbody>";
  }
  titleElement.innerHTML = title;
  tableElement.innerHTML = html;
  displayPS(); /* Force to refresh the tr highlight on running models */
  makeTableSortable();
}

function displayDevice() {
  const device = proxy.device;
  let icon = `bi-windows`;
  if (device.os == "Linux") {
    icon = `bi-linux`;
  } else if (device.os == "Mac") {
    icon = `bi-apple`;
  }

  const deviceElement = document.getElementById("card-device");
  let ram_used = device.ram_installed - device.ram_available;
  const ramUsagePercentage = Math.round(
    (ram_used / device.ram_installed) * 100
  );
  let gpus = "",
    discrete_gpus = "";
  for (i = 0; i < device.gpus.length; i++) {
    if (device.gpus[i].memoryTotal == 0) {
      gpus = "not found";
      break;
    }

    let num = "";
    if (device.gpus.length > 1) {
      num = `#${i + 1} `;
    }
    let vram = formatBytes(device.gpus[i].memoryTotal, 0);
    gpus += `<div>${num}${sanitizeHTML(
      device.gpus[i].name + " " + vram
    )}</div>`;
  }
  discrete_gpus =
    gpus != ""
      ? `<b>Discrete GPU${device.gpus.length > 1 ? "s" : ""}:</b> ${gpus}<br>`
      : "";

  html = `Proxy is running on <b>${sanitizeHTML(device.cpu_name)}</b><br>
      <b>OS Version:</b> <i class="bi ${icon}" style="font-size: 1.2rem;" title=""></i> ${sanitizeHTML(
    device.os + " " + device.os_version
  )}<br>
    <b>CPU threads:</b> ${sanitizeHTML(device.cpu_threads)}<br>
    <b>Installed RAM:</b> ${formatBytes(device.ram_installed, 0)}<br>
    <div class="progress" style="height: 20px; margin-bottom: 5px;">
    <div id="ram-usage" class="progress-bar" role="progressbar" style="width: ${ramUsagePercentage}%; background-color: ${
    ramUsagePercentage > 80 ? "red" : "green"
  };" aria-valuenow="${ramUsagePercentage}" aria-valuemin="0" aria-valuemax="100">${ramUsagePercentage.toFixed(
    0
  )}%</div>
    </div>

    ${discrete_gpus}
    `;
  deviceElement.innerHTML = html;
}

/* Display running model on the card */
function displayPS() {
  const tableElement = document.getElementById("table-running-models");
  const titleElement = document.getElementById("title-running-models");
  let html = "",
    title = "";
  if (proxy.ps.length == 0) {
    title = "No Model Running";
    html = "<thead><tr><th>No Model Running</th></tr></thead>";
  } else {
    html +=
      "<thead><tr><th>Name</th><th colspan='2' class='text-center'>RAM Size</th><th class='text-end'>Expires</th></tr></thead>";
    html += "<tbody>";
    let ram = 0;
    for (let i = 0; i < proxy.ps.length; i++) {
      ram += proxy.ps[i].size;
      let pct = Math.round((proxy.ps[i].size_vram / proxy.ps[i].size) * 100);
      let pill = "";
      if (pct == 100) {
        pill = `<span class="badge bg-success rounded-pill">${pct}% GPU</span>`;
      } else {
        if (pct < 80) {
          pill = `<span class="badge bg-danger rounded-pill">${pct}% GPU</span>`;
        } else {
          pill = `<span class="badge bg-warning rounded-pill">${pct}% GPU</span>`;
        }
      }
      html +=
        "<tr data-digest='" +
        sanitizeHTML(proxy.ps[i].digest) +
        "'><td>" +
        sanitizeHTML(proxy.ps[i].name) +
        "</td><td class='text-end'>" +
        formatBytes(proxy.ps[i].size) +
        "</td><td class='text-end'>" +
        pill +
        "</td><td class='text-end'>" +
        sanitizeHTML(proxy.ps[i].expires_in) +
        "</td></tr>";
    }
    html += "</tbody>";
    title = `${proxy.ps.length} model${
      proxy.ps.length > 1 ? "s" : ""
    } running, using ${formatBytes(ram)} RAM</title>`;
  }
  tableElement.innerHTML = html;
  titleElement.innerHTML = title;
  // Update available models table to highlight the running models
  $("table#table-available-models tr").each(function () {
    const digest = $(this).data("digest");
    const runningModel = proxy.ps.find((model) => model.digest === digest);
    if (runningModel) {
      $(this).addClass("highlight");
    } else {
      $(this).removeClass("highlight");
    }
  });
}

function makeTableSortable() {
  $(".sortable").click(function () {
    const table = $(this).parents("table").eq(0);
    const rows = table
      .find("tr:gt(0)")
      .toArray()
      .sort(comparer($(this).index()));
    this.asc = !this.asc;

    // Update sort indicators
    $(".sortable").removeClass("asc desc");
    $(this).addClass(this.asc ? "asc" : "desc");

    // Sort the rows
    if (!this.asc) {
      rows.reverse();
    }

    // Reattach sorted rows to table
    for (let i = 0; i < rows.length; i++) {
      table.append(rows[i]);
    }
  });
}

function convertValueEndsWithBOrM(value) {
  return value.endsWith("b")
    ? parseFloat(value) * 1e9
    : value.endsWith("m")
    ? parseFloat(value) * 1e6
    : parseFloat(value);
}

function comparer(index) {
  return function (a, b) {
    const valA = getCellValue(a, index).toLowerCase();
    const valB = getCellValue(b, index).toLowerCase();

    // Check if the values are numbers
    const numA = parseFloat(valA);
    const numB = parseFloat(valB);
    if (!isNaN(numA) && !isNaN(numB)) {
      // Check if string ends with a B or a M
      if (
        (valA.endsWith("b") || valA.endsWith("m")) &&
        (valB.endsWith("b") || valB.endsWith("m"))
      ) {
        // Convert B or M to bytes
        const bytesA = convertValueEndsWithBOrM(valA);
        const bytesB = convertValueEndsWithBOrM(valB);
        return bytesA - bytesB;
      } else {
        if (valA == numA.toString() && valB == numB.toString()) {
          /* Real numbers */
          return numA - numB;
        } else {
          return valA.toString().localeCompare(valB);
        }
      }
    }

    // If not numbers, compare as strings
    return valA.toString().localeCompare(valB);
  };
}

function getCellValue(row, index) {
  const cell = $(row).children("td").eq(index);
  // Check if there's a data-sort attribute
  return cell.attr("data-sort") || cell.text();
}

/* Check if the token is valid by a call to the proxy server. If valid, store to cookie and start */
function send_token(token) {
  console.log("send_token(" + token + ")");
  var checked = false;
  if (token != "") {
    if (token.length > 10) {
      if (token.substring(0, 4) == "pro_") {
        checked = true;
      }
    }
  }
  if (!checked) {
    document.getElementById("div-check-token").innerHTML =
      "<span class='error'>Token is not well formatted. It must start with 'pro_' and be at least 10 characters long.</span>";
    return false;
  }

  ping(token)
    .then((data) => {
      if (data.ping == true) {
        proxy.lastPingSuccess = new Date();
        console.log("ping call success");
        console.log(data);
        if (data.user.user_type == "anonymous") {
          proxy.validToken = false;
          showAlert("alert-error");
          return false;
        } else {
          setCookie("proxy-token", token, 100);
          showAlert("alert-success");
          proxy.validToken = true;
          startUIWhenLogin();
        }
      } else if (data.ping == false) {
        if (data.user.user_type == "anonymous") {
          showAlert("alert-error");
          proxy.validToken = false;
          return false;
        }
      } else {
        showAlert("alert-error");
        proxy.validToken = false;
        return false;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showAlert("alert-error");
      return false;
    });
}

/* Update the header with user information */
function updateHeader() {
  if (proxy.validToken) {
    document.getElementById(
      "header-user"
    ).innerHTML = `Welcome <b>${sanitizeHTML(proxy.ping.user.user_name)}</b><br>
      <small class="text-muted">Type ${sanitizeHTML(
        proxy.ping.user.user_type
      )}</small>`;
    document.getElementById("btn-logout").classList.remove("d-none");
  } else {
    document.getElementById("header-user").innerText =
      "Please log in with token";
  }
}

/* Launch the UI when a valid token is provided */
function startUIWhenLogin() {
  updateHeader();

  setTimeout(() => {
    document.getElementById("div-connect").style.display = "none";
  }, 10);
  document.getElementById("div-ui").classList.remove("d-none");

  Promise.all([getModels(), getPS(), getDevice()])
    .then((results) => {
      const [models, ps, device] = results;
      console.log("Device:", device);
      displayPS();
      displayModels();
      displayDevice();
      displaySoft();
    })
    .catch((error) => {
      console.error("Error on startUIWhenLogin() :", error);
      return false;
    });
}

/* Heart Beat of the UI app to check connexion and LLM server usage */
function heartBeat() {
  setInterval(() => {
    Promise.all([getModels(), getPS(), getDevice()])
      .then((data) => {
        displayPS();
        displayModels();
        displayDevice();
      })
      .catch((error) => {
        console.error("Error on heartBeat() :", error);
        document.getElementById("div-check-token").innerHTML =
          "<span class='error'>An error occurred. Proxy seems to be down.</span>";
      });
  }, 10000); // Check every 10 seconds
}

function showAlert(name, message = "") {
  document.getElementById(name)?.classList.remove("d-none");
  // document.getElementById(name)?.innerHTML = message;
  autoHideAlert(name);
}

function autoHideAlert(name) {
  setTimeout(() => {
    document.getElementById(name)?.classList.add("d-none");
  }, 5000); // Hide the alert after 5 seconds
}

// Function to update tooltip title dynamically
function updateTooltipTitle(elementId, newTitle) {
  var element = document.getElementById(elementId);
  if (element) {
    element.setAttribute("title", newTitle);
    element.setAttribute("data-bs-original-title", newTitle);
    element.setAttribute("aria-label", newTitle);

    var tooltip = bootstrap.Tooltip.getInstance(element);
    if (tooltip) {
      tooltip.dispose();
      tooltip = new bootstrap.Tooltip(element);
    }
  }
}

/* Function that starts the proxy UI */
function startProxyUI() {
  /* First Ping to check connexion to server and cookie to logged in*/
  ping().then((response) => {
    // Check if a token is stored in the cookie
    if (response.user.user_type != "anonymous") {
      let token = getCookie("proxy-token");
      if (token) {
        send_token(token);
      }
    }
  });
  /* Then start the heartBeat function */
  heartBeat();
}
