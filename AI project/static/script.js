const form = document.getElementById("analyzeForm");
const resultBox = document.getElementById("result");
const loading = document.getElementById("loading");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  resultBox.classList.add("hidden");
  loading.classList.remove("hidden");

  const formData = new FormData(form);

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    loading.classList.add("hidden");

    if (data.error) {
      alert(data.error);
      return;
    }

    document.getElementById("resumeScore").textContent = data.resume_score;
    document.getElementById("toxicityPercent").textContent = data.toxicity_percent;
    document.getElementById("penalty").textContent = data.penalty;
    document.getElementById("finalScore").textContent = data.final_score;

    const skillsList = document.getElementById("skillsList");
    skillsList.innerHTML = "";

    data.skills.forEach(skill => {
      const li = document.createElement("li");
      li.textContent = skill;
      skillsList.appendChild(li);
    });

    const flaggedPostsDiv = document.getElementById("flaggedPosts");
    flaggedPostsDiv.innerHTML = "";

    const details = data.background_report.details;

    details.forEach(item => {
      if (item.flagged) {
        const div = document.createElement("div");
        div.classList.add("post-card");

        div.innerHTML = `
          <p><b>Post:</b> ${item.post}</p>
          <p><b>Flagged Labels:</b> ${item.flagged_labels.map(l => l.label + " (" + l.score + ")").join(", ")}</p>
        `;

        flaggedPostsDiv.appendChild(div);
      }
    });

    if (flaggedPostsDiv.innerHTML === "") {
      flaggedPostsDiv.innerHTML = "<p>No toxic posts detected.</p>";
    }

    resultBox.classList.remove("hidden");

  } catch (err) {
    loading.classList.add("hidden");
    alert("Error connecting to server");
    console.log(err);
  }
});
