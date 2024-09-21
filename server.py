import uvicorn, json
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from docent import AiDocent
from docent_tts import AiSpeech

app = FastAPI()
aispeech = AiSpeech()

@app.get('/docent')
async def docent(text:dict=Body(...)):
    loc = text.get('text')
    aidocent = AiDocent(loc)
    aidocent_text = aidocent.run_llm()
    aispeech.inference(aidocent_text)
    speech_file = 'output.wav'
    return JSONResponse(content={'docent':aidocent_text, 'audio':speech_file})

@app.get('/audio')
async def audio(path:dict=Body(...)):
    audio = path.get('path')
    return FileResponse(audio, media_type='audio/wav')
  
 
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9000)