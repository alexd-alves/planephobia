from fastapi import APIRouter, Request

router = APIRouter(prefix='', tags=['players'])


@router.get('/')
async def getPlayers(request: Request):
  print(request.app.db)
  return {'message': 'API Route test.'}
