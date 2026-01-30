/*
BEGINNER-FRIENDLY FRONTEND SCRIPT

What it does:
- Filters table rows (search)
- Loads items from API (/items)
- Adds or updates items using POST/PUT
- Deletes items using DELETE
*/

const q = document.getElementById("q");
const tbody = document.getElementById("tbody");
const countEl = document.getElementById("count");

const f_id = document.getElementById("item_id");
const f_name = document.getElementById("name");
const f_sku = document.getElementById("sku");
const f_qty = document.getElementById("qty");
const f_price = document.getElementById("price");

document.getElementById("refresh").addEventListener("click", loadItems);
document.getElementById("clear").addEventListener("click", clearForm);
document.getElementById("save").addEventListener("click", saveItem);

q.addEventListener("input", () => filterTable(q.value));

function filterTable(text){
  const term = (text || "").toLowerCase().trim();
  const rows = Array.from(tbody.querySelectorAll("tr"));
  let visible = 0;

  rows.forEach(r => {
    const name = (r.querySelector(".name")?.innerText || "").toLowerCase();
    const sku  = (r.querySelector(".sku")?.innerText || "").toLowerCase();
    const ok = !term || name.includes(term) || sku.includes(term);
    r.style.display = ok ? "" : "none";
    if(ok) visible++;
  });

  countEl.innerText = `${visible} shown`;
}

async function loadItems(){
  const res = await fetch("/items");
  const items = await res.json();

  tbody.innerHTML = items.map(it => `
    <tr data-id="${it.id}">
      <td class="actions">
        <button class="chip" onclick="uiEdit(${it.id})">Edit</button>
        <button class="chip danger" onclick="uiDelete(${it.id})">Delete</button>
      </td>
      <td>${it.id}</td>
      <td class="name">${escapeHtml(it.name ?? "")}</td>
      <td class="sku">${escapeHtml(it.sku ?? "")}</td>
      <td class="num">${it.qty ?? 0}</td>
      <td class="num">${(it.price === null || it.price === undefined) ? "-" : it.price}</td>
    </tr>
  `).join("");

  filterTable(q.value);
}

function uiEdit(id){
  const row = tbody.querySelector(`tr[data-id="${id}"]`);
  if(!row) return;

  f_id.value = id;
  f_name.value = row.querySelector(".name").innerText;
  f_sku.value  = row.querySelector(".sku").innerText;
  f_qty.value  = row.children[4].innerText;
  const priceText = row.children[5].innerText;
  f_price.value = (priceText === "-") ? "" : priceText;

  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function uiDelete(id){
  const ok = confirm(`Delete item #${id}?`);
  if(!ok) return;

  const res = await fetch(`/items/${id}`, { method: "DELETE" });
  if(!res.ok){
    alert("Delete failed.");
    return;
  }
  await loadItems();
}

async function saveItem(){
  // Basic validation (beginner-friendly)
  const name = f_name.value.trim();
  const sku  = f_sku.value.trim();
  const qty  = Number(f_qty.value || 0);
  const price = (f_price.value === "") ? null : Number(f_price.value);

  if(!name){
    alert("Name is required.");
    return;
  }
  if(!sku){
    alert("SKU is required.");
    return;
  }

  const payload = { name, sku, qty, price };

  const id = f_id.value.trim();

  // If ID is empty => Create (POST)
  if(!id){
    const res = await fetch("/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if(!res.ok){
      alert("Create failed. Check /docs for API validation errors.");
      return;
    }
    clearForm();
    await loadItems();
    return;
  }

  // If ID exists => Update (PUT)
  const res = await fetch(`/items/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if(!res.ok){
    alert("Update failed. Make sure the ID exists.");
    return;
  }
  clearForm();
  await loadItems();
}

function clearForm(){
  f_id.value = "";
  f_name.value = "";
  f_sku.value = "";
  f_qty.value = "";
  f_price.value = "";
}

function escapeHtml(s){
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// On first load, refresh the count for server-rendered table
filterTable("");






