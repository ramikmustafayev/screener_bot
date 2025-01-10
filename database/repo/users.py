from database.repo.base import BaseRepo
from database.models import User
class UserRepo(BaseRepo):
    model=User
    async def get_or_create_user(
        self,
        user_id,
        name
    ):


        user=await self.session.get(User,user_id)
        if user is None:
            user=self.model(id=user_id,name=name)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        
        return user
        

        

    