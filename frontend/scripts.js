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

      row.innerHTML = `
        <td>${jail.Name}</td>
        <td>${jail.JID}</td>
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

window.onload = loadJails;
