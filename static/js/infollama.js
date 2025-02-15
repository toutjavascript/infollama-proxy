/* Infollama.js file to be included in index.html web UI */

var dynamicTooltipList = [];

const logLevels = [];
logLevels["NEVER"] = "No logs at all";
logLevels["ERROR"] = "Log only error and not authorised requests";
logLevels["INFO"] =
  "Log usefull access (not api/ps, api/tags, ...), excluding prompts";
logLevels["PROMPT"] =
  "Log useful access (not api/ps, api/tags, ...), including prompts";
logLevels["ALL"] = "Log every event, including prompts";

const user = {
  user_name: "",
  user_type: "",
};
const proxy = {
  models: [],
  modelDetails: [],
  needModelDisplayUpdate: true,
  ps: [],
  device: {},
  ping: {},
  lastPing: 0,
  lastPingSuccess: 0,
  lastOllamaPingSuccess: 0,
  nbPing: 0,
  validToken: false,
};

class UsageSynthese {
  constructor(usage) {
    this.eval_count = usage.eval_count;
    this.load_duration = usage.load_duration / 1e9; /* Loading model */
    this.eval_duration = usage.eval_duration / 1e9; /* Response time */
    this.prompt_eval_count = usage.prompt_eval_count;
    this.prompt_eval_duration =
      usage.prompt_eval_duration / 1e9; /* Prompt reading time */
    this.total_duration =
      usage.total_duration /
      1e9; /* Total time : load + input time + output time */
    this.prompt_token_per_second =
      this.prompt_eval_count / this.prompt_eval_duration;
    this.response_token_per_second = this.eval_count / this.eval_duration;
    this.num_ctx = Math.min(
      usage.prompt_estimate_tokens,
      usage.prompt_eval_count
    );
  }

  getSummary() {
    return `Response: ${
      this.eval_count
    } tokens | Load duration: ${this.load_duration.toFixed(
      3
    )}s | Response time: ${this.eval_duration.toFixed(
      3
    )}s | Prompt reading time: ${this.prompt_eval_duration.toFixed(
      3
    )}s | Total time: ${this.total_duration.toFixed(
      3
    )}s | Prompt token per second: ${this.prompt_token_per_second.toFixed(
      2
    )} | Response token per second: ${this.response_token_per_second.toFixed(
      2
    )} | num_ctx: ${this.num_ctx}`;
  }
}

class Usage {
  constructor(data, prompt_estimate_tokens = 0) {
    this.prompt_estimate_tokens = parseInt(prompt_estimate_tokens);
    this.created_at = data?.created_at;
    this.done = data?.done;
    this.done_reason = data?.done_reason;
    this.response = data?.response;
    this.eval_count = parseInt(data?.eval_count) || 0;
    this.eval_duration = parseInt(data?.eval_duration) || 0;
    this.load_duration = parseInt(data?.load_duration) || 0;
    this.prompt_eval_count = parseInt(data?.prompt_eval_count) || 0;
    this.prompt_eval_duration = parseInt(data?.prompt_eval_duration) || 0;
    this.total_duration = parseInt(data?.total_duration) || 0;
  }

  // Add any other methods to manage the usage data as needed
}

function logout() {
  var logoutModal = new bootstrap.Modal(document.getElementById("logoutModal"));
  logoutModal.show();

  document.getElementById("confirmLogout").addEventListener(
    "click",
    function () {
      const token = getCookie("proxy-token");
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

/* Ping proxy that pings ollama */
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
        /* A response is received. Proxy pings successfully. Update the last ping success date and status */
        proxy.lastPingSuccess = new Date();
        proxy.ping = data;
        if (proxy.ping.ping) {
          /* Means ollama is pinging */
          proxy.lastOllamaPingSuccess = new Date();
          const iconHeart = document.getElementById("icon-heart");
          iconHeart.classList.add("green-heart");
          iconHeart.classList.remove("broken-heart");
          updateTooltipTitle("icon-heart", "Proxy and Ollama servers are up");
        } else {
          /* Means ollama is not pinging */
          const iconHeart = document.getElementById("icon-heart");
          iconHeart.classList.add("broken-heart");
          iconHeart.classList.remove("green-heart");
          updateTooltipTitle("icon-heart", "Ollama server is down");
        }
        resolve(data);
      })
      .catch((error) => {
        /* Proxy does not respond */
        const iconHeart = document.getElementById("icon-heart");
        iconHeart.classList.remove("green-heart");
        iconHeart.classList.add("broken-heart");
        updateTooltipTitle("icon-heart", "Proxy is down");
        reject(error);
      });
  });
}

