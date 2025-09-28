"""API router for offer management endpoints"""

from fastapi import APIRouter, HTTPException
import logging

from app.models.offer import OfferModel
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/offer")
async def create_offer(offer: OfferModel):
    """Store product/offer information for lead scoring"""
    try:
        # Validate and store the offer
        StorageService.set_offer(offer)

        logger.info(f"Offer stored successfully: {offer.name}")

        return {
            "message": "Offer stored successfully",
            "offer_name": offer.name,
            "value_props_count": len(offer.value_props),
            "use_cases_count": len(offer.ideal_use_cases)
        }

    except Exception as e:
        logger.error(f"Failed to store offer: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to store offer: {str(e)}"
        )