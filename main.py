import asyncio
import time

import requests
from pyrogram import Client
from fastapi import FastAPI
import telebot

app = FastAPI()
api_id = 25910820
api_hash = "10a2c01ca3d4c79a6c66a486f15af986"

client = Client("test_account", api_id=api_id, api_hash=api_hash)

@app.get('/')
def home():
    return {"key": "Hello"}

@app.get("/sign_in")
async def login_get(phone: str):
    try:
        resp = await client.send_code(phone)
        return {"phone_code_hash": resp.phone_code_hash}
    except Exception as con_err:
        return {"error": con_err.__str__()}


@app.get("/sign_in_code")
async def login_get(phone: str, phone_hash: str, code: str):
    try:
        await client.sign_in(phone_number=phone, phone_code_hash=phone_hash, phone_code=code)
        return {"success": "Hello World"}
    except Exception as con_err:
        return {"error": con_err.__str__()}


@app.get("/logout")
async def logout():
    try:
        await client.log_out()
        return {"success": "logout"}
    except Exception as con_err:
        return {"error": con_err.__str__()}

# to'g'ri ishlayotgan kod
@app.get("/rassilka/{item_id}")
async def rassilka(item_id: int):
    try:
        await client.start()  # Telegram clientni ishga tushirish

        # MetalDesk API'dan ma'lumot olish
        metaldesk = requests.get(f'http://api.metaldesk.uz/api/telegrams/{item_id}')

        if metaldesk.json()['success']:
            photo_url = metaldesk.json()['data']['photo']
            caption = metaldesk.json()['data']['text']
            groups = metaldesk.json()['data']['groups']

            # Matnni qismlarga ajratish funksiyasi
            def split_text_custom(text):
   
                parts = []
                lengths = [1031, 589, 596, 629]  # Bo'lak uzunliklari ketma-ketligi

                # Bo'laklarga ajratish
                for length in lengths:
                    if len(text) > length:
                        parts.append(text[:length])  # Bo'lakni ajratamiz
                        text = text[length:]        # Qolgan qismni saqlaymiz
                    else:
                        break  # Agar matn bo'lakdan qisqa bo'lsa, tsiklni to'xtatamiz

                # Oxirgi qolgan qismni qo'shamiz
                if text:
                    parts.append(text)

                return parts

            # Captionni bo'lish
            caption_parts = split_text_custom(caption)

            success_list = []
            failed_list = []
            deleted_list = []

            try:
                # Rasmni vaqtinchalik fayl sifatida yuklab olish
                response = requests.get(photo_url, stream=True)
                if response.status_code == 200:
                    with open("temp_photo.jpg", "wb") as temp_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            temp_file.write(chunk)

                    i = 0  # Guruhlar o'rtasida sanash uchun hisoblagich

                    for group in groups:
                        group_link = group['link']
                        group_name = group.get('name', "Noma'lum guruh")

                        group_success = True
                        for part in caption_parts:
                            try:
                                resp = await client.send_photo(
                                    chat_id=group_link,  # Guruh havolasi
                                    photo="temp_photo.jpg",  # Rasm fayl yo'li
                                    caption=part  # Bo'lingan matn qismi
                                )
                                print(f"Habar yuborildi: {group_link} -> {part}")
                            except Exception as ex:
                                print(f"Xato yuborishda: {group_link} -> {str(ex)}")
                                group_success = False

                            time.sleep(1)  # Xabarlar o'rtasida qisqa kutish

                        if group_success:
                            success_list.append(group_name)
                        else:
                            failed_list.append(group_name)

                        i += 1
                        if i == 19:
                            i = 0
                            await asyncio.sleep(20)  # 20 soniya pauza

                    # Hisobotni shakllantirish
                    success_text = "\n".join([f"\u2714 {name}" for name in success_list])
                    failed_text = "\n".join([f"\u274C {name}" for name in failed_list])

                    report_message = (
                        f"<b>Guruhlar bo'yicha xabar tarqatish</b>\n"
                        f"<b>Jami guruhlar:</b> {len(groups)}\n"
                        f"<b>Muvaffaqiyatli:</b> {len(success_list)}\n"
                        f"<b>Muvaffaqiyatsiz:</b> {len(failed_list)}\n"
                        f"===================\n"
                        f"<b>Muvaffaqiyatli guruhlar:</b>\n{success_text}\n\n"
                        f"<b>Muvaffaqiyatsiz guruhlar:</b>\n{failed_text}\n"
                    )
                    # Hisobotni yuborish
                    print(report_message)
                    # bot = TeleBot("5415557799:AAGPDjywgbz-JBLaXnYugPn4oQnNJXRrFeU")
                    # bot.parse_mode = 'html'
                    # bot.send_message(-1002183703081, 'test12345')
                    bot = telebot.TeleBot("5415557799:AAGPDjywgbz-JBLaXnYugPn4oQnNJXRrFeU", parse_mode='html')
                    try:
                        print("Sending message to Telegram...")
                        bot.send_message(-1002183703081, report_message)
                        print("Message sent successfully")
                    except Exception as e:
                        print(f"Error sending message: {e}")

                    return {"success": "Message sent successfully to all groups"}
                else:
                    return {"error": f"Failed to download photo. Status code: {response.status_code}"}
            except Exception as ex:
                return {"error": f"Failed to send message: {str(ex)}"}
            finally:
                # Faylni o'chirish
                if os.path.exists("temp_photo.jpg"):
                    os.remove("temp_photo.jpg")
        else:
            return {"error": "API response did not indicate success"}

    except Exception as ex:
        return {"error": ex.__str__()}

    

# bu ishlagan kod

# @app.get("/rassilka/{item_id}")
# async def rassilka(item_id: int):
#     try:
#         await client.start()  # Telegram clientni ishga tushirish

