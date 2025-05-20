document.addEventListener("DOMContentLoaded", () => {
  const analyzeButton = document.getElementById("analyzeButton");
  const articleInput = document.getElementById("articleInput");
  const summarySection = document.getElementById("요약");

  // Create and add a status message element for user feedback
  const statusMessage = document.createElement("p");
  statusMessage.id = "statusMessage";
  statusMessage.style.marginTop = "10px";
  statusMessage.style.fontWeight = "bold";
  summarySection.appendChild(statusMessage);

  // Event listener for the button
  analyzeButton.addEventListener("click", async () => {
    const articleText = articleInput.value.trim();

    // Clear previous results
    summarySection.innerHTML = "<h2>요약</h2>";
    summarySection.appendChild(statusMessage);

    // Validate input
    if (!articleText) {
      showStatus("⚠️ 뉴스 기사를 입력해주세요.", "red");
      return;
    }

    // Show loading status
    showStatus("🔍 분석 중입니다... 잠시만 기다려주세요.", "#007bff");

    try {
      // Send the article to the backend
      const response = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: articleText }),
      });

      // Check response status
      if (!response.ok) {
        throw new Error("서버 응답 오류");
      }

      const data = await response.json();

      // Display the results
      const resultColor = data.is_fake ? "red" : "green";
      const resultText = data.is_fake
        ? "❌ 이 뉴스는 가짜일 가능성이 높습니다."
        : "✅ 이 뉴스는 진짜일 가능성이 높습니다.";

      summarySection.innerHTML = `
        <h2>요약</h2>
        <p><strong>뉴스 요약:</strong> ${data.summary}</p>
        <p><strong>예측 결과:</strong> 
          <span style="color: ${resultColor}; font-weight: bold;">${resultText}</span>
        </p>
        <p><strong>신뢰도:</strong> ${data.confidence}%</p>
      `;
      showStatus("✅ 분석이 완료되었습니다.", "green");
    } catch (error) {
      console.error("분석 실패:", error);
      showStatus("❌ 서버와 통신 중 문제가 발생했습니다.", "red");
    }
  });

  // Helper function for status messages
  function showStatus(message, color) {
    statusMessage.textContent = message;
    statusMessage.style.color = color;
  }
});
