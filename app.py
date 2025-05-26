import os
from pytube import YouTube
import whisper
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import streamlit as st

# Configurações da ElevenLabs
API_KEY = "SUA_API_KEY_AQUI"
VOICE_ID = "SEU_VOICE_ID_AQUI"

def baixar_video(link):
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=False, file_extension='mp4').first()
    output_path = "videos"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    stream.download(output_path=output_path, filename="original.mp4")
    return os.path.join(output_path, "original.mp4")

def transcrever(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    return result["text"]

def traduzir_texto(texto, idioma_destino):
    return GoogleTranslator(source="auto", target=idioma_destino).translate(texto)

def gerar_audio(texto, saida_path):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"xi-api-key": API_KEY},
        json={
            "text": texto,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
    )
    with open(saida_path, "wb") as f:
        f.write(response.content)

def substituir_audio(video_path, audio_path, saida_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video_final = video.set_audio(audio)
    video_final.write_videofile(saida_path, codec="libx264", audio_codec="aac")

def main():
    st.title("Bot de Dublagem Automática de Vídeos")

    link = st.text_input("Cole o link do vídeo do YouTube:")
    idioma_destino = st.selectbox("Selecione o idioma para tradução e dublagem:", ["pt", "en", "es", "fr", "de", "it", "ru", "zh"])

    if st.button("Processar vídeo"):
        if not link:
            st.error("Por favor, insira o link do vídeo.")
            return

        with st.spinner("Baixando vídeo..."):
            video_path = baixar_video(link)

        with st.spinner("Transcrevendo áudio..."):
            texto_original = transcrever(video_path)
            st.text_area("Transcrição Original:", value=texto_original, height=150)

        with st.spinner("Traduzindo texto..."):
            texto_traduzido = traduzir_texto(texto_original, idioma_destino)
            st.text_area("Texto Traduzido:", value=texto_traduzido, height=150)

        with st.spinner("Gerando voz dublada..."):
            audio_path = "videos/voz_dublada.mp3"
            gerar_audio(texto_traduzido, audio_path)

        with st.spinner("Substituindo áudio no vídeo..."):
            saida_path = "videos/video_dublado.mp4"
            substituir_audio(video_path, audio_path, saida_path)

        st.success(f"Vídeo dublado gerado com sucesso! [Clique para baixar](./{saida_path})")

if __name__ == "__main__":
    main()
