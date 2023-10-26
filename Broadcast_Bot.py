import telebot
import pymongo
from telebot import types

# Initialize the bot
bot = telebot.TeleBot('6405987197:AAGxNvapAVDc-ny_rcrmri586Wau1NamR1A')

# Initialize the MongoDB client and database
mongo_client = pymongo.MongoClient('mongodb+srv://telkomroc7:1hzi8GmOaVcm5YtA@cluster0.rjupjti.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp')
db = mongo_client['telkomroc7']

# Create collections for registered users and registration requests
registered_users = db['registered_users']
registration_requests = db['registration_requests']


template_message = "+-----------+-----------+---------------+---------+\n"
# Admin user IDs

def is_user_admin(user_id):
    user = registered_users.find_one({'chat_id' : user_id})
    if user:
        return user.get('role') == 'admin'
    else:
        return False

def is_user_broadcaster(user_id):
    user = registered_users.find_one({'chat_id' : user_id})
    if user:
        return user.get('role') == 'broadcaster'
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

def is_user_registered(chat_id):
    return bool(registered_users.find_one({'chat_id': chat_id}))

def is_registration_pending(chat_id):
    return bool(registration_requests.find_one({'chat_id': chat_id}))

admin_user_ids = get_admin_users()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        if is_user_admin(user_id):
            bot.send_message(user_id, 
                             "======================\n Broadcast Bot | ROC7\n======================\n\n" 
                             + 'Welcome Admin, Saya siap membantu Anda.\n\n' 
                             + template_message)
        elif is_user_broadcaster(user_id):
            bot.send_message(user_id, "======================\n Broadcast Bot | ROC7\n======================\n\n" 
                             + 'Welcome Admin, Saya siap membantu Anda.\n\n' 
                             + template_message)
        else:
            bot.send_message(user_id, "======================\n Broadcast Bot | ROC7\n======================\n\n" 
                             + 'Welcome to the bot!\n\n' 
                             + template_message)
    elif is_registration_pending(user_id):
        bot.send_message(user_id, "======================\n Broadcast Bot | ROC7\n======================\n\n" 
                             + 'Welcome to the bot! Registrasi anda pending, harap menghubungi admin untuk menerima registrasi anda\n\n' 
                             + template_message)
    else:
        bot.send_message(user_id, "======================\n Broadcast Bot | ROC7\n======================\n\n" 
                             + 'Welcome to the bot, anda belum terdaftar. Silahkan menggunakan /register untuk mendaftar!\n\n' 
                             + template_message)

# Menambahkan langkah-langkah dalam proses registrasi

form_features = ['nama', 'nik', 'jabatan', 'witel']

data = {}

registration_step = 0

def register(form, user_id, buttons=None, markup=None):
    if not is_user_registered(user_id):
        if form == 'nama':
            bot.send_message(user_id, "======================\n| Masukkan nama |\n======================\n\n")
        elif form == 'nik':
            bot.send_message(user_id, "======================\n| Masukkan NIK |\n======================\n\n")
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

            bot.send_message(user_id, "======================\n| Pilih Jabatan anda |\n======================\n\n" , reply_markup=markup)
        elif form == 'witel':
            if buttons is None:
                buttons = [
                    types.InlineKeyboardButton('ROC 7', callback_data=f'witel_ROC 7'),
                    types.InlineKeyboardButton('SULSEL', callback_data=f'witel_SULSEL')
                ], [
                    types.InlineKeyboardButton('SULSELBAR', callback_data=f'witel_SULSELBAR'),
                    types.InlineKeyboardButton('SULTRA', callback_data=f'witel_SULTRA')
                ], [
                    types.InlineKeyboardButton('SULTENG', callback_data=f'witel_SULTENG'),
                    types.InlineKeyboardButton('SULUT', callback_data=f'witel_SULUT')
                ], [
                    types.InlineKeyboardButton('GORONTALO', callback_data=f'witel_GORONTALO'),
                    types.InlineKeyboardButton('MALUKU', callback_data=f'witel_MALUKU')
                ], [
                    types.InlineKeyboardButton('PAPUA', callback_data=f'witel_PAPUA'),
                    types.InlineKeyboardButton('PAPUA BARAT', callback_data=f'witel_PAPUA BARAT')
                ]

            if markup is None:
                markup = types.InlineKeyboardMarkup(row_width=2)
                for btn_row in buttons:
                    markup.add(*btn_row)

            bot.send_message(user_id, "======================\n| Pilih Witel anda |\n======================\n\n", reply_markup=markup)
        else:
            bot.send_message(user_id, 'Input form tidak sesuai')
    else:
        bot.send_message(user_id, 'You are already registered')