function getDevice() {
  if (!proxy.validToken) {
    /* Return resolved if not logged in */
    /*
    return new Promise((resolve, reject) => {
       resolve({ ended: true });
    });
    */
  }
  return new Promise((resolve, reject) => {
    const token = getCookie("proxy-token");
    if (true) {
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
      //const message = "Please give a valid token to see the UI.";
      //document.getElementById("promise-result").innerHTML = message;
      reject(message);
    }
  });
}

function getPS() {
  if (!proxy.validToken) {
    /* Return resolved if not logged in */
    //return new Promise((resolve, reject) => {
    //resolve({ ended: true });
    //});
  }
  return new Promise((resolve, reject) => {
    const token = getCookie("proxy-token");
    if (true) {
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
  const token = getCookie("proxy-token");
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
    const token = getCookie("proxy-token");
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
        } else {
          proxy.needModelDisplayUpdate = false;
        }
        proxy.models = data.models;
        resolve(data);
      })
      .catch((error) => {
        console.error("Error on getModels():", error);
        reject(error);
      });
  });
}

/* Call all the /api/show to get details */
function getAllShowModels() {
  /* Check if details is not already fetched */
  const token = getCookie("proxy-token");

  proxy.models.forEach((model, index) => {
    if (!proxy.modelDetails.includes(model.name)) {
      fetch("/api/show", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        stream: false,
        body: JSON.stringify({ model: model.name }),
      })
        .then((response) => response.json())
        .then((data) => {
          proxy.modelDetails[model.name] = data;
        })
        .catch((error) => {
          console.error("Error on getAllShowModels():", error);
        });
    }
  });
}

/* Display software and network card */
function displaySoft() {
  const cardElement = document.getElementById("card-soft");
  const userType = sanitizeHTML(proxy.ping.user.user_type);
  const connectType = getCurrentConnectType();
  let api = "view models, view device and chat completion API";
  if (userType == "admin") {
    api = "all the APIs of Ollama";
  }
  let lanAccess = sanitizeHTML(
    "http://" + proxy.ping.config.lan_ip + ":" + proxy.ping.config.port
  );
  if (proxy.ping.config.host != "0.0.0.0") {
    lanAccess = "not possible (change host to 0.0.0.0)";
  }
  let wanAccess = "See doc to open web access";
  let domain = "";
  if (connectType == "WAN") {
    domain = window.location.hostname;
    const htmlProtocol =
      window.location.protocol == "http:"
        ? `<span class="badge bg-danger"><i class="bi bi-shield-exclamation"></i> NO SSL </span>`
        : `<span class="badge bg-danger"><i class="bi bi-shield-check"></i>SSL</span>`;

    wanAccess = `<span class="wanAccess">From <strong>${domain}</strong> tunnel ${htmlProtocol}</span>`;
  }

  let html = `
  <div class="">Your token is associated to <b>${sanitizeHTML(
    proxy.ping.user.user_name
  )}</b></div>
  <div class="">As <b>${userType}</b>, you have access to ${api}</div>
  <div class=""><b>Infollama Proxy:</b> v${sanitizeHTML(
    proxy.ping.proxy_version
  )}</div>
  <div class=""><b>Ollama Server:</b> v${sanitizeHTML(
    proxy.ping.ollama_version
  )}</div>
  <div class=""><b>Cors Policy, Allow-Origin:</b> ${sanitizeHTML(
    proxy.ping.config.cors_policy
  )}</div>
  <div class=""><b>Log level:</b> ${sanitizeHTML(
    proxy.ping.config.log_level
  )} <i class='bi bi-info-circle-fill' data-bs-toggle='dynamic-tooltip' title='${
    logLevels[proxy.ping.config.log_level]
  }'></i></div>
  <div class=""><b>Log file size:</b> ${formatBytes(
    proxy.device.log_file_size,
    1,
    ""
  )} </div>  
  <div class=""><b>LAN API access:</b> ${lanAccess}</div>
  <div class=""><b>WAN API access:</b> ${wanAccess}</div>
  `;
  cardElement.innerHTML = html;
}

