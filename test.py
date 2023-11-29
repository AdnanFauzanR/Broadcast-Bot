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

registration_step = {}
broadcast_step = {}
user_states = {}
incidents = {}
all_messages_broadcast_id = {}
chosen_witel = {}
broadcaster_id = {}
broadcast_id = {}
tickets = {}
last_status = {}
broadcasts = {}
user_id = {}
users_message = {}
index = {}

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
    if jabatan == 'HD ROC':
        data[user_id]['jabatan'] = jabatan
        data[user_id]['witel'] = 'ROC 7'
        data[user_id]['role'] = 'broadcaster'
        del registration_step[user_id]
        messages_id = []
        send_registration_request_to_admin(user_id, data[user_id])
        bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
        add_registration_request(user_id, data[user_id])
        del user_states[user_id]
    else:
        data[user_id]['jabatan'] = jabatan
        registration_step[user_id] += 1
        register('witel', user_id)

@bot.callback_query_handler(func=lambda call:call.data.startswith('witel_'))
def button_click(call):
    global messages_id
    user_id = call.message.chat.id
    message = call.message.message_id
    witel = call.data.split('_')[1]
    # bot.send_message(user_id, f'Anda memilih witel: {witel}')
    data[user_id]['witel'] = witel
    data[user_id]['role'] = 'member'
    del registration_step[user_id]
    bot.delete_message(user_id, message)
    messages_id = []
    bot.send_message(user_id, f'Anda memilih {witel}')
    send_registration_request_to_admin(user_id, data[user_id])
    bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
    add_registration_request(user_id, data[user_id])
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call:call.data.startswith('choose_'))
def button_click(call):
    user_id = call.message.chat.id
    message = call.message.message_id
    chosen_witel[user_id] = call.data.split('_')[1]
    bot.edit_message_text(template_message +f'\nAnda memilih broadcast ke witel *{chosen_witel[user_id]}*, Masukkan nomor tiket incident: \n\n'
                     +template_message, user_id, message)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith('response_'))
def response_broadcast_message(call):
    user_id = call.from_user.id
    broadcaster_id[user_id] = int(call.data.split('_')[1])
    broadcast_id[user_id] = int(call.data.split('_')[2])
    bot.send_message(user_id, 'Kirim pesan respons Anda: ')
    user_states[user_id] = 'response'

@bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast'))
def send_broadcast(call):
    user_id = call.from_user.id
    broadcast_type = call.data.split('_')[0]
    response = call.data.split('_')[1]
    if response == 'kirim':
        broadcast_message_id = call.data.split('_')[2]
        broadcast_message_index = int(call.data.split('_')[3])
        broadcast_message = broadcasts[user_id][broadcast_message_index]
        markup = types.InlineKeyboardMarkup()
        response_button = types.InlineKeyboardButton('Response', callback_data=f'response_{user_id}_{broadcast_message_id}')
        markup.add(response_button)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if broadcast_type == 'broadcast6':
            chat_ids = registered_users.distinct('chat_id',{'jabatan':{'$in':['HD Witel', 'HD ROC','TL']}, 'witel': chosen_witel[user_id]})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, broadcast_message, reply_markup=markup)
                bot.send_message(user_id, "Broadcast sent to registered users")
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
        elif broadcast_type == 'broadcast12':
            chat_ids = registered_users.distinct('chat_id',{'jabatan':{'$in':['SM']}, 'witel': chosen_witel[user_id]})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, broadcast_message, reply_markup=markup)
                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
        elif broadcast_type == 'broadcast36':
            chat_ids = registered_users.distinct('chat_id', {'witel': chosen_witel[user_id]})
            if chat_ids:
                for selected_registered_users_id in chat_ids:
                    # Send the broadcast message to each selected contact
                    if selected_registered_users_id  != user_id:
                        bot.send_message(selected_registered_users_id, broadcast_message, reply_markup=markup)
                # Confirm to the user who initiated the broadcast
                bot.send_message(user_id, "Broadcast sent to registered users")
            else:
                bot.send_message(user_id, "There are no registered users in the database.")
        else:
            bot.send_message(user_id, 'Broadcast type not found')

        del user_states[user_id]
        del broadcast_step[user_id]
        del chosen_witel[user_id]
        del broadcasts[user_id]
    elif response == 'tidak':
        del chosen_witel[user_id]
        del user_states[user_id]
        bot.edit_message_text('Pengiriman broadcast dibatalkan', user_id, call.message.message_id)

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

    del data

