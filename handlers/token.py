import asyncio
import time
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from aiogram import Router ,F
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message
from states.states import TokenState,EmaState,TokenInfoState
from database.models.tokens import Token
from client_api.schemas import Token as TokenSchema
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from services.calculate_rsi import process_symbol_data
from services.track_prices import track_target_prices
from services.sma_calculator import calculate_sma50
from services.ema_calculator import calculate_ema
from services.calculate_volume_changes import calculate_volume_changes
from keyboards.all_keyboards import create_cancel_keyboard,get_token_info_kb
from client_api.crypto_rank import CryptoRankCLient
from client_api.bybit_api import BybitClient
from services.update_database import update_database



token_router = Router()


@token_router.message(F.text=='/add_to_watchlist')
async def add_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_name)
    await message.answer('Введите токен, таргет-цену и направление("+"-выше, "-"-ниже) через пробел',reply_markup=create_cancel_keyboard())

@token_router.message(TokenState.token_name)
async def process_add_token(message:Message,state:FSMContext,user,config,repo:RequestsRepo):
    data=message.text
    if len(data.split(' '))!=3:
        await message.answer('Введите данные согласно шаблону')
        return



    ticker,price,direction=data.split(' ')

    token_repo=repo.tokens
    watch_list_repo=repo.watchlist
    ticker=ticker.upper()+'USDT'
    token=await token_repo.get_one_or_none(ticker=ticker)

    if not token:
        await message.answer('Токен не торгуется на бирже Bybit')
        return

    await watch_list_repo.add(user_id=user.id,ticker=ticker,target_price=float(price),direction=direction)
    await message.answer('Токен успешно добавлен в список отслеживаемых',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)
    await track_target_prices(message,repo,config,user)


@token_router.message(F.text=='/delete_from_watchlist')
async def delete_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_id)
    await message.answer('Введите ID токена',reply_markup=create_cancel_keyboard())


@token_router.message(TokenState.token_id)
async def process_delete_token(message:Message,state:FSMContext,user,repo:RequestsRepo):
    try:
        id = int(message.text)
    except ValueError:
        await message.answer('Введите корректный ID токена (целое число)')
        return
    repo=repo.watchlist
    row_count=await repo.delete({'user_id':user.id,'id':id})
    if row_count>0:
        await message.answer(f'Токен с идентификатором {id} успешно удален из списка отслеживаемых',reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f'Токен с таким идентификатором не существует в списке отслеживаемых',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)

@token_router.message(F.text=='/watchlist')
async def get_tokens_list(message:Message,user,repo:RequestsRepo):
    repo=repo.watchlist
    
    tokens=await repo.get_all(user_id=user.id)
    if not tokens:
        await message.answer('У вас нет отслеживаемых токенов')
    for token in tokens:
        await message.answer(f'id: {token.id} ticker: {token.ticker} target-price: {token.target_price} direction: {token.direction}')





@token_router.message(F.text=='Отмена')
async def cancel(message:Message,state:FSMContext):
    await state.set_state(None)
    await message.answer('Отмена',reply_markup=ReplyKeyboardRemove())


