from fastapi import status

from app.core.exceptions.base import CustomException


class RecordNotFound(CustomException):
    code = status.HTTP_404_NOT_FOUND
    message_code = "record_not_found"
    message = "Record not found"


class FieldNotFound(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    message_code = "field_not_found"
    message = "Model field not found"


class RelationRecordIdNotFound(CustomException):
    code = status.HTTP_400_BAD_REQUEST
    message_code = "relation_record_id_not_found"
    message = "Relation record with given ID not found"