/* Display a modal box with model details */
function showModelDetail(name, num_model) {
  if (proxy.modelDetails[name]) {
    const file_size = proxy.models[num_model].size;
    const show = proxy.modelDetails[name];
    const arch = show.model_info["general.architecture"];
    const languages = show.model_info["general.languages"] || null;
    const licence = show.model_info["general.license"] || null;
    const context_length = show.model_info[arch + ".context_length"] || 0;
    $("#show-model-name").html(`Detail configuration for <strong>${sanitizeHTML(
      name
    )}</strong><br>
     <span class="badge bg-info rounded-pill">${show.details.family}</span>
     <span class="badge bg-secondary rounded-pill mx-3">${
       show.details.parameter_size
     }</span>
     <span class="badge bg-secondary rounded-pill">${
       show.details.quantization_level
     } </span>
     <span class="mx-3">File size: ${formatBytes(file_size)}</span>

      `);
    let html = `
      <div>
      </div>
      ${
        languages
          ? "<div><strong>Languages</strong>: " +
            languages.join(", ") +
            "</div>"
          : ""
      }
      ${
        context_length
          ? "<div><strong>Max context length: </strong>: " +
            Math.round(context_length / 1024) +
            "k" +
            "</div>"
          : ""
      }
      <div><strong>Parameters: </strong>
      ${
        typeof show.parameters === "undefined"
          ? "<small class='text-muted ml-4'>Not defined</small>"
          : "<br><pre class='pre-template'>" +
            sanitizeHTML(show.parameters) +
            " </pre>"
      }</div>      
      <div><strong>System Prompt:</strong>
      ${
        typeof show.system === "undefined"
          ? "<small class='text-muted ml-4'>Not defined</small>"
          : "<br><pre class='pre-template'>" + sanitizeHTML(show.system)
      }</pre></div>
      <div><strong>Template:</strong><pre class='pre-template'>${sanitizeHTML(
        show.template
      )}</pre></div>
      ${licence ? "<div><strong>Licence: </strong>: " + licence + "</div>" : ""}
    
    `;
    $("#show-model-body").html(html);
    $("#show-model").modal("show");
  }
}

function confirmLoadModel(button) {
  const name = button.parentElement.parentElement?.dataset?.name;
  const digest = button.parentElement.parentElement?.dataset?.digest;
  if (!name) return false;
  const show = proxy.modelDetails[name];
  const arch = show.model_info["general.architecture"];
  const context_length = show.model_info[arch + ".context_length"] || 0;

  document.getElementById("loadModalModel").innerText = name;
  document.getElementById("loadModalDigest").innerText = digest;
  document.getElementById("max_num_ctx").innerText = context_length;
  document.getElementById("load_num_ctx").max = context_length;

  var loadModal = new bootstrap.Modal(document.getElementById("loadModal"));
  loadModal.show();

  document.getElementById("confirmLoad").addEventListener(
    "click",
    function () {
      loadModel();
    },
    { once: true }
  );
}

