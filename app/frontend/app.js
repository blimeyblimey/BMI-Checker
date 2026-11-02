const state = {
  fullname: "", weight: "", weight_unit: "kg",
  height: "", height_unit: "cm", age: "",
  bmi: null, category: "", advice: "",
  health_result: null, health_advice: null, answers: []
};

const questions = [
  "Do you exercise regularly?",
  "Do you eat fruits and vegetables daily?",
  "Do you sleep at least 7 hours a night?",
  "Do you drink at least 8 glasses of water daily?",
  "Do you avoid sugary drinks regularly?",
  "Do you limit junk food and processed foods?",
  "Do you perform stretching or light activity?",
  "Do you manage stress well (hobbies, relaxing)?"
];

document.addEventListener("DOMContentLoaded", () => {
  renderQuestions();
});

function renderQuestions() {
  const container = document.getElementById("questions-list");
  container.innerHTML = questions.map((q, idx) => `
    <label class="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition">
      <input type="checkbox" id="q-${idx}" class="w-5 h-5 text-[#c00000] focus:ring-[#c00000] rounded">
      <span class="text-gray-700 text-sm font-medium">${q}</span>
    </label>
  `).join("");
}

function showError(msg) {
  const banner = document.getElementById("error-banner");
  document.getElementById("error-message").textContent = msg;
  banner.classList.remove("hidden");
}

function clearError() {
  document.getElementById("error-banner").classList.add("hidden");
}

function switchPage(pageId) {
  clearError();
  ["page-1", "page-questions", "page-results"].forEach(id => {
    document.getElementById(id).classList.add("hidden");
  });
  document.getElementById(pageId).classList.remove("hidden");
}

async function handleCalculate(e) {
  e.preventDefault();
  clearError();

  state.fullname = document.getElementById("fullname").value;
  state.weight = document.getElementById("weight").value;
  state.weight_unit = document.getElementById("weight_unit").value;
  state.height = document.getElementById("height").value;
  state.height_unit = document.getElementById("height_unit").value;
  state.age = document.getElementById("age").value;

  try {
    const res = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        weight: state.weight, weight_unit: state.weight_unit,
        height: state.height, height_unit: state.height_unit, age: state.age
      })
    });

    const data = await res.json();
    if (!data.success) {
      showError(data.message);
      return;
    }

    state.bmi = data.data.bmi;
    state.category = data.data.category;
    state.advice = data.data.advice;

    if (confirm("Continue to health questions?")) {
      switchPage("page-questions");
    } else {
      showResults();
    }
  } catch (err) {
    showError("Failed to calculate BMI. Please check network connection.");
  }
}

async function submitAssessment() {
  clearError();
  state.answers = questions.map((_, idx) => document.getElementById(`q-${idx}`).checked);

  try {
    const res = await fetch("/api/assess-health", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: state.answers })
    });

    const data = await res.json();
    if (data.success) {
      state.health_result = data.data.health_result;
      state.health_advice = data.data.health_advice;
      showResults();
    }
  } catch (err) {
    showError("Failed to calculate health assessment.");
  }
}

function showResults() {
  document.getElementById("res-bmi").textContent = state.bmi;
  document.getElementById("res-category").textContent = state.category;
  document.getElementById("res-advice").textContent = state.advice;

  const healthContainer = document.getElementById("health-assessment-container");
  if (state.health_result) {
    document.getElementById("res-health").textContent = state.health_result;
    document.getElementById("res-health-advice").textContent = state.health_advice;
    healthContainer.classList.remove("hidden");
  } else {
    healthContainer.classList.add("hidden");
  }

  switchPage("page-results");
}

function goBackFromResults() {
  if (state.health_result) {
    switchPage("page-questions");
  } else {
    switchPage("page-1");
  }
}

function resetForm() {
  document.getElementById("bmi-form").reset();
  state.bmi = state.category = state.advice = state.health_result = state.health_advice = null;
  state.answers = [];
  renderQuestions();
  clearError();
}

async function exportPDF() {
  try {
    const res = await fetch("/api/export-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state)
    });

    if (!res.ok) throw new Error("Download failed.");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${state.fullname || "User"}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (err) {
    showError("Error exporting PDF report.");
  }
}