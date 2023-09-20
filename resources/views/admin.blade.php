<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link href="{{asset('style.css') }}" rel="stylesheet">
    <script src="{{ asset('app.js') }}"></script>
    <title>Role Management</title>
</head>

<body>
    <div class="header-container">
        <img src="logo-telkom.svg" alt="logo telkom">
        <span>Admin Telkom</span>
    </div>
    <div class="title-container">
        Role Management
        <p>Lorem Ipsum is simply dummy text of the printing and typesetting industry</p>
    </div>
    <div class="role-container">
        <button class="tab-button active" data-tab-id="admin" onclick="changeTab('admin')">Admin</button>
        <button class="tab-button" data-tab-id="broadcaster" onclick="changeTab('broadcaster')">Broadcaster</button>
        <button class="tab-button" data-tab-id="member" onclick="changeTab('member')">Member</button>
    </div>
    <div class="button-container">
        <button id="openModalBtn">
            <img src="add-icon.svg" alt="add icon">
            <span>Add New</span>
        </button>
    </div>

    <!-- The Modal -->
    <div id="myModal" class="modal">
        <div class="modal-content">
            <span id="closeModalBtn" class="close">&times;</span>
            <div class="window-container">
                <div class="title-window-container">
                    Admin Role Management
                </div>
                <p>Lorem Ipsum is simply dummy text of the printing and typesetting industry</p>
                <div id="user-window-container">
                    <ul class="user-list-checkbox">
                        <div class="user-list-window-container">
                            <label for="user1"><input type="checkbox" id="" name="" value=""> </label>
                            <div class="userinfo-container">
                                <div class="userinfo-name-container">
                                </div>
                                <div class="userinfo-username-container">
                                </div>
                            </div>
                        </div>
                    </ul>
                </div>
                <div class="button-container">
                    <button id="addNewBtn">
                        <img src=" add-icon.svg" alt="add icon">
                        <span>Add New</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
    <div id="user-list">
        <div class="user-container">
            <div class="userinfo-container">
                <div class="userinfo-name-container">
                </div>
                <div class="userinfo-username-container">
                </div>
            </div>
            <div class="delete-container">
                <img src="delete-icon.svg" alt="delete icon" class="delete-icon">
            </div>
        </div>
    </div>

    </div>
    </div>
    <script>
    let activeTabId = "admin"; // Default active tab is 'admin'

    async function displayUsernameList(role) {
        try {
            const usernames = await getUsernames(role);
            const userWindowContainer = document.getElementById('user-window-container');
            userWindowContainer.innerHTML = '';
            const usernameList = usernames.usernames;

            usernameList.forEach(username => {
                displayUsername(username);
            })
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    }


    async function displayUserByRole(role) {
        try {
            const users = await getUsersByRole(role);
            const userListContainer = document.getElementById('user-list');
            userListContainer.innerHTML = ''; // Clear previous content

            users.forEach(user => {
                displayUser(user);

            });
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    }

    function changeTab(tabId) {
        activeTabId = tabId; // Update active tab
        displayUserByRole(tabId);
        displayUsernameList(tabId);


        // Set the clicked tab as active
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(tabButton => {
            if (tabButton.getAttribute('data-tab-id') === tabId) {
                tabButton.classList.add('active');
            } else {
                tabButton.classList.remove('active');
            }
        });

    }

    displayUserByRole(activeTabId);
    displayUsernameList(activeTabId)
    </script>
    <script>
    // Get references to the modal and buttons
    var modal = document.getElementById("myModal");
    var openBtn = document.getElementById("openModalBtn");
    var closeBtn = document.getElementById("closeModalBtn");
    var addBtn = document.getElementById("addNewBtn");
    var titleWindowContainer = document.querySelector('.title-window-container'); // Tambahan

    // Open the modal when the button is clicked
    openBtn.onclick = function() {
        modal.style.display = "block";
    }

    // Close the modal when the close button is clicked
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    addBtn.addEventListener('click', function() {
        handleButtonClick();
        modal.style.display = "none";
    });

    // Close the modal when the user clicks anywhere outside the modal
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Function to change the title in the modal
    function changeModalTitle(tabId) {
        switch (tabId) {
            case 'admin':
                titleWindowContainer.textContent = 'Admin Role Management';
                break;
            case 'broadcaster':
                titleWindowContainer.textContent = 'Broadcaster Role Management';
                break;
            case 'member':
                titleWindowContainer.textContent = 'Member Role Management';
                break;
            default:
                titleWindowContainer.textContent = 'Role Management';
        }
    }

    // // Add event listeners to tab buttons
    // var tabButtons = document.querySelectorAll('.tab-button');
    // tabButtons.forEach(function(tabButton) {
    //     tabButton.addEventListener('click', function() {
    //         var tabId = tabButton.getAttribute('data-tab-id');
    //         changeModalTitle(tabId);
    //     });
    // });
    function handleButtonClick() {
        const checkedCheckboxes = document.querySelectorAll(
            '.user-list-window-container input[type="checkbox"]:checked');
        const selectedUsers = Array.from(checkedCheckboxes).map(checkbox => checkbox.value);
        console.log('Selected users:', selectedUsers);

        // You can perform further actions with the selected users here

        // Close the modal (you may want to replace this with your modal closing logic)
        modal.style.display = "none";
    }
    </script>
    <script>
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Hapus kelas 'active' dari semua tombol tab
            tabButtons.forEach(tabButton => {
                tabButton.classList.remove('active');
            });

            // Tambahkan kelas 'active' ke tombol yang diklik
            button.classList.add('active');
        });
        var tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(function(tabButton) {
            tabButton.addEventListener('click', function() {
                var tabId = tabButton.getAttribute('data-tab-id');
                changeModalTitle(tabId);
            });
        });
    });
    </script>
    <!-- <script>
    // ... Kode JavaScript lainnya

    // Function to change the title and user list in the modal
    function changeModalContent(tabId) {
        switch (tabId) {
            case 'admin':
                titleWindowContainer.textContent = 'Admin Role Management';
                userList.innerHTML = `
                    <h2>List of Admins</h2>
                    <ul>
                        <li>
                            <label for="admin1"><input type="checkbox" id="admin1" name="users[]" value="Admin 1"> Admin 1</label>
                        </li>
                        <li>
                            <label for="admin2"><input type="checkbox" id="admin2" name="users[]" value="Admin 2"> Admin 2</label>
                        </li>
                        <li>
                            <label for="admin3"><input type="checkbox" id="admin3" name="users[]" value="Admin 3"> Admin 3</label>
                        </li>
                    </ul>
                `;
                break;
            case 'broadcaster':
                titleWindowContainer.textContent = 'Broadcaster Role Management';
                userList.innerHTML = `
                    <h2>List of Broadcasters</h2>
                    <ul>
                        <li>
                            <label for="broadcaster1"><input type="checkbox" id="broadcaster1" name="users[]" value="Broadcaster 1"> Broadcaster 1</label>
                        </li>
                        <li>
                            <label for="broadcaster2"><input type="checkbox" id="broadcaster2" name="users[]" value="Broadcaster 2"> Broadcaster 2</label>
                        </li>
                        <li>
                            <label for="broadcaster3"><input type="checkbox" id="broadcaster3" name="users[]" value="Broadcaster 3"> Broadcaster 3</label>
                        </li>
                    </ul>
                `;
                break;
            case 'member':
                titleWindowContainer.textContent = 'Member Role Management';
                userList.innerHTML = `
                    <h2>List of Members</h2>
                    <ul>
                        <li>
                            <label for="member1"><input type="checkbox" id="member1" name="users[]" value="Member 1"> Member 1</label>
                        </li>
                        <li>
                            <label for="member2"><input type="checkbox" id="member2" name="users[]" value="Member 2"> Member 2</label>
                        </li>
                        <li>
                            <label for="member3"><input type="checkbox" id="member3" name="users[]" value="Member 3"> Member 3</label>
                        </li>
                    </ul>
                `;
                break;
            default:
                titleWindowContainer.textContent = 'Role Management';
                userList.innerHTML = ''; // Clear the user list
        }
    }

    // ... Kode event listener lainnya
    </script> -->
</body>

</html>

</body>

</html>