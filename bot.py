import os
import re
# Importamos la nueva librería que sí funciona
import PyPDF2
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ▼▼▼ ¡OJO! ¡RECUERDA CAMBIAR ESTO POR TU TOKEN REAL! ▼▼▼
TOKEN = "8235897302:AAHWEYr70BmpW1g6EF5hAlvHZxfkL-rUMNQ"

def procesar_pdf(ruta_pdf):
    try:
        texto_completo = ""
        # Usamos PyPDF2 en lugar de las otras librerías
        with open(ruta_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texto_completo += page.extract_text() + "\n"
        
        # Buscamos datos simples como ejemplo
        nit_match = re.search(r"NIT\s*(\d+)", texto_completo, re.IGNORECASE)
        di_match = re.search(r"(DI-\d{4}-\d{3}-\d+)", texto_completo)

        datos_extraidos = {
            'Número Declaración': di_match.group(1) if di_match else 'No encontrado',
            'NIT Importador': nit_match.group(1) if nit_match else 'No encontrado',
        }
        return datos_extraidos
    except Exception as e:
        print(f"Error procesando PDF: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy tu bot extractor. Envíame un archivo PDF para analizarlo.")

async def manejar_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Analizando PDF...")
    try:
        archivo_id = update.message.document.file_id
        archivo = await context.bot.get_file(archivo_id)
        ruta_temporal = f"temp_{archivo_id}.pdf"
        await archivo.download_to_drive(ruta_temporal)

        datos = procesar_pdf(ruta_temporal)

        if datos:
            respuesta = "✅ ¡Datos extraídos!\n\n"
            for campo, valor in datos.items():
                respuesta += f"*{campo}:* {valor}\n"
            await update.message.reply_text(respuesta, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ No pude encontrar datos en este archivo.")
    except Exception as e:
        print(f"Error general: {e}")
        await update.message.reply_text("Ocurrió un error inesperado.")
    finally:
        if 'ruta_temporal' in locals() and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)

def main():
    print("🚀 Encendiendo bot...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.PDF, manejar_documento))
    print("✅ Bot en línea.")
    application.run_polling()

if __name__ == "__main__":
    main()
