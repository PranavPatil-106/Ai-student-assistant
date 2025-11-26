from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from services.file_service import get_file_service
from services.embedding_service import get_embedding_service
from services.rag_service import get_rag_service

router = APIRouter()

# Response models
class UploadResponse(BaseModel):
    status: str
    message: str
    subject: str
    unit: str
    filename: str

class StatusResponse(BaseModel):
    status: str
    subject: str
    unit: str
    embedding_done: bool
    documents: List[dict]

class GenerateResponse(BaseModel):
    status: str
    message: str

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    subject: str = Form(...),
    unit: str = Form(...),
    file: UploadFile = File(...),
    replace: str = Form("false"),  # "true" or "false" string
    background_tasks: BackgroundTasks = None
):

    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file (with replace option)
        file_service = get_file_service()
        replace_mode = replace.lower() == "true"
        save_path = file_service.save_file(subject, unit, file.filename, file_content, replace=replace_mode)
        
        # Automatically generate embeddings in background
        if background_tasks:
            embedding_service = get_embedding_service()
            background_tasks.add_task(
                embedding_service.process_and_embed_documents,
                subject,
                unit
            )
            if replace_mode:
                message = "File uploaded successfully. Previous files replaced. Embeddings are being generated automatically."
            else:
                message = "File uploaded successfully. Embeddings are being generated automatically in the background."
        else:
            message = "File uploaded successfully. Embeddings will be generated."
        
        return UploadResponse(
            status="success",
            message=message,
            subject=subject,
            unit=unit,
            filename=file.filename
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@router.get("/status", response_model=StatusResponse)
async def get_status(subject: str, unit: str):

    
    file_service = get_file_service()
    
    try:
        metadata = file_service.load_metadata(subject, unit)
        
        return StatusResponse(
            status="success",
            subject=subject,
            unit=unit,
            embedding_done=metadata.get("embedding_done", False),
            documents=metadata.get("documents", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting status: {str(e)}"
        )

@router.post("/generate-embeddings")
async def generate_embeddings(
    subject: str = Form(...),
    unit: str = Form(...),
    background_tasks: BackgroundTasks = None
):

    
    embedding_service = get_embedding_service()
    
    try:
        # Process in background if BackgroundTasks is available
        if background_tasks:
            background_tasks.add_task(
                embedding_service.process_and_embed_documents,
                subject,
                unit
            )
            return {
                "status": "processing",
                "message": "Embedding generation started in background"
            }
        else:
            # Process synchronously
            result = embedding_service.process_and_embed_documents(subject, unit)
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )

@router.post("/generate-content")
async def generate_content(
    subject: str = Form(...),
    unit: str = Form(...),
    content_type: str = Form(...)  # 'summary', 'mcq', or 'flashcards'
):

    
    file_service = get_file_service()
    
    # Check if embeddings are done
    if not file_service.is_embedding_done(subject, unit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please generate embeddings first"
        )
    
    rag_service = get_rag_service()
    
    try:
        if content_type == "summary":
            result = rag_service.generate_summary(subject, unit)
        elif content_type == "mcq":
            result = rag_service.generate_mcqs(subject, unit, count=10)
        elif content_type == "flashcards":
            result = rag_service.generate_flashcards(subject, unit, count=10)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content_type. Must be 'summary', 'mcq', or 'flashcards'"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )

@router.get("/subjects")
async def get_subjects():

    file_service = get_file_service()
    subjects = file_service.get_all_subjects()
    return {"subjects": subjects}

@router.get("/units/{subject}")
async def get_units(subject: str):

    file_service = get_file_service()
    units = file_service.get_units_for_subject(subject)
    return {"subject": subject, "units": units}
