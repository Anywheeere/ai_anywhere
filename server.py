from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

app = FastAPI()

@app.post('/docent')
async def docent(text:str=Form(...)):
    docent = text
    audio = './result.wav'
    return JSONResponse(content={'docent':docent, 'audio':audio})

@app.post('/audio')
async def audio(path:str=Form(...)):
    audio = './result.wav'
    return FileResponse(audio, media_type='audio/wav')
  
 
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9000)