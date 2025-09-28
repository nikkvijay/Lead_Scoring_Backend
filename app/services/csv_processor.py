"""CSV processing service for lead data import"""

import pandas as pd
import logging
from typing import List
from fastapi import UploadFile

from app.models.lead import LeadModel
from app.core.exceptions import CSVProcessingException
from app.core.config import settings

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Handle CSV file processing and validation"""

    REQUIRED_COLUMNS = [
        "name", "role", "company", "industry", "location", "linkedin_bio"
    ]

    @staticmethod
    async def process_csv(file: UploadFile) -> List[LeadModel]:
        """Process uploaded CSV file and return list of validated LeadModel objects"""
        try:
            # Check file size first
            await CSVProcessor._validate_file_size(file)

            # Reset file pointer to beginning
            await file.seek(0)

            # Read CSV content
            df = pd.read_csv(file.file)
            logger.info(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")

            # Validate CSV structure
            CSVProcessor._validate_csv_structure(df)

            # Check lead count limits
            if len(df) > settings.max_leads_per_upload:
                raise CSVProcessingException(
                    f"Too many leads: {len(df)}. Maximum allowed: {settings.max_leads_per_upload}"
                )

            # Convert DataFrame to LeadModel objects
            leads = CSVProcessor._convert_to_lead_models(df)

            logger.info(f"Successfully processed {len(leads)} leads from CSV")
            return leads

        except pd.errors.EmptyDataError:
            raise CSVProcessingException("CSV file is empty")
        except pd.errors.ParserError as e:
            raise CSVProcessingException(f"CSV parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"CSV processing failed: {str(e)}")
            raise CSVProcessingException(f"CSV processing error: {str(e)}")

    @staticmethod
    async def _validate_file_size(file: UploadFile):
        """Validate uploaded file size"""
        # Check file size (convert MB to bytes)
        max_size = settings.max_file_size_mb * 1024 * 1024

        # Get file size by seeking to end
        await file.seek(0, 2)  # Seek to end
        file_size = await file.tell()
        await file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise CSVProcessingException(
                f"File too large: {file_size / (1024 * 1024):.2f}MB. "
                f"Maximum allowed: {settings.max_file_size_mb}MB"
            )

    @staticmethod
    def _validate_csv_structure(df: pd.DataFrame):
        """Validate that CSV has required columns and data"""
        missing_columns = [col for col in CSVProcessor.REQUIRED_COLUMNS if col not in df.columns]

        if missing_columns:
            raise CSVProcessingException(
                f"CSV missing required columns: {missing_columns}. "
                f"Required columns: {CSVProcessor.REQUIRED_COLUMNS}"
            )

        # Check for empty DataFrame
        if df.empty:
            raise CSVProcessingException("CSV file contains no data rows")

    @staticmethod
    def _convert_to_lead_models(df: pd.DataFrame) -> List[LeadModel]:
        """Convert DataFrame rows to LeadModel objects with validation"""
        leads = []
        errors = []

        for index, row in df.iterrows():
            try:
                # Convert row to dictionary and create LeadModel
                lead_data = row.to_dict()

                # Handle NaN values by converting to empty strings
                for key, value in lead_data.items():
                    if pd.isna(value):
                        lead_data[key] = ""

                # Create and validate LeadModel
                lead = LeadModel(**lead_data)
                leads.append(lead)

            except Exception as e:
                error_msg = f"Row {index + 2}: {str(e)}"  # +2 for 1-based indexing and header
                errors.append(error_msg)
                logger.warning(f"Skipping invalid lead at {error_msg}")

        # If too many errors, raise exception
        if len(errors) > len(df) * 0.1:  # More than 10% errors
            raise CSVProcessingException(
                f"Too many validation errors ({len(errors)} out of {len(df)} rows). "
                f"First few errors: {errors[:3]}"
            )

        if errors:
            logger.warning(f"Processed CSV with {len(errors)} validation errors: {errors}")

        if not leads:
            raise CSVProcessingException("No valid leads found in CSV file")

        return leads