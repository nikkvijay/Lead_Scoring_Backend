"""API router for lead management endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from app.services.csv_processor import CSVProcessor
from app.services.storage_service import StorageService
from app.core.exceptions import CSVProcessingException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """Upload leads via CSV file for scoring"""

    # Validate file format
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV format (.csv extension required)"
        )

    try:
        # Process the CSV file
        leads = await CSVProcessor.process_csv(file)

        # Store the leads (this will also clear any previous results)
        StorageService.set_leads(leads)

        logger.info(f"Successfully uploaded {len(leads)} leads from file: {file.filename}")

        return {
            "message": "Leads uploaded successfully",
            "count": len(leads),
            "filename": file.filename
        }

    except CSVProcessingException as e:
        logger.warning(f"CSV processing failed for {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error uploading leads from {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CSV file: {str(e)}"
        )