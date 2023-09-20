function getUsersByRole(role) {
    return fetch(`api/user/${role}`).then((response) => response.json());
}

function deleteUser(userId) {
    return fetch(`api/user/${userId}`, {
        method: "DELETE",
    });
}

function getUsernames(role) {
    return fetch(`api/username/${role}`).then((response) => response.json());
}

function displayUser(user) {
    const userContainer = document.createElement("div");
    userContainer.classList.add("user-container");

    const userinfoContainer = document.createElement("div");
    userinfoContainer.classList.add("userinfo-container");

    const userinfoNameContainer = document.createElement("div");
    userinfoNameContainer.classList.add("userinfo-name-container");
    userinfoNameContainer.innerText = `${user.first_name} ${user.last_name}`;

    const userinfoUsernameContainer = document.createElement("div");
    userinfoUsernameContainer.classList.add("userinfo-username-container");
    userinfoUsernameContainer.innerText = `@${user.username}`;

    userinfoContainer.appendChild(userinfoNameContainer);
    userinfoContainer.appendChild(userinfoUsernameContainer);

    const deleteContainer = document.createElement("div");
    deleteContainer.classList.add("delete-container");

    const deleteIcon = document.createElement("img");
    deleteIcon.src = "delete-icon.svg";
    deleteIcon.alt = "delete icon";
    deleteIcon.classList.add("delete-icon");

    deleteIcon.addEventListener("click", () => {
        if (confirm("Are you user want to delete this user?")) {
            deleteUser(user._id)
                .then(() => {
                    userContainer.remove();
                })
                .catch((error) => {
                    console.error("Error deleting user: ", error);
                });
        }
    });

    deleteContainer.appendChild(deleteIcon);

    userContainer.appendChild(userinfoContainer);
    userContainer.appendChild(deleteContainer);

    document.getElementById("user-list").appendChild(userContainer);
}

function displayUsername(user) {
    const userListCheckbox = document.createElement("ul");
    userListCheckbox.classList.add("user-list-checkbox");

    const userWindowContainer = document.createElement("div");
    userWindowContainer.classList.add("user-list-window-container");

    const username = document.createElement("label");
    username.classList.add("user");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = user;

    const userInfoContainer = document.createElement("div");
    userInfoContainer.classList.add("userinfo-container");

    const userInfoNameContainer = document.createElement("div");
    userInfoNameContainer.classList.add("userinfo-name-container");
    userInfoNameContainer.innerText = "NAMA PANJANG";

    const userInfoUsernameContainer = document.createElement("div");
    userInfoUsernameContainer.classList.add("userinfo-username-container");
    userInfoUsernameContainer.innerText = user ? `@${user}` : "";

    username.appendChild(checkbox);

    userWindowContainer.appendChild(username);
    userWindowContainer.appendChild(userInfoContainer);
    userListCheckbox.appendChild(userWindowContainer);
    userInfoContainer.appendChild(userInfoNameContainer);
    userInfoContainer.appendChild(userInfoUsernameContainer);

    document
        .getElementById("user-window-container")
        .appendChild(userListCheckbox);
}
