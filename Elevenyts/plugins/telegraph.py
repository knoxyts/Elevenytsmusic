import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Elevenyts import app
import requests


def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}

    try:
        with open(file_path, "rb") as f:
            files = {"fileToUpload": f}
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            return True, response.text.strip()
        else:
            return False, f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return False, str(e)


@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "❍ Please reply to a media file to upload."
        )

    media = message.reply_to_message
    file_size = 0

    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("❍ File size must be under 200MB.")

    text = await message.reply("❍ Processing...")

    async def progress(current, total):
        try:
            percent = current * 100 / total
            await text.edit_text(f"❍ Downloading... {percent:.1f}%")
        except:
            pass

    local_path = None

    try:
        # Download
        local_path = await media.download(progress=progress)

        await text.edit_text("❍ Uploading...")

        # Upload
        success, upload_path = upload_file(local_path)

        if success:
            await text.edit_text(
                f"❍ Upload Complete!\n\n<a href='{upload_path}'>🔗 Tap here to open</a>",
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔗 Open Link",
                                url=upload_path,
                            )
                        ]
                    ]
                ),
                disable_web_page_preview=True
            )
        else:
            await text.edit_text(
                f"❍ Upload Failed\n\nReason: {upload_path}"
            )

    except Exception as e:
        await text.edit_text(
            f"❍ Upload Failed\n\nReason: {str(e)}"
        )

    finally:
        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except:
                pass