def choose_witel_for_broadcast(user_id, buttons=None, markup=None):
    buttons = [
            types.InlineKeyboardButton('ROC 7', callback_data=f'choose_ROC 7'),
            types.InlineKeyboardButton('SULSEL', callback_data=f'choose_SULSEL')
        ], [
            types.InlineKeyboardButton('SULSELBAR', callback_data=f'choose_SULSELBAR'),
            types.InlineKeyboardButton('SULTRA', callback_data=f'choose_SULTRA')
        ], [
            types.InlineKeyboardButton('SULTENG', callback_data=f'choose_SULTENG'),
            types.InlineKeyboardButton('SULUT', callback_data=f'choose_SULUT')
        ], [
            types.InlineKeyboardButton('GORONTALO', callback_data=f'choose_GORONTALO'),
            types.InlineKeyboardButton('MALUKU', callback_data=f'choose_MALUKU')
        ], [
            types.InlineKeyboardButton('PAPUA', callback_data=f'choose_PAPUA'),
            types.InlineKeyboardButton('PAPUA BARAT', callback_data=f'choose_PAPUA BARAT')
        ]
    if markup is None:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for btn_row in buttons:
            markup.add(*btn_row)

        bot.send_message(user_id, "======================\n| Pilih Witel untuk dikirimkan broadcast |\n======================\n\n" +template_message, reply_markup=markup)
    else:
        bot.send_message(user_id, 'Input form tidak sesuai')


@bot.callback_query_handler(func=lambda call:call.data.startswith('jabatan_'))
def button_click(call):
    user_id = call.message.chat.id
    jabatan = call.data.split('_')[1]

    # bot.send_message(user_id, f'Anda memilih jabatan: {jabatan}')
    global registration_step
    if jabatan == 'HD ROC':
        data['jabatan'] = jabatan
        data['witel'] = 'ROC 7'
        data['role'] = 'broadcaster'
        registration_step = 0
        send_registration_request_to_admin(user_id, data)
        bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
        add_registration_request(user_id, data)
        del user_states[user_id]
    else:
        data['jabatan'] = jabatan
        registration_step += 1
        register('witel', user_id)

@bot.callback_query_handler(func=lambda call:call.data.startswith('witel_'))
def button_click(call):
    user_id = call.message.chat.id
    witel = call.data.split('_')[1]

    # bot.send_message(user_id, f'Anda memilih witel: {witel}')
    data['witel'] = witel
    data['role'] = 'member'
    global registration_step
    registration_step = 0
    send_registration_request_to_admin(user_id, data)
    bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
    add_registration_request(user_id, data)
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call:call.data.startswith('choose_'))
def button_click(call):
    user_id = call.message.chat.id
    global chosen_witel
    chosen_witel = call.data.split('_')[1]

    bot.send_message(user_id,   template_message +f'\nAnda memilih broadcast ke witel *{chosen_witel}*, Masukkan pesan Anda: \n\n'
                     +template_message, parse_mode= 'Markdown')

@bot.message_handler(commands=['accessweb'])
def access_web(message):
    user_id = message.from_user.id

    if is_user_admin(user_id):
        markup = types.InlineKeyboardMarkup()
        web_button = types.InlineKeyboardButton('Access Web', url=f'http://127.0.0.1:8000/authorized?chat_id={user_id}/')
        markup.add(web_button)
        bot.send_message(user_id, 'Click the button below to access the web:', reply_markup=markup)

    else:
        bot.send_message(user_id, 'You are not allowed to access web')

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_registration(call):
    user_id = call.from_user.id
    if is_user_admin(user_id):
        request_id = int(call.data.split('_')[1])
        if is_registration_request(request_id):
            approve_user_registration(request_id)
            bot.send_message(request_id, template_message+'\n\nPermintaan registrasi Anda telah diterima\n\n' + template_message)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, 'Registration request approved')
        else:
            bot.answer_callback_query(call.id, 'Already Approved')
    else:
        bot.answer_callback_query(call.id, 'You are not an admin')

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def reject_registration(call):
    user_id = call.from_user.id
    if is_user_admin(user_id):
        request_id = int(call.data.split('_')[1])
        if is_registration_request(request_id):
            registration_requests.find_one_and_delete({'chat_id': request_id})
            bot.send_message(request_id, template_message+'\n\nPermintaan registrasi Anda telah ditolak\n\n' + template_message)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, 'Registration request rejected')
        else:
            bot.answer_callback_query(call.id, 'Already Approved or Rejected')
    else:
        bot.answer_callback_query(call.id, 'You are not an admin')
        