def broadcast_message(incident, chat_id, last_status):
    try:
        worksheet = client.open_by_key(spreadsheet_key).sheet1
        cell = worksheet.find(incident)

        if not cell:
            bot.send_message(chat_id, f'Data incident {incident} tidak ditemukan')
            return None

        row_data = worksheet.row_values(cell.row)
        segmen, layanan, witel, sto, start_time, ttr, no_tiket, sid, customer_name, headline = row_data[6], row_data[7], row_data[8], row_data[9], row_data[3], row_data[1], row_data[0], row_data[28], row_data[27], row_data[2]

        broadcaster_data = registered_users.find_one({'chat_id': chat_id})

        if broadcaster_data:
            nama = broadcaster_data.get('nama')
            jabatan = broadcaster_data.get('jabatan')
            broadcaster_witel = broadcaster_data.get('witel')
            message = f"""
Broadcast Ticketing
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
------------------------\n
{last_status}\n
------------------------\n
{nama} - IOC {jabatan} {broadcaster_witel}
                         """
            return message
        else:
            bot.send_message(chat_id, 'Data broadcaster tidak ada')
            return None
    except Exception as e:
        bot.send_message(chat_id, "Terjadi kesalahan saat mengakses data. Coba lagi")
        broadcast_step[chat_id] = 0
        return None

