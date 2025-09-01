const usersBlock = document.querySelector(".users-block");
const pagination = document.querySelector(".pagination");
const access = localStorage.getItem("access");
if (!access) {
    window.location.href = "http://127.0.0.1:8000/login/";
} 

function redirect (url) {
    window.location.href = url
}

(async () => {
    try {
        const response = await fetch("/api/v1/users/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${access}`
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}`);
        }

        const apiData = await response.json();
        console.log(apiData);

        // Рендерим пользователей
        usersBlock.innerHTML = apiData.results.map(user => `
            <div class="user-card">
                <p>${user.username}</p>
                <p>${user.email}</p>
            </div>
        `).join("");
        if (apiData.next) {
            const btn = document.createElement("button");
            btn.textContent = "Next";
            btn.addEventListener("click", () => redirect(apiData.next));
            pagination.innerHTML = "";
            pagination.appendChild(btn);
        } else {
            pagination.innerHTML = "";
        }

    } catch (err) {
        console.error("Ошибка при запросе:", err);
        usersBlock.innerHTML = `<p style="color:red;">Не удалось загрузить пользователей</p>`;
    }
})();
document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('add-friend-btn');
  if (btn) {
    btn.onclick = function() {
      fetch('/api/friends/invites/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ to_user: btn.dataset.userId })
      })
      .then(resp => {
        if (resp.ok) {
          alert('Заявка отправлена!');
          btn.disabled = true;
        } else {
          alert('Ошибка отправки заявки');
        }
      });
    }
  }
});