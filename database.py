from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

DATABASE_URL = "sqlite+aiosqlite:///heavyweight_math.db"
engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Player(Base):
    __tablename__ = 'players'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    xp_score = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    title = Column(String, default="Beginner")
    freezes = Column(Integer, default=0) # Kolom baru untuk inventory Freeze

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_or_create_player(user_id, username):
    async with async_session() as session:
        result = await session.execute(select(Player).where(Player.user_id == user_id))
        player = result.scalars().first()
        if not player:
            player = Player(user_id=user_id, username=username)
            session.add(player)
            await session.commit()
        return player

async def update_player_score(user_id, xp_add, coins_add):
    async with async_session() as session:
        result = await session.execute(select(Player).where(Player.user_id == user_id))
        player = result.scalars().first()
        if player:
            player.xp_score += xp_add
            player.coins += coins_add
            await session.commit()

# FUNGSI BARU: Beli Item (Mendukung Gelar dan Item Consumable)
async def buy_item(user_id, item_type, item_name, price):
    async with async_session() as session:
        result = await session.execute(select(Player).where(Player.user_id == user_id))
        player = result.scalars().first()
        
        if player and player.coins >= price:
            player.coins -= price
            if item_type == "title":
                player.title = item_name
            elif item_type == "consumable":
                player.freezes += 1
            await session.commit()
            return True 
        return False

# FUNGSI BARU: Pakai Item Freeze
async def use_freeze_item(user_id):
    async with async_session() as session:
        result = await session.execute(select(Player).where(Player.user_id == user_id))
        player = result.scalars().first()
        
        if player and player.freezes > 0:
            player.freezes -= 1
            await session.commit()
            return True
        return False

async def get_leaderboard():
    async with async_session() as session:
        result = await session.execute(select(Player).order_by(Player.xp_score.desc()).limit(5))
        return result.scalars().all()