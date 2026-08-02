from fastapi import APIRouter

router = APIRouter(prefix='/doctor', tags=['Doctor'])

@router.get('/')
async def list_doctors():
    return {'message': 'List of doctors'}

@router.get('/{doctor_id}')
async def get_doctor(doctor_id: str):
    return {'message': f'Doctor {doctor_id}'}