def send_registration_request_to_admin(user_id, data):
    admin_user_ids = get_admin_users()
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


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global user
    user = message.chat.id
    commands= ['/register', '/broadcast', '/broadcast6', '/broadcast12', '/broadcast36']
    user_id[message.chat.id] = message.chat.id
    users_message[user_id[message.chat.id]] = message.text
    message_error_bc = 'Anda tidak dapat mengirim broadcast'
    if users_message[message.chat.id] not in commands:
        # Check if the user is in broadcasting mode
        try:
            if user_states[user_id[message.chat.id]] in ['broadcast6', 'broadcast12', 'broadcast36']:
                if broadcast_step[user_id[message.chat.id]] == 0:
                    try:
                        if incidents[user_id[message.chat.id]]:
                            last_status[user_id[message.chat.id]].append(users_message[message.chat.id])
                    except KeyError:
                        incidents[user_id[message.chat.id]] = users_message[message.chat.id].split()
                        tickets[user_id[message.chat.id]] = 0
                        last_status[user_id[message.chat.id]] = []
                    bot.send_message(user_id[message.chat.id],
                                     f"Masukkan status terakhir tiket {incidents[user_id[message.chat.id]][tickets[user_id[message.chat.id]]]}:\nFormat: [Tanggal/Bulan/Tahun Jam/Menit] Status terakhir"
                                     )
                    tickets[user_id[message.chat.id]] += 1
                    if tickets[user_id[message.chat.id]] >= len(incidents[user_id[message.chat.id]]):
                        broadcast_step[user_id[message.chat.id]] += 1
                        del tickets[user_id[message.chat.id]]
                elif broadcast_step[user_id[message.chat.id]] == 1:
                    last_status[user_id[message.chat.id]].append(users_message[message.chat.id])
                    broadcasts[user_id[message.chat.id]] = [
                        broadcast_message(
                            incidents[user_id[message.chat.id]][i],
                            user_id[message.chat.id],
                            last_status[user_id[message.chat.id]][i]
                            ) for i in range(len(incidents[user_id[message.chat.id]]))
                        ]
                    index[user_id[message.chat.id]] = 0
                    for broadcast in broadcasts[user_id[message.chat.id]]:
                        if broadcast:
                            message_broadcast = bot.send_message(user_id[message.chat.id], broadcast)
                        else:
                            broadcasts[user_id[message.chat.id]].remove(broadcast)
                            if len(broadcasts[user_id[message.chat.id]]) == 0:
                                del last_status[user_id[message.chat.id]]
                                del incidents[user_id[message.chat.id]]
                                del broadcast_step[user_id[message.chat.id]]
                                del index[user_id[message.chat.id]]
                                return
                        # all_messages_broadcast_id[user_id[message.chat.id]].append(message_broadcast.message_id)

                        # broadcasts_id = "_".join(all_messages_broadcast_id)
                        # bot.send_message(user_id, broadcasts_id)
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        if user_states[user_id[message.chat.id]] == 'broadcast6':
                            item_kirim = types.InlineKeyboardButton('Kirim', callback_data=f'broadcast6_kirim_{message_broadcast.message_id}_{index[user_id[message.chat.id]]}')
                            item_tidak = types.InlineKeyboardButton('Tidak', callback_data='broadcast6_tidak')
                        elif user_states[user_id[message.chat.id]] == 'broadcast12':
                            item_kirim = types.InlineKeyboardButton('Kirim', callback_data=f'broadcast12_kirim_{message_broadcast.message_id}_{index[user_id[message.chat.id]]}')
                            item_tidak = types.InlineKeyboardButton('Tidak', callback_data='broadcast12_tidak')
                        elif user_states[user_id[message.chat.id]] == 'broadcast36':
                            item_kirim = types.InlineKeyboardButton('Kirim', callback_data=f'broadcast36_kirim_{message_broadcast.message_id}_{index[user_id[message.chat.id]]}')
                            item_tidak = types.InlineKeyboardButton('Tidak', callback_data='broadcast36_tidak')
                        markup.add(item_kirim, item_tidak)
                        bot.send_message(user_id[message.chat.id],'Apakah Anda ingin mengirim pesan broadcast ini?', reply_markup=markup)
                        index[user_id[message.chat.id]] += 1
                    del last_status[user_id[message.chat.id]]
                    del incidents[user_id[message.chat.id]]
                    del broadcast_step[user_id[message.chat.id]]
                    del index[user_id[message.chat.id]]
            elif user_states[user_id[message.chat.id]] == 'response':
                dataUser = registered_users.find_one({'chat_id': user_id[message.chat.id]})
                response_message = f'From {dataUser["nama"]}: {users_message[message.chat.id]}'
                bot.send_message(broadcaster_id[user_id[message.chat.id]], response_message, reply_to_message_id=broadcast_id[user_id[message.chat.id]])
                bot.send_message(user_id[message.chat.id], 'Response sent to broadcaster')
                del broadcast_id[message.chat.id]
                del broadcaster_id[message.chat.id]
                del user_states[user_id[message.chat.id]]
            elif user_states[user_id[message.chat.id]] == 'register':
                if form_features[registration_step[user_id[message.chat.id]]] == 'nik':
                    try:
                        users_message[message.chat.id] = int(users_message[message.chat.id])
                        data[user_id[message.chat.id]][form_features[registration_step[user_id[message.chat.id]]]] = users_message[message.chat.id]
                        registration_step[user_id[message.chat.id]] += 1
                    except ValueError:
                        bot.send_message(user_id[message.chat.id], 'Masukkan nik yang benar')
                elif form_features[registration_step[user_id[message.chat.id]]] == 'jabatan':
                    Jabatan = ['HD WITEL', 'HD ROC', 'TL', 'SM', 'MGR OPS', 'GM']
                    if users_message[message.chat.id] not in Jabatan:
                        bot.send_message(user_id[message.chat.id], 'Pilih Jabatan yang benar')
                    else:
                        data[user_id[message.chat.id]][form_features[registration_step[user_id[message.chat.id]]]] = users_message[message.chat.id]
                        registration_step[user_id[message.chat.id]] += 1
                elif form_features[registration_step[user_id[message.chat.id]]] == 'witel':
                    Witel = ['ROC 7', 'SULSEL', 'SULSELBAR', 'SULTRA', 'SULTENG', 'SULUT', 'GORONTALO', 'MALUKU', 'PAPUA', 'PAPUA BARAT']
                    if users_message[message.chat.id] not in Witel:
                        bot.send_message(user_id[message.chat.id], 'Pilih Witel yang benar')
                    else:
                        data[user_id[message.chat.id]][form_features[registration_step[user_id[message.chat.id]]]] = users_message[message.chat.id]
                        registration_step[user_id[message.chat.id]] += 1
                else:
                    data[user_id[message.chat.id]][form_features[registration_step[user_id[message.chat.id]]]] = users_message[message.chat.id]
                    registration_step[user_id[message.chat.id]] += 1

                if registration_step[user_id[message.chat.id]] < len(form_features):
                    register(form_features[registration_step[user_id[message.chat.id]]], user_id[message.chat.id])
                    user_states[user_id[message.chat.id]] = 'register'
                else:
                    del registration_step[user_id[message.chat.id]]
                    send_registration_request_to_admin(user_id[message.chat.id], data[user_id[message.chat.id]])
                    bot.send_message(user_id, 'Permintaan register Anda telah diajukan untuk persetujuan')
                    add_registration_request(user_id[message.chat.id], data[user_id[message.chat.id]])
                    del user_states[user_id[message.chat.id]]
        except Exception as e:
            bot.send_message(user_id[message.chat.id], f'Terjadi exception: {type(e).__name__}')
            bot.send_message(user_id[message.chat.id], f'Detail exception: {e}')
            bot.send_message(user_id[message.chat.id], "Invalid command. Please use a correct command.")
    else:
        if users_message[message.chat.id] == '/broadcast':
            try:
                if user_states[user_id[message.chat.id]]:
                    del user_states[user_id[message.chat.id]]
                    if incidents[user_id[message.chat.id]]:
                        del incidents[user_id[message.chat.id]]
            except Exception as e:
                    print(e)
            if (is_user_admin(user_id[message.chat.id])) or (is_user_broadcaster(user_id[message.chat.id])):
                user_states[user_id[message.chat.id]] = 'broadcast'
                bot.send_message(user_id[message.chat.id], "Enter your message for broadcasting: ")
            else:
                bot.send_message(user_id[message.chat.id], message_error_bc)
        elif users_message[message.chat.id] == '/broadcast6':
            try:
                if user_states[user_id[message.chat.id]]:
                    del user_states[user_id[message.chat.id]]
                    if incidents[user_id[message.chat.id]]:
                        del incidents[user_id[message.chat.id]]
            except Exception as e:
                    print(e)
            if (is_user_admin(user_id[message.chat.id])) or (is_user_broadcaster(user_id[message.chat.id])):
                user_states[user_id[message.chat.id]] = 'broadcast6'
                broadcast_step[user_id[message.chat.id]] = 0
                choose_witel_for_broadcast(user_id[message.chat.id])
            else:
                bot.send_message(user_id[message.chat.id], message_error_bc)
        elif users_message[message.chat.id] == '/broadcast12':
            try:
                if user_states[user_id[message.chat.id]]:
                    del user_states[user_id[message.chat.id]]
                    if incidents[user_id[message.chat.id]]:
                        del incidents[user_id[message.chat.id]]
            except Exception as e:
                    print(e)
            if (is_user_admin(user_id[message.chat.id])) or (is_user_broadcaster(user_id[message.chat.id])):
                user_states[user_id[message.chat.id]] = 'broadcast12'
                broadcast_step[user_id[message.chat.id]] = 0
                choose_witel_for_broadcast(user_id[message.chat.id])
            else:
                bot.send_message(user_id[message.chat.id], message_error_bc)
        elif users_message[message.chat.id] == '/broadcast36':
            try:
                if user_states[user_id[message.chat.id]]:
                    del user_states[user_id[message.chat.id]]
                    if incidents[user_id[message.chat.id]]:
                        del incidents[user_id[message.chat.id]]
            except Exception as e:
                    print(e)
            if (is_user_admin(user_id[message.chat.id])) or (is_user_broadcaster(user_id[message.chat.id])):
                user_states[user_id[message.chat.id]] = 'broadcast36'
                broadcast_step[user_id[message.chat.id]] = 0
                choose_witel_for_broadcast(user_id[message.chat.id])
            else:
                bot.send_message(user_id[message.chat.id], message_error_bc)
        elif users_message[message.chat.id] == '/register':
            try:
                if user_states[user_id[message.chat.id]]:
                    del user_states[user_id[message.chat.id]]
            except Exception as e:
                print(e)

            registration_step[user_id[message.chat.id]] = 0
            if is_user_registered(user_id[message.chat.id]):
                bot.send_message(user_id[message.chat.id], 'You are already registered')
            else:
                user_states[user_id[message.chat.id]] = 'register'
                data[user_id[message.chat.id]] = {}
                data[user_id[message.chat.id]]['username'] = message.from_user.username
                register('nama', user_id[message.chat.id])

        else:
            bot.send_message(user_id[message.chat.id], "Invalid command. Please use a correct command.")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            # bot.send_message(user, f'{type(e).__name__} last')
            print(f"Error: {str(e)}")
