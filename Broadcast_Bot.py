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

form_features = ['nama', 'nik', 'jabatan', 'witel', 'wilayah']

data = {}

registration_step = 0

def register(form, user_id, buttons=None, markup=None):
    if form == 'nama':
        bot.send_message(user_id, 'Masukkan nama')
    elif form == 'nik':
        bot.send_message(user_id, 'Masukkan NIK')
    elif form == 'jabatan':
        if buttons is None:
            buttons = [
                types.InlineKeyboardButton('HD  Witel', callback_data=f'jabatan_HD Witel'),
                types.InlineKeyboardButton('HD ROC', callback_data=f'jabatan_HD ROC')
            ], [
                types.InlineKeyboardButton('TL', callback_data=f'jabatan_TL'),
                types.InlineKeyboardButton('SM', callback_data=f'jabatan_SM')
            ], [
                types.InlineKeyboardButton('GM', callback_data=f'jabatan_GM'),
                types.InlineKeyboardButton('MGR OPS', callback_data=f'jabatan_MGR OPS')
            ]

        if markup is None:
            markup = types.InlineKeyboardMarkup(row_width=2)
            for btn_row in buttons:
                markup.add(*btn_row)

        bot.send_message(user_id, 'Pilih jabatan Anda', reply_markup=markup)
    elif form == 'witel':
        if buttons is None:
            buttons = [
                types.InlineKeyboardButton('Witel 1', callback_data=f'witel_Witel 1'),
                types.InlineKeyboardButton('Witel 2', callback_data=f'witel_Witel 2')
            ], [
                types.InlineKeyboardButton('Witel 3', callback_data=f'witel_Witel 3'),
                types.InlineKeyboardButton('Witel 4', callback_data=f'witel_Witel 4')
            ], [
                types.InlineKeyboardButton('Witel 5', callback_data=f'witel_Witel 5'),
                types.InlineKeyboardButton('Witel 6', callback_data=f'witel_Witel 6')
            ], [
                types.InlineKeyboardButton('Witel 7', callback_data=f'witel_Witel 7'),
                types.InlineKeyboardButton('Witel 8', callback_data=f'witel_Witel 8')
            ]

        if markup is None:
            markup = types.InlineKeyboardMarkup(row_width=2)
            for btn_row in buttons:
                markup.add(*btn_row)

        bot.send_message(user_id, 'Pilih witel Anda', reply_markup=markup)
    elif form == 'wilayah':
        if buttons is None:
            buttons = [
                types.InlineKeyboardButton('Wilayah 1', callback_data=f'wilayah_Wilayah 1'),
                types.InlineKeyboardButton('Wilayah 2', callback_data=f'wilayah_Wilayah 2')
            ], [
                types.InlineKeyboardButton('Wilayah 3', callback_data=f'wilayah_Wilayah 3'),
                types.InlineKeyboardButton('Wilayah 4', callback_data=f'wilayah-Wilayah 4')
            ], [
                types.InlineKeyboardButton('Wilayah 5', callback_data=f'wilayah_Wilayah 5'),
                types.InlineKeyboardButton('Wilayah 6', callback_data=f'wilayah_Wilayah 6')
            ]

        if markup is None:
            markup = types.InlineKeyboardMarkup(row_width=2)
            for btn_row in buttons:
                markup.add(*btn_row)

        bot.send_message(user_id, 'Pilih wilayah', reply_markup=markup)
    else:
        bot.send_message(user_id, 'Input form tidak sesuai')


@bot.callback_query_handler(func=lambda call:call.data.startswith('jabatan_'))
def button_click(call):
    user_id = call.message.chat.id
    jabatan = call.data.split('_')[1]

    bot.send_message(user_id, f'Anda memilih jabatan: {jabatan}')
    data['jabatan'] = jabatan
    global registration_step
    registration_step += 1
    register('witel', user_id)

@bot.callback_query_handler(func=lambda call:call.data.startswith('witel_'))
def button_click(call):
    user_id = call.message.chat.id
    witel = call.data.split('_')[1]

    bot.send_message(user_id, f'Anda memilih witel: {witel}')
    data['witel'] = witel
    global registration_step
    registration_step += 1
    register('wilayah', user_id)

@bot.callback_query_handler(func=lambda call:call.data.startswith('wilayah_'))
def button_click(call):
    user_id = call.message.chat.id
    wilayah = call.data.split('_')[1]

    bot.send_message(user_id, f'Anda memilih wilayah: {wilayah}')
    data['wilayah'] = wilayah
    global registration_step
    registration_step = 0
    send_registration_request_to_admin(user_id, data)
    bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
    add_registration_request(user_id, data)
    del user_states[user_id]

# @bot.message_handler(commands=['register'])
# def register(message):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     first_name = message.from_user.first_name
#     last_name = message.from_user.last_name if message.from_user.last_name else ""

#     if not is_user_registered(user_id) and not is_registration_pending(user_id):
#         # Mulai proses registrasi dengan mengirim NIK pertama
#         user_state[user_id] = {'step': 'nik', 'data': {}}
#         bot.send_message(user_id, registration_steps['nik'])
#     else:
#         bot.send_message(user_id, 'Anda sudah terdaftar atau memiliki permintaan registrasi yang sedang diproses.')

