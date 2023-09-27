import telebot
import pymongo
from telebot import types

# Initialize the bot
bot = telebot.TeleBot('6405987197:AAGxNvapAVDc-ny_rcrmri586Wau1NamR1A')

# Initialize the MongoDB client and database
mongo_client = pymongo.MongoClient('mongodb+srv://bot-user-db:M25nrDd9jQYfsMs2@clusterbot.xwfjecq.mongodb.net/?retryWrites=true&w=majority')
db = mongo_client['bot_user_db']

# Create collections for registered users and registration requests
registered_users = db['registered_users']
registration_requests = db['registration_requests']

# Admin user IDs

def is_user_admin(user_id):
    user = registered_users.find_one({'chat_id' : user_id})
    if user:
        return user.get('role') == 'admin'
    else:
        return False

def is_user_broadcaster(user_id):
    user = registered_users.find_one({'chat_id': user_id})
    if user:
        return user.get('role') == 'broadcaster'
    else:
        return False

def get_admin_users():
    admin_users = registered_users.find({'role' : 'admin'})
    if admin_users:
        admin_chat_ids = [user.get('chat_id') for user in admin_users]
    else:
        return 'No admin users'
    return admin_chat_ids

admin_user_ids = get_admin_users()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        if is_user_admin(user_id):
            bot.send_message(user_id, 'Welcome Admin')
        else:
            bot.send_message(user_id, 'Welcome to the bot! You are registered')
    elif is_registration_pending(user_id):
        bot.send_message(user_id, 'Your registration request is pending')
    else:
        bot.send_message(user_id, 'You are not registered. Use /register to request registration')

# Menambahkan langkah-langkah dalam proses registrasi
registration_steps = {
    'nik': 'Enter your NIK:',
    'jabatan': 'Enter your jabatan:',
    'witel': 'Enter your Witel:',
}

@bot.message_handler(commands=['register'])
def register(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name else ""

    if not is_user_registered(user_id) and not is_registration_pending(user_id):
        # Mulai proses registrasi dengan mengirim NIK pertama
        user_state[user_id] = {'step': 'nik', 'data': {}}
        bot.send_message(user_id, registration_steps['nik'])
    else:
        bot.send_message(user_id, 'Anda sudah terdaftar atau memiliki permintaan registrasi yang sedang diproses.')

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) and user_state[message.from_user.id]['step'] in registration_steps)
def continue_registration(message):
    user_id = message.from_user.id
    user_state_data = user_state[user_id]
    current_step = user_state_data['step']
    user_message = message.text

    # Simpan data yang diinput oleh pengguna ke dalam state
    user_state_data['data'][current_step] = user_message

    # Cek apakah masih ada langkah berikutnya
    next_step_index = list(registration_steps.keys()).index(current_step) + 1

    if next_step_index < len(registration_steps):
        next_step = list(registration_steps.keys())[next_step_index]
        user_state_data['step'] = next_step
        bot.send_message(user_id, registration_steps[next_step])
    else:
        # Registrasi selesai, proses data dan tambahkan permintaan registrasi
        add_registration_request(user_id, message.from_user.username, message.from_user.first_name,
                                 message.from_user.last_name, user_state_data['data']['nik'],
                                 user_state_data['data']['jabatan'], user_state_data['data']['witel'])
        send_registration_request_to_admin(user_id, message.from_user.username,
                                           message.from_user.first_name, message.from_user.last_name,
                                           user_state_data['data']['nik'], user_state_data['data']['jabatan'],
                                           user_state_data['data']['witel'])
        bot.send_message(user_id, 'Permintaan registrasi Anda telah diajukan untuk persetujuan.')

        # Hapus state registrasi
        del user_state[user_id]

@bot.message_handler(commands=['accessweb'])
def access_web(message):
    user_id = message.from_user.id

    if is_user_admin(user_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(
            text="Open Mini App",
            web_app = telebot.types.WebAppInfo(url="https://google.com")
        )
        keyboard.add(button)

        bot.send_message(
            message.chat.id,
            "Click the button to open the Mini App!",
            reply_markup=keyboard
        )
    else:
        bot.send_message(user_id, 'You are not allowed to access web')

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_registration(call):
    user_id = call.from_user.id
    if is_user_admin(user_id):
        request_id = int(call.data.split('_')[1])
        if is_registration_request(request_id):
            approve_user_registration(request_id)
            bot.send_message(request_id, 'Your registration request has been approved')
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, 'Registration request approved')
        else:
            bot.answer_callback_query(call.id, 'Already Approved')
    else:
        bot.answer_callback_query(call.id, 'You are not an admin')

def is_user_registered(chat_id):
    return bool(registered_users.find_one({'chat_id': chat_id}))

def is_registration_pending(chat_id):
    return bool(registration_requests.find_one({'chat_id': chat_id}))

def add_registration_request(chat_id, username, first_name, last_name, nik, jabatan, witel):
    registration_requests.insert_one({'chat_id': chat_id, 'username': username, 'first_name': first_name, 'last_name': last_name, 'nik' : nik, 'jabatan': jabatan, 'witel': witel, 'role': 'member'})

def send_registration_request_to_admin(user_id, username, first_name, last_name, nik, jabatan, witel):
    for admin_id in admin_user_ids:
        markup = types.InlineKeyboardMarkup()
        approve_button = types.InlineKeyboardButton('Approve', callback_data=f'approve_{user_id}')
        markup.add(approve_button)
        bot.send_message(admin_id,
                         f'A user wants to register with the following information:\n'
                         f'Username: {username}\n'
                         f'First Name: {first_name}\n'
                         f'Last Name: {last_name}\n'
                         f'NIK      : {nik}\n'
                         f'Jabatan  : {jabatan}\n'
                         f'Witel    : {witel}\n'
                         'Do you want to approve?',
                         reply_markup=markup)

def approve_user_registration(chat_id):
    user_data = registration_requests.find_one_and_delete({'chat_id': chat_id})
    if user_data:
        registered_users.insert_one(user_data)

def is_registration_request(chat_id):
    return bool(registration_requests.find_one({'chat_id': chat_id}))

# Define a dictionary to store the user's state
user_state = {}
user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = message.text

    if user_id in user_states:
        # Check if the user is in broadcasting mode
        if user_states[user_id] == 'broadcast':
            chat_ids = registered_users.distinct('chat_id')
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, user_message)

                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")


                # for admin_id in admin_user_ids:
                #     if admin_id != user_id:
                #         bot.send_message(admin_id, user_message)

            else:
                bot.send_message(user_id, "There are no registered users in the database.")
        else:
            bot.send_message(user_id, "Invalid command. Please use /broadcast to start broadcasting.")

        # Remove the user from the broadcast mode
        del user_states[user_id]
    else:
        # Check if the message is the "/broadcast" command
        if user_message.startswith('/broadcast'):
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # Set the user's state to broadcasting
                user_states[user_id] = 'broadcast'
                # Prompt the user to enter the message for broadcasting
                bot.send_message(user_id, "Enter your message for broadcasting: ")
            else:
                bot.send_message(user_id, 'You are not allowed to send broadcast')
        else:
            bot.send_message(user_id, "Invalid command. Please use /broadcast to start broadcasting.")



# Start polling
bot.polling()