@token_router.message(TokenState.token_name)
async def process_add_to_black_list(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    ticker=data.upper()+'USDT'
    black_list_repo=repo.blacklist
    await black_list_repo.add(ticker=ticker)
    await message.answer('Токен успешно добавлен в черный список',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)



    

@token_router.message(F.text=='/token_info')
async def get_token_info(message:Message,state:FSMContext):
    await state.set_state(TokenInfoState.token_name)
    await message.answer('Введите название токена, чтобы получить информацию о токене',reply_markup=create_cancel_keyboard())  





@token_router.message(TokenInfoState.token_name)
async def process_get_token_info(message:Message,state:FSMContext,repo:RequestsRepo,user,config):
    data=message.text
    token_repo=repo.tokens
    ticker=data.upper()+'USDT'
    token:Token=await token_repo.get_one_or_none(ticker=ticker,user_id=user.id)

    if not token:
        await message.answer('Токен отсуствует в базе данных')
        return
    
    rank=token.rank
    total_supply=token.total_supply
    circulating_supply=token.circulating_supply
    market_cap=token.market_cap
    ath_value=token.ath_value
    atl_value=token.atl_value

    await message.answer(f'''Токен {token.ticker}
<b>В черном списке:</b> {token.is_in_blacklist}
<b>Позиция:</b> {rank}
<b>Таймфрейм:</b> {token.timeframe}
<b>Процент от EMA:</b> {token.percent_change_ema}
<b>Цена:</b> ${token.last_price:.8f}
<b>Total Supply:</b> {total_supply:,.0f}
<b>Circulating Supply:</b> {circulating_supply:,.0f}
<b>Market Cap:</b> ${market_cap:,.2f}
<b>ATH Value:</b> ${ath_value:,.8f}
<b>ATH Percent Change:</b> {token.ath_percent_change:,.2f}%
<b>ATL Value:</b> ${atl_value:,.8f}
<b>ATL Percent Change:</b> {token.atl_percent_change:,.2f}%
''', parse_mode='HTML', reply_markup=get_token_info_kb(token))
    await message.answer('-----------------------------------------------------------------------',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)


@token_router.message(TokenInfoState.token_timeframe)
async def process_change_timeframe(message:Message,repo:RequestsRepo,state:FSMContext,user):
    data=await state.get_data()
    timeframe=message.text.strip()
    ticker=data.get('ticker',None)

    if timeframe not in ['60','120','240','D']:
        await message.answer('Недопустимый таймфрейм')
        return



    if ticker is not None:
        if ticker=='all':
            await repo.tokens.update({'user_id':user.id},{'timeframe':timeframe})
            await message.answer(f'Значение для всех  токенов  изменено на <b>{timeframe}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
        else:
            await repo.tokens.update({'user_id':user.id,'ticker':ticker},{'timeframe':timeframe})
            await message.answer(f'Значение для токена <b>{ticker}</b> изменено на <b>{timeframe}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
    else:
        await state.set_state(None)
        await state.update_data(ticker=None)
        await message.answer('Ошибка при извлечении данных',reply_markup=ReplyKeyboardRemove())



@token_router.message(EmaState.ema_percent)
async def process_change_pump_percent(message:Message,repo:RequestsRepo,state:FSMContext,user):
    data=await state.get_data()
    ticker=data.get('ticker',None)


    try:
        percent = float(message.text)
    except ValueError:
        await message.answer('Введите корректное число')
        return

    

    if ticker is not None:
        if ticker=='all':
            await repo.tokens.update({'user_id':user.id},{'percent_change_ema':percent})
            await message.answer(f'Значение для всех токенов изменено на <b>{percent}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
        else:        
            await repo.tokens.update({'user_id':user.id,'ticker':ticker},{'percent_change_ema':percent})
            await message.answer(f'Значение для токена <b>{ticker}</b> изменено на <b>{percent}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
    else:
        await state.set_state(None)
        await state.update_data(ticker=None)
        await message.answer('Ошибка при извлечении данных',reply_markup=ReplyKeyboardRemove())

    


@token_router.message(F.text.startswith('/update_token_info'))
async def update_token_info(message:Message,repo:RequestsRepo,user,config,session):
    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Пожалуйста, укажи номер страницы. Пример: /update_token_info 2 [limit]")
        return
    
    page = int(parts[1])
    limit = 100  # значение по умолчанию

    if len(parts) >= 3:
        if parts[2].isdigit() and 1 <= int(parts[2]) <= 1000:
            limit = int(parts[2])
        else:
            await message.answer("Некорректный параметр limit. Укажи число от 1 до 1000.")
            return

    offset = (page - 1) * 100

    # Отправляем начальное сообщение с прогресс-баром
    start = time.monotonic()
    progress_message = await message.answer("Обновление токенов: ⬜⬜⬜⬜⬜ 0%")
    
    crypto_rank_client = CryptoRankCLient(config.api.crypto_rank_url)
    try:
        # Этапы и их веса для прогресса (в процентах)
        stages = {
            'fetch_tokens': 20,  # Получение токенов из базы
            'fetch_token_info': 60,  # Загрузка информации о токенах
            'update_db': 20  # Обновление базы данных
        }
        total_stages = sum(stages.values())
        current_progress = 0

        # Функция для обновления прогресс-бара
        async def update_progress(stage):
            nonlocal current_progress
            current_progress += stages[stage]
            percent = int((current_progress / total_stages) * 100)
            filled = int(percent / 20)  # 5 блоков по 20%
            bar = "🟩" * filled + "⬜" * (5 - filled)
            await progress_message.edit_text(f"Обновление токенов: {bar} {percent}%")

        # Этап 1: Получение токенов из базы данных
        token_repo = repo.tokens
        tokens_from_db: list[Token] = await token_repo.get_all(
            order_by=Token.ticker,
            offset=offset,
            limit=limit,
            is_in_blacklist=False,
        )
        await update_progress('fetch_tokens') 
        # Этап 2: Загрузка информации о токенах
        for token in tokens_from_db:
            ticker = token.ticker

            try:
                data = await crypto_rank_client.get_token_info(ticker[:-4], config)
                
           
                
            except Exception as e:
                await message.answer(f"Error fetching token info for {token.ticker}")
                break
                
                

            if not data:
                await message.answer(f"Информация о токене {ticker} не найдена")
                continue
         
            token_info = data[0]
            rank = token_info.get('rank') or 0
            total_supply = int(token_info.get('totalSupply') or 0)
            circulating_supply = int(token_info.get('circulatingSupply') or 0)
            ath_value = float(token_info.get('ath', {}).get('value') or 0)
            atl_value = float(token_info.get('atl', {}).get('value') or 0)

            # Этап 3: Обновление базы данных (выполняется внутри цикла)
            await token_repo.update(
                {'ticker': token.ticker, 'user_id': user.id},
                {
                    'rank': rank,
                    'ath_value': ath_value,
                    'atl_value': atl_value,
                    'total_supply': total_supply,
                    'circulating_supply': circulating_supply
                }
            )
        
        await update_progress('fetch_token_info')
        await update_progress('update_db')

    except Exception as e:
        print("Error fetching tokens from database",e)
        await progress_message.edit_text(f"Ошибка при получении токенов из базы данных: {str(e)}")
        await crypto_rank_client.close()
        return
    finally:
        await crypto_rank_client.close()
    
    

    end = time.monotonic()
    await progress_message.edit_text(f"Токены обновлены! Время выполнения: {end - start:.2f} секунд")

@token_router.message(F.text == '/refresh_database')
async def refresh_database(message: Message, repo, state, user, config, session):
    start = time.monotonic()
    bybit_client = BybitClient(config.api.bybit_url)
    token_repo = repo.tokens

    # Отправляем начальное сообщение с прогресс-баром
    progress_message = await message.answer("Обновление данных: ⬜⬜⬜⬜⬜ 0%")
    
    try:
        # Этапы и их веса для прогресса (в процентах)
        stages = {
            'update_db': 10,  # Обновление базы
            'fetch_vol': 15,  # Загрузка свечей для объёма
            'calc_vol': 15,   # Расчёт изменения объёма
            'fetch_sma_rsi': 15,  # Загрузка свечей для SMA/RSI
            'calc_sma': 15,   # Расчёт SMA
            'calc_rsi': 15,   # Расчёт RSI
            'fetch_ema': 5,   # Загрузка свечей для EMA
            'calc_ema': 5,    # Расчёт EMA
            'update_db_final': 5  # Финальное обновление базы
        }
        total_stages = sum(stages.values())
        current_progress = 0

        # Функция для обновления прогресс-бара
        async def update_progress(stage):
            nonlocal current_progress
            current_progress += stages[stage]
            percent = int((current_progress / total_stages) * 100)
            filled = int(percent / 20)  # 5 блоков по 20%
            bar = "🟩" * filled + "⬜" * (5 - filled)
            await progress_message.edit_text(f"Обновление данных: {bar} {percent}%")

        # Этап 1: Обновление базы данных
        await update_database(bybit_client, token_repo, user)
        await update_progress('update_db')

        # Получение списка токенов
        tokens = await token_repo.get_all()
        tokens_list = [token.ticker for token in tokens]

        # Этап 2: Загрузка свечей для изменения объёма
        tasks = [bybit_client.fetch_klines(token, 'D', 2) for token in tokens_list]
        results = await asyncio.gather(*tasks)
        await update_progress('fetch_vol')

        # Этап 3: Расчёт изменения объёма
        if results:
            with ProcessPoolExecutor(max_workers=min(len(tokens_list), 4)) as executor:
                token_percent_list = list(executor.map(calculate_volume_changes, results))
            
            for token_percent in token_percent_list:
                await token_repo.update(
                    {'ticker': token_percent['symbol'], 'user_id': user.id},
                    {'volume_change': token_percent['percent']}
                )
            await update_progress('calc_vol')

        # Этап 4: Загрузка свечей для SMA и RSI
        tasks = [bybit_client.fetch_klines(token, '240', 100) for token in tokens_list]
        results = await asyncio.gather(*tasks)
        await update_progress('fetch_sma_rsi')

        

        # Этап 5: Расчёт SMA
        if results:
            def calculate_sma_rsi(klines):
                sma_result = calculate_sma50(klines)
                rsi_result = process_symbol_data(klines)
                return {
                    'symbol': sma_result['symbol'],
                    'sma50': sma_result['sma50'],
                    'rsi14': rsi_result['rsi14']
                }

            with ThreadPoolExecutor(max_workers=min(len(tokens_list), 4)) as executor:
                combined_results = list(executor.map(calculate_sma_rsi, results))

            for result in combined_results:
                await token_repo.update(
                    {'ticker':result['symbol'],
                    'user_id':user.id},
                   {'rsi': result['rsi14'], 'sma': result['sma50']}
                )

            await update_progress('calc_sma')

        
        
       
        

       

    except Exception as e:
        print(f"Error fetching klines: {e}")
        await bybit_client.close()
        await progress_message.edit_text(f"Ошибка при обновлении данных: {str(e)}")
        return

    finally:
        await bybit_client.close()

    end = time.monotonic()
    await progress_message.edit_text(f"Данные обновлены! Время выполнения: {end - start:.2f} секунд")
