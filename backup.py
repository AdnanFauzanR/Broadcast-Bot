import telebot
import pymongo
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload
import openpyxl
import gspread.exceptions as exceptions

# Initialize the bot
bot = telebot.TeleBot('6405987197:AAGxNvapAVDc-ny_rcrmri586Wau1NamR1A')

# Initialize the MongoDB client and database
mongo_client = pymongo.MongoClient('mongodb+srv://telkomroc7:1hzi8GmOaVcm5YtA@cluster0.rjupjti.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp')
db = mongo_client['telkomroc7']

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('broadcast-bot-405401-1b87de6e7576.json', scope)
client = gspread.authorize(credentials)
spreadsheet_key = '11SDJGATOVASTo76qmXacYuVVq2MuF99vow_plA5yCSM'
worksheet = client.open_by_key(spreadsheet_key).sheet1


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

@bot.message_handler(commands=['updatedata'])
def update_handler(message):
    chat_id = message.chat.id

    markup = types.InlineKeyboardMarkup(row_width=2)
    item_yes = types.InlineKeyboardButton('Yes', callback_data='update_yes')
    item_no = types.InlineKeyboardButton('No', callback_data='update_no')
    markup.add(item_yes, item_no)

    bot.send_message(chat_id, 'Upload file excel untuk mengupdate data', reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id

    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_content = bot.download_file(file_info.file_path)

        wb = openpyxl.load_workbook(filename=BytesIO(file_content))
        sheet = wb.active

        excel_data = []
        for row in sheet.iter_rows(values_only=True):
            excel_data.append(row)

        worksheet = client.open_by_key(spreadsheet_key).sheet1
        worksheet.clear()
        worksheet.insert_rows(excel_data)

        bot.send_message(chat_id, 'Data berhasil diupdate')
    except Exception as e:
        print(e)
        bot.send_message(chat_id, 'Terjadi kesalahan saat mengupdate data. Coba lagi')
        bot.send_message(chat_id, e)

@bot.callback_query_handler(func=lambda call:call.data.startswith('update_'))
def handle_update_button(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    answer = call.data.split('_')[1]

    if answer == 'yes':
        bot.send_message(chat_id, 'Silahkan unggah file excel Anda')
    elif answer == 'no':
        bot.edit_message_text('Pengunggahan dibatalkan', chat_id, message_id)


# def download_and_save_to_sheets():
#     excel_url = 'https://oss-incident.telkom.co.id/jw/web/json/app/ticketIncidentService/42/plugin/org.joget.marketplace.DownloadCsvOrExcelDatalistAction/service?uniqueId=74c9ea1f-3110-4a26-90d5-81d6ce50c628&filename=report.xlsx'

#     response = requests.get(url=excel_url)

#     content = response.content
#     worksheet.clear()
#     client.import_csv(spreadsheet_key, content)

# @bot.message_handler(commands=['updatedata'])
# def updateData(message):
#     download_and_save_to_sheets()
#     bot.reply_to(message, 'Data telah diperbarui')
# Menambahkan langkah-langkah dalam proses registrasi

form_features = ['nama', 'nik', 'jabatan', 'witel']

data = {}

registration_step = 0

def register(form, user_id, buttons=None, markup=None):
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
    global messages_id
    user_id = call.message.chat.id
    message = call.message.message_id
    jabatan = call.data.split('_')[1]
    # bot.send_message(user_id, f'Anda memilih jabatan: {jabatan}')
    bot.delete_message(user_id, message)
    bot.send_message(user_id, f'Anda memilih {jabatan}')
    global registration_step
    if jabatan == 'HD ROC':
        data['jabatan'] = jabatan
        data['witel'] = 'ROC 7'
        data['role'] = 'broadcaster'
        registration_step = 0
        messages_id = []
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
    global messages_id
    user_id = call.message.chat.id
    message = call.message.message_id
    witel = call.data.split('_')[1]
    # bot.send_message(user_id, f'Anda memilih witel: {witel}')
    data['witel'] = witel
    data['role'] = 'member'
    global registration_step
    registration_step = 0
    bot.delete_message(user_id, message)
    messages_id = []
    bot.send_message(user_id, f'Anda memilih {witel}')
    send_registration_request_to_admin(user_id, data)
    bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
    add_registration_request(user_id, data)
    del user_states[user_id]


chosen_witel = 0
@bot.callback_query_handler(func=lambda call:call.data.startswith('choose_'))
def button_click(call):
    global messages_id
    global chosen_witel
    user_id = call.message.chat.id
    message = call.message.message_id
    chosen_witel = call.data.split('_')[1]
    bot.delete_message(user_id, message, timeout=10)
    bot.send_message(user_id, f'Anda memilih {chosen_witel}')
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

broadcaster_id = 0
broadcast_id = 0

@bot.callback_query_handler(func=lambda call: call.data.startswith('response_'))
def response_broadcast_message(call):
    user_id = call.from_user.id
    global broadcaster_id
    global broadcast_id
    broadcaster_id = int(call.data.split('_')[1])
    broadcast_id = int(call.data.split('_')[2])
    bot.send_message(user_id, 'Kirim pesan respons Anda')
    user_states[user_id] = 'response'

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

def broadcast_message(incident, chat_id):
    try:
        worksheet = client.open_by_key(spreadsheet_key).sheet1
        cell = worksheet.find(incident)

        row_data = worksheet.row_values(cell.row)
        segmen, layanan, witel, sto, start_time, ttr, no_tiket, sid, customer_name, headline = row_data[6], row_data[7], row_data[8], row_data[9], row_data[3], row_data[1], row_data[0], row_data[28], row_data[27], row_data[2]

        bot.send_message(chat_id,f"""
Kepada Teknisi
Status: OPEN
Segmen Customer: {segmen}
Layanan: {layanan}
Witel: {witel}
STO: {sto}
Start Time: {start_time}
TTR Aktif: {ttr}
No Tiket: {no_tiket}
SID: {sid}
Customer Name: {customer_name}
Headline: {headline}
                         """)
    except exceptions.CellNotFound:
        bot.send_message(chat_id, f"Tidak ada data dengan nilai incident {incident}. Coba lagi.")
    except Exception as e:
        bot.send_message(chat_id, "Terjadi kesalahan saat mengakses data. Coba lagi")

@bot.message_handler(func=lambda message: message.text.startswith('test'))
def test(message):
    chat_id = message.chat.id
    incident = message.text.split(' ')[1]
    broadcast_message(incident, chat_id)

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

def remove_message(messages, user_id):
    for message in messages:
        bot.delete_message(user_id, message)
    messages = []
    return messages

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global chosen_witel
    commands= ['/register', '/broadcast', '/broadcast6', '/broadcast12', '/broadcast36']
    user_id = message.chat.id
    broadcast_message_id = message.message_id
    user_message = message.text
    message_error_bc = 'Anda tidak dapat mengirim broadcast'
    markup = types.InlineKeyboardMarkup()
    response_button = types.InlineKeyboardButton('Response', callback_data=f'response_{user_id}_{broadcast_message_id}')
    markup.add(response_button)

    if user_message not in commands:
        # Check if the user is in broadcasting mode
        if user_states[user_id] == 'broadcast':
            chat_ids = registered_users.distinct('chat_id')
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:

                        bot.send_message(selected_registered_users_id, user_message, reply_markup=markup)
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
                        bot.send_message(selected_registered_users_id, user_message, reply_markup=markup)

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
                        bot.send_message(selected_registered_users_id, user_message, reply_markup=markup)

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
                        bot.send_message(selected_registered_users_id, user_message, reply_markup=markup)

                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
                chosen_witel= {}
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
            del user_states[user_id]
        elif user_states[user_id] == 'response':
            global broadcaster_id, broadcast_id
            dataUser = registered_users.find_one({'chat_id': user_id})
            response_message = f'From {dataUser["nama"]}: {user_message}'
            bot.send_message(broadcaster_id, response_message, reply_to_message_id=broadcast_id)
            bot.send_message(user_id, 'Response sent to broadcaster')
            broadcaster_id = 0
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
                # if not user_states:
                #     user_states[user_id] = 'broadcast'
                # else:
                #     del user_states[user_id]

                if user_states:
                    del user_states[user_id]

                user_states[user_id] = 'broadcast'

                # Prompt the user to enter the message for broadcasting
                bot.send_message(user_id, "Enter your message for broadcasting: ")
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast6':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # if not user_states:
                #     user_states[user_id] = 'broadcast6'
                # else:
                #     del user_states[user_id]

                if user_states:
                    del user_states[user_id]

                user_states[user_id] = 'broadcast6'

                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast12':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # if not user_states:
                #     user_states[user_id] = 'broadcast12'
                # else:
                #     del user_states[user_id]
                if user_states:
                    del user_states[user_id]

                user_states[user_id] = 'broadcast12'

                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/broadcast36':
            if (is_user_admin(user_id)) or (is_user_broadcaster(user_id)):
                # if not user_states:
                #     user_states[user_id] = 'broadcast36'
                # else:
                #     del user_states[user_id]

                if user_states:
                    del user_states[user_id]

                user_states[user_id] = 'broadcast36'
                # Set the user's state to broadcasting

                choose_witel_for_broadcast(user_id)
            else:
                bot.send_message(user_id, message_error_bc)
        elif user_message == '/register':
            registration_step = 0
            # if not user_states:
            #     user_states[user_id] = 'register'
            # else:
            #     del user_states[user_id]

            if user_states:
                del user_states[user_id]

            user_states[user_id] = 'register'

            if is_user_registered(user_id):
                bot.send_message(user_id, 'You are already registered')
            else:
                user_states[user_id] = 'register'
                data['username'] = message.from_user.username
                register('nama', user_id)

        else:
            bot.send_message(user_id, "Invalid command. Please use a correct command.")



# Start polling
if __name__ == "__main__":
    bot.polling(none_stop=True)
