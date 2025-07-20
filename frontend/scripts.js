// let selectedJail = null;

function logout() {
  fetch("/", {
    headers: {
      "Authorization": "Basic " + btoa("logout:logout")
    }
  }).then(() => {
    alert("Logged out. You may need to close the tab or reload.");
    window.location.reload();
  });
}

function openPriorityModal(jailName, currentPriority) {
  selectedJail = jailName;
  document.getElementById("priorityModalTitle").textContent = `Set Priority for ${jailName}`;
  document.getElementById("priorityInput").value = currentPriority;
  document.getElementById("priorityModal").style.display = "flex";
}

function closePriorityModal() {
  document.getElementById("priorityModal").style.display = "none";
  selectedJail = null;
}

async function confirmPriority() {
  const priorityValue = document.getElementById("priorityInput").value;
  const output = document.getElementById("output");

  const num = parseInt(priorityValue, 10);
  if (isNaN(num) || num < 0 || num > 99) {
    alert("Invalid priority. Must be 0–99.");
    return;
  }

  output.textContent = `Setting priority on ${selectedJail} to ${num}...`;

  try {
    const res = await fetch(`/api/set_priority?jail=${encodeURIComponent(selectedJail)}&priority=${num}`);
    const text = await res.text();
    output.textContent = `Output from ${selectedJail}:\n\n${text}`;
    await loadJails();
  } catch (err) {
    output.textContent = `Failed to set priority: ${err}`;
  }

  closePriorityModal();
}

async function loadJails() {
  const tableBody = document.querySelector("#jail-table tbody");
  tableBody.innerHTML = '';

  try {
    const res = await fetch("/api/list_jails");
    const jails = await res.json();

    if (!Array.isArray(jails) || jails.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="5">No jails found.</td></tr>';
      return;
    }

    jails.forEach(jail => {
      const row = document.createElement("tr");

      const bootClass = (jail.Boot.toLowerCase() === 'on') ? 'btn-blue' : 'btn-red';

      row.innerHTML = `
        <td>${jail.Name}</td>
        <td>
        <button class="${bootClass}" title="Toggle whether this jail starts at boot" onclick="toggleBoot('${jail.Name}', '${jail.Boot}')">
          ${jail.Boot}
        </button>
        </td>
        <td><button title="Set the priority this jail has in boot order.  Lower number = higher priority" onclick="openPriorityModal('${jail.Name}', '${jail.Prio}')">${jail.Prio}</button></td>
        <td>${jail.State}</td>
        <td>${jail["IP Address"]}</td>
        <td>
        <button onclick="restartJail('${jail.Name}')">Restart</button>
        <button onclick="startJail('${jail.Name}')">Start</button>
        <button onclick="stopJail('${jail.Name}')">Stop</button>
        </td>
      `;

      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to load jail list:", err);
    tableBody.innerHTML = '<tr><td colspan="5">Failed to load jail list.</td></tr>';
  }
}

async function restartJail(jail) {
  const output = document.getElementById("output");
  output.textContent = `Restarting ${jail}...`;

  try {
    const res = await fetch(`/api/restart?jail=${encodeURIComponent(jail)}`);
    const text = await res.text();
    output.textContent = `Output from ${jail}:\n\n${text}`;
    await loadJails();  // reload status in case state changes
  } catch (err) {
    output.textContent = `Failed to restart jail: ${err}`;
  }
}

async function startJail(jail) {
  const output = document.getElementById("output");
  output.textContent = `Starting ${jail}...`;

  try {
    const res = await fetch(`/api/start?jail=${encodeURIComponent(jail)}`);
    const text = await res.text();
    output.textContent = `Output from ${jail}:\n\n${text}`;
    await loadJails();  // reload status in case state changes
  } catch (err) {
    output.textContent = `Failed to start jail: ${err}`;
  }
}

async function stopJail(jail) {
  const output = document.getElementById("output");
  output.textContent = `Stopping ${jail}...`;

  try {
    const res = await fetch(`/api/stop?jail=${encodeURIComponent(jail)}`);
    const text = await res.text();
    output.textContent = `Output from ${jail}:\n\n${text}`;
    await loadJails();  // reload status in case state changes
  } catch (err) {
    output.textContent = `Failed to stop jail: ${err}`;
  }
}

async function toggleBoot(jail, bootState) {
  const output = document.getElementById("output");
  output.textContent = `Toggling Boot setting on ${jail}...`;

  try {
    let boot = (bootState === 'on') ? 'off' : 'on';
    const res = await fetch(`/api/set_boot?jail=${encodeURIComponent(jail)}&boot=${boot}`);
    const text = await res.text();
    output.textContent = `Output from ${jail}:\n\n${text}`;
    await loadJails();  // reload status in case state changes
  } catch (err) {
    output.textContent = `Failed to stop jail: ${err}`;
  }
}

async function setPriority(jailName, currentPriority) {
  const newPriority = prompt(`Current priority for ${jailName} is ${currentPriority}. Enter new priority (0-99):`, currentPriority);

  if (newPriority === null) return;  // user cancelled
  const num = parseInt(newPriority, 10);

  if (isNaN(num) || num < 0 || num > 99) {
    alert("Invalid priority. Must be a number between 0 and 99.");
    return;
  }

  const output = document.getElementById("output");
  output.textContent = `Setting priority on ${jailName} to ${num}...`;

  try {
    const res = await fetch(`/api/set_priority?jail=${encodeURIComponent(jailName)}&priority=${num}`);
    const text = await res.text();
    output.textContent = `Output from ${jailName}:\n\n${text}`;
    await loadJails();  // refresh to show updated value
  } catch (err) {
    output.textContent = `Failed to set priority: ${err}`;
  }
}

window.onload = loadJails;
