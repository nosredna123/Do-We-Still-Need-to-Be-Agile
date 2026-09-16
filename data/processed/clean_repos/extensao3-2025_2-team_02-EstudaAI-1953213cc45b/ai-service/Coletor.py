from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from docling.document_converter import DocumentConverter, PdfFormatOption, AudioFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import OcrOptions, AsrPipelineOptions
from docling.datamodel import asr_model_specs
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

ocr_opts = OcrOptions(
    do_ocr=True,
    ocr_engine="rapidocr",
    lang=["eng", "por"],
)

pdf_config = PdfFormatOption(
    ocr_options=ocr_opts,
    do_table_structure=True,
    preserve_layout=False,
)

audio_config = AudioFormatOption()
pipeline_options = AsrPipelineOptions()
pipeline_options.asr_options = asr_model_specs.WHISPER_LARGE

conversor = DocumentConverter(format_options={
    InputFormat.PDF: pdf_config,
    
})

def pdf2md_extractor(file_path:str):
    result = conversor.convert(file_path)
    text = result.document.export_to_markdown() or ""
    if not text.strip():
        return ["Sem texto reconhecido no documento"]
    return text

def mp2txt_extractor(file_path:str):
        
    result = conversor.convert(file_path)
    text = result.document.export_to_markdown() or ""
    if not text.strip():
        return ["Sem texto reconhecido no documento"]
    return text

def has_audio(file_path:str):

    if file_path.lower().endswith((".mp3", ".ogg")):
        try:
            clip = AudioFileClip(file_path)
        except FileExistsError:
            return False
        
    elif file_path.lower().endswith(".mp4"):
        try:
            clip = VideoFileClip(file_path)
        except FileExistsError:
            return False
        
    if clip is not None:
        return True

def gerar_embeddings(chunk):
    return embedding_model.embed_query(chunk)