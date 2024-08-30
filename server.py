from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
import uvicorn, json

app = FastAPI()

@app.get('/docent')
async def docent(text:dict=Body(...)):
    docent = text.get('text')
    audio = './result.wav'
    return JSONResponse(content={'docent':docent, 'audio':audio})

@app.get('/audio')
async def audio(path:dict=Body(...)):
    audio = path.get('path')
    return FileResponse(audio, media_type='audio/wav')
  
 
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9000)