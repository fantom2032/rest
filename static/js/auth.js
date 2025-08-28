const form = document.querySelector(".auth_form");

form.addEventListener("submit", async (e) => {
    e.preventDefault(); 
    // не даём форме перезагрузить страницу
    const formData = new FormData(form);
    // формируем объект
    const payload = {
        username: formData.get("username"),
        password: formData.get("password")
    };
    try {
        const response = await fetch("/api/token/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // "X-CSRFToken": getCookie("csrftoken") 
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}`);
        }
        const data = await response.json();
        console.log("Успешный логин:", data);
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
    } catch (err) {
        console.error("Ошибка при запросе:", err);
    }
});

document.getElementById('registration-form').onsubmit = async function(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const avatarFile = formData.get('avatar');

    let avatarId = null;

    if (avatarFile && avatarFile.size > 0) {
        const imageForm = new FormData();
        imageForm.append('image', avatarFile);

        const imageResp = await fetch('/api/images/', {
            method: 'POST',
            body: imageForm,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        if (!imageResp.ok) {
            alert('Ошибка загрузки фото');
            return;
        }

        const imageData = await imageResp.json();
        avatarId = imageData.id;
    }

    const regData = {};
    formData.forEach((value, key) => {
        if (key !== 'avatar') regData[key] = value;
    });
    if (avatarId) regData.avatar = avatarId;

    const regResp = await fetch('/api/users/registration/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(regData)
    });

    if (regResp.ok) {
        alert('Регистрация успешна!');
    } else {
        alert('Ошибка регистрации');
    }
};