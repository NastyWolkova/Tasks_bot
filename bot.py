from aiogram import Bot, Dispatcher
from aiogram.filters import Text, Command
from aiogram.types import Message
from aiogram import F
import datetime
from config_data.config import load_config

config = load_config('.env')
superadmin = config.tg_bot.admin_ids[0]
bot_token = config.tg_bot.token
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher()


users: dict = {1111111: {'current_task': 1,
                          'total_score': 0,
                          'start_time': 35,
                          'finish_time': 48,
                           1: 0,
                           2: 0,
                           3: 0}
                }

tasks: dict = {1: ('Вес рюкзака - 4 кг и ещё \nтреть собственного веса.', '6', 1),
               2: ('Если у трехзначного числа \nпоменять местами вторую \nи третью цифры, то число \nуменьшится на 9. \nЕсли поменять местами \nпервую и вторую, то \nничего не изменится.Найдите наименьшее такое число.', '110', 3),
               3: ('В мешке 20 шариков: \n6 белых, 10 черных и 4 желтых. \nСколько шариков нужно \nдостать негдлядя, чтобы \nсреди них точно \nбыло 2 белых?', '16', 2)}

def result_dict(users):
    my_dict: dict = {}
    for key, item in users.items():
        for inkey, initem in item.items():
            if inkey == 'current_task' and initem == 0:
                my_dict[key] = item
    return my_dict


@dp.message(Command(commands=['start']))
async def command_start(message: Message):
    if message.from_user.id in users and (users[message.from_user.id]['current_task'] == 0 or datetime.datetime.now() >= users[message.from_user.id]['finish_time']):
        if users[message.from_user.id]['current_task'] != 0:
            users[message.from_user.id]['current_task'] = 0
        await message.answer(f'Вы уже проходили испытания. \nВаши баллы: {users[message.from_user.id]["total_score"]}')
    elif message.from_user.id in users and users[message.from_user.id]['current_task'] != 0:
        await message.answer(f'Вы проходите испытания. '
                             f'\nДля получения следующего задания отправьте ответ, \nприкрепив его к последней из полученных задач.')
    else:
        dt1 = datetime.datetime.today()
        dt2 = dt1 + datetime.timedelta(minutes=3)
        print(dt1, dt2)
        users[message.from_user.id] = {'current_task': 0,
                                        'total_score': 0,
                                        'start_time': dt1,
                                        'finish_time': dt2,
                                        1: 0,
                                        2: 0,
                                        3: 0}
        users[message.from_user.id]['current_task'] = 1
        await message.answer(f'Тестирование состоит из 3 задач, которые надо решить за 3 минуты.'
                             f'\nЗадача №1: {tasks[1][0]}')

@dp.message(Command(commands=['help']))
async def command_help(message:Message):
    await message.answer(f'Пройти испытание можно только один раз.'
                         f'\nВремя тестирования - 3 минуты.'
                         f'\nПолучить первое задание можно командой /start.'
                         f'\nОтвет должен быть числом.'
                         f'\nВсе задачи решаются последовательно - '
                         f'\nследующее задание отправится после получения от вас ответа на предыдущее.')



@dp.message(Command(commands=['stat']), F.from_user.id == superadmin)
async def command_stat(message:Message):
    await message.answer(f'Data of players: \n{result_dict(users)}')

@dp.message(lambda x: x.text and x.text.isdigit())
async def get_answer(message: Message):
    delta_time = users[message.from_user.id]["finish_time"] - datetime.datetime.today()
    if users[message.from_user.id]['current_task'] != 0 and message.from_user.id in users:
        if datetime.datetime.now() < users[message.from_user.id]['finish_time']:
            answer = message.text
            users[message.from_user.id][users[message.from_user.id]['current_task']] = (answer, answer == tasks[users[message.from_user.id]['current_task']][1])
            if answer == tasks[users[message.from_user.id]['current_task']][1]:
                users[message.from_user.id]['total_score'] += tasks[users[message.from_user.id]['current_task']][2]
            if users[message.from_user.id]['current_task'] == list(tasks.keys())[-1]:
                users[message.from_user.id]['current_task'] = 0
                print(users)
                await message.answer(f'Это была последняя задача! \nВаши баллы: {users[message.from_user.id]["total_score"]} '
                                     f'\nВремя тестирования: {str(delta_time).split(":")[1].lstrip("0")} мин. {round(float(str(delta_time).split(":")[-1]))} сек.')
            else:
                users[message.from_user.id]['current_task'] += 1
                await message.answer(f'Ответ принят! '
                                     f'\nCледующая задача №{users[message.from_user.id]["current_task"]}: \n{tasks[users[message.from_user.id]["current_task"]][0]} '
                                     f'\nУ вас осталось: {str(delta_time).split(":")[1].lstrip("0")} мин. {round(float(str(delta_time).split(":")[-1]))} сек.')
        else:
            print(users)
            await message.answer(f'У вас закончилось время тестирования. '
                                 f'\nВаши баллы: {users[message.from_user.id]["total_score"]}')


@dp.message()
async def send_task(message: Message):
    if message.from_user.id in users:
        if datetime.datetime.now() < users[message.from_user.id]['finish_time']:
            if users[message.from_user.id]['current_task'] != 0:
                await message.answer(f'Вы проходите испытания. \nДля получения следующего задания отправьте числовой ответ.')
            else:
                await message.answer(f'Вы выполнили все задания. '
                                     f'\nВаши баллы: {users[message.from_user.id]["total_score"]}')
        else:
            await message.answer(f'У вас закончилось время тестирования. '
                                 f'\nВаши баллы: {users[message.from_user.id]["total_score"]}')
    else:
        await message.answer(f'Для начала испытания используйте команду /start')


if __name__ == '__main__':
    dp.run_polling(bot)