/* Create the flow chart of proxy, ollama and user */

function getFlowContainer() {
  const hostType = getCurrentHostType();
  let hardware = sanitizeHTML(proxy.device.cpu_name);
  hardware += ` ${formatBytes(proxy.device.ram_installed, 0)}`;
  if (proxy.device.gpus) {
    const vram = proxy.device.gpus.reduce(
      (vram, gpu) => vram + gpu.memoryTotal,
      0
    );
    hardware += ` + ${formatBytes(vram, 0)} VRAM`;
  }
  const lan_ip = sanitizeHTML(proxy.ping.config.lan_ip);
  const port = sanitizeHTML(proxy.ping.config.port);

  return `
  <div class="text-center m-1"><strong>This flowchart explains how the proxy, ollama and user interact with each other.</strong></div>
  
  <div class="flowContainer">
<div class="lan lanWAN">
  <div id="titleLAN" class="">LAN ${lan_ip}</div>

  <div class="localhost localhost${hostType}">
    <div id="titleDevice">${hardware}</div>
    <div id="boxYou" class="box boxYou${hostType}">YOU</div>
    <div id="boxProxy" class="box">Infollama <br />port: ${port}</div>
    <div id="boxOllama" class="box">Ollama server</div>
    <div id="lineYou" class="line lineYou${hostType}"></div>
    <div id="lineProxy" class="line"></div>
  </div>
    <div class="vertical-line"></div>
  <div id="titleWAN">This is WEB</div>
    <div id="titleLOCALHOST">localhost</div>

</div>
</div>`;
}

function updateFlowContainer() {
  const flowContainer = getFlowContainer();
  document.getElementById("flowIsHere").innerHTML = flowContainer;
  showAlert("alert-flow", 0);
}
