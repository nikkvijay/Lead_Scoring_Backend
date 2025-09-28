"""API router for scoring and results endpoints"""

import io
import csv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging

from app.services.scoring_engine import ScoringEngine
from app.services.ai_service import AIService, AIUsageTracker
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
ai_service = AIService()
scoring_engine = ScoringEngine()
scoring_engine.set_ai_service(ai_service)  # Inject AI service dependency


@router.post("/score")
async def score_leads():
    """Execute scoring pipeline on uploaded leads against stored offer"""

    # Validate that we have both offer and leads
    offer = StorageService.get_offer()
    leads = StorageService.get_leads()

    if not offer:
        raise HTTPException(
            status_code=400,
            detail="No offer found. Please upload an offer first using POST /api/v1/offer"
        )

    if not leads:
        raise HTTPException(
            status_code=400,
            detail="No leads found. Please upload leads first using POST /api/v1/leads/upload"
        )

    try:
        logger.info(f"Starting scoring for {len(leads)} leads against offer: {offer.name}")

        # Execute scoring
        results = await scoring_engine.score_leads(leads, offer)

        # Store results
        StorageService.set_results(results)

        logger.info(f"Scoring completed successfully for {len(results)} leads")

        return {
            "message": "Scoring completed successfully",
            "leads_scored": len(results),
            "offer_name": offer.name
        }

    except Exception as e:
        logger.error(f"Scoring failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scoring failed: {str(e)}"
        )


@router.get("/results")
async def get_results():
    """Retrieve scoring results in the required format"""

    results = StorageService.get_results()

    if not results:
        return []

    # Format results according to assignment requirements
    formatted_results = [
        {
            "name": result.name,
            "role": result.role,
            "company": result.company,
            "intent": result.intent,
            "score": result.score,
            "reasoning": result.reasoning
        }
        for result in results
    ]

    logger.info(f"Returning {len(formatted_results)} scoring results")
    return formatted_results


@router.get("/results/export")
async def export_results():
    """Export scoring results as CSV file (bonus feature)"""

    results = StorageService.get_results()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No scoring results available. Please run scoring first."
        )

    # Create CSV content
    output = io.StringIO()
    fieldnames = ["name", "role", "company", "intent", "score", "reasoning"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    # Write header and data
    writer.writeheader()
    for result in results:
        writer.writerow({
            "name": result.name,
            "role": result.role,
            "company": result.company,
            "intent": result.intent,
            "score": result.score,
            "reasoning": result.reasoning
        })

    # Prepare response
    output.seek(0)
    content = output.getvalue()
    output.close()

    logger.info(f"Exporting {len(results)} results as CSV")

    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scoring_results.csv"}
    )


@router.get("/usage-stats")
async def get_usage_stats():
    """Get AI usage statistics for cost monitoring (bonus feature)"""

    stats = AIUsageTracker.get_stats()

    # Add some analysis
    total_calls = sum(provider["calls"] for provider in stats.values() if isinstance(provider, dict))
    total_cost = stats.get("openai", {}).get("estimated_cost", 0.0)

    analysis = {
        "total_ai_calls": total_calls,
        "estimated_total_cost": round(total_cost, 6),
        "cost_per_call": round(total_cost / max(total_calls, 1), 6),
        "primary_provider_recommended": "gemini" if stats["gemini"]["calls"] < 1000 else "openai"
    }

    return {
        "usage_stats": stats,
        "analysis": analysis
    }