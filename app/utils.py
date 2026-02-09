# utils.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, func
from sqlalchemy.exc import SQLAlchemyError
from math import ceil

async def paginated_data_count(
	db: AsyncSession,
	db_table,
	per_page: int = 10,  
	is_archived_check: bool = False):
	
	count_q = select(func.count()).select_from(db_table)
	
	if is_archived_check:
		count_q = count_q.where(db_table.is_archived.is_(False))
		total_data = (await db.execute(count_q)).scalar_one()

	else:	
		total_data = (await db.execute(count_q)).scalar_one()		
	
	total_page = ceil(total_data/per_page)

	return total_data, total_page