function loadModel() {
  const digest = document.getElementById("loadModalDigest").innerText;
  const name = document.getElementById("loadModalModel").innerText;
  const num_ctx = parseInt(document.getElementById("load_num_ctx").value);
  const num_gpu = parseInt(document.getElementById("load_num_gpu").value);
  const keep_alive = document.getElementById("load_keep_alive").value;

  return new Promise((resolve, reject) => {
    const token = getCookie("proxy-token");
    fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        model: name,
        messages: [],
        stream: false,
        keep_alive: keep_alive,
        options: {
          num_ctx: num_ctx,
          num_gpu: num_gpu,
        },
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data?.done_reason === "load") {
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("loadModal")
          );
          modal.hide();
          new jBox("Notice", {
            content:
              "Good news. Model <b>" +
              name +
              "</b> is loading!<br>It will appear in running model list in the next few seconds.",
            color: "blue",
          });
          setTimeout(() => {
            getPS().then(() => {
              displayPS();
            });
          }, 1000);
        }
        resolve(data);
      })
      .catch((error) => {
        reject(error.message);
      });
  });
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
    let totalSize = 0;
    html +=
      "<thead><tr><th class='sortable' colspan='3'>Name</th><th class='text-end sortable'>File Size</th><th class='text-end sortable'>Family</th><th class='text-end sortable'>Params</th><th class='text-end sortable'>Quantization</th><th class='text-end sortable'>Installed</th></tr></thead>";
    html += "<tbody>";
    for (let i = 0; i < proxy.models.length; i++) {
      pill2 = `<span class="badge bg-secondary rounded-pill">${sanitizeHTML(
        proxy.models[i].details.parameter_size
      )}</span>`;
      pill1 = `<span class="badge bg-info rounded-pill">${sanitizeHTML(
        proxy.models[i].details.family
      )}</span>`;
      pill3 = `<span class="badge bg-secondary rounded-pill">${sanitizeHTML(
        proxy.models[i].details.quantization_level
      )}</span>`;
      installed = getDeltaTime(proxy.models[i].modified_at);
      /* Sorting name with size. IE smollm2:135m is lower than smollm2:1.7b
        So we must convert :1.5b or 150m to the real integer value padded with 0 
      */
      sortingName = proxy.models[i].name;
      let reg = new RegExp("^([a-z0-9.-]+:)([0-9.]+)([mb]{1})", "g");
      let parts = reg.exec(sortingName);
      if (parts) {
        sortingName =
          parts[1] +
          (parseFloat(parts[2]) * (parts[3] == "m" ? 1e6 : 1e9))
            .toString()
            .padStart(18, 0);
      }

      totalSize += proxy.models[i].size;
      html +=
        "<tr data-digest='" +
        sanitizeHTML(proxy.models[i].digest) +
        "' data-name='" +
        sanitizeHTML(proxy.models[i].name) +
        "'><td data-sort='" +
        sanitizeHTML(sortingName) +
        "'>" +
        sanitizeHTML(proxy.models[i].name) +
        "</td><td>" +
        '<i class="bi bi-play-circle-fill btnLoad" data-bs-toggle="dynamic-tooltip" title="Load this model" onclick="confirmLoadModel(this)"></i></td>' +
        "<td><button class='form-control btn btn-sm btn-info p-0 btn-detail-model' data-name='" +
        sanitizeHTML(proxy.models[i].name) +
        "' onclick='showModelDetail(this.dataset.name, " +
        i +
        ")'>details</button>" +
        "</td><td class='text-end' data-sort='" +
        sanitizeHTML(proxy.models[i].size) +
        "'>" +
        formatBytes(proxy.models[i].size) +
        "</td><td class='text-end'>" +
        pill1 +
        "</td><td class='text-end'>" +
        pill2 +
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
    html += "</tbody>";

    title = `${proxy.models.length} model${
      proxy.models.length > 1 ? "s" : ""
    } available using ${formatBytes(
      totalSize
    )} on disk <input type="text" id="searchInput" class="form-control" placeholder="Filter this list by name...">`;
  }
  titleElement.innerHTML = title;
  tableElement.innerHTML = html;
  displayPS(); /* Force to refresh the tr highlight on running models */
  makeTableSortable();

  /* Filtering by name */
  $("#searchInput").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#table-available-models tbody tr").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
}

