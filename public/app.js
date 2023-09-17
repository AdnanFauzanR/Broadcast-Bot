function getUsersByRole(role) {
    return fetch(`api/user/${role}`)
        .then(response => response.json());
}

function deleteUser(userId) {
    return fetch(`api/user/${userId}`, {
        method: 'DELETE',
    });
}

function getUsername() {
    return fetch(`api/username`)
        .then(response => response.json());
}

function displayUser(user) {
    const userContainer = document.createElement('div');
    userContainer.classList.add('user-container');

    const userinfoContainer = document.createElement('div');
    userinfoContainer.classList.add('userinfo-container');

    const userinfoNameContainer = document.createElement('div');
    userinfoNameContainer.classList.add('userinfo-name-container');
    userinfoNameContainer.innerText = `${user.first_name} ${user.last_name}`;

    const userinfoUsernameContainer = document.createElement('div');
    userinfoUsernameContainer.classList.add('userinfo-username-container');
    userinfoUsernameContainer.innerText = user.username;

    userinfoContainer.appendChild(userinfoNameContainer);
    userinfoContainer.appendChild(userinfoUsernameContainer);

    const editDeleteContainer = document.createElement('div');
    editDeleteContainer.classList.add('edit-delete-container');

    const editIcon = document.createElement('img');
    editIcon.src = 'edit-icon.svg';
    editIcon.alt = 'edit icon';
    editIcon.classList.add('edit-icon');

    const deleteIcon = document.createElement('img');
    deleteIcon.src = 'delete-icon.svg';
    deleteIcon.alt = 'delete icon';
    deleteIcon.classList.add('delete-icon');

    deleteIcon.addEventListener('click', () => {
        if(confirm('Are you user want to delete this user?')) {
            deleteUser(user._id)
                .then(() => {
                    userContainer.remove();
                })
                .catch(error => {
                    console.error('Error deleting user: ', error);
                })
        }
    });

    editDeleteContainer.appendChild(editIcon);
    editDeleteContainer.appendChild(deleteIcon);

    userContainer.appendChild(userinfoContainer);
    userContainer.appendChild(editDeleteContainer);

    document.getElementById('user-list').appendChild(userContainer);

}