# @bot.message_handler(func=lambda message: user_state.get(message.from_user.id) and user_state[message.from_user.id]['step'] in registration_steps)
# def continue_registration(message):
#     user_id = message.from_user.id
#     user_state_data = user_state[user_id]
#     current_step = user_state_data['step']
#     user_message = message.text

#     # Simpan data yang diinput oleh pengguna ke dalam state
#     user_state_data['data'][current_step] = user_message

#     # Cek apakah masih ada langkah berikutnya
#     next_step_index = list(registration_steps.keys()).index(current_step) + 1

#     if next_step_index < len(registration_steps):
#         next_step = list(registration_steps.keys())[next_step_index]
#         user_state_data['step'] = next_step
#         bot.send_message(user_id, registration_steps[next_step])
#     else:
#         # Registrasi selesai, proses data dan tambahkan permintaan registrasi
#         add_registration_request(user_id, message.from_user.username, message.from_user.first_name,
#                                  message.from_user.last_name, user_state_data['data']['nik'],
#                                  user_state_data['data']['jabatan'], user_state_data['data']['witel'])
#         send_registration_request_to_admin(user_id, message.from_user.username,
#                                            message.from_user.first_name, message.from_user.last_name,
#                                            user_state_data['data']['nik'], user_state_data['data']['jabatan'],
#                                            user_state_data['data']['witel'])
#         bot.send_message(user_id, 'Permintaan registrasi Anda telah diajukan untuk persetujuan.')

#         # Hapus state registrasi
#         del user_state[user_id]

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

def add_registration_request(chat_id, data):
    registration_requests.insert_one(
        {'chat_id': chat_id,
         'nama': data['nama'],
         'username': data['username'],
         'nik' : data['nik'],
         'jabatan': data['jabatan'],
         'witel': data['witel'],
         'wilayah': data['wilayah'],
         'role': 'member'
         })

    data = {}

def send_registration_request_to_admin(user_id, data):
    for admin_id in admin_user_ids:
        markup = types.InlineKeyboardMarkup()
        approve_button = types.InlineKeyboardButton('Approve', callback_data=f'approve_{user_id}')
        markup.add(approve_button)
        bot.send_message(admin_id,
                         f'A user wants to register with the following information:\n'
                         f'Nama: {data["nama"]}\n'
                         f'Chat Id: {user_id}\n'
                         f'Username: {data["username"]}\n'
                         f'NIK      : {data["nik"]}\n'
                         f'Jabatan  : {data["jabatan"]}\n'
                         f'Witel    : {data["witel"]}\n'
                         f'Wilayah    : {data["wilayah"]}\n'
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
                del user_states[user_id]


                # for admin_id in admin_user_ids:
                #     if admin_id != user_id:
                #         bot.send_message(admin_id, user_message)

            else:
                bot.send_message(user_id, "There are no registered users in the database.")
        elif user_states[user_id] == 'register':
            global registration_step
            if form_features[registration_step] == 'nik':
                try:
                    user_message = int(user_message)
                    data[form_features[registration_step]] = user_message
                    registration_step += 1
                except ValueError:
                    bot.send_message(user_id, 'Masukkan nik yang benar')
            elif form_features[registration_step] == 'jabatan':
                Jabatan = ['HD WITEL', 'HD ROC', 'TL', 'SM', 'MGR OPS', 'GM']
                if user_message not in Jabatan:
                    bot.send_message(user_id, 'Pilih Jabatan yang benar')
                else:
                    data[form_features[registration_step]] = user_message
                    registration_step += 1
            elif form_features[registration_step] == 'witel':
                Witel = ['Witel 1', 'Witel 2', 'Witel 3', 'Witel 4', 'Witel 5', 'Witel 6', 'Witel 7', 'Witel 8']
                if user_message not in Witel:
                    bot.send_message(user_id, 'Pilih Witel yang benar')
                else:
                    data[form_features[registration_step]] = user_message
                    registration_step += 1
            elif form_features[registration_step] == 'wilayah':
                Wilayah = ['Wilayah 1', 'Wilayah 2', 'Wilayah 3', 'Wilayah 4', 'Wilayah 5', 'Wilayah 6']
                if user_message not in Wilayah:
                    bot.send_message(user_id, 'Pilih wilayah yang benar')
                else:
                    data[form_features[registration_step]] = user_message
                    registration_step += 1
            else:
                data[form_features[registration_step]] = user_message
                registration_step += 1

            if registration_step < len(form_features):
                register(form_features[registration_step], user_id)
                user_states[user_id] = 'register'
            else:
                registration_step = 0
                send_registration_request_to_admin(user_id, data)
                bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
                add_registration_request(user_id, data)
                del user_states[user_id]
        else:
            bot.send_message(user_id, "Invalid command. Please use /broadcast to start broadcasting.")

        # Remove the user from the broadcast mode

    else:
        # Check if the message is the "/broadcast" command
        if user_message == '/broadcast':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # Set the user's state to broadcasting
                user_states[user_id] = 'broadcast'
                # Prompt the user to enter the message for broadcasting
                bot.send_message(user_id, "Enter your message for broadcasting: ")
            else:
                bot.send_message(user_id, 'You are not allowed to send broadcast')
        elif user_message == '/register':
            registration_step = 0
            user_states[user_id] = 'register'
            data['username'] = message.from_user.username
            register('nama', user_id)
        else:
            bot.send_message(user_id, "Invalid command. Please use /broadcast to start broadcasting.")



# Start polling
bot.polling()