/* Return a gauge based on the VRAM GPU usage */
function displayGPUChart(gpu) {
  const ramUsagePercentage = Math.round(
    (gpu.memoryUsed / gpu.memoryTotal) * 100
  );

  let gauge = `<div class="progress" style="height: 20px; margin-bottom: 5px;">
  <div id="ram-usage" class="progress-bar" role="progressbar" style="width: ${ramUsagePercentage}%; background-color: ${
    ramUsagePercentage > 80 ? "red" : "green"
  };" aria-valuenow="${ramUsagePercentage}" aria-valuemin="0" aria-valuemax="100">${ramUsagePercentage.toFixed(
    0
  )}%</div>
  </div>`;

  return gauge;
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
  if (device.gpus) {
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
      let temp = "";
      let color_badge = "";
      if (device.gpus[i].temperature != null) {
        color_badge = "#01DD00";
        if (device.gpus[i].temperature >= 70) {
          color_badge = "#FF020C";
        } else if (device.gpus[i].temperature >= 50) {
          color_badge = "orange";
        }
        temp = ` <span class="badge" style="color:white !important; background-color:${color_badge} !important; font-weight:bold; font-size:12px !important; margin-bottom:2px;">${device.gpus[i].temperature}°C</span>`;
      }

      gpus += `<div  class='d-flex justify-content-between'><span><small>${num}</small>${
        sanitizeHTML(device.gpus[i].name) + " <b>" + vram + "</b></span>" + temp
      }</div>${displayGPUChart(device.gpus[i])}`;
    }
  }
  discrete_gpus =
    gpus != ""
      ? `<b>Discrete GPU${device.gpus.length > 1 ? "s" : ""}:</b> ${gpus}<br>`
      : "";

  html = `<b>${sanitizeHTML(device.cpu_name)}</b><br>
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

  const headerDeviceElement = document.getElementById("header-device");
  html = "";

  headerDeviceElement.innerHTML = `Proxy running on: <br><strong>${device.hostname}</strong>`;

  document.title = `Infollama Proxy - ${device.hostname}`;
}

/* Function to confirm unloading a running model */
function confirmUnloadModel(button) {
  const name = button.parentElement.parentElement?.dataset?.name;
  if (!name) return false;
  document.getElementById("unloadModalModel").innerText = name;

  var unloadModal = new bootstrap.Modal(document.getElementById("unloadModal"));
  unloadModal.show();

  document.getElementById("confirmUnload").addEventListener(
    "click",
    function () {
      unloadModel();
    },
    { once: true }
  );
}

/* Function to stop a running model */
function unloadModel() {
  return new Promise((resolve, reject) => {
    const name = document.getElementById("unloadModalModel").innerText;
    const token = getCookie("proxy-token");
    fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        model: name,
        messages: [],
        stream: false,
        keep_alive: 0,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("unloadModal")
        );
        modal.hide();
        if (data?.done_reason === "unload") {
          new jBox("Notice", {
            content:
              "Good news. Model <b>" +
              name +
              "</b> is unloading!<br>It will desappear from running model list in the next few seconds.",
            color: "blue",
          });
          setTimeout(() => {
            getPS().then(() => {
              displayPS();
            });
          }, 1000);
        }
        resolve(data);
      })
      .catch((error) => {
        reject(error.message);
      });
  });
}

/* Open a modal to confirm the run model */
function confirmRunModel(button) {
  const name = button.parentElement.parentElement?.dataset?.name;
  if (!name) return false;
  document.getElementById("runModalModel").innerText = name;

  var rundModal = new bootstrap.Modal(document.getElementById("runModal"));
  rundModal.show();

  document.getElementById("confirmRun").addEventListener(
    "click",
    function () {
      runModel();
    },
    { once: true }
  );
}

function runModel() {
  const name = document.getElementById("runModalModel").innerText;
  if (!name) return false;
  const token = getCookie("proxy-token");
  const prompt =
    generateText(32000) +
    "\n-----\n Ignore all previous text content and simply give me your name";
  new jBox("Notice", {
    content:
      "API sent to model <b>" +
      name +
      "</b><br>Response will appear in a few seconds",
    color: "blue",
  });
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("runModal")
  );
  modal.hide();

  fetch("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token,
    },
    body: JSON.stringify({
      model: name,
      prompt: prompt,
      stream: false,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data?.done) {
        const usage = new Usage(data, estimateTokens(prompt));
        const summary = new UsageSynthese(usage);

        new jBox("Notice", {
          content:
            "Model response is:<br><b>" +
            sanitizeHTML(data?.response) +
            "</b><br>Summary: " +
            summary.getSummary(),
          color: "green",
        });
        console.log(usage);
        console.log(summary.getSummary());
      }
    })
    .catch((error) => {
      console.log(error.message);
      new jBox("Notice", {
        content:
          "Model response error:<br><b>" + sanitizeHTML(error.message) + "</b>",
        color: "green",
      });
    });
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
      "<thead><tr><th>Name</th><th colspan='1' class='text-center'>RAM Size</th><th class='text-end'>Expires</th><th class='text-end'></th></tr></thead>";
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
        "' data-name='" +
        sanitizeHTML(proxy.ps[i].name) +
        "'><td>" +
        "<i class='bi bi-rocket-takeoff-fill btnRun' data-bs-toggle='dynamic-tooltip' onclick='confirmRunModel(this)' title='Click to run a request on this Model'></i> " +
        sanitizeHTML(proxy.ps[i].name) +
        "</td><td class='text-end'>" +
        formatBytes(proxy.ps[i].size) +
        "<br>" +
        pill +
        "</td><td class='text-end'>" +
        sanitizeHTML(proxy.ps[i].expires_in) +
        "</td><td class='text-end'>" +
        "<i class='bi bi-x-square-fill btnStop' data-bs-toggle='dynamic-tooltip' onclick='confirmUnloadModel(this)' title='Click to unload this model from RAM'></i>";
      ("</td></tr>");
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

/* Re activate the tooltips that are updated by the refreshed UI */
function activateTooltips() {
  /* Remove all tooltips before adding new ones */
  dynamicTooltipList.map(function (tooltipTriggerEl) {
    tooltipTriggerEl?.dispose();
  });
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="dynamic-tooltip"]')
  );
  dynamicTooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/* Check if the token is valid by a call to the proxy server. If valid, store to cookie and start web ui */
function send_token(token) {
  var token_checked = false;
  if (token != "") {
    if (token.length > 10) {
      if (token.substring(0, 4) == "pro_") {
        token_checked = true;
      }
    }
  }
  if (!token_checked) {
    showAlertError(
      "Token is not well formatted. It must start with 'pro_' and be at least 10 characters long."
    );
    return false;
  }

  ping(token)
    .then((data) => {
      if (data.ping == true) {
        proxy.lastPingSuccess = new Date();
        if (data.user.user_type == "anonymous") {
          //proxy.validToken = false;
          showAlertError(
            "Token is not valid. Please check your users.conf file and try again."
          );
          return false;
        } else {
          if (data.user.user_name == "openbar") {
            /* if proxy access is opened without token control */

            Promise.all([getModels(), getPS(), getDevice()])
              .then((results) => {
                displayPS();
                displayDevice();
                proxy.needModelDisplayUpdate = true;
                displayModels();
                displaySoft();
                startUIWhenLogin();
                showAlert("alert-openbar");
                activateTooltips();
              })
              .catch((error) => {
                console.log(error);
              });
          } else {
            setCookie("proxy-token", token, 100);
            showAlert("alert-success");
            startUIWhenLogin();
          }
        }
      } else if (data.ping == false) {
        if (data.user.user_type == "anonymous") {
          showAlertError("Ollama seems to be down. Please try again later.");
          return false;
        }
      } else {
        showAlertError("Infollama seems to be down.");
        return false;
      }
    })
    .catch((error) => {
      console.error("Error ping(token):", error);
      showAlertError("Infollama seems to be down.");
      return false;
    });
}

/* Update the header with user information */
function updateHeader() {
  if (proxy?.ping?.user && proxy?.ping?.user?.user_name != "anonymous") {
    document.getElementById(
      "header-user"
    ).innerHTML = `Welcome <b>${sanitizeHTML(proxy.ping.user.user_name)}</b><br>
      <small class="text-muted">Type ${sanitizeHTML(
        proxy.ping.user.user_type
      )}</small>`;
    if (proxy?.ping?.user.user_name == "openbar") {
      document.getElementById("btn-logout").classList.add("d-none");
    } else {
      document.getElementById("btn-logout").classList.remove("d-none");
    }
  } else {
    document.getElementById("header-user").innerText =
      "Please log in with token";
  }
}

/* Launch the UI when a valid token is provided */
function startUIWhenLogin() {
  document.getElementById("div-connect").style.display = "none";
  document.getElementById("div-ui").classList.remove("d-none");

  Promise.all([getModels(), getPS(), getDevice()])
    .then((results) => {
      const [models, ps, device] = results;
      displayPS();
      displayModels();
      displayDevice();
      displaySoft();
      updateHeader();
      updateFlowContainer();
      getAllShowModels();
      activateTooltips();
    })
    .catch((error) => {
      console.error("Error on startUIWhenLogin() :", error);
      return false;
    });
}

/* Heart Beat of the UI app to check connexion and LLM server usage */
function heartBeat() {
  setInterval(() => {
    Promise.all([ping(), getModels(), getPS(), getDevice()])
      .then((data) => {
        displayPS();
        displayModels();
        displayDevice();
        activateTooltips();
      })
      .catch((error) => {
        console.error("Error on heartBeat() :", error);
      });
  }, 10000); // Check every 10 seconds
}

function showAlert(name, autoClose = 5000) {
  document.getElementById(name)?.classList.remove("d-none");
  if (autoClose > 0) {
    setTimeout(() => {
      document.getElementById(name)?.classList.add("d-none");
    }, autoClose); // Hide the alert after autoClose/1000 seconds
  }
}

function showAlertError(message, autoClose = 5000) {
  document.getElementById("alert-error-message").innerText = message;
  document.getElementById("alert-error").classList.remove("d-none");
  if (autoClose > 0) {
    setTimeout(() => {
      document.getElementById("alert-error").classList.add("d-none");
    }, autoClose); // Hide the alert after autoClose/1000 seconds
  }
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
      if (proxy.ping.config.anonymous_access === true) {
        /* If openbar on proxy is enabled */
        console.log(
          "Openbar is enabled on proxy, user_name=" + proxy.ping.user.user_name
        );
        send_token("pro_token_openbar");
      }
      const token = getCookie("proxy-token");
      if (token) {
        send_token(token);
      }
    }
  });
  /* Then start the heartBeat function */
  heartBeat();
}
