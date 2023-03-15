from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


def check_required_fields(data: BaseModel | dict, field_names: list):
    if isinstance(data, BaseModel):
        data = jsonable_encoder(data)
    errors = []
    for field_name in field_names:
        value = data.get(field_name)
        if not value:
            errors.append(f'`{field_name}` field is required')
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='\n'.join(errors)
        )
