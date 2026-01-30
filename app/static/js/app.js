// app/static/js/app.js
// این فایل کل منطق UI را کنترل می‌کند (بدون فریم‌ورک، ساده و قابل فهم)

const API = {
    listItems: () => fetch("/items"),
    addItem:  (payload) => fetch("/items", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)}),
    updateItem: (id, payload) => fetch(`/items/${id}`, { method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)}),
    deleteItem: (id) => fetch(`/items/${id}`, { method: "DELETE" }),
  };
  
  let allItems = [];
  
  function $(id){ return document.getElementById(id); }
  
  function showLoading(on){
    const el = $("appLoading");
    if(!el) return;
    el.classList.toggle("hidden", !on);
  }
  
  function toast(msg){
    const el = $("toast");
    if(!el) return;
    el.textContent = msg;
    el.classList.remove("hidden");
    setTimeout(() => el.classList.add("hidden"), 2200);
  }
  
  // تبدیل قیمت به متن قشنگ
  function fmtMoney(v){
    if(v === null || v === undefined || v === "") return "-";
    const num = Number(v);
    if(Number.isNaN(num)) return String(v);
    return num.toLocaleString("en-US");
  }
  
  function safeNum(v){
    const n = Number(v);
    return Number.isNaN(n) ? 0 : n;
  }
  
  function renderKPIs(items){
    $("kpiCount").textContent = items.length.toLocaleString("en-US");
  
    const totalQty = items.reduce((s, it) => s + safeNum(it.qty), 0);
    $("kpiQty").textContent = totalQty.toLocaleString("en-US");
  
    const totalValue = items.reduce((s, it) => {
      const q = safeNum(it.qty);
      const p = (it.price === null || it.price === undefined) ? 0 : safeNum(it.price);
      return s + (q * p);
    }, 0);
  
    $("kpiValue").textContent = fmtMoney(totalValue);
  }
  
  function renderTable(items){
    const tbody = $("itemsTbody");
    tbody.innerHTML = "";
  
    for(const it of items){
      const tr = document.createElement("tr");
  
      tr.innerHTML = `
        <td>${it.id ?? "-"}</td>
        <td>${it.name ?? ""}</td>
        <td>${it.sku ?? ""}</td>
        <td>${it.qty ?? 0}</td>
        <td>${fmtMoney(it.price)}</td>
        <td>
          <div class="actions">
            <button class="btn btn-ghost" data-act="edit" data-id="${it.id}">ویرایش</button>
            <button class="btn btn-danger" data-act="del" data-id="${it.id}">حذف</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    }
  
    // اکشن‌ها
    tbody.querySelectorAll("button[data-act='edit']").forEach(btn => {
      btn.addEventListener("click", () => fillFormForEdit(btn.dataset.id));
    });
    tbody.querySelectorAll("button[data-act='del']").forEach(btn => {
      btn.addEventListener("click", () => deleteItem(btn.dataset.id));
    });
  }
  
  async function fetchItems(){
    showLoading(true);
    try{
      const res = await API.listItems();
      if(!res.ok) throw new Error("Failed to load items");
      allItems = await res.json();
  
      renderKPIs(allItems);
      renderTable(allItems);
    }catch(err){
      console.error(err);
      toast("خطا در دریافت آیتم‌ها");
    }finally{
      showLoading(false);
    }
  }
  
  function applySearch(){
    const q = ($("searchBox").value || "").trim().toLowerCase();
    if(!q){
      renderTable(allItems);
      renderKPIs(allItems);
      return;
    }
    const filtered = allItems.filter(it => {
      const name = (it.name || "").toLowerCase();
      const sku = (it.sku || "").toLowerCase();
      return name.includes(q) || sku.includes(q);
    });
  
    renderTable(filtered);
    renderKPIs(filtered);
  }
  
  function clearForm(){
    $("fId").value = "";
    $("fName").value = "";
    $("fSku").value = "";
    $("fQty").value = "";
    $("fPrice").value = "";
  }
  
  function fillFormForEdit(id){
    const it = allItems.find(x => String(x.id) === String(id));
    if(!it) return;
  
    $("fId").value = it.id ?? "";
    $("fName").value = it.name ?? "";
    $("fSku").value = it.sku ?? "";
    $("fQty").value = it.qty ?? 0;
    $("fPrice").value = (it.price === null || it.price === undefined) ? "" : it.price;
  
    toast("آیتم برای ویرایش وارد فرم شد");
  }
  
  async function saveItem(){
    // خواندن فرم
    const id = $("fId").value.trim();
    const name = $("fName").value.trim();
    const sku  = $("fSku").value.trim();
    const qty  = $("fQty").value.trim();
    const price = $("fPrice").value.trim();
  
    // اعتبارسنجی ساده
    if(!name){
      toast("نام آیتم اجباری است");
      return;
    }
    if(!sku){
      toast("SKU اجباری است");
      return;
    }
  
    const payload = {
      name,
      sku,
      qty: safeNum(qty),
      price: price === "" ? null : safeNum(price),
    };
  
    showLoading(true);
    try{
      let res;
      if(id){
        // ویرایش
        res = await API.updateItem(id, payload);
      }else{
        // افزودن
        res = await API.addItem(payload);
      }
  
      if(!res.ok){
        const txt = await res.text();
        console.error(txt);
        toast("خطا در ذخیره");
        return;
      }
  
      clearForm();
      toast("ذخیره شد ✅");
      await fetchItems();
  
    }catch(err){
      console.error(err);
      toast("خطا در عملیات ذخیره");
    }finally{
      showLoading(false);
    }
  }
  
  async function deleteItem(id){
    if(!confirm(`آیتم ${id} حذف شود؟`)) return;
  
    showLoading(true);
    try{
      const res = await API.deleteItem(id);
      if(!res.ok){
        toast("حذف انجام نشد");
        return;
      }
      toast("حذف شد ✅");
      await fetchItems();
    }catch(err){
      console.error(err);
      toast("خطا در حذف");
    }finally{
      showLoading(false);
    }
  }
  
  // Tabs (برای اینکه حس “سیستم” بده)
  function setupTabs(){
    document.querySelectorAll(".nav-item").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
        btn.classList.add("active");
  
        const tab = btn.dataset.tab;
        document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
        document.getElementById(`tab-${tab}`).classList.add("active");
  
        // تغییر عنوان بالا
        const titles = {
          inventory: ["داشبورد انبار", "مدیریت آیتم‌ها، خروجی Excel/PDF، و عملیات"],
          reports:   ["گزارش‌ها", "گزارش‌های ورود/خروج/انتقال و..."],
          settings:  ["تنظیمات", "تم، پالت رنگی، و تنظیمات سیستم"],
        };
        $("pageTitle").textContent = titles[tab][0];
        $("pageSub").textContent   = titles[tab][1];
      });
    });
  }
  
  window.addEventListener("DOMContentLoaded", async () => {
    setupTabs();
  
    $("btnRefresh").addEventListener("click", fetchItems);
    $("btnSave").addEventListener("click", saveItem);
    $("btnClear").addEventListener("click", clearForm);
    $("searchBox").addEventListener("input", applySearch);
  
    await fetchItems();
  });
  