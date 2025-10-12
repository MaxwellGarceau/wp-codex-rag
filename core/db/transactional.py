from functools import wraps

from core.db import session


class Transactional:
    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return result

        return _transactional
