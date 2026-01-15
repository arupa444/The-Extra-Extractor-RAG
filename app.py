from fastapi import FastAPI, APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from typing import Annotated, Literal, Optional, List, Dict
from pydantic import BaseModel, Field, field_validator, computed_field, AnyUrl, EmailStr
import requests
import shutil
import tempfile
from pathlib import Path
import os

from utils.dataExtrationAndRendering import DataExtAndRenderingService

from config.config_file import Config

from utilsForRAG import agenticChunker, ragAnswer, DBretrieve, chunkMemoryIndex

from dotenv import load_dotenv

from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool



load_dotenv()
config = Config()
#
app = FastAPI(title="Multi Input Rag END-TO-END")
#
#
#
# rawDataDir = DataExtAndRenderingService.websiteDataExtration("https://parivahan.gov.in/")
# rawDataDir = DataExtAndRenderingService.anyThingButJSOrSPA("https://parivahan.gov.in/")
# print(rawDataDir)
# config.storeMDContent(rawDataDir)

# ac = agenticChunker.AgenticChunker()
#
# # 1. Raw Text Input
# raw_text = """
# The Apollo program was a series of spaceflight missions conducted by NASA between 1961 and 1972.
# It succeeded in landing the first humans on the Moon in 1969.
# Neil Armstrong and Buzz Aldrin walked on the lunar surface while Michael Collins orbited above.
# Meanwhile, in the ocean depths, the blue whale is the largest animal known to have ever lived.
# It can reach lengths of up to 29.9 meters and weigh 199 metric tons.
# Blue whales feed almost exclusively on krill.
# """
#
# # 2. Ingest Data (Layer 1)
# propositions = ac.generate_propositions(raw_text)
# ac.add_propositions(propositions)
# ac.pretty_print_chunks()
#
# # 3. Build Memory Index (Layer 3)
# #    We initialize this AFTER ingestion is done.
# print("\n[bold blue]Building Memory Index...[/bold blue]")
# memory_index = chunkMemoryIndex.ChunkMemoryIndex(dim=768)
#
# for chunk_id, chunk_data in ac.chunks.items():
#     memory_index.add(chunk_id, chunk_data['embedding'])
#
# # 4. Retrieval (Layer 4)
# query = "Who walked on the moon?"
# retrieved_docs = DBretrieve.Retrieve.retrieve(query, ac, memory_index)
#
# print(f"\n[green]Top Result:[/green] {retrieved_docs[0]['title']} (Score: {retrieved_docs[0]['score']:.4f})")
#
# # 5. RAG Answer (Layer 5)
# print("\n[bold blue]Generating Answer...[/bold blue]")
# final_answer = ragAnswer.Answer.answer(query, retrieved_docs, ac.llm)
# print(f"\n[bold]Final Answer:[/bold]\n{final_answer}")
# config.save_results(propositions)
# #
# #


class ChatRequest(BaseModel):
    query: str
    saved_location: str



# OCR Part....

@app.post("/OCR_On_Single_Upload", summary="You can upload any kind of source file and get the OCR output....")
async def OCR_On_Single_Upload(file: UploadFile = File(...)):

    file_suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(tmp_path)
        savedLocation = config.storeMDContent(markdown_content)
        return {"markdown_content": markdown_content, "SavedLocation": savedLocation}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/OCR_On_Folder_Or_Multiple_file_Uploads", summary="Upload a folder or select multiple files and collectively perform OCR and save all the results in a json......")
