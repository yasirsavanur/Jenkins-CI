const list = document.querySelector("#todo-list");
const form = document.querySelector("#todo-form");
const field = document.querySelector("#sampletodotext");
const completedCount = document.querySelector("#completed-count");

function updateSummary() {
  const completed = list.querySelectorAll("input:checked").length;
  completedCount.textContent = `${completed} completed`;
}

function bindCheckbox(checkbox) {
  checkbox.addEventListener("change", () => {
    const label = checkbox.closest("li").querySelector("span");
    label.className = checkbox.checked ? "done-true" : "done-false";
    updateSummary();
  });
}

list.querySelectorAll("input[type='checkbox']").forEach(bindCheckbox);

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const task = field.value.trim();
  if (!task) return;

  const item = document.createElement("li");
  const checkbox = document.createElement("input");
  const label = document.createElement("label");
  const text = document.createElement("span");
  const id = `task-${Date.now()}-${list.children.length}`;

  checkbox.id = id;
  checkbox.type = "checkbox";
  label.htmlFor = id;
  text.className = "done-false";
  text.textContent = task;
  label.append(text);
  item.append(checkbox, label);
  list.append(item);
  bindCheckbox(checkbox);
  field.value = "";
  field.focus();
});