def add_registration_request(chat_id, data):
    registration_requests.insert_one(
        {'chat_id': chat_id,
         'nama': data['nama'],
         'username': data['username'],
         'nik' : data['nik'],
         'jabatan': data['jabatan'],
         'witel': data['witel'],
         'role': data['role']
         })

    data = {}

def send_registration_request_to_admin(user_id, data):
    for admin_id in admin_user_ids:
        markup = types.InlineKeyboardMarkup(row_width=2)
        button = [
            types.InlineKeyboardButton('Approve', callback_data=f'approve_{user_id}'),
            types.InlineKeyboardButton('Reject', callback_data=f'reject_{user_id}')
            ]
            
        markup.add(*button)
        bot.send_message(admin_id, template_message +
                         f'\nA user wants to register with the following information:\n'
                         f'Nama: {data["nama"]}\n'
                         f'Chat Id: {user_id}\n'
                         f'Username: {data["username"]}\n'
                         f'NIK      : {data["nik"]}\n'
                         f'Jabatan  : {data["jabatan"]}\n'
                         f'Witel    : {data["witel"]}\n\n'
                         + template_message
                         + '\nDo you want to approve?',
                         reply_markup=markup)

def approve_user_registration(chat_id):
    user_data = registration_requests.find_one_and_delete({'chat_id': chat_id})
    if user_data:
        registered_users.insert_one(user_data)


def is_registration_request(chat_id):
    return bool(registration_requests.find_one({'chat_id': chat_id}))

# Define a dictionary to store the user's state
user_states = {}



@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = message.text
    global chosen_witel
    message_error_bc = 'Anda tidak dapat mengirim broadcast'

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
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
            del user_states[user_id]
        elif user_states[user_id] == 'broadcast6':
            chat_ids = registered_users.distinct('chat_id',{'jabatan':{'$in':['HD Witel', 'HD ROC','TL']}, 'witel': chosen_witel})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, user_message)

                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
                chosen_witel= {}
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
            del user_states[user_id]
        elif user_states[user_id] == 'broadcast12':
            chat_ids = registered_users.distinct('chat_id',{'jabatan':{'$in':['SM']}, 'witel': chosen_witel})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, user_message)

                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
                chosen_witel= {}
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
            del user_states[user_id]
        elif user_states[user_id] == 'broadcast36':
            chat_ids = registered_users.distinct('chat_id',{'jabatan':{'$in':['MGR OPS', 'GM']},'witel': chosen_witel})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, user_message)

                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
                chosen_witel= {}
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
            del user_states[user_id]
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
                Witel = ['ROC 7', 'SULSEL', 'SULSELBAR', 'SULTRA', 'SULTENG', 'SULUT', 'GORONTALO', 'MALUKU', 'PAPUA', 'PAPUA BARAT']
                if user_message not in Witel:
                    bot.send_message(user_id, 'Pilih Witel yang benar')
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
            bot.send_message(user_id, "Invalid command. Please use a correct command.")

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
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast6':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # Set the user's state to broadcasting
                user_states[user_id] = 'broadcast6'
                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast12':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # Set the user's state to broadcasting
                user_states[user_id] = 'broadcast12'
                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast36':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # Set the user's state to broadcasting
                user_states[user_id] = 'broadcast36'
                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/register':
            registration_step = 0
            user_states[user_id] = 'register'
            data['username'] = message.from_user.username
            register('nama', user_id)
        else:
            bot.send_message(user_id, "Invalid command. Please use a correct command.")



# Start polling
if __name__ == "__main__":
    bot.polling(none_stop=True)