#         # MetalDesk API'dan ma'lumot olish
#         metaldesk = requests.get(f'http://api.metaldesk.uz/api/telegrams/{item_id}')

#         if metaldesk.json()['success']:
#             photo_url = metaldesk.json()['data']['photo']
#             caption = metaldesk.json()['data']['text']

#             # Matnni qismlarga ajratish funksiyasi
#             # def split_text_custom(text):
#             #     parts = []
#             #     if len(text) <= 1024:
#             #         parts.append(text)
#             #     else:
#             #         parts.append(text[:1031])  # Birinchi qism 1024 belgi
#             #         text = text[1031:]
#             #         while len(text) > 1031:
#             #             parts.append(text[:589])  # Keyingi qismlar 1000 belgi
#             #             text = text[1024:]
#             #         while len(text) > 1024:
#             #             parts.append(text[:589])  # Keyingi qismlar 1000 belgi
#             #             text = text[889:]
#             #         if text:
#             #             parts.append(text)  # Oxirgi qism (agar qolgan bo'lsa)
#             #     return parts

#             def split_text_custom(text):
   
#                 parts = []
#                 lengths = [1031, 589, 596, 629]  # Bo'lak uzunliklari ketma-ketligi

#                 # Bo'laklarga ajratish
#                 for length in lengths:
#                     if len(text) > length:
#                         parts.append(text[:length])  # Bo'lakni ajratamiz
#                         text = text[length:]        # Qolgan qismni saqlaymiz
#                     else:
#                         break  # Agar matn bo'lakdan qisqa bo'lsa, tsiklni to'xtatamiz

#                 # Oxirgi qolgan qismni qo'shamiz
#                 if text:
#                     parts.append(text)

#                 return parts

#             # Captionni bo'lish
#             caption_parts = split_text_custom(caption)

#             try:
#                 # Rasmni vaqtinchalik fayl sifatida yuklab olish
#                 response = requests.get(photo_url, stream=True)
#                 if response.status_code == 200:
#                     with open("temp_photo.jpg", "wb") as temp_file:
#                         for chunk in response.iter_content(chunk_size=8192):
#                             temp_file.write(chunk)

#                     # Faylni yuborish va barcha qismlarni yuborish
#                     for part in caption_parts:
#                         resp = await client.send_photo(
#                             chat_id="@FeruzbekEastMetProkat",  # Kanal yoki foydalanuvchi
#                             photo="temp_photo.jpg",  # Rasm fayl yo'li
#                             caption=part  # Bo'lingan matn qismi
#                         )
#                         print(f"Habar yuborildi: {part}")

#                     return {"success": "Message sent successfully with multiple parts"}
#                 else:
#                     return {"error": f"Failed to download photo. Status code: {response.status_code}"}
#             except Exception as ex:
#                 return {"error": f"Failed to send message: {str(ex)}"}
#             finally:
#                 # Faylni o'chirish
#                 import os
#                 if os.path.exists("temp_photo.jpg"):
#                     os.remove("temp_photo.jpg")
#         else:
#             return {"error": "API response did not indicate success"}

#     except Exception as ex:
#         return {"error": ex.__str__()}



                   

# bu eski kod
        
        # if metaldesk.json()['success']:
        #     for itemcha in metaldesk.json()['data']['groups']:
        #         i = i + 1
        #         try:
        #             resp = await client.send_message(itemcha['link'], text=metaldesk.json()['data']['text'])
        #             resplist.append(resp)
        #         except Exception as ex:
        #             b.append('▪' + itemcha['link'])

        #         time.sleep(1)
        #         if i == 19:
        #             i = 0
        #             await asyncio.sleep(20)
        # await asyncio.sleep(20)


    #     b_text = ""
    #     s_text = ""
    #     for resp in resplist:
    #         await asyncio.sleep(5)
    #         message = await client.get_messages(resp.chat.id, resp.id)
    #         if message.empty:
    #             s.append('🔸' + resp.chat.username)
    #         else:
    #             a.append("В группу {1} {2} отправлено :{0}".format(resp.link, itemcha['name'],
    #                                                                'успешно' if resp.id > 0 else 'не'))
    #     for b_t in b:
    #         b_text = b_text + b_t + "\n"
    #     for s_t in s:
    #         s_text = s_text + s_t + "\n"

    #     bot_message = "<b>Рассылка в группах по металлу</b>\n<b>Всего:</b>\t\t{0}\n<b>Успешно:</b>\t\t{1}\n<b>Удалено:</b>\t\t{4}\n=======================\n{5}\n\n<b>Не отправлено:</b>\t\t{2}\n=======================\n{3}\n\n".format(
    #         len(metaldesk.json()['data']['groups']), len(a), len(b), b_text, len(s), s_text)
    #     bot = telebot.TeleBot("5415557799:AAGPDjywgbz-JBLaXnYugPn4oQnNJXRrFeU")
    #     bot.parse_mode = 'html'  # Bu yerda parse_mode ni qo'lda o'rnatamiz
    #     bot.send_message(-1001821396067, bot_message)
    #     return {"success": "success"}
    # except Exception as ex:
    #     return {"error": ex.__str__()}


@app.get("/start")
async def start():
    try:
        await client.connect()
        return {"success": "started"}
    except Exception as con_err:
        return {"error": con_err.__str__()}

@app.get("/test")
async def start():
    try:
        await client.send_message('lipeapp', 'hello world')
        return {"success": "started"}
    except Exception as con_err:
        return {"error": con_err.__str__()}


@app.get("/stop")
async def stop():
    try:
        await client.disconnect()
        return {"success": "stopped"}
    except Exception as con_err:
        return {"error": con_err.__str__()}