async def OCR_On_Folder_Or_Multiple_file_Upload(
        files: List[UploadFile] = File(...)
):
    results = []
    with tempfile.TemporaryDirectory() as temp_dir:

        for file in files:
            file_result = {}
            file_path = None

            try:
                safe_filename = Path(file.filename).name
                file_path = os.path.join(temp_dir, safe_filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(file_path)

                file_result = {
                    "filename": file.filename,
                    "status": "success",
                    "markdown_content": markdown_content
                }

            except Exception as e:
                file_result = {
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                }

            results.append(file_result)

            await file.close()

    config.jsonStoreForMultiDoc(results)
    return {"results": results}


@app.post("/OCR_On_nonJS_nonSPA_Website", summary="OCR on Non js and Non SPA website")
async def OCR_On_nonJS_nonSPA_Website(webLink: str = Form(...)):
    try:
        markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(webLink)
        config.storeMDContent(markdown_content)
        return {"markdown_content": markdown_content}
    except Exception as e:
        return {"error": str(e)}


@app.post("/Multiple_OCRs_On_nonJS_nonSPA_Website", summary="Multiple OCRs on Non js and Non SPA website")
async def Multiple_OCRs_On_nonJS_nonSPA_Website(
        webLinks: List[str] = Form(...)
):

    cleaned_links = []
    for entry in webLinks:
        cleaned_links.extend([url.strip() for url in entry.split(',') if url.strip()])

    webLinks = cleaned_links

    results = []

    for webLink in webLinks:
        web_result = {}
        try:
            markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(webLink)
            web_result = {
                "webName": webLink,
                "markdownContent": markdown_content,
                "status": "success",
            }

        except Exception as e:
            web_result = {
                "filename": webLink,
                "status": "error",
                "error": str(e)
            }

        results.append(web_result)

    config.jsonStoreForMultiDoc(results)
    return {"results": results}


@app.post("/OCR_On_JS_SPA_Website", summary="OCR on JS SPA website")
async def OCR_On_JS_SPA_Website(webLink: str = Form(...)):
    try:
        print(webLink)
        markdown_content = await DataExtAndRenderingService.websiteDataExtrationJs(webLink)
        config.storeMDContent(markdown_content)
        return {"markdown_content": markdown_content}
    except Exception as e:
        return {"error": str(e)}



@app.post("/Multiple_OCRs_On_JS_SPA_Websites", summary="Multiple OCRs on JS SPA website")
async def Multiple_OCRs_On_JS_SPA_Websites(
        webLinks: List[str] = Form(...)
):

    cleaned_links = []
    for entry in webLinks:
        cleaned_links.extend([url.strip() for url in entry.split(',') if url.strip()])

    webLinks = cleaned_links
    results = []

    for webLink in webLinks:
        web_result = {}
        try:
            markdown_content = await DataExtAndRenderingService.websiteDataExtrationJs(webLink)
            web_result = {
                "webName": webLink,
                "markdownContent": markdown_content,
                "status": "success",
            }

        except Exception as e:
            web_result = {
                "filename": webLink,
                "status": "error",
                "error": str(e)
            }

        results.append(web_result)

    config.jsonStoreForMultiDoc(results)
    return {"results": results}







# RAG Part....

@app.post("/RAG_On_Single_Upload", summary="You can upload any kind of source file and get the RAG output....")
async def RAG_On_Single_Upload(file: UploadFile = File(...), query: str = Form(...)):

    file_suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        # 0
        markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(tmp_path)
        savedLocation = config.storeMDContent(markdown_content)
        ac = agenticChunker.AgenticChunker()

        # 1. Raw Text Input
        raw_text = markdown_content

        # 2. Ingest Data (Layer 1)
        propositions = ac.generate_propositions(raw_text)

        print(f"\n[bold cyan]Generated {len(propositions)} Propositions[/bold cyan]")


        ac.add_propositions(propositions)
        ac.pretty_print_chunks()

        # 3. Build Memory Index (Layer 3)
        #    We initialize this AFTER ingestion is done.
        print("\n[bold blue]Building Memory Index...[/bold blue]")
        memory_index = chunkMemoryIndex.ChunkMemoryIndex(dim=768)

        for chunk_id, chunk_data in ac.chunks.items():
            memory_index.add(chunk_id, chunk_data['embedding'])

        # 4. Retrieval (Layer 4)
        retrieved_docs = DBretrieve.Retrieve.retrieve(query, ac, memory_index)

        print(f"\n[green]Top Result:[/green] {retrieved_docs[0]['title']} (Score: {retrieved_docs[0]['score']:.4f})")

        # 5. RAG Answer (Layer 5)
        print("\n[bold blue]Generating Answer...[/bold blue]")


        final_answer = ragAnswer.Answer.answer(query, retrieved_docs, ac.llm)
        print(f"\n[bold]Final Answer:[/bold]\n{final_answer}")



        config.save_results(savedLocation, propositions, ac.chunks, memory_index)
        return {"Top Result": f"{retrieved_docs[0]['title']} (Score: {retrieved_docs[0]['score']:.4f})" ,"Final Answer":final_answer, "markdown_content": markdown_content, "SavedLocation": savedLocation}


    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/RAG_On_Folder_Or_Multiple_file_Uploads", summary="Upload a folder or select multiple files and collectively perform RAG and save all the results in a json......")
async def RAG_On_Folder_Or_Multiple_file_Upload(
        files: List[UploadFile] = File(...)
):
    results = []
    with tempfile.TemporaryDirectory() as temp_dir:

        for file in files:
            file_result = {}
            file_path = None

            try:
                safe_filename = Path(file.filename).name
                file_path = os.path.join(temp_dir, safe_filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(file_path)

                file_result = {
                    "filename": file.filename,
                    "status": "success",
                    "markdown_content": markdown_content
                }

            except Exception as e:
                file_result = {
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                }

            results.append(file_result)

            await file.close()

    config.jsonStoreForMultiDoc(results)
    return {"results": results}


@app.post("/RAG_On_nonJS_nonSPA_Website", summary="RAG on Non js and Non SPA website")
async def RAG_On_nonJS_nonSPA_Website(webLink: str = Form(...)):
    try:
        markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(webLink)
        config.storeMDContent(markdown_content)
        return {"markdown_content": markdown_content}
    except Exception as e:
        return {"error": str(e)}


@app.post("/RAG_On_Multiple_nonJS_nonSPA_Website", summary="RAG on Multiple Non js and Non SPA website")
async def RAG_On_Multiple_nonJS_nonSPA_Website(
        webLinks: List[str] = Form(...)
):

    cleaned_links = []
    for entry in webLinks:
        cleaned_links.extend([url.strip() for url in entry.split(',') if url.strip()])

    webLinks = cleaned_links

    results = []

    for webLink in webLinks:
        web_result = {}
        try:
            markdown_content = await DataExtAndRenderingService.anyThingButJSOrSPA(webLink)
            web_result = {
                "webName": webLink,
                "markdownContent": markdown_content,
                "status": "success",
            }

        except Exception as e:
            web_result = {
                "filename": webLink,
                "status": "error",
                "error": str(e)
            }

        results.append(web_result)

    config.jsonStoreForMultiDoc(results)
    return {"results": results}


@app.post("/RAG_On_JS_SPA_Website", summary="RAG on JS SPA website")
async def RAG_On_JS_SPA_Website(webLink: str = Form(...)):
    try:
        print(webLink)
        markdown_content = await DataExtAndRenderingService.websiteDataExtrationJs(webLink)
        config.storeMDContent(markdown_content)
        return {"markdown_content": markdown_content}
    except Exception as e:
        return {"error": str(e)}



@app.post("/RAG_On_Multiple_JS_SPA_Websites", summary="RAG on Multiple JS SPA website")
async def RAG_On_Multiple_JS_SPA_Websites(
        webLinks: List[str] = Form(...)
):

    cleaned_links = []
    for entry in webLinks:
        cleaned_links.extend([url.strip() for url in entry.split(',') if url.strip()])

    webLinks = cleaned_links
    results = []

    for webLink in webLinks:
        web_result = {}
        try:
            markdown_content = await DataExtAndRenderingService.websiteDataExtrationJs(webLink)
            web_result = {
                "webName": webLink,
                "markdownContent": markdown_content,
                "status": "success",
            }

        except Exception as e:
            web_result = {
                "filename": webLink,
                "status": "error",
                "error": str(e)
            }

        results.append(web_result)

    config.jsonStoreForMultiDoc(results)
    return {"results": results}



@app.post("/Chat_With_Saved_Data", summary="Chat with a previously uploaded/processed file")
async def chat_with_saved_data(request: ChatRequest):
    try:
        ac = agenticChunker.AgenticChunker()

        # 2. Load Data from Disk
        # This is fast (reading JSON)
        print(f"[INFO] Loading data from: {request.saved_location}")
        loaded = ac.load_chunks(request.saved_location)

        if not loaded:
            raise HTTPException(status_code=404, detail="Saved chunks not found at this location.")

        # 3. Rebuild Memory Index (In-Memory)
        # We must feed the embeddings back into FAISS
        print("[INFO] Rebuilding FAISS Index...")
        memory_index = chunkMemoryIndex.ChunkMemoryIndex(dim=768)

        for chunk_id, chunk_data in ac.chunks.items():
            if "embedding" in chunk_data:
                memory_index.add(chunk_id, chunk_data['embedding'])

        # 4. Retrieval (Layer 4)
        # Run in threadpool to prevent blocking
        retrieved_docs = await run_in_threadpool(
            DBretrieve.Retrieve.retrieve,
            request.query,
            ac,
            memory_index
        )

        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the uploaded document.",
                "sources": []
            }

        # 5. Generate Answer (Layer 5)
        print("[INFO] Generating Answer...")
        final_answer = await run_in_threadpool(
            ragAnswer.Answer.answer,
            request.query,
            retrieved_docs,
            ac.llm
        )

        # 6. Return Response
        return {
            "query": request.query,
            "final_answer": final_answer,
            "top_sources": [
                {"title": doc['title'], "score": doc['score']} for doc in retrieved_docs
            ]
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}